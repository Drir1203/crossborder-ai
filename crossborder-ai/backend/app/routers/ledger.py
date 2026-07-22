"""VeyaShip - 净利计算路由（F9 Ledger）

计算商品净利：收入 - 成本（商品成本 + 平台费用 + 运费）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ledger", tags=["净利计算"])


class ProfitRequest(BaseModel):
    selling_price: float = Field(..., ge=0, description="售价")
    platform_fee_rate: float = Field(0.15, ge=0, le=1, description="平台费率（默认 15%）")
    product_cost: float = Field(0, ge=0, description="商品成本")
    shipping_cost: float = Field(0, ge=0, description="运费")
    advertising_cost: float = Field(0, ge=0, description="广告费")
    exchange_rate: float = Field(1, ge=0, description="汇率（默认 1:1）")


class ProfitResponse(BaseModel):
    selling_price_cny: float
    platform_fee: float
    total_cost: float
    net_profit: float
    profit_margin: float


@router.post("/calculate")
async def calculate_profit(
    payload: ProfitRequest,
    current_user: User = Depends(get_current_user),
):
    """计算商品净利

    公式：净利 = 售价 - 平台费 - 商品成本 - 运费 - 广告费
    """
    price_cny = payload.selling_price * payload.exchange_rate
    platform_fee = price_cny * payload.platform_fee_rate
    total_cost = platform_fee + payload.product_cost + payload.shipping_cost + payload.advertising_cost
    net_profit = price_cny - total_cost
    margin = (net_profit / price_cny * 100) if price_cny > 0 else 0

    return ProfitResponse(
        selling_price_cny=round(price_cny, 2),
        platform_fee=round(platform_fee, 2),
        total_cost=round(total_cost, 2),
        net_profit=round(net_profit, 2),
        profit_margin=round(margin, 1),
    )
