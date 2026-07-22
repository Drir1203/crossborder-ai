"""VeyaShip - Shopify 路由（F8 Publisher + F7 Concierge）

功能：
1. Shopify OAuth 授权绑定
2. 合规审查（违禁词检测）
3. 推送商品到 Shopify
4. 拉取订单（F7）
5. 自动退款（F7，真调 Shopify Refund API）
"""

import json
import re
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.shopify_channel import ShopifyChannel
from app.models.user import User
router = APIRouter(prefix="/shopify", tags=["Shopify"])

# ── 违禁词正则（F8 合规审查）─────────────────────────────────
BANNED_PATTERNS = [
    r"最[好优棒强劲大低价实惠](?!.*[的之])",
    r"第[一二三123][名位]",
    r"绝对[^不]",
    r"永不[^能会]",
    r"全网[最唯第]",
    r"100%[^的]",
    r"零风险",
    r"无效退款",
    r"全国第一",
    r"销量[第冠]",
]


def compliance_check(text: str) -> list[str]:
    """合规审查：检测文本中是否含违禁词

    Args:
        text: 要检查的文本

    Returns:
        匹配到的违禁词列表（空列表表示通过）
    """
    hits = []
    for pattern in BANNED_PATTERNS:
        found = re.findall(pattern, text)
        hits.extend(found)
    return hits


async def ai_compliance_check(text: str) -> dict:
    """AI 合规复查：调 DeepSeek 审查文本是否含平台违规风险。

    作为正则审查的补充层。AI 调用失败时降级为正则结果，不阻断流程。

    Returns:
        {"safe": bool, "reason": str | None}
    """
    try:
        from app.services.ai.deepseek import DeepSeekService
        llm = DeepSeekService()
        prompt = (
            "你是 Temu/Amazon 平台合规审核员。检查以下商品文本是否含平台违规风险。"
            "违规类型包括：虚假宣传、夸大功效、绝对化用语、价格欺诈、侵权风险。\n\n"
            f"文本：{text[:2000]}\n\n"
            "返回 JSON：{\"safe\": boolean, \"reason\": string|null}\n"
            "safe=false 时 reason 说明违规原因，safe=true 时 reason 为 null。"
        )
        result = await llm.generate(
            "你是一个严格的电商平台合规审核员，只返回 JSON。",
            prompt,
            max_tokens=300,
        )
        import json, re
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    # 降级：AI 调用失败时返回通过，依赖正则拦截
    return {"safe": True, "reason": None}


# ── 数据模型 ──────────────────────────────────────────────────

class ComplianceRequest(BaseModel):
    text: str = ""


class ComplianceResult(BaseModel):
    passed: bool
    violations: list[str] = []


class PushProductRequest(BaseModel):
    product_id: str = Field(..., description="商品 ID")
    channel_id: str = Field(..., description="Shopify 渠道 ID")


# ── 工具函数 ──────────────────────────────────────────────────

async def get_channel(channel_id: str, user_id, db) -> ShopifyChannel:
    from uuid import UUID
    try:
        uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的渠道 ID")
    result = await db.execute(
        select(ShopifyChannel).where(ShopifyChannel.id == uid, ShopifyChannel.user_id == user_id)
    )
    ch = result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=404, detail="Shopify 渠道不存在")
    return ch


# ── 路由 ──────────────────────────────────────────────────────

@router.get("/auth")
async def shopify_oauth_url(
    shop: str = Query(..., description="Shopify 店铺名，如 my-store"),
):
    """生成 Shopify OAuth 授权链接"""
    api_key = settings.SHOPIFY_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="未配置 Shopify API Key")

    redirect_uri = settings.SHOPIFY_REDIRECT_URI or f"{settings.APP_URL}/api/v1/shopify/callback"
    scopes = "write_products,read_products,read_orders,write_orders"

    auth_url = (
        f"https://{shop}.myshopify.com/admin/oauth/authorize"
        f"?client_id={api_key}"
        f"&scope={scopes}"
        f"&redirect_uri={redirect_uri}"
    )
    return {"auth_url": auth_url, "shop": shop}


