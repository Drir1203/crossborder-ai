"""VeyaShip - 设置路由

演示了 key-value 表的读写操作。
SystemConfig 表就是一个简单的键值对存储，
管理员在网页上配置 API Key，保存到数据库。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.system_config import SystemConfig
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/settings", tags=["Settings"])


class ScrapingConfigRequest(BaseModel):
    """请求体：保存爬虫 API 配置"""
    api_key: str = Field("", description="Onebound API Key")
    api_secret: str = Field("", description="Onebound API Secret")


class ScrapingConfigResponse(BaseModel):
    """响应体：当前 API 配置状态"""
    api_key: str = ""
    api_secret: str = ""
    configured: bool = False


@router.get("/scraping", response_model=ScrapingConfigResponse)
async def get_scraping_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询当前的 1688 抓取配置。

    SQL：
        SELECT * FROM system_config WHERE key IN ('onebound_api_key', 'onebound_api_secret')
    """
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.key.in_(["onebound_api_key", "onebound_api_secret"])
        )
    )
    rows = result.scalars().all()
    config = {row.key: row.value or "" for row in rows}

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
    """保存 API 配置。

    这是 UPSERT 操作（INSERT OR UPDATE）：
    如果 key 已存在 → 更新 value
    如果 key 不存在 → 插入新行

    保存后立即生效，不需要重启后端。

    SQL（PostgreSQL 语法）：
        INSERT INTO system_config (key, value)
        VALUES ('onebound_api_key', 'xxx')
        ON CONFLICT (key) DO UPDATE SET value = 'xxx'
    """
    for key, value in [
        ("onebound_api_key", payload.api_key),
        ("onebound_api_secret", payload.api_secret),
    ]:
        # 先查有没有这条记录
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        existing = result.scalar_one_or_none()

        if existing:
            # key 已存在 → 更新
            existing.value = value
        else:
            # key 不存在 → 插入
            db.add(SystemConfig(key=key, value=value))

    await db.flush()

    return ScrapingConfigResponse(
        api_key=payload.api_key,
        api_secret=payload.api_secret,
        configured=bool(payload.api_key),
    )
