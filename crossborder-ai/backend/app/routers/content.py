"""VeyaShip - AI 内容生成路由（F2 Refinery）

【全栈学习者必读】
这个模块展示了后端最复杂的业务流程：
1. 数据库操作：查商品、查品牌调性、查/改积分
2. 外部 API 调用：DeepSeek AI、Replicate FLUX
3. 业务逻辑：积分扣减、品牌调性注入、生成模式选择
4. 异常处理：各种失败场景的优雅处理

多层架构：
- routers/ 层：处理 HTTP 请求/响应（本文件）
- services/ai/ 层：调用 LLM API
- models/ 层：数据库数据结构
- schemas/ 层：API 请求/响应校验

请求处理流程：
1. 验证用户认证 → get_current_user
2. 检查积分 → 不够则 402
3. 查数据库 → 从 products 表读商品
4. 查品牌调性 → 从 personas 表读用户配置
5. 调用 AI → services/ai/deepseek.py
6. 可选生成图片 → services/ai/replicate.py
7. 扣减积分 → user.deduct_credits()
8. 返回结果 → GenerateResponse
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import RateLimit
from app.dependencies import get_current_user
from app.models.persona import Persona
from app.models.product import Product
from app.models.user import User
from app.services.ai.deepseek import DeepSeekService
from app.services.ai.aliyun_image import AliyunImageService
from app.services.ai.replicate import ReplicateService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/content", tags=["AI 内容生成"])


# ── 请求/响应模型 ──────────────────────────────────────────────
# Pydantic 模型 vs SQLAlchemy 模型：
# - Pydantic 模型：校验 HTTP 请求/响应的数据格式（本文件）
# - SQLAlchemy 模型：定义数据库表结构（models/ 下）
# 两者分层清晰，各司其职

class GenerateRequest(BaseModel):
    """AI 生成请求的参数

    FastAPI 会自动：
    1. 从请求体 JSON 解析
    2. 按类型校验（product_id 必须是字符串）
    3. 按约束校验（min_length、ge=1 等）
    4. 不符合就返回 422 错误
    """
    product_id: str = Field(..., description="商品 ID（UUID 字符串）")
    platform: str = Field(default="amazon", description="目标平台: amazon, ebay, shopify, etsy, shein, temu, tiktok, aliexpress, walmart, shopee, lazada")
    tone: str = Field(default="professional", description="语气: professional, casual, luxury")
    language: str = Field(default="en", description="输出语言: en, ja, es, fr, de, pt 等")
    generate_image: bool = Field(default=False, description="是否同时用 FLUX 生成商品主图")
    image_prompt: str = Field(default="", description="自定义图片描述，留空则自动根据商品标题生成")
    expert_mode: bool = Field(default=False, description="启用 Agent 深度优化（多轮自检+优化，较慢但质量更高）")


class GenerateResponse(BaseModel):
    """AI 生成的结果"""
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
    request: Request,
    # RateLimit("ai_generate") 限制 AI 生成频率：10 次/分钟
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """【核心】AI 根据商品数据自动生成 Listing 内容

    这就是 F2 模块的核心功能：
    1. 选一个已抓取的商品
    2. 选目标平台（Amazon/eBay/Shopify 等）
    3. AI 自动生成：标题、描述、卖点、SEO

    为什么不在前端直接调 DeepSeek API？
    - 安全性：API Key 不能暴露给前端
    - 业务逻辑：品牌调性注入、积分扣减在后端做
    - 可控性：可以限流、监控、计费
    - 扩展性：未来可以切换 AI 服务商，前端无感知

    Args:
        payload: 生成请求参数（商品ID、平台、语气等）
        request: HTTP 请求对象
        current_user: 当前登录的用户（从 JWT 解析）
        db: 数据库会话

    Returns:
        GenerateResponse: AI 生成的标题、描述、卖点、SEO

    Raises:
        HTTPException 402: 积分不足
        HTTPException 400: 商品 ID 无效或商品缺标题
        HTTPException 404: 商品不存在
        HTTPException 502: AI 服务不可用
    """
    from uuid import UUID

    # ════════════════════════════════════════════════════════════
    # 第 1 步：积分检查
    # ════════════════════════════════════════════════════════════
    # 每次 AI 生成消耗 1 积分
    # credit 字段在 User 模型上，通过 deduct_credits 方法原子扣减
    if current_user.credits < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="积分不足，每次 AI 生成消耗 1 积分",
        )

    # ════════════════════════════════════════════════════════════
    # 第 2 步：查商品
    # ════════════════════════════════════════════════════════════
    # SELECT * FROM products WHERE id = ?
    # UUID 字符串转 UUID 对象，格式错误则 400
    try:
        product_id = UUID(payload.product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的商品 ID 格式",
        )

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )

    if not product.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品缺少标题，请先补充商品信息",
        )

    # ════════════════════════════════════════════════════════════
    # 第 3 步：加载品牌调性（F5 Persona）
    # ════════════════════════════════════════════════════════════
    # 从 personas 表读取用户的品牌配置
    # 如果没有配置，persona 为 None，跳过品牌调性注入
    # 这是"可组合功能模块"的典型例子：F2 生成内容时集成 F5 调性
    persona_str = ""
    persona_result = await db.execute(
        select(Persona).where(Persona.user_id == current_user.id)
    )
    persona = persona_result.scalar_one_or_none()
    if persona:
        import json
        parts = []
        if persona.brand_name:
            parts.append(f"品牌：{persona.brand_name}")
        if persona.tagline:
            parts.append(f"标语：{persona.tagline}")
        if persona.description:
            parts.append(f"品牌描述：{persona.description}")
        tone_text = persona.tone_custom or persona.tone
        parts.append(f"语气：{tone_text}")
        if persona.banned_words:
            words = json.loads(persona.banned_words)
            if words:
                parts.append(f"禁止使用的词汇：{'、'.join(words)}")
        persona_str = "，".join(parts)

    # ════════════════════════════════════════════════════════════
    # 第 4 步：调用 AI 生成内容
    # ════════════════════════════════════════════════════════════
    # 两种模式：
    # 1. 普通模式：三步调用 DeepSeek（标题 → 描述 → 卖点 → SEO）
    # 2. 专家模式：用 LangGraph Agent 自动自检和优化
    try:
        if payload.expert_mode:
            # ── 专家模式（多轮自检） ────────────────────────
            # ListingAgent 是一个 LangGraph 驱动的 Agent
            # 它会自我审视、优化、再审视，重复多次
            from app.services.ai.agent import ListingAgent
            agent = ListingAgent()
            agent_result = await agent.run(
                product_title=product.title or "",
                product_description=product.description or "",
                features=f"价格: {product.price}" if product.price else "",
                platform=payload.platform,
                tone=payload.tone,
                target_language=payload.language if payload.language != "en" else None,
                max_iterations=2,
            )
            title = agent_result.get("title", "")
            description = agent_result.get("description", "")
            bullets = agent_result.get("bullet_points", [])
            seo = {
                "seo_title": agent_result.get("seo_title", ""),
                "seo_description": agent_result.get("seo_description", ""),
            }
        else:
            # ── 普通模式（分步调用） ────────────────────────
            llm = DeepSeekService()
            title = await _generate_title(llm, product, payload, persona_str)
            description = await _generate_description(llm, product, payload, persona_str)
            bullets = await _generate_bullets(llm, product, payload, persona_str)
            seo = await _optimize_seo(llm, title, description, payload)
    except Exception as e:
        # 捕获所有 AI 调用异常，返回统一的中文错误提示
        # 不暴露具体的 API 错误信息，因为终端用户看不懂
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 生成服务暂不可用，请稍后重试",
        )

    # ════════════════════════════════════════════════════════════
    # 第 5 步：生成商品主图（可选）
    # ════════════════════════════════════════════════════════════
    # 优先阿里云通义万相，失败降级 Replicate
    image_url = ""
    if payload.generate_image:
        from app.core.config import settings
        if not settings.ALIYUN_DASHSCOPE_API_KEY and not settings.REPLICATE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片生成功能暂未配置",
            )

        prompt = payload.image_prompt or (
            f"Professional e-commerce product photo of {product.title}, "
            f"white background, studio lighting, 8K, photorealistic"
        )

        # 阿里云
        if settings.ALIYUN_DASHSCOPE_API_KEY:
            try:
                img_service = AliyunImageService()
                images = await img_service.generate_image(prompt, num_outputs=1)
                if images:
                    image_url = images[0]
            except Exception:
                pass  # 降级

        # 阿里云失败或未配置 → Replicate
        if not image_url and settings.REPLICATE_API_KEY:
            try:
                img_service = ReplicateService()
                images = await img_service.generate_image(prompt, num_outputs=1)
                if images:
                    image_url = images[0]
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"图片生成失败：{str(e)}",
                )

    # ════════════════════════════════════════════════════════════
    # 第 6 步：扣减积分
    # ════════════════════════════════════════════════════════════
    # deduct_credits 用了行级锁（select_for_update），防并发扣超
    # 如果只剩 1 分，但两个请求同时来，锁确保只有一个能成功
    await current_user.deduct_credits(db, 1)

    # ════════════════════════════════════════════════════════════
    # 第 7 步：返回结果
    # ════════════════════════════════════════════════════════════
    # FastAPI 自动把 GenerateResponse 序列化为 JSON
    # response_model=GenerateResponse 也起到了文档作用（自动生成 API 文档）
    return GenerateResponse(
        title=title,
        description=description,
        bullet_points=bullets,
        seo_title=seo.get("seo_title", ""),
        seo_description=seo.get("seo_description", ""),
        image_url=image_url,
        model_used="deepseek-chat",
    )


# ── 辅助函数（私有，不暴露为 API 路由） ─────────────────────
# 这些函数以下划线开头，是 Python 约定：表示"内部使用，不要外部导入"
# 它们拆分了生成流程，使主函数更清晰

async def _generate_title(
    llm: DeepSeekService,
    product: Product,
    payload: GenerateRequest,
    persona: str = "",
) -> str:
    """调用 AI 生成商品标题

    把所有上下文拼成一个 prompt，传给 DeepSeek。
    这就是"Prompt Engineering"的实际应用：
    - 商品标题 + 价格 + 店铺名
    - 品牌调性（如果配置了）
    - 目标平台和语气
    """
    brand_context = f"\n品牌调性：{persona}" if persona else ""
    prompt = (
        f"为以下商品生成一个优化的 {payload.platform} 标题"
        f"（不超过 200 字符，{payload.language} 语言，{payload.tone} 语气）："
        f"{brand_context}\n"
        f"商品：{product.title}\n"
        f"价格：{product.price}\n"
        f"店铺：{product.shop_name or ''}"
    )
    return await llm.generate(
        system_prompt=f"你是一个 {payload.platform} 平台的专业 Listing 优化师",
        user_prompt=prompt,
        max_tokens=300,
    )


async def _generate_description(
    llm: DeepSeekService,
    product: Product,
    payload: GenerateRequest,
    persona: str = "",
) -> str:
    """调用 AI 生成商品描述"""
    return await llm.generate_product_description(
        product_title=product.title,
        platform=payload.platform,
        tone=payload.tone,
        target_language=payload.language if payload.language != "en" else None,
    )


async def _generate_bullets(
    llm: DeepSeekService,
    product: Product,
    payload: GenerateRequest,
    persona: str = "",
) -> list[str]:
    """调用 AI 生成卖点列表（Bullet Points）"""
    features = f"价格: {product.price}" if product.price else ""
    return await llm.generate_bullet_points(
        product_title=product.title,
        features=features,
        platform=payload.platform,
    )


async def _optimize_seo(
    llm: DeepSeekService,
    title: str,
    description: str,
    payload: GenerateRequest,
) -> dict:
    """调用 AI 生成 SEO 标题和描述"""
    return await llm.optimize_seo(
        title=title,
        description=description,
        platform=payload.platform,
    )
