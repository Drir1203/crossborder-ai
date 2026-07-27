"""VeyaShip - 1688 商品爬虫

【全栈学习者必读】
这个文件展示了后端的"多源降级策略"：
1. 首选：Onebound API（官方数据接口，稳定高效）
2. 备选：httpx 直接抓取（解析 HTML）
3. 最终：curl_cffi 模拟浏览器（处理反爬）

为什么做多层降级？
- 跨境电商场景中，1688 有严格的反爬机制
- 没有"一劳永逸"的抓取方案，需要多管齐下
- Onebound 是付费 API，不是所有用户都配置了

数据流向：
  用户粘贴 1688 链接 → products.py 路由 → 本爬虫
  → {优先 API} 或 {降级抓取}
  → 返回结构化数据 → 存入数据库
"""

import re
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup
from app.core.config import settings


async def scrape_1688(
    url: str,
    api_key: str = "",
    api_secret: str = "",
) -> dict[str, Any]:
    # 优先用 .env 配置的平台级 Key，未配置则用调用方传入的 Key
    if not api_key and settings.ONEBOUND_API_KEY:
        api_key = settings.ONEBOUND_API_KEY
        api_secret = settings.ONEBOUND_API_SECRET or api_secret
    """【核心】抓取 1688 商品信息

    执行策略（双保险）：
    1️⃣ Onebound API：如果管理员配置了 API Key，优先用官方接口
    2️⃣ 直接抓取：API 失败或未配置时，模拟浏览器访问页面
    3️⃣ 报错：全部失败时，给用户清晰的错误指引

    Args:
        url: 1688 商品详情页 URL
        api_key: Onebound API Key（从数据库读取，管理员在设置页面配置）
        api_secret: Onebound API Secret

    Returns:
        dict: 包含 title、main_image_url、price、sales_count、shop_name

    Raises:
        ValueError: URL 格式不对（不是 1688 链接）
        RuntimeError: 所有方案都失败了
    """
    # ── 1. 校验链接 ─────────────────────────────────────────
    # 只支持 1688 链接，淘宝/拼多多不走这个爬虫
    if "1688.com" not in url:
        raise ValueError("仅支持 1688.com 的商品链接")

    # 从链接中提取商品 ID（如 https://detail.1688.com/offer/123456.html → 123456）
    offer_id = _extract_offer_id(url)
    if not offer_id:
        raise ValueError("无法从链接中识别商品 ID")

    # ── 2. 方案一：Onebound API ─────────────────────────────
    # Onebound 是第三方 1688 数据接口服务商
    # 需要管理员在设置页配置 API Key
    # 优势：稳定可靠，不受反爬限制
    if api_key:
        data = await _try_onebound_api(offer_id, api_key, api_secret)
        if data:
            return {"url": url, **data}

    # ── 3. 方案二：直接抓取 HTML ────────────────────────────
    # API 失败或没配置时，尝试直接抓取页面
    # 先用 httpx（轻量级 HTTP 客户端）
    # 如果被拦截，用 curl_cffi（模拟浏览器指纹）
    html = await _try_direct_scrape(url)
    if html and not _is_blocked(html):
        data = _parse_html(html)
        if data.get("title"):
            return {"url": url, **data}

    # ── 4. 全部失败 ─────────────────────────────────────────
    # 给用户清晰的错误指引，而不是模糊的"抓取失败"
    if api_key:
        raise RuntimeError(
            "scrape_failed",
            "获取商品信息失败，请确认 API Key 是否正确",
        )
    raise RuntimeError(
        "scrape_failed",
        "1688 对自动化访问有严格限制，当前无法自动抓取。请先在「设置」页面配置数据接口。",
    )


def _extract_offer_id(url: str) -> str | None:
    """从 1688 URL 中提取商品 ID

    支持的 URL 格式：
    - https://detail.1688.com/offer/123456789.html
    - https://detail.1688.com/offer/123456789.html?spm=a...
    """
    m = re.search(r"/offer/(\d+)", url)
    return m.group(1) if m else None


# ════════════════════════════════════════════════════════════════
# 方案一：Onebound API
# ════════════════════════════════════════════════════════════════

ONEBOUND_URL = "https://api-gw.onebound.cn/1688/item_get"


