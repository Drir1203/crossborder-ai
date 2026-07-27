"""VeyaShip - 设置路由（爬虫配置 + 品牌调性）"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.persona import Persona
from app.models.system_config import SystemConfig
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/settings", tags=["Settings"])


# ── 白名单管理（测试账号免限制） ────────────────────────────

class WhitelistRequest(BaseModel):
    email: str = Field(..., description="要添加/移除的邮箱")


@router.post("/whitelist/add")
async def add_whitelist(
    payload: WhitelistRequest,
    current_user: User = Depends(get_current_user),
):
    """添加白名单账号（测试账号不受套餐限制）"""
    from app.core.access_control import add_whitelist as _add
    _add(payload.email)
    return {"message": f"已添加白名单: {payload.email}"}


@router.post("/whitelist/remove")
async def remove_whitelist(
    payload: WhitelistRequest,
    current_user: User = Depends(get_current_user),
):
    """移除白名单账号"""
    from app.core.access_control import remove_whitelist as _remove
    _remove(payload.email)
    return {"message": f"已移除白名单: {payload.email}"}


@router.get("/whitelist")
async def list_whitelist():
    """查看所有白名单账号"""
    from app.core.access_control import WHITELIST_EMAILS
    return {"emails": list(WHITELIST_EMAILS)}

# ════════════════════════════════════════════════════════════════
# 爬虫配置
# ════════════════════════════════════════════════════════════════

class ScrapingConfigRequest(BaseModel):
    api_key: str = Field("", description="Onebound API Key")
    api_secret: str = Field("", description="Onebound API Secret")

class ScrapingConfigResponse(BaseModel):
    api_key: str = ""
    api_secret: str = ""
    configured: bool = False

@router.get("/scraping", response_model=ScrapingConfigResponse)
async def get_scraping_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key.in_(["onebound_api_key", "onebound_api_secret"]))
    )
    config = {row.key: row.value or "" for row in result.scalars().all()}
    return ScrapingConfigResponse(
        api_key=config.get("onebound_api_key", ""),
        api_secret=config.get("onebound_api_secret", ""),
        configured=bool(config.get("onebound_api_key")),
    )

@router.put("/scraping", response_model=ScrapingConfigResponse)
async def update_scraping_config(
    payload: ScrapingConfigRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for key, value in [("onebound_api_key", payload.api_key), ("onebound_api_secret", payload.api_secret)]:
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = value
        else:
            db.add(SystemConfig(key=key, value=value))
    await db.flush()
    return ScrapingConfigResponse(api_key=payload.api_key, api_secret=payload.api_secret, configured=bool(payload.api_key))


# ════════════════════════════════════════════════════════════════
# 品牌调性（F5 Persona）
# ════════════════════════════════════════════════════════════════

class PersonaRequest(BaseModel):
    brand_name: Optional[str] = Field(None, max_length=200)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    tone: str = "professional"
    tone_custom: Optional[str] = Field(None, max_length=500)
    banned_words: list[str] = []

class PersonaResponse(BaseModel):
    brand_name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    tone: str = "professional"
    tone_custom: Optional[str] = None
    banned_words: list[str] = []


@router.get("/persona", response_model=PersonaResponse)
async def get_persona(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的品牌调性配置"""
    result = await db.execute(select(Persona).where(Persona.user_id == current_user.id))
    p = result.scalar_one_or_none()
    if not p:
        return PersonaResponse()
    return PersonaResponse(
        brand_name=p.brand_name,
        tagline=p.tagline,
        description=p.description,
        tone=p.tone,
        tone_custom=p.tone_custom,
        banned_words=json.loads(p.banned_words) if p.banned_words else [],
    )


@router.put("/persona", response_model=PersonaResponse)
async def update_persona(
    payload: PersonaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """保存品牌调性配置"""
    result = await db.execute(select(Persona).where(Persona.user_id == current_user.id))
    persona = result.scalar_one_or_none()
    if not persona:
        persona = Persona(user_id=current_user.id)
        db.add(persona)
    persona.brand_name = payload.brand_name
    persona.tagline = payload.tagline
    persona.description = payload.description
    persona.tone = payload.tone
    persona.tone_custom = payload.tone_custom
    persona.banned_words = json.dumps(payload.banned_words, ensure_ascii=False)
    await db.flush()
    return PersonaResponse(
        brand_name=persona.brand_name,
        tagline=persona.tagline,
        description=persona.description,
        tone=persona.tone,
        tone_custom=persona.tone_custom,
        banned_words=json.loads(persona.banned_words) if persona.banned_words else [],
    )
