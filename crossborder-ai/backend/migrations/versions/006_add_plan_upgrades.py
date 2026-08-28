"""VeyaShip - 套餐升级申请表：人工收款闭环

用户提交升级申请落库（带订单号/金额/联系方式），管理员核对转账后
一键开通/拒绝，形成可追溯对账单。pending → approved | rejected。

Revision ID: 006
Revises: 005
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建套餐升级申请表"""
    op.create_table(
        "plan_upgrade_requests",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", PG_UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("contact", sa.String(100), nullable=False),
        sa.Column("order_id", sa.String(40), nullable=False, unique=True),
        sa.Column("amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("note", sa.String(200), nullable=True),
        sa.Column("handled_by", PG_UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plan_upgrade_requests_status", "plan_upgrade_requests", ["status"])


def downgrade() -> None:
    """回滚：删除套餐升级申请表"""
    op.drop_index("ix_plan_upgrade_requests_status", table_name="plan_upgrade_requests")
    op.drop_table("plan_upgrade_requests")
