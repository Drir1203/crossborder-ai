"""VeyaShip - Agent 任务加中间进度列：流式输出

执行器每完成一步把累积 steps 写入 progress（JSON），SSE 端点
轮询该列实时推流，前端替代 2s 轮询看到步骤逐步完成。

Revision ID: 007
Revises: 006
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """给 agent_tasks 加 progress 列（执行中间进度 JSON）"""
    op.add_column("agent_tasks", sa.Column("progress", sa.Text(), nullable=True))


def downgrade() -> None:
    """回滚：删除 progress 列"""
    op.drop_column("agent_tasks", "progress")
