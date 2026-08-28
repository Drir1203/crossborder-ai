"""VeyaShip - API 限流

两种实现：
- 生产（PostgreSQL）：固定窗口限流，计数落 `rate_limits` 表，所有 uvicorn worker
  共享同一张表，限流全局生效——修复单机内存限流在 4 worker 下被放大 4 倍的问题。
- 开发（SQLite）：回退到进程内内存限流，不落表。

窗口用墙钟时间（floor(now/window)*window），因为不同进程的
time.monotonic() 不可比，跨 worker 对齐窗口必须用墙钟。

支持按用户 ID 或 IP 地址限制：
- 已登录用户 → user:{user_id}:{limit_key}（需在路由签名里把
  get_current_user 声明在 RateLimit 之前，request.state.user 才有值）
- 未登录 → ip:{ip}:{limit_key}
"""

import asyncio
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.rate_limit import RateLimitWindow


# ── 测试模式开关 ──────────────────────────────────────────────
# 测试时通过 conftest 设置为 True，跳过限流检查
RATE_LIMIT_DISABLED = False


# ── 内存限流存储（SQLite 开发模式回退） ───────────────────────
_rate_store: dict[str, list[float]] = {}
_lock = asyncio.Lock()

# 默认限流规则
DEFAULT_LIMITS = {
    "default":     (60,   60),     # 60次/分钟
    "ai_generate": (10,   60),     # AI生成 10次/分钟
    "scrape":      (20,   60),     # 抓取 20次/分钟
    "batch":       (5,    60),     # 批量 5次/分钟
    "auth":        (5,    60),     # 登录注册 5次/分钟
}


# ── 通用 ─────────────────────────────────────────────────────
def get_client_ip(request: Request) -> str:
    """从请求中获取客户端 IP。"""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_key(request: Request, limit_key: str) -> str:
    """生成限流 key：已登录用户按用户粒度，未登录按 IP 兜底。

    用户粒度可防单账号刷接口；IP 粒度覆盖注册/登录等未登录请求。
    """
    user = getattr(request.state, "user", None)
    if user is not None:
        return f"user:{user.id}:{limit_key}"
    return f"ip:{get_client_ip(request)}:{limit_key}"


# ── 内存限流（开发模式） ─────────────────────────────────────
async def _cleanup_memory(key: str, window: int):
    """清理过期的请求记录。"""
    now = time.monotonic()
    cutoff = now - window
    async with _lock:
        if key in _rate_store:
            _rate_store[key] = [t for t in _rate_store[key] if t > cutoff]
            if not _rate_store[key]:
                del _rate_store[key]


async def _check_rate_memory(key: str, max_requests: int, window: int) -> bool:
    """检查是否超过限流（内存实现，仅开发用）。"""
    await _cleanup_memory(key, window)
    async with _lock:
        records = _rate_store.get(key, [])
        if len(records) >= max_requests:
            return False
        records.append(time.monotonic())
        _rate_store[key] = records
        return True


# ── PG 固定窗口限流（生产，多 worker 共享） ───────────────────
# 每累计多少次请求触发一次旧窗口清理（避免表无限增长）
_PG_CLEANUP_INTERVAL = 100
# 清理一小时前的窗口
_PG_CLEANUP_AGE_SECONDS = 3600

_pg_cleanup_counter = 0


async def _cleanup_old_windows() -> None:
    """删除一小时前结束的旧窗口行。失败不影响限流主流程。"""
    cutoff = int(time.time()) - _PG_CLEANUP_AGE_SECONDS
    try:
        async with async_session_factory() as session:
            await session.execute(
                delete(RateLimitWindow).where(RateLimitWindow.window_start < cutoff)
            )
            await session.commit()
    except Exception:
        pass


async def _check_rate_pg(key: str, max_requests: int, window: int) -> bool:
    """PG 固定窗口限流：所有 worker 共享 `rate_limits` 表，全局生效。

    并发安全：
    - 同一 (key, window_start) 的计数用 SELECT ... FOR UPDATE 行锁串行化；
    - 窗口首个请求（行不存在）并发插入时靠唯一约束 uq_rate_limit_window
      兜底，插入失败方回滚后重新走计数路径。
    """
    now = int(time.time())
    window_start = now - (now % window)

    # 周期性清理旧窗口（计数器是每进程的，4 worker 下约 4 倍频率，可接受）
    global _pg_cleanup_counter
    _pg_cleanup_counter += 1
    if _pg_cleanup_counter % _PG_CLEANUP_INTERVAL == 0:
        await _cleanup_old_windows()

    async with async_session_factory() as session:
        for attempt in range(2):
            result = await session.execute(
                select(RateLimitWindow)
                .where(
                    RateLimitWindow.key == key,
                    RateLimitWindow.window_start == window_start,
                )
                .with_for_update()
            )
            row = result.scalar_one_or_none()
            if row is None:
                # 本窗口还没有记录：尝试插入。并发下可能撞唯一约束，失败方回滚重试。
                try:
                    session.add(RateLimitWindow(key=key, window_start=window_start, count=1))
                    await session.commit()
                    return True
                except IntegrityError:
                    await session.rollback()
                    continue

            if row.count >= max_requests:
                await session.commit()
                return False

            row.count += 1
            await session.commit()
            return True

        # 两次插入都被并发抢先（极端竞态）：放行，限流不能误伤正常流量
        return True


# ── 限流分发 ─────────────────────────────────────────────────
async def _check_rate(key: str, max_requests: int, window: int) -> bool:
    """检查是否超过限流：生产 PG 全局限流，开发 SQLite 回退内存。"""
    if settings.USE_SQLITE:
        return await _check_rate_memory(key, max_requests, window)
    return await _check_rate_pg(key, max_requests, window)


# ── 限流依赖工厂 ──────────────────────────────────────────────
# 用法:
#   @router.post("/generate")
#   async def generate(
#       current_user: User = Depends(get_current_user),   # 必须声明在 RateLimit 之前
#       _=Depends(RateLimit("ai_generate")),
#   ):
#       ...
def RateLimit(limit_key: str = "default", max_requests: Optional[int] = None, window: int = 60):
    """创建限流依赖。

    Args:
        limit_key: 限流规则名称，在 DEFAULT_LIMITS 中定义
        max_requests: 可选，覆盖默认的最大请求数
        window: 时间窗口（秒）
    """
    if max_requests is None:
        max_requests, window = DEFAULT_LIMITS.get(limit_key, DEFAULT_LIMITS["default"])

    async def _dependency(request: Request):
        # 测试模式下跳过限流
        if RATE_LIMIT_DISABLED:
            return
        key = _rate_key(request, limit_key)
        allowed = await _check_rate(key, max_requests, window)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，请稍后重试（{limit_key}: {max_requests}次/{window}秒）",
            )

    return _dependency
