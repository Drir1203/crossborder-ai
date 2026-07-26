"""VeyaShip - AI 图片生成路由

双模式图片生成：
1. 阿里云通义万相（优先，国内速度快）
2. Replicate FLUX（备选，海外服务）
自动降级，用户无感知。
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limit import RateLimit
from app.dependencies import get_current_user
from app.models.persona import Persona
from app.models.user import User
from app.services.ai.aliyun_image import AliyunImageService
from app.services.ai.replicate import ReplicateService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/images", tags=["AI 图片生成"])


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="图片描述词")
    num_outputs: int = Field(default=1, ge=1, le=4)


class GenerateImageResponse(BaseModel):
    image_urls: list[str] = []
    model_used: str = ""


@router.post("/generate", response_model=GenerateImageResponse)
async def generate_image(
    payload: GenerateImageRequest,
    request: Request,
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成商品图片

    优先用阿里云通义万相（国内服务器速度快），
    如果阿里云未配置，降级到 Replicate FLUX。
    """
    # 检查是否至少配置了一个服务
    if not settings.ALIYUN_DASHSCOPE_API_KEY and not settings.REPLICATE_API_KEY:
        raise HTTPException(status_code=400, detail="图片生成功能暂未配置，请联系管理员开通")

    # 加载品牌调性
    enhanced_prompt = payload.prompt
    persona_result = await db.execute(select(Persona).where(Persona.user_id == current_user.id))
    persona = persona_result.scalar_one_or_none()
    if persona:
        tone_text = persona.tone_custom or persona.tone or ''
        if tone_text:
            suffix = f", {tone_text}" if 'style' in tone_text.lower() else f", {tone_text} style"
            enhanced_prompt = f"{payload.prompt}{suffix}"
        if persona.brand_name:
            enhanced_prompt += f", {persona.brand_name} brand identity"

    # 优先：阿里云通义万相
    if settings.ALIYUN_DASHSCOPE_API_KEY:
        try:
            svc = AliyunImageService()
            urls = await svc.generate_image(
                prompt=enhanced_prompt,
                num_outputs=payload.num_outputs,
            )
            if urls:
                return GenerateImageResponse(image_urls=urls, model_used=settings.ALIYUN_IMAGE_MODEL)
        except Exception as e:
            # 阿里云失败，降级到 Replicate
            if not settings.REPLICATE_API_KEY:
                raise HTTPException(status_code=502, detail=f"图片生成失败：{str(e)}")

    # 备选：Replicate FLUX
    try:
        svc = ReplicateService()
        urls = await svc.generate_image(
            prompt=enhanced_prompt,
            num_outputs=payload.num_outputs,
        )
        return GenerateImageResponse(image_urls=urls, model_used=settings.REPLICATE_MODEL)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"图片生成失败：{str(e)}")
