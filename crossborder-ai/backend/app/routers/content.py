"""VeyaShip - AI Content Generation Routes.

Generate optimized product listings from scraped 1688 product data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.user import User
from app.services.ai.deepseek import DeepSeekService
from app.services.ai.replicate import ReplicateService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/content", tags=["AI 内容生成"])


class GenerateRequest(BaseModel):
    product_id: str = Field(..., description="商品 ID")
    platform: str = Field(default="amazon", description="目标平台: amazon, ebay, shopify, etsy, shein, temu, tiktok, aliexpress, walmart, shopee, lazada")
    tone: str = Field(default="professional", description="语气: professional, casual, luxury")
    language: str = Field(default="en", description="输出语言: en, ja, es, fr, de, pt")
    generate_image: bool = Field(default=False, description="是否同时生成商品主图")
    image_prompt: str = Field(default="", description="自定义图片描述，留空则根据商品标题自动生成")


class GenerateResponse(BaseModel):
    title: str = ""
    description: str = ""
    bullet_points: list[str] = []
    seo_title: str = ""
    seo_description: str = ""
    image_url: str = ""
    model_used: str = ""


@router.post("/generate", response_model=GenerateResponse)
async def generate_listing(
    payload: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 根据商品数据自动生成 Listing 内容。

    选择商品和目标平台，AI 自动生成：
    - 优化的标题
    - 商品描述
    - 卖点列表
    - SEO 标题/描述
    """
    from uuid import UUID

    # 验证积分
    if current_user.credits < 1:
        raise HTTPException(status_code=402, detail="积分不足，每次生成消耗 1 积分")

    # 获取商品
    try:
        result = await db.execute(select(Product).where(Product.id == UUID(payload.product_id)))
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的商品 ID")

    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if not product.title:
        raise HTTPException(status_code=400, detail="商品缺少标题，请先补充商品信息")

    # 调用 DeepSeek
    try:
        llm = DeepSeekService()
        title = await _generate_title(llm, product, payload)
        description = await _generate_description(llm, product, payload)
        bullets = await _generate_bullets(llm, product, payload)
        seo = await _optimize_seo(llm, title, description, payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail="AI 生成服务暂不可用，请稍后重试")

    # 生成商品主图
    image_url = ""
    if payload.generate_image:
        from app.core.config import settings
        if not settings.REPLICATE_API_KEY:
            raise HTTPException(status_code=400, detail="图片生成功能暂未配置，请联系管理员开通")
        try:
            img_service = ReplicateService()
            prompt = payload.image_prompt or f"Professional e-commerce product photo of {product.title}, white background, studio lighting, 8K, photorealistic"
            images = await img_service.generate_image(prompt, num_outputs=1)
            if images:
                image_url = images[0]
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"图片生成失败：{str(e)}")

    # 扣积分
    await current_user.deduct_credits(db, 1)

    return GenerateResponse(
        title=title,
        description=description,
        bullet_points=bullets,
        seo_title=seo.get("seo_title", ""),
        seo_description=seo.get("seo_description", ""),
        image_url=image_url,
        model_used="deepseek-chat",
    )


async def _generate_title(llm: DeepSeekService, product: Product, payload: GenerateRequest) -> str:
    prompt = (
        f"为以下商品生成一个优化的 {payload.platform} 标题（不超过 200 字符，{payload.language} 语言，{payload.tone} 语气）：\n"
        f"商品：{product.title}\n"
        f"价格：{product.price}\n"
        f"店铺：{product.shop_name or ''}"
    )
    return await llm.generate(
        f"你是一个 {payload.platform} 平台的专业 Listing 优化师",
        prompt,
        max_tokens=300,
    )


async def _generate_description(llm: DeepSeekService, product: Product, payload: GenerateRequest) -> str:
    return await llm.generate_product_description(
        product_title=product.title,
        platform=payload.platform,
        tone=payload.tone,
        target_language=payload.language if payload.language != "en" else None,
    )


async def _generate_bullets(llm: DeepSeekService, product: Product, payload: GenerateRequest) -> list[str]:
    features = f"价格: {product.price}" if product.price else ""
    return await llm.generate_bullet_points(
        product_title=product.title,
        features=features,
        platform=payload.platform,
    )


async def _optimize_seo(llm: DeepSeekService, title: str, description: str, payload: GenerateRequest) -> dict:
    return await llm.optimize_seo(
        title=title,
        description=description,
        platform=payload.platform,
    )
