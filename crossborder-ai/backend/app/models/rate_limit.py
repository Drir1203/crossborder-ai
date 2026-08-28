"""VeyaShip - 限流计数模型

跨进程（多 uvicorn worker）共享的固定窗口限流计数器。
生产用 PostgreSQL：所有 worker 共享这一张表，限流全局生效；
开发 SQLite 用内存限流（见 core/rate_limit.py），不落表。

窗口用墙钟时间（floor(now/window)*window），
不同 worker 的 time.monotonic() 不可比，必须用墙钟。
"""

from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RateLimitWindow(Base):
    """固定窗口限流计数：同一 (key, window_start) 只增 count。"""

    __tablename__ = "rate_limits"
    __table_args__ = (
        UniqueConstraint("key", "window_start", name="uq_rate_limit_window"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 限流 key：user:{user_id}:{limit_key} 或 ip:{ip}:{limit_key}
    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    # 窗口起始时间戳（秒，墙钟），如 floor(time.time()/60)*60
    window_start: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # 该窗口内已计数请求数
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
