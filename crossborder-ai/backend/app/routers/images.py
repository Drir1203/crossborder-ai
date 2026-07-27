"""VeyaShip - AI 图片生成路由

生产级设计：异步任务模式。
用户提交生成请求 → 立即返回 task_id → 前端轮询结果。
不会阻塞请求 10+ 秒。
"""

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limit import RateLimit
from app.dependencies import get_current_user
from app.models.persona import Persona
from app.models.user import User
from app.services.ai.aliyun_image import AliyunImageService
from app.core.access_control import check_feature_access
from app.services.ai.replicate import ReplicateService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/images", tags=["AI 图片生成"])

# ── 内存任务存储（生产环境建议换 Redis） ─────────────────
_task_store: dict[str, dict] = {}


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="图片描述词")
    num_outputs: int = Field(default=1, ge=1, le=4)


class TaskResponse(BaseModel):
    task_id: str
    status: str  # pending / processing / completed / failed
    image_urls: list[str] = []
    model_used: str = ""
    error: Optional[str] = None


async def _run_generation(task_id: str, prompt: str, num_outputs: int):
    """后台执行图片生成（不阻塞主请求）"""
    _task_store[task_id]["status"] = "processing"

    # 品牌调性由主请求拼接，prompt 已包含

    # 优先阿里云
    if settings.ALIYUN_DASHSCOPE_API_KEY:
        try:
            svc = AliyunImageService()
            urls = await svc.generate_image(prompt=prompt, num_outputs=num_outputs)
            if urls:
                _task_store[task_id].update({
                    "status": "completed",
                    "image_urls": urls,
                    "model_used": settings.ALIYUN_IMAGE_MODEL,
                })
                return
        except Exception:
            pass  # 降级

    # 降级 Replicate
    if settings.REPLICATE_API_KEY:
        try:
            svc = ReplicateService()
            urls = await svc.generate_image(prompt=prompt, num_outputs=num_outputs)
            if urls:
                _task_store[task_id].update({
                    "status": "completed",
                    "image_urls": urls,
                    "model_used": settings.REPLICATE_MODEL,
                })
                return
        except Exception as e:
            _task_store[task_id].update({"status": "failed", "error": str(e)})
            return

    _task_store[task_id].update({"status": "failed", "error": "无可用的图片生成服务"})


@router.post("/generate", response_model=TaskResponse)
async def generate_image(
    payload: GenerateImageRequest,
    request: Request,
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交图片生成任务（异步，立即返回 task_id）

    前端通过 GET /api/v1/images/status/{task_id} 轮询结果。
    """
    if not check_feature_access(current_user, "ai_image"):
        raise HTTPException(status_code=403, detail="图片生成功能仅限专业版套餐使用，请升级套餐")

    if not settings.ALIYUN_DASHSCOPE_API_KEY and not settings.REPLICATE_API_KEY:
        raise HTTPException(status_code=400, detail="图片生成功能暂未配置")

    # 拼接品牌调性
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

    # 创建异步任务
    task_id = str(uuid.uuid4())
    _task_store[task_id] = {"status": "pending", "image_urls": [], "model_used": "", "error": None}

    # 后台执行（不 await，立即返回）
    asyncio.create_task(_run_generation(task_id, enhanced_prompt, payload.num_outputs))

    return TaskResponse(task_id=task_id, status="pending")


@router.get("/status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """查询图片生成任务状态"""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        image_urls=task.get("image_urls", []),
        model_used=task.get("model_used", ""),
        error=task.get("error"),
    )
