"""VeyaShip - AI 图片生成路由"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limit import RateLimit
from app.dependencies import get_current_user
from app.models.persona import Persona
from app.models.user import User
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
    """用 FLUX AI 生成商品图片（AI 增强：拼接品牌调性到 prompt）。"""
    if not settings.REPLICATE_API_KEY:
        raise HTTPException(status_code=400, detail="图片生成功能暂未配置")

    # 加载品牌调性（F5 Persona），拼接到图片 prompt
    enhanced_prompt = payload.prompt
    persona_result = await db.execute(select(Persona).where(Persona.user_id == current_user.id))
    persona = persona_result.scalar_one_or_none()
    if persona:
        tone_text = persona.tone_custom or persona.tone or ''
        if tone_text:
            # 避免重复 "style"（tone_custom 可能已含 style）
            suffix = f", {tone_text}" if 'style' in tone_text.lower() else f", {tone_text} style"
            enhanced_prompt = f"{payload.prompt}{suffix}"
        if persona.brand_name:
            enhanced_prompt += f", {persona.brand_name} brand identity"

    try:
        svc = ReplicateService()
        urls = await svc.generate_image(
            prompt=enhanced_prompt,
            num_outputs=payload.num_outputs,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"生成失败：{str(e)}")

    return GenerateImageResponse(image_urls=urls, model_used="black-forest-labs/flux-schnell")
