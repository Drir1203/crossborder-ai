"""VeyaShip - Billing & Plans Routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["Billing"])

PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price": 0,
        "price_label": "免费",
        "description": "试试基本功能",
        "features": [
            "AI 生成文案 3 次/月",
            "1688 抓取 1 次/月",
            "1 个平台",
            "仅英文",
        ],
        "recommended": False,
    },
    {
        "id": "standard",
        "name": "Standard",
        "price": 79,
        "price_label": "¥79/月",
        "description": "适合个人卖家",
        "features": [
            "AI 生成文案 不限次",
            "1688 抓取 不限次",
            "全部 11 个平台",
            "17 种语言翻译",
            "邮件支持",
        ],
        "recommended": True,
    },
    {
        "id": "professional",
        "name": "Professional",
        "price": 199,
        "price_label": "¥199/月",
        "description": "适合工作室/团队",
        "features": [
            "所有 Standard 功能",
            "AI 生成商品主图",
            "Shopify 自动发布",
            "优先技术支持",
        ],
        "recommended": False,
    },
]


@router.get("/plans")
async def get_plans():
    """返回所有套餐信息."""
    return {"plans": PLANS}


class UpgradeRequest:
    pass


@router.post("/upgrade")
async def upgrade_plan(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员手动升级用户套餐."""
    from pydantic import BaseModel, Field

    class UpgradeReq(BaseModel):
        plan: str = Field(..., description="目标套餐: standard, professional")

    req = UpgradeReq(**payload)
    target_plan = req.plan

    if target_plan not in ["standard", "professional"]:
        raise HTTPException(status_code=400, detail="无效的套餐")

    current_user.plan = target_plan
    if target_plan == "standard":
        current_user.credits = 9999
    elif target_plan == "professional":
        current_user.credits = 99999

    db.add(current_user)
    await db.flush()

    return {"message": f"已升级到 {target_plan} 套餐", "plan": current_user.plan, "credits": current_user.credits}
