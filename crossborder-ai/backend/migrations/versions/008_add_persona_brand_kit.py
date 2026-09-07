"""VeyaShip - Persona 加 Brand Kit 扩展字段（CAP-04）

给 personas 表加三个可空字段：target_market（目标市场/站点）、
product_category（主营类目）、image_style（图片风格提示词）。
字段均可空，老数据无需回填。

Revision ID: 008
Revises: 007
Create Date: 2026-09-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """给 personas 加 Brand Kit 三个可空列（幂等、不破坏既有数据）"""
    op.add_column("personas", sa.Column("target_market", sa.String(length=200), nullable=True))
    op.add_column("personas", sa.Column("product_category", sa.String(length=200), nullable=True))
    op.add_column("personas", sa.Column("image_style", sa.String(length=500), nullable=True))


def downgrade() -> None:
    """回滚：删除这三个列"""
    op.drop_column("personas", "image_style")
    op.drop_column("personas", "product_category")
    op.drop_column("personas", "target_market")