@router.get("/callback")
async def shopify_oauth_callback(
    code: str = Query(...),
    shop: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Shopify OAuth 回调：用 code 换 token，存入数据库"""
    api_key = settings.SHOPIFY_API_KEY
    api_secret = settings.SHOPIFY_API_SECRET
    if not api_key or not api_secret:
        raise HTTPException(status_code=400, detail="未配置 Shopify API Key/Secret")

    # 用 code 换 access_token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://{shop}/admin/oauth/access_token",
            json={"client_id": api_key, "client_secret": api_secret, "code": code},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="授权失败，请重试")
        token_data = resp.json()
        access_token = token_data.get("access_token")

    # 查重/保存
    result = await db.execute(
        select(ShopifyChannel).where(ShopifyChannel.user_id == current_user.id, ShopifyChannel.shop_name == shop)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.access_token = access_token
    else:
        db.add(ShopifyChannel(
            user_id=current_user.id,
            shop_name=shop,
            shop_domain=f"{shop}.myshopify.com",
            access_token=access_token,
        ))
    await db.flush()

    return {"message": f"Shopify 店铺 {shop} 绑定成功", "shop": shop}


@router.get("/channels")
async def list_channels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看已绑定的 Shopify 店铺列表"""
    result = await db.execute(
        select(ShopifyChannel).where(
            ShopifyChannel.user_id == current_user.id,
            ShopifyChannel.is_active == True,
        )
    )
    channels = result.scalars().all()
    return [
        {"id": str(c.id), "shop_name": c.shop_name, "domain": c.shop_domain, "created_at": str(c.created_at)}
        for c in channels
    ]


@router.post("/compliance")
async def check_compliance(
    payload: ComplianceRequest,
):
    """合规审查：检测文本中的违禁词"""
    violations = compliance_check(payload.text)
    return ComplianceResult(passed=len(violations) == 0, violations=violations)


@router.post("/push")
async def push_product(
    payload: PushProductRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """推送商品到 Shopify（含合规审查）

    流程：
    1. 查商品
    2. 查 Shopify 渠道
    3. 合规审查 → 不通过则拦截
    4. 调 Shopify API 创建商品
    """
    from uuid import UUID

    # 查商品
    try:
        pid = UUID(payload.product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的商品 ID")
    result = await db.execute(select(Product).where(Product.id == pid))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 查 Shopify 渠道
    channel = await get_channel(payload.channel_id, current_user.id, db)

    # 合规审查（双重：正则 + AI 复查）
    check_text = f"{product.title or ''} {product.description or ''}"

    # 第一层：正则快速拦截
    violations = compliance_check(check_text)
    if violations:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "商品内容含违禁词，发布被拦截",
                "violations": violations,
            },
        )

    # 第二层：AI 深度复查（失败时降级为通过，不阻断）
    ai_result = await ai_compliance_check(check_text)
    if not ai_result.get("safe", True):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "AI 合规审查未通过",
                "reason": ai_result.get("reason", "未知违规"),
            },
        )

    # 调用 Shopify API 创建商品（F8 Publisher）
    shop_url = f"https://{channel.shop_name}.myshopify.com/admin/api/2024-10"
    headers = {
        "X-Shopify-Access-Token": channel.access_token,
        "Content-Type": "application/json",
    }

    product_data = {
        "product": {
            "title": product.title or "Untitled",
            "body_html": product.description or "",
            "status": "draft",
            "variants": [{"price": str(product.price)}] if product.price else [],
        }
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{shop_url}/products.json", json=product_data, headers=headers)
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail=f"Shopify 发布失败：{resp.text[:200]}")

        shopify_product = resp.json().get("product", {})
        return {
            "message": "商品已发布到 Shopify（草稿状态）",
            "shopify_product_id": shopify_product.get("id"),
            "shopify_url": f"https://{channel.shop_name}.myshopify.com/admin/products/{shopify_product.get('id')}",
        }


# ════════════════════════════════════════════════════════════════
# F7 Concierge — 订单拉取 + 自动退款
# ════════════════════════════════════════════════════════════════

