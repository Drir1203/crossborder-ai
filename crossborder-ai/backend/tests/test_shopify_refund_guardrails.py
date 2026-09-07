"""VeyaShip - 自动退款护栏测试（CAP-03）

覆盖：
1. 无 confirm=true → 400「请确认后再发起退款」
2. 单次请求退款总金额 > MAX_REFUND_AMOUNT → 400，且不发任何退款请求
3. 单日累计退款达上限 → 400，且不发任何退款请求
4. 确认 + 未超限 → 走真实逻辑（mock Shopify 订单/退款 API），返回 attempted/succeeded/failed/skipped + 金额
5. Shopify 拒绝退款时 → 200 摘要含 failed 与原因，不吞错、不累计当日金额
"""

import json
import time
from datetime import date
from uuid import UUID

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.crypto import encrypt_value
from app.core.security import decode_token
from app.models.shopify_channel import ShopifyChannel
import app.routers.shopify as shopify_router

JWT_TEST_SECRET = "test-jwt-secret-key-0123456789-abcd"


def _configure(monkeypatch) -> None:
    """统一配置 JWT 密钥（注册 token 与渠道加密共用同一密钥）。"""
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", JWT_TEST_SECRET)


@pytest.fixture(autouse=True)
def _reset_refund_counters():
    """每个用例前清空/后还原进程内日累计退款计数，避免用例间互相污染。"""
    snapshot = dict(shopify_router._DAILY_REFUND_TOTALS)
    shopify_router._DAILY_REFUND_TOTALS.clear()
    yield
    shopify_router._DAILY_REFUND_TOTALS.clear()
    shopify_router._DAILY_REFUND_TOTALS.update(snapshot)


async def _register(client, email=None):
    email = email or f"r{time.time_ns()}@test.com"
    data = {"email": email, "username": email.split("@")[0], "password": "testpass123"}
    resp = await client.post("/api/v1/auth/register", json=data)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return token, {"Authorization": f"Bearer {token}"}


async def _make_channel(db_session, user_id: UUID, shop: str = "mystore") -> ShopifyChannel:
    """直接落一条绑定渠道（含加密 token），供退款/订单接口用。"""
    ch = ShopifyChannel(
        user_id=user_id,
        shop_name=shop,
        shop_domain=f"{shop}.myshopify.com",
        access_token=encrypt_value("shpat_refund_test"),
    )
    db_session.add(ch)
    await db_session.commit()
    return ch


class _FakeResp:
    """极简 httpx.Response 替身。"""

    def __init__(self, status_code, payload, text=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text if text is not None else json.dumps(payload)

    def json(self):
        return self._payload


def _fake_shopify(monkeypatch, orders, refund_status: int = 200) -> dict:
    """替换 httpx.AsyncClient：GET 返回 mock 订单，POST 返回退款结果，同时记录调用。

    生产调用发生在 app/routers/shopify 模块里以 httpx.AsyncClient() 实例化，
    因此 monkeypatch 该模块引用的 httpx.AsyncClient。
    """
    state = {"orders": orders, "refund_status": refund_status, "gets": [], "posts": []}

    class _FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url, **kw):
            state["gets"].append(url)
            return _FakeResp(200, {"orders": state["orders"]})

        async def post(self, url, **kw):
            state["posts"].append((url, kw))
            if state["refund_status"] in (200, 201):
                payload = {"refund": {"id": 7000 + len(state["posts"])}}
            else:
                payload = {"errors": "refund rejected by shopify"}
            return _FakeResp(state["refund_status"], payload)

    monkeypatch.setattr(shopify_router.httpx, "AsyncClient", _FakeClient)
    return state


