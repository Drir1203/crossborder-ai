"""CAP-01 · 1688 抓取健壮性与平台级 Key 就绪体验测试（backend/app/services/scraper.py + /products/scrape）

覆盖：
1. 平台未配置 Key → 就绪校验 400 中文（service_not_configured）
2. GET /products/scrape/status 就绪探针（false → true）
3. 无效 URL → InvalidUrlError / invalid_url 中文映射（且兼容旧 ValueError）
4. 商品不存在/下架 → product_not_found（404）
5. Onebound 失败 → 降级直抓成功 → data_source=direct
6. 全部失败 → 4xx 分类错误，绝不 500
7. 字段兜底：价格缺失 → None，不整单失败
8. 明显异常（价格 0 / 标题空）→ parse_error
9. 直抓被风控 → anti_bot（单元层）
"""

import pytest
from httpx import AsyncClient

from app.models.system_config import SystemConfig
from app.services import scraper as scraper_mod
from app.services.scraper import (
    AntiBotError,
    InvalidUrlError,
    ProductNotFoundError,
    ServiceUnavailableError,
    ScrapeError,
    scrape_1688,
)

# 一个结构上合法的 1688 商品详情链接（测试中不会发真实网络请求）
OFFER_URL = "https://detail.1688.com/offer/610699151352.html"


async def _configure_onebound(db) -> None:
    """向 SystemConfig 写入平台级 Onebound 凭据（明文即可，decrypt 兼容）。"""
    db.add(SystemConfig(key="onebound_api_key", value="test-key"))
    db.add(SystemConfig(key="onebound_api_secret", value="test-secret"))
    await db.flush()


# ── R1 平台级 Key 未配置 → 就绪校验 ──────────────────────────────

@pytest.mark.asyncio
async def test_scrape_rejected_when_service_not_configured(client, auth_headers):
    """平台未配置 Onebound key → 400 中文引导，不发网络请求。"""
    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "service_not_configured"
    assert "客服" in detail["message"] or "开通" in detail["message"]


