"""VeyaShip - 商品模型

存储从 1688 抓取或手动录入的商品信息。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    """商品表 —— 存储抓取或录入的商品数据

    用户通过 1688 链接抓取或手动录入后，数据存在这里。
    后续 AI 生成 Listing 时，从这个表读取商品信息。
    """

    __tablename__ = "products"

    # ── 主键 ──────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── 核心数据 ──────────────────────────────────────────────
    # url 加了唯一索引，防止重复抓取同一个商品
    url: Mapped[str] = mapped_column(
        String(500), unique=True, index=True, nullable=False
    )
    # title 可为空，因为手动录入时可以只填链接不填标题
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 主图链接，后续 AI 生成 Listing 时可以直接引用
    main_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── 价格/销量/店铺 ────────────────────────────────────────
    # Float 适合价格，但要注意精度问题（生产环境建议用 Decimal）
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    sales_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shop_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── 时间戳 ──────────────────────────────────────────────
    # created_at 在插入时自动填
    # updated_at 在更新时自动更新（onupdate）
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Product {self.id}: {self.title}>"