# ── 护栏分支 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refund_requires_confirm(client, monkeypatch, db_session):
    """没有显式 confirm=true → 400「请确认后再发起退款」，不发请求。"""
    _configure(monkeypatch)
    token, headers = await _register(client)
    ch = await _make_channel(db_session, UUID(decode_token(token)["sub"]))
    state = _fake_shopify(monkeypatch, [])

    resp = await client.post(
        "/api/v1/shopify/auto-refund",
        params={"channel_id": str(ch.id), "threshold": 10},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "请确认后再发起退款" in resp.json()["detail"]
    assert state["gets"] == [] and state["posts"] == []


@pytest.mark.asyncio
async def test_refund_single_request_amount_cap(client, monkeypatch, db_session):
    """单次退款总额超 MAX_REFUND_AMOUNT → 整体 400，不触发任何退款。"""
    _configure(monkeypatch)
    token, headers = await _register(client)
    ch = await _make_channel(db_session, UUID(decode_token(token)["sub"]))

    # 两笔都在阈值下：60 + 50 = 110 > MAX_REFUND_AMOUNT(100)
    orders = [
        {"id": 1, "total_price": "60.00", "financial_status": "paid"},
        {"id": 2, "total_price": "50.00", "financial_status": "paid"},
    ]
    state = _fake_shopify(monkeypatch, orders)

    resp = await client.post(
        "/api/v1/shopify/auto-refund",
        params={"channel_id": str(ch.id), "threshold": 100, "confirm": "true"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "超过单次上限" in resp.json()["detail"]
    assert len(state["posts"]) == 0  # 整体拒绝，一笔都没退


@pytest.mark.asyncio
async def test_refund_daily_cap(client, monkeypatch, db_session):
    """单日累计退款达到 MAX_DAILY_REFUND_TOTAL → 400，不触发退款。"""
    _configure(monkeypatch)
    token, headers = await _register(client)
    uid_str = decode_token(token)["sub"]
    ch = await _make_channel(db_session, UUID(uid_str))

    orders = [{"id": 3, "total_price": "20.00", "financial_status": "paid"}]
    state = _fake_shopify(monkeypatch, orders)

    # 预置：今日已累计到上限，再来一笔必超
    shopify_router._DAILY_REFUND_TOTALS[uid_str] = [
        date.today().isoformat(),
        shopify_router.MAX_DAILY_REFUND_TOTAL,
    ]

    resp = await client.post(
        "/api/v1/shopify/auto-refund",
        params={"channel_id": str(ch.id), "threshold": 50, "confirm": "true"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "累计退款已达上限" in resp.json()["detail"]
    assert len(state["posts"]) == 0


# ── 正常执行 + 摘要 ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refund_success_summary_and_daily_record(client, monkeypatch, db_session):
    """确认 + 未超限 → 走真实逻辑：attempted/succeeded/failed/skipped + 金额，并记当日累计。"""
    _configure(monkeypatch)
    token, headers = await _register(client)
    uid_str = decode_token(token)["sub"]
    ch = await _make_channel(db_session, UUID(uid_str))

    # 9 + 5 < 10 两笔会退；20 不满足阈值 → skipped
    orders = [
        {"id": 101, "total_price": "9.00", "financial_status": "paid"},
        {"id": 102, "total_price": "5.00", "financial_status": "paid"},
        {"id": 103, "total_price": "20.00", "financial_status": "paid"},
    ]
    state = _fake_shopify(monkeypatch, orders)

    resp = await client.post(
        "/api/v1/shopify/auto-refund",
        params={"channel_id": str(ch.id), "threshold": 10, "confirm": "true"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    summary = data["summary"]
    assert summary["attempted"] == 2
    assert summary["succeeded"] == 2
    assert summary["failed"] == 0
    assert summary["skipped"] == 1
    assert summary["requested_amount"] == 14.0
    assert summary["refunded_amount"] == 14.0
    assert len(data["results"]) == 2
    assert all(item["status"] == "refunded" for item in data["results"])
    assert len(state["posts"]) == 2  # 每个低于阈值的订单各发一次退款

    # 域名拼对：请求打到正确店铺，不双重域名
    assert len(state["gets"]) == 1
    assert "mystore.myshopify.com" in state["gets"][0]
    assert "mystore.myshopify.com.myshopify.com" not in state["gets"][0]

    # 当日累计已记录 14（process-internal dict）
    record = shopify_router._DAILY_REFUND_TOTALS.get(uid_str)
    assert record is not None
    assert record[0] == date.today().isoformat()
    assert record[1] == pytest.approx(14.0)


@pytest.mark.asyncio
async def test_refund_reports_failure_reason(client, monkeypatch, db_session):
    """Shopify 拒绝退款 → 200 摘要 failed=1 且带原因，失败金额不计入当日累计。"""
    _configure(monkeypatch)
    token, headers = await _register(client)
    uid_str = decode_token(token)["sub"]
    ch = await _make_channel(db_session, UUID(uid_str))

    orders = [{"id": 201, "total_price": "8.00", "financial_status": "paid"}]
    state = _fake_shopify(monkeypatch, orders, refund_status=422)  # Shopify 拒绝

    resp = await client.post(
        "/api/v1/shopify/auto-refund",
        params={"channel_id": str(ch.id), "threshold": 10, "confirm": "true"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    summary = data["summary"]
    assert summary["attempted"] == 1
    assert summary["succeeded"] == 0
    assert summary["failed"] == 1
    assert summary["refunded_amount"] == 0.0
    item = data["results"][0]
    assert item["status"] == "failed"
    assert "error" in item and item["error"]  # 失败项返回原因，不吞错

    # 失败金额不计入当日累计（仍是空）
    assert uid_str not in shopify_router._DAILY_REFUND_TOTALS


# ── 未认证 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refund_requires_login(client):
    """未登录调退款 → 401。"""
    resp = await client.post("/api/v1/shopify/auto-refund", params={"channel_id": "x"})
    assert resp.status_code == 401
