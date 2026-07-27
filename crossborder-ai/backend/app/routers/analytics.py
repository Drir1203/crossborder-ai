"""VeyaShip - 数据统计与看板路由（F1 Dashboard）

提供卖家真正关心的业务数据，而不是冰冷的数字。
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
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
            "used": 100 - current_user.credits,
        },
    }


@router.get("/category")
async def analyze_category(
    keyword: str = Query(..., description="品类关键词，如：蓝牙耳机"),
    current_user: User = Depends(get_current_user),
):
    """AI 品类分析：输入品类名，返回市场分析报告

    用于 Agent 的"蓝牙耳机能不能做"类指令。
    """
    from app.services.ai.deepseek import DeepSeekService
    llm = DeepSeekService()

    report = await llm.generate(
        "你是一个跨境电商数据分析师。输出结构化市场分析报告，数据具体合理。Markdown格式。",
        f"分析品类「{keyword}」Amazon US市场：1.市场概览（搜索量、商品数、均价）2.价格分布 3.竞争格局 4.用户痛点Top3 5.1688到Amazon利润模型 6.选品建议和评分。数据用具体数字。",
        max_tokens=4000,
    )
    return {"category": keyword, "report": report, "market": "Amazon US"}


@router.get("/insights")
async def get_ai_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 分析经营数据，给出经营建议"""
    from app.services.ai.deepseek import DeepSeekService

    total = (await db.execute(select(func.count(Product.id)).where(Product.user_id == current_user.id))).scalar() or 0
    no_title = (await db.execute(select(func.count(Product.id)).where(Product.user_id == current_user.id, Product.title.is_(None)))).scalar() or 0

    data = f"商品总数：{total}个\n待补充信息：{no_title}个\n剩余积分：{current_user.credits}\n套餐：{current_user.plan}"

    try:
        llm = DeepSeekService()
        advice = await llm.generate("你是跨境电商运营顾问。根据数据给出3条简短建议，每条一行用数字开头。", data, max_tokens=500)
        lines = [l.strip() for l in advice.strip().split("\n") if l.strip() and l[0].isdigit()]
    except Exception:
        lines = ["1. 完善商品信息，补充标题和描述", "2. 利用 AI 批量生成 Listing", "3. 定期检查商品销售数据"]

    return {"stats": {"total": total, "pending": no_title, "credits": current_user.credits}, "advice": lines[:3]}