@pytest.mark.asyncio
async def test_scrape_status_probe_tracks_configuration(client, auth_headers, db_session):
    """就绪探针：未配置 → false；写入 Key 后 → true。"""
    resp = await client.get("/api/v1/products/scrape/status", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["configured"] is False

    await _configure_onebound(db_session)
    resp = await client.get("/api/v1/products/scrape/status", headers=auth_headers)
    assert resp.json()["configured"] is True


# ── R2 无效 URL 分类 ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scrape_non_1688_url_maps_to_invalid_url(client, auth_headers, db_session):
    """Key 已配置但链接非 1688 → 400 invalid_url，且不发网络请求。"""
    await _configure_onebound(db_session)
    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": "https://taobao.com/item/123.html"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "invalid_url"
    assert "1688" in detail["message"]


@pytest.mark.asyncio
async def test_invalid_url_error_is_value_error_compatible():
    """InvalidUrlError 需兼容既有代码 `except ValueError`（安全测试不回归）。"""
    with pytest.raises(ValueError) as excinfo:
        await scrape_1688("https://taobao.com/item/123.html")
    assert isinstance(excinfo.value, InvalidUrlError)
    assert isinstance(excinfo.value, ScrapeError)
    assert "1688" in str(excinfo.value)


# ── R3 商品不存在 / 已下架 → 404 ─────────────────────────────────

@pytest.mark.asyncio
async def test_scrape_product_not_found_returns_404(
    client, auth_headers, db_session, monkeypatch
):
    """Onebound 暂时失败 + 直抓发现已下架 → 404 product_not_found（不 500）。"""
    await _configure_onebound(db_session)

    async def onebound_down(offer_id, api_key, api_secret):
        raise ServiceUnavailableError("数据服务暂时不可用，请稍后再试")

    async def direct_gone(url):
        raise ProductNotFoundError("该商品不存在或已下架，请换一个 1688 商品链接试试")

    monkeypatch.setattr(scraper_mod, "_fetch_onebound", onebound_down)
    monkeypatch.setattr(scraper_mod, "_direct_fetch", direct_gone)

    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert detail["code"] == "product_not_found"
    assert ("下架" in detail["message"]) or ("不存在" in detail["message"])


# ── R4 Onebound 失败 → 降级直抓成功 → data_source=direct ─────────

@pytest.mark.asyncio
async def test_onebound_failure_falls_back_to_direct(
    client, auth_headers, db_session, monkeypatch
):
    """Onebound 暂时不可用 → 自动降级直抓 → 201 且 data_source=direct。"""
    await _configure_onebound(db_session)

    async def onebound_down(offer_id, api_key, api_secret):
        raise ServiceUnavailableError("数据服务暂时不可用，请稍后再试")

    async def direct_ok(url):
        return {
            "title": "夏季新款女装连衣裙",
            "price": "¥9.90",
            "sales_count": "已售123件",
            "shop_name": "优质源头工厂",
            "main_image_url": "//img.alicdn.com/abc123.jpg",
        }

    monkeypatch.setattr(scraper_mod, "_fetch_onebound", onebound_down)
    monkeypatch.setattr(scraper_mod, "_direct_fetch", direct_ok)

    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["data_source"] == "direct"
    product = body["product"]
    assert product["title"] == "夏季新款女装连衣裙"
    assert product["price"] == 9.9
    assert product["sales_count"] == 123
    assert product["shop_name"] == "优质源头工厂"
    # 协议相对图片地址 → 归一为 https
    assert product["main_image_url"].startswith("https://")


# ── R5 全部失败 → 4xx 分类错误，不 500 ───────────────────────────

@pytest.mark.asyncio
async def test_all_sources_failed_returns_4xx_not_500(
    client, auth_headers, db_session, monkeypatch
):
    """Onebound 与直抓都失败 → 返回分类错误（保留数据服务分类），绝不 500。"""
    await _configure_onebound(db_session)

    async def onebound_down(offer_id, api_key, api_secret):
        raise ServiceUnavailableError("数据服务暂时不可用，请稍后再试")

    async def direct_down(url):
        raise AntiBotError("1688 有访问保护，暂时无法自动抓取，请稍后重试")

    monkeypatch.setattr(scraper_mod, "_fetch_onebound", onebound_down)
    monkeypatch.setattr(scraper_mod, "_direct_fetch", direct_down)

    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert 400 <= resp.status_code < 500
    detail = resp.json()["detail"]
    assert detail["code"] == "service_unavailable"
    assert detail["message"]


# ── R6 字段兜底 / 明显异常 ───────────────────────────────────────

@pytest.mark.asyncio
async def test_price_missing_falls_back_without_failing(
    client, auth_headers, db_session, monkeypatch
):
    """接口只返回标题/销量，缺价格 → 落库成功，price=None。"""
    await _configure_onebound(db_session)

    async def onebound_ok(offer_id, api_key, api_secret):
        return {
            "title": "无线蓝牙耳机",
            "sales_count": "已售1000",
            "shop_name": "数码源头工厂",
        }

    monkeypatch.setattr(scraper_mod, "_fetch_onebound", onebound_ok)

    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    product = resp.json()["product"]
    assert product["title"] == "无线蓝牙耳机"
    assert product["price"] is None
    assert product["sales_count"] == 1000
    assert resp.json()["data_source"] == "onebound"


@pytest.mark.asyncio
async def test_price_zero_is_parse_error(client, auth_headers, db_session, monkeypatch):
    """解析到价格 0 → 归类 parse_error（400 中文），不落库。"""
    await _configure_onebound(db_session)

    async def onebound_down(offer_id, api_key, api_secret):
        raise ServiceUnavailableError("数据服务暂时不可用，请稍后再试")

    async def direct_weird(url):
        return {"title": "异常价格商品", "price": 0.0}

    monkeypatch.setattr(scraper_mod, "_fetch_onebound", onebound_down)
    monkeypatch.setattr(scraper_mod, "_direct_fetch", direct_weird)

    resp = await client.post(
        "/api/v1/products/scrape",
        json={"url": OFFER_URL},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "parse_error"
    assert "价格" in detail["message"] or "手动录入" in detail["message"]


# ── 直抓被风控 → anti_bot（服务层单元）──────────────────────────

@pytest.mark.asyncio
async def test_direct_antibot_classified_when_no_key(monkeypatch):
    """无 Key 直接走直抓且被风控 → anti_bot 分类，不裸抛异常。"""

    async def direct_blocked(url):
        raise AntiBotError("1688 有访问保护，请稍后再试")

    monkeypatch.setattr(scraper_mod, "_direct_fetch", direct_blocked)
    # 确保 settings 兜底 Key 为空，走"直抓-only"路径
    monkeypatch.setattr(scraper_mod.settings, "ONEBOUND_API_KEY", None)

    with pytest.raises(ScrapeError) as excinfo:
        await scrape_1688(OFFER_URL)
    assert excinfo.value.code == "anti_bot"
    assert "1688" in excinfo.value.message


# ── 销量数值解析（收口修复：万/亿 量级不再被剥错） ──────────────

def test_clean_int_handles_chinese_magnitude():
    """「已售1.2万+」应解析为 12000，而不是老版本的 12。"""
    from app.services.scraper import _clean_int

    assert _clean_int("已售1.2万+") == 12000
    assert _clean_int("10万+") == 100000
    assert _clean_int("已售3.5亿") == 350000000
    assert _clean_int("已售123件") == 123
    assert _clean_int(5200) == 5200
    assert _clean_int("5,000") == 5000
    assert _clean_int(None) is None
    assert _clean_int("") is None
