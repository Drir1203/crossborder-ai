"""VeyaShip - 限流计数表：跨进程（多 uvicorn worker）共享固定窗口限流

为 rate_limits 表，配合 core/rate_limit.py 的 PG 分支使用：
所有 worker 共享同一张表，限流全局生效，不再受单机内存限制。

Revision ID: 004
Revises: 003
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建限流计数表"""
    op.create_table(
        "rate_limits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "window_start", name="uq_rate_limit_window"),
    )
    op.create_index("ix_rate_limits_key", "rate_limits", ["key"])


def downgrade() -> None:
    """回滚：删除限流计数表"""
    op.drop_index("ix_rate_limits_key", table_name="rate_limits")
    op.drop_table("rate_limits")
