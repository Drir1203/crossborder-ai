"""VeyaShip - 竞品分析路由（F6 Radar）

功能：
1. 输入竞品链接/关键词 → 抓取竞品数据
2. 展示价格、销量对比
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.scraper import scrape_1688
from pydantic import BaseModel, Field

router = APIRouter(prefix="/radar", tags=["竞品分析"])


@router.get("/scrape")
async def scrape_competitor(
    url: str = Query(..., description="竞品 1688 链接"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """抓取竞品商品信息

    提取竞品的标题、价格、销量、店铺名，
    供卖家做竞品对比分析。
    """
    try:
        from app.models.system_config import SystemConfig
        from sqlalchemy import select

        config_rows = await db.execute(
            select(SystemConfig).where(SystemConfig.key.in_(["onebound_api_key", "onebound_api_secret"]))
        )
        sys_config = {row.key: row.value or "" for row in config_rows.scalars().all()}

        data = await scrape_1688(
            url,
            api_key=sys_config.get("onebound_api_key", ""),
            api_secret=sys_config.get("onebound_api_secret", ""),
        )
        return {"competitor": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"竞品抓取失败：{str(e)}")
