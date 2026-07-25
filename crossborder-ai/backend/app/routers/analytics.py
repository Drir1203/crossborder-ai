"""VeyaShip - 数据统计与看板路由（F1 Dashboard）

提供卖家真正关心的业务数据，而不是冰冷的数字。
"""

from datetime import datetime, timedelta, timezone

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
    """获取看板业务数据"""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── 本月商品数 ──────────────────────────────────────────
    product_count = (
        await db.execute(
            select(func.count(Product.id)).where(Product.user_id == current_user.id)
        )
    ).scalar() or 0

    month_products = (
        await db.execute(
            select(func.count(Product.id)).where(
                Product.user_id == current_user.id,
                Product.created_at >= month_start,
            )
        )
    ).scalar() or 0

    # ── 待处理：缺标题或描述的商品 ──────────────────────────
    pending_products = (
        await db.execute(
            select(func.count(Product.id)).where(
                Product.user_id == current_user.id,
                Product.title.is_(None),
            )
        )
    ).scalar() or 0

    # ── 最近操作（最新 5 个商品） ──────────────────────────
    recent_result = await db.execute(
        select(Product)
        .where(Product.user_id == current_user.id)
        .order_by(Product.created_at.desc())
        .limit(5)
    )
    recent_products = [
        {
            "id": str(p.id),
            "title": p.title or "未命名商品",
            "price": p.price,
            "status": "待补充" if not p.title else "正常",
            "created_at": str(p.created_at),
        }
        for p in recent_result.scalars().all()
    ]

    return {
        "products": {
            "total": product_count,
            "this_month": month_products,
            "pending": pending_products,
        },
        "recent": recent_products,
        "credits": {
            "remaining": current_user.credits,
            "used": 100 - current_user.credits,  # 按默认 100 算
        },
    }
