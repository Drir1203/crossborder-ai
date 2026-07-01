"""VeyaShip - 1688 Product Scraper.

Two-tier strategy:
1. Onebound API (official data channel, configured via admin UI)
2. Direct scrape (httpx + curl_cffi fallback)
"""

import re
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup


async def scrape_1688(url: str, api_key: str = "", api_secret: str = "") -> dict[str, Any]:
    """Scrape product info from a 1688 product page.

    Args:
        url: 1688 product page URL.
        api_key: Onebound API Key (configured by admin in settings page).
        api_secret: Onebound API Secret.

    Returns:
        Structured dict with: title, main_image_url, price, sales_count, shop_name.

    Raises:
        ValueError: If URL is invalid.
        RuntimeError: If all methods fail.
    """
    if "1688.com" not in url:
        raise ValueError("仅支持 1688.com 的商品链接")

    offer_id = _extract_offer_id(url)
    if not offer_id:
        raise ValueError("无法从链接中识别商品 ID")

    # Tier 1: Onebound API (official data channel)
    if api_key:
        data = await _try_onebound_api(offer_id, api_key, api_secret)
        if data:
            return {"url": url, **data}

    # Tier 2: Direct scrape (httpx + curl_cffi)
    html = await _try_direct_scrape(url)
    if html and not _is_blocked(html):
        data = _parse_html(html)
        if data.get("title"):
            return {"url": url, **data}

    # 都没抓到
    if api_key:
        raise RuntimeError("scrape_failed", "获取商品信息失败，请确认 API Key 是否正确")
    raise RuntimeError(
        "scrape_failed",
        "1688 对自动化访问有严格限制，当前无法自动抓取。请先在「设置」页面配置数据接口。",
    )


def _extract_offer_id(url: str) -> str | None:
    m = re.search(r"/offer/(\d+)", url)
    return m.group(1) if m else None


# ── Tier 1: Onebound API ─────────────────────────────────────────

ONEBOUND_URL = "https://api-gw.onebound.cn/1688/item_get"


async def _try_onebound_api(offer_id: str, api_key: str, api_secret: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(ONEBOUND_URL, params={
                "key": api_key,
                "secret": api_secret,
                "num_iid": offer_id,
            })
            if resp.status_code != 200:
                return None
            result = resp.json()
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
        return None


# ── Tier 2: Direct scrape ────────────────────────────────────────

async def _try_direct_scrape(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.1688.com/",
                "Accept-Language": "zh-CN,zh;q=0.9",
            })
            resp.raise_for_status()
            if resp.text and len(resp.text) > 5000:
                return resp.text
    except Exception:
        pass

    try:
        from curl_cffi.requests import AsyncSession as CurlSession
        async with CurlSession() as s:
            resp = await s.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.1688.com/",
            }, impersonate="chrome120")
            if resp.text and len(resp.text) > 5000:
                return resp.text
    except Exception:
        pass

    return None


# ── Helpers ──────────────────────────────────────────────────────

def _is_blocked(html: str) -> bool:
    return len(html.strip()) < 500 or ("验证码" in html and "x5sec" in html)


def _safe_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> int | None:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _parse_html(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    result = {}
    meta = soup.find("meta", attrs={"property": "og:title"})
    if meta and meta.get("content"):
        result["title"] = meta["content"].split(" - ")[0].strip()
    if not result.get("title"):
        for sel in ["h1[class*='title']", "h1", "[class*='offer-title']"]:
            tag = soup.select_one(sel)
            if tag and (t := tag.get_text(strip=True)) and len(t) > 5:
                result["title"] = t
                break
    meta = soup.find("meta", attrs={"property": "og:image"})
    if meta and meta.get("content"):
        result["main_image_url"] = meta["content"]
    for sel in ["[class*='price']", "[itemprop='price']"]:
        tag = soup.select_one(sel)
        if tag:
            nums = re.findall(r"[\d.]+", tag.get_text(strip=True))
            if nums:
                result["price"] = _safe_float(nums[0])
                break
    for sel in ["[class*='shop-name']", "[class*='company']"]:
        tag = soup.select_one(sel)
        if tag and (t := tag.get_text(strip=True)) and len(t) > 1:
            result["shop_name"] = t
            break
    return result
