"""VeyaShip - 限流加固测试

覆盖：
1. 内存路径（SQLite 开发模式）计数正确：达到上限后拒绝，不同 key 独立
2. _rate_key：已登录用户按用户粒度，未登录按 IP（含 X-Forwarded-For）
3. PG 路径（_check_rate_pg）：计数落表、达到上限后拒绝（用测试库 SQLite 模拟，
   验证计数与并发插入逻辑正确；生产 PG 的真实行锁行为由同一逻辑驱动）
"""

from types import SimpleNamespace

import pytest
import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import rate_limit as rl
from app.models.rate_limit import RateLimitWindow


def _fake_request(user=None, headers=None):
    """构造最小 Request 替代对象，只暴露 _rate_key 需要的属性。"""
    return SimpleNamespace(
        state=SimpleNamespace(user=user),
        client=SimpleNamespace(host="1.2.3.4"),
        headers=headers or {},
    )


@pytest.mark.asyncio
async def test_memory_rate_limit_blocks_over_limit():
    """内存限流：3 次/窗口内放行，第 4 次拒绝；不同 key 独立计数。"""
    rl._rate_store.clear()
    key = "test:mem"

    assert await rl._check_rate_memory(key, 3, 60) is True
    assert await rl._check_rate_memory(key, 3, 60) is True
    assert await rl._check_rate_memory(key, 3, 60) is True
    assert await rl._check_rate_memory(key, 3, 60) is False

    # 不同 key 不受影响
    assert await rl._check_rate_memory("test:other", 3, 60) is True


def test_rate_key_uses_user_when_logged_in():
    """已登录用户 → user:{id}:{limit_key} 粒度。"""
    user = SimpleNamespace(id="uuid-123")
    assert rl._rate_key(_fake_request(user=user), "ai_generate") == "user:uuid-123:ai_generate"


def test_rate_key_falls_back_to_ip():
    """未登录 → ip 粒度，优先取 X-Forwarded-For 第一个地址。"""
    req = _fake_request(headers={"X-Forwarded-For": "9.9.9.9, 8.8.8.8"})
    assert rl._rate_key(req, "auth") == "ip:9.9.9.9:auth"


def test_rate_key_uses_client_ip_when_no_forwarded():
    """无 X-Forwarded-For 时用 request.client.host。"""
    assert rl._rate_key(_fake_request(), "auth") == "ip:1.2.3.4:auth"


@pytest.mark.asyncio
async def test_pg_rate_limit_counts_and_blocks(test_engine):
    """PG 路径：计数落表，达到上限后拒绝（SQLite 测试库模拟验证逻辑）。"""
    factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    orig_factory = rl.async_session_factory
    rl.async_session_factory = factory
    try:
        key = "test:pg"

        assert await rl._check_rate_pg(key, 2, 60) is True
        assert await rl._check_rate_pg(key, 2, 60) is True
        assert await rl._check_rate_pg(key, 2, 60) is False

        # 落表断言：当前窗口行 count 应为 2
        window_start = int(time.time()) - (int(time.time()) % 60)
        async with factory() as session:
            result = await session.execute(
                select(RateLimitWindow).where(
                    RateLimitWindow.key == key,
                    RateLimitWindow.window_start == window_start,
                )
            )
            row = result.scalar_one_or_none()
            assert row is not None, "PG 限流应写入 rate_limits 表"
            assert row.count == 2
    finally:
        rl.async_session_factory = orig_factory
