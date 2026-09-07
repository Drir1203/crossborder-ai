"""VeyaShip - AI 图片生成任务模型（CAP-07 落库）"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImageGenerationTask(Base):
    """图片生成任务表 —— 每个图片生成请求一行记录

    从内存 _task_store 升级为落库：状态与结果写 DB，前端可轮询 /status、
    拉取 /history 展示画廊。图片生成仍在后台异步执行。
    """

    __tablename__ = "image_generation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # 使用的图片描述词（已含品牌调性拼接）
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    # 状态: pending / processing / completed / failed
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    # 生成结果图片 URL 列表（JSON 数组文本，参考 persona.banned_words 做法）
    image_urls: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 使用的模型（阿里云通义万相 / Replicate FLUX）
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 失败原因（仅 status=failed 时非空）
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