@router.get("/orders")
async def list_shopify_orders(
    channel_id: str = Query(..., description="Shopify 渠道 ID"),
    limit: int = Query(50, ge=1, le=250),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """拉取 Shopify 订单列表（F7 Concierge）

    从绑定的 Shopify 店铺拉取最近订单，
    返回订单 ID、金额、状态等信息。
    """
    channel = await get_channel(channel_id, current_user.id, db)
    shop_url = f"https://{channel.shop_name}.myshopify.com/admin/api/2024-10"
    headers = {"X-Shopify-Access-Token": channel.access_token}

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{shop_url}/orders.json", headers=headers, params={
            "status": "any",
            "limit": limit,
            "order": "created_at desc",
        })
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"获取订单失败：{resp.text[:200]}")

        orders = resp.json().get("orders", [])
        return [
            {
                "id": o["id"],
                "order_number": o.get("order_number"),
                "total_price": o.get("total_price"),
                "currency": o.get("currency"),
                "financial_status": o.get("financial_status"),
                "fulfillment_status": o.get("fulfillment_status"),
                "created_at": o.get("created_at"),
                "customer_email": o.get("email") or (o.get("customer") or {}).get("email", ""),
            }
            for o in orders
        ]


@router.post("/auto-refund")
async def auto_refund(
    channel_id: str = Query(..., description="Shopify 渠道 ID"),
    threshold: float = Query(10.0, description="自动退款阈值，低于此金额的订单自动退"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """自动退款（F7 Concierge）

    规则：金额 < threshold（默认 ¥10）的已付款订单自动退款。

    流程：
    1. 拉取最近 50 笔订单
    2. 过滤已付款且金额 < threshold 的订单
    3. 对每笔符合条件的订单真调 Shopify Refund API
    4. 返回退款结果明细

    ⚠️ 此为真实退款操作，会真扣 Shopify 商户账户余额。
    """
    channel = await get_channel(channel_id, current_user.id, db)
    shop_url = f"https://{channel.shop_name}.myshopify.com/admin/api/2024-10"
    headers = {"X-Shopify-Access-Token": channel.access_token}

    # 1. 拉取订单
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{shop_url}/orders.json", headers=headers, params={
            "status": "any",
            "limit": 50,
            "financial_status": "paid",
            "order": "created_at desc",
        })
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"获取订单失败：{resp.text[:200]}")

        orders = resp.json().get("orders", [])

    # 2. 过滤出金额小于阈值的已付款订单
    refundable = []
    for o in orders:
        try:
            price = float(o.get("total_price", 0))
            if price < threshold:
                refundable.append(o)
        except (ValueError, TypeError):
            continue

    # 3. 逐笔自动退款（真调 Shopify Refund API）
    results = []
    async with httpx.AsyncClient() as client:
        for order in refundable:
            order_id = order["id"]
            total = order.get("total_price", "0")

            # 构造退款请求体
            refund_data = {
                "refund": {
                    "notify": False,
                    "note": "VeyaShip 自动退款：金额低于阈值",
                    "transactions": [
                        {
                            "kind": "refund",
                            "amount": total,
                            "gateway": order.get("gateway", ""),
                        }
                    ],
                    "refund_line_items": [],
                }
            }

            try:
                resp = await client.post(
                    f"{shop_url}/orders/{order_id}/refunds.json",
                    json=refund_data,
                    headers=headers,
                )
                if resp.status_code in (200, 201):
                    refund = resp.json().get("refund", {})
                    results.append({
                        "order_id": order_id,
                        "amount": total,
                        "status": "refunded",
                        "refund_id": refund.get("id"),
                    })
                else:
                    results.append({
                        "order_id": order_id,
                        "amount": total,
                        "status": "failed",
                        "error": resp.text[:100],
                    })
            except Exception as e:
                results.append({
                    "order_id": order_id,
                    "amount": total,
                    "status": "error",
                    "error": str(e),
                })

    return {
        "total_orders_checked": len(orders),
        "refundable_count": len(refundable),
        "refunded_count": sum(1 for r in results if r["status"] == "refunded"),
        "total_refunded_amount": sum(float(r["amount"]) for r in results if r["status"] == "refunded"),
        "results": results,
    }
