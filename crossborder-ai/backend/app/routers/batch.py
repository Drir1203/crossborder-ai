"""VeyaShip - 批量处理路由（F4 Batch）

功能：
1. CSV 上传解析
2. batch_jobs 表存任务
3. /api/cron/process-batch 逐条处理
"""

import csv
import io
import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import RateLimit
from app.core.access_control import check_feature_access
from app.dependencies import get_current_user
from app.models.batch_job import BatchJob
from app.models.product import Product
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/batch", tags=["批量处理"])

EXPECTED_HEADERS = ["title", "url", "price", "description"]


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(..., description="CSV 文件，含标题头：title, url, price, description"),
    _ratelimit=Depends(RateLimit("batch")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传 CSV 文件，解析后创建批量任务。

    CSV 格式：
        title,url,price,description
        商品A,https://...,29.99,描述文字
        商品B,https://...,19.99,描述文字
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="请上传 .csv 文件")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("gbk", errors="replace")

    reader = csv.DictReader(io.StringIO(text))

    # 校验标题头
    if reader.fieldnames:
        headers = [h.strip().lower() for h in reader.fieldnames]
        missing = [h for h in EXPECTED_HEADERS if h not in headers]
        if missing:
            raise HTTPException(status_code=400, detail=f"CSV 缺少必要列：{', '.join(missing)}")

    # 逐行创建任务
    jobs = []
    row_count = 0
    for row in reader:
        row_count += 1
        job = BatchJob(
            user_id=current_user.id,
            source_type="csv",
            source_filename=file.filename,
            row_index=row_count,
            title=row.get("title", "").strip(),
            url=row.get("url", "").strip(),
            price=row.get("price", "").strip(),
            description=row.get("description", "").strip(),
            status="pending",
        )
        db.add(job)
        jobs.append(job)

    if row_count == 0:
        raise HTTPException(status_code=400, detail="CSV 文件为空")

    await db.flush()

    return {
        "message": f"已导入 {row_count} 条任务",
        "total": row_count,
    }


@router.get("/jobs")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="过滤状态"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看批量任务列表"""
    query = select(BatchJob).where(BatchJob.user_id == current_user.id)
    if status_filter:
        query = query.where(BatchJob.status == status_filter)
    query = query.order_by(BatchJob.created_at.desc())

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    jobs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(j.id),
                "row_index": j.row_index,
                "title": j.title,
                "url": j.url,
                "status": j.status,
                "error": j.error,
                "created_at": str(j.created_at),
                "processed_at": str(j.processed_at) if j.processed_at else None,
            }
            for j in jobs
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil((total or 0) / page_size)),
    }


@router.post("/process/{job_id}")
async def process_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """处理单条批量任务：将 CSV 行转为商品

    可从 /api/cron/process-batch 调度批量执行。
    """
    from uuid import UUID
    try:
        uid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的任务 ID")

    result = await db.execute(
        select(BatchJob).where(BatchJob.id == uid, BatchJob.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.status == "processed":
        raise HTTPException(status_code=400, detail="任务已处理")

    # 处理：创建商品
    try:
        product = Product(
            title=job.title or "",
            url=job.url or f"batch://{job.id}",
            price=float(job.price) if job.price else None,
        )
        db.add(product)
        job.status = "processed"
        job.processed_at = datetime.now(timezone.utc)
        await db.flush()
        return {"message": "处理成功", "product_id": str(product.id)}
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        await db.flush()
        raise HTTPException(status_code=500, detail=f"处理失败：{str(e)}")


@router.post("/cron/process-batch")
async def cron_process_batch(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量处理所有 pending 状态的任务

    设计为可被 APScheduler 定时调用。
    """
    result = await db.execute(
        select(BatchJob).where(
            BatchJob.user_id == current_user.id,
            BatchJob.status == "pending",
        ).limit(10)
    )
    jobs = result.scalars().all()

    results = []
    for job in jobs:
        try:
            product = Product(
                title=job.title or "",
                url=job.url or f"batch://{job.id}",
                price=float(job.price) if job.price else None,
            )
            db.add(product)
            job.status = "processed"
            job.processed_at = datetime.now(timezone.utc)
            results.append({"job_id": str(job.id), "status": "success"})
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            results.append({"job_id": str(job.id), "status": "failed", "error": str(e)})

    await db.flush()
    return {"processed": len(results), "results": results}


@router.post("/process-ai")
async def batch_process_with_ai(
    platform: str = "amazon",
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量 AI 处理：对 pending 状态的批量任务执行 AI 生成

    流程：
    1. 取所有 pending 任务
    2. 逐条创建商品
    3. AI 生成 Listing（标题/描述/卖点）
    4. 标记完成
    """
    if not check_feature_access(current_user, "batch_ai"):
        raise HTTPException(status_code=403, detail="批量 AI 处理仅限 Standard 及以上套餐使用")

    if current_user.credits < len([1]):
        raise HTTPException(status_code=402, detail="积分不足")

    result = await db.execute(
        select(BatchJob).where(BatchJob.user_id == current_user.id, BatchJob.status == "pending").limit(20)
    )
    jobs = result.scalars().all()
    if not jobs:
        return {"message": "没有待处理的任务", "processed": 0}

    from app.services.ai.deepseek import DeepSeekService
    llm = DeepSeekService()
    results = []

    for job in jobs:
        try:
            # 创建商品
            product = Product(
                user_id=current_user.id,
                title=job.title or "",
                url=job.url or f"batch://{job.id}",
                price=float(job.price) if job.price else None,
                description=job.description or "",
            )
            db.add(product)
            await db.flush()

            # AI 生成 Listing
            title = await llm.generate(
                f"You are a professional {platform} listing copywriter.",
                f"Generate an optimized {platform} product title (max 200 chars) in {language}.\nProduct: {product.title}\nPrice: {product.price}",
                max_tokens=300,
            )
            desc = await llm.generate_product_description(
                product_title=product.title or "",
                platform=platform,
            )
            bullets = await llm.generate_bullet_points(
                product_title=product.title or "",
                features=f"Price: {product.price}" if product.price else "",
                platform=platform,
            )

            job.status = "processed"
            job.processed_at = datetime.now(timezone.utc)
            results.append({
                "job_id": str(job.id), "product_id": str(product.id),
                "title": title[:50], "bullet_count": len(bullets),
                "status": "success",
            })
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            results.append({"job_id": str(job.id), "status": "failed", "error": str(e)})

    await db.flush()
    return {"message": f"已处理 {len(results)} 条", "processed": len(results), "results": results}