async def _try_onebound_api(
    offer_id: str,
    api_key: str,
    api_secret: str,
) -> dict | None:
    """尝试调用 Onebound API 获取商品数据

    Onebound 的 API 格式：
    GET https://api-gw.onebound.cn/1688/item_get?key=xxx&secret=xxx&num_iid=xxx

    Returns:
        dict（标题/图片/价格/销量/店铺）或 None（失败时）

    为什么这里用 try/except 而不是 raise？
    - 这只是"方案一"的尝试，失败了还有方案二
    - 如果抛异常，整个请求就断了，必须用 try 捕获
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                ONEBOUND_URL,
                params={
                    "key": api_key,
                    "secret": api_secret,
                    "num_iid": offer_id,
                },
            )
            if resp.status_code != 200:
                return None

            result = resp.json()
            # code=0 表示 API 调用成功
            if result.get("code") != 0:
                return None

            data = result.get("data", {})
            return {
                "title": data.get("title"),
                "main_image_url": data.get("pic_url") or data.get("main_pic"),
                "price": _safe_float(data.get("price") or data.get("batch_price")),
                "sales_count": _safe_int(data.get("sales") or data.get("sales_30day")),
                "shop_name": data.get("shop_name") or data.get("nick"),
            }
    except Exception:
        # 任何异常都不抛，让上层走降级方案
        return None


# ════════════════════════════════════════════════════════════════
# 方案二：直接抓取 HTML
# ════════════════════════════════════════════════════════════════

async def _try_direct_scrape(url: str) -> str | None:
    """尝试直接抓取 1688 页面 HTML

    两层策略：
    1. httpx：标准 HTTP 客户端，速度快
    2. curl_cffi：模拟 Chrome 浏览器指纹，可以绕过部分反爬

    为什么要模拟 User-Agent？
    - 1688 会检查请求的 User-Agent，非浏览器请求被拒绝
    - Chrome/120 是目前主流版本，模拟它通过率最高
    """
    # ── 第一层：httpx ────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://www.1688.com/",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
            )
            resp.raise_for_status()
            if resp.text and len(resp.text) > 5000:
                return resp.text
    except Exception:
        pass

    # ── 第二层：curl_cffi（模拟浏览器指纹） ────────────
    # curl_cffi 能模拟 TLS 指纹，看起来就是真正的 Chrome
    # 1688 的反爬系统会检查 TLS 握手特征
    try:
        from curl_cffi.requests import AsyncSession as CurlSession

        async with CurlSession() as s:
            resp = await s.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://www.1688.com/",
                },
                impersonate="chrome120",  # 模拟 Chrome 120 的 TLS 指纹
            )
            if resp.text and len(resp.text) > 5000:
                return resp.text
    except Exception:
        pass

    return None


# ════════════════════════════════════════════════════════════════
# 辅助函数
# ════════════════════════════════════════════════════════════════


def _is_blocked(html: str) -> bool:
    """检测是否被反爬机制拦截

    1688 被拦截的典型特征：
    - HTML 非常短（< 500 字符）
    - 页面包含"验证码"或"x5sec"关键字
    """
    return len(html.strip()) < 500 or ("验证码" in html and "x5sec" in html)


def _safe_float(v: Any) -> float | None:
    """安全地将值转为 float，失败返回 None"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> int | None:
    """安全地将值转为 int，失败返回 None"""
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _parse_html(html: str) -> dict[str, Any]:
    """从 HTML 中解析商品信息

    使用 BeautifulSoup 解析 HTML，提取关键数据。
    各种选择器（selector）是"碰运气"式的——不同页面结构不同。
    这就是为什么 API 方案比 HTML 解析更可靠。

    Returns:
        dict: 可能包含 title、main_image_url、price、shop_name
    """
    soup = BeautifulSoup(html, "lxml")
    result = {}

    # ── 提取标题 ────────────────────────────────────────
    # 优先从 og:title meta 标签获取（Open Graph 标准）
    meta = soup.find("meta", attrs={"property": "og:title"})
    if meta and meta.get("content"):
        result["title"] = meta["content"].split(" - ")[0].strip()

    # 如果 og:title 没抓到，试各种 CSS 选择器
    if not result.get("title"):
        for sel in ["h1[class*='title']", "h1", "[class*='offer-title']"]:
            tag = soup.select_one(sel)
            if tag and (t := tag.get_text(strip=True)) and len(t) > 5:
                result["title"] = t
                break

    # ── 提取主图 ────────────────────────────────────────
    meta = soup.find("meta", attrs={"property": "og:image"})
    if meta and meta.get("content"):
        result["main_image_url"] = meta["content"]

    # ── 提取价格 ────────────────────────────────────────
    for sel in ["[class*='price']", "[itemprop='price']"]:
        tag = soup.select_one(sel)
        if tag:
            nums = re.findall(r"[\d.]+", tag.get_text(strip=True))
            if nums:
                result["price"] = _safe_float(nums[0])
                break

    # ── 提取店铺名 ──────────────────────────────────────
    for sel in ["[class*='shop-name']", "[class*='company']"]:
        tag = soup.select_one(sel)
        if tag and (t := tag.get_text(strip=True)) and len(t) > 1:
            result["shop_name"] = t
            break

    return result
