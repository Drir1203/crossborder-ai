"""VeyaShip - API 限流

基于内存的请求频率限制器。
生产环境可切换到 Redis 实现（当 settings.REDIS_URL 配置时）。
支持按用户 ID 或 IP 地址限制。
"""

import os
import time
import asyncio
from typing import Optional
from collections import defaultdict
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


# ── 测试模式开关 ──────────────────────────────────────────────
# 测试时通过 conftest 设置为 True，跳过限流检查
RATE_LIMIT_DISABLED = False


# ── 内存限流存储 ──────────────────────────────────────────────
# {key: [(timestamp, ...)]}
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


async def _cleanup(key: str, window: int):
    """清理过期的请求记录。"""
    now = time.monotonic()
    cutoff = now - window
    async with _lock:
        if key in _rate_store:
            _rate_store[key] = [t for t in _rate_store[key] if t > cutoff]
            if not _rate_store[key]:
                del _rate_store[key]


async def _check_rate(key: str, max_requests: int, window: int) -> bool:
    """检查是否超过限流。"""
    await _cleanup(key, window)
    async with _lock:
        records = _rate_store.get(key, [])
        if len(records) >= max_requests:
            return False
        records.append(time.monotonic())
        _rate_store[key] = records
        return True


def get_client_ip(request: Request) -> str:
    """从请求中获取客户端 IP。"""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── 限流依赖工厂 ──────────────────────────────────────────────
# 用法:
#   @router.post("/generate")
#   async def generate(_=Depends(RateLimit("ai_generate"))):
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
        ip = get_client_ip(request)
        key = f"ip:{ip}:{limit_key}"
        allowed = await _check_rate(key, max_requests, window)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，请稍后重试（{limit_key}: {max_requests}次/{window}秒）",
            )

    return _dependency
