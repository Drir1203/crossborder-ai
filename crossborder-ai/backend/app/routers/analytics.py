"""VeyaShip - 数据统计与看板路由（F1 Dashboard）

功能：
1. 看板总览：商品数、AI 生成次数、积分用量
2. 使用趋势：按天统计 AI 生成量

注意：
- 当前商品表（products）没有 user_id 字段，所以商品统计是全局的
- AI 生成记录（content_generations）表存在但当前路由未写入记录
- 后续迭代可以优化为按用户统计
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["数据统计"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取看板统计数据（F1）

    返回内容：
    - products: 商品总数（当前是全局统计）
    - listings: Listing 统计（暂为 0，等待 Listing 功能上线）
    - content: AI 生成统计（暂为 0，等待 ContentGeneration 记录写入）
    - platforms: 平台分布（暂为空）
    """
    # ── 商品总数（按用户统计） ──────────────────────────────
    # Product 表已经有 user_id 字段，可以按当前用户过滤了
    product_count = (
        await db.execute(
            select(func.count(Product.id)).where(Product.user_id == current_user.id)
        )
    ).scalar()

    # ── 返回数据 ──────────────────────────────────────────────
    # listings / content 的统计功能依赖 Listing 和 ContentGeneration 表
    # 目前这两个表存在但路由层还没有写入逻辑，所以返回 0
    # 后续 F2 Refinery 完善后会写入 content_generations 表
    return {
        "products": {
            "total": product_count or 0,
        },
        "listings": {
            "draft": 0,
            "published": 0,
            "total": 0,
        },
        "content": {
            "total_generations": 0,
            "recent_7_days": 0,
        },
        "platforms": {},
    }


@router.get("/usage-trend")
async def get_usage_trend(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取每日使用趋势（暂未实现）

    待 ContentGeneration 表有数据后，这里会按天返回生成量趋势。
    """
    return {
        "days": days,
        "trend": [],
        "total": 0,
    }
