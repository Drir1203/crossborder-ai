"""VeyaShip - 可观测性基础设施测试

覆盖：
1. 每个 HTTP 响应带 X-Request-ID 请求头
2. RequestIDFilter 把当前 request_id 注入日志记录（无则 "-"）
"""

import logging

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_header_on_response(client: AsyncClient):
    """健康检查响应应带 12 位 X-Request-ID 请求头。"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    rid = resp.headers.get("x-request-id")
    assert rid, "响应缺少 X-Request-ID 头"
    assert len(rid) == 12


def test_request_id_filter_injects_context():
    """RequestIDFilter 把当前 request_id 注入日志记录；无请求时为 '-'。"""
    from app.core.observability import RequestIDFilter, request_id_var

    filt = RequestIDFilter()
    base = ("veyaship", logging.INFO, __file__, 1, "hello", (), None)

    # 无请求上下文 → "-"
    record = logging.LogRecord(*base)
    assert filt.filter(record)
    assert record.request_id == "-"

    # 有请求上下文 → 注入当前 request_id
    request_id_var.set("abc123")
    record2 = logging.LogRecord(*base)
    assert filt.filter(record2)
    assert record2.request_id == "abc123"

    # 清理上下文
    request_id_var.set(None)


def test_new_request_id_unique_and_hex():
    from app.core.observability import new_request_id

    a, b = new_request_id(), new_request_id()
    assert a != b
    assert all(c in "0123456789abcdef" for c in a)
