"""VeyaShip AI - 套餐与支付路由"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/billing", tags=["套餐与支付"])

PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price": 0,
        "price_label": "免费",
        "description": "试试基本功能",
        "features": ["AI 生成文案 30 次", "1688 商品抓取", "利润计算器", "合规审查"],
        "recommended": False,
    },
    {
        "id": "standard",
        "name": "Standard",
        "price": 99,
        "price_label": "¥99/月",
        "description": "适合个人卖家",
        "features": ["AI 生成不限次", "1688 抓取不限次", "全部 11 个平台", "16 种语言翻译", "AI 智能助手", "邮件支持"],
        "recommended": True,
    },
    {
        "id": "professional",
        "name": "Professional",
        "price": 249,
        "price_label": "¥249/月",
        "description": "适合工作室/团队",
        "features": ["所有 Standard 功能", "AI 商品主图生成", "Shopify 一键发布", "优先技术支持"],
        "recommended": False,
    },
]


class UpgradeRequest(BaseModel):
    plan: str = Field(..., description="目标套餐: standard, professional")
    contact: str = Field("", description="联系方式（微信/手机），用于付款后通知")


@router.get("/plans")
async def get_plans():
    return {"plans": PLANS}


@router.post("/upgrade")
async def upgrade_plan(
    payload: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交升级申请

    流程：
    1. 提交升级申请，记录目标套餐和联系方式
    2. 转账到平台账户
    3. 联系客服确认后手动升级
    4. 或等待系统自动处理（1-2 小时）
    """
    if payload.plan not in ["standard", "professional"]:
        raise HTTPException(status_code=400, detail="无效的套餐")

    plan_info = next((p for p in PLANS if p["id"] == payload.plan), None)
    order_id = str(uuid.uuid4())[:12]

    return {
        "order_id": order_id,
        "plan": payload.plan,
        "amount": plan_info["price"] if plan_info else 0,
        "message": f"升级申请已提交。请转账 ¥{plan_info['price'] if plan_info else 0} 到以下账户，备注订单号 {order_id}，客服确认后即升级。",
        "account": {
            "type": "支付宝 / 微信",
            "note": "请添加客服微信手动处理",
        },
    }


@router.post("/verify")
async def verify_upgrade(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """验证并执行升级（管理员调用）

    生产环境应接入自动支付回调。
    """
    return {"message": "请联系客服手动升级", "contact": "微信: your-wechat-id"}
