"""VeyaShip - 数据库配置

数据库引擎和会话管理，负责连接数据库、创建会话、自动提交/回滚。
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ── 创建异步数据库引擎 ──────────────────────────────────────────
# 引擎 = 数据库连接池，所有数据库操作都通过它
# SQLite 连接参数加 check_same_thread=False 允许跨线程使用
engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.USE_SQLITE else {},
)

# ── SQLite 优化 ────────────────────────────────────────────────
# WAL 模式 = 写入不阻塞读取，提高并发性能
# foreign_keys=ON = SQLite 默认外键不生效，手动开启
if settings.USE_SQLITE:
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ── 会话工厂 ──────────────────────────────────────────────────
# 每次请求创建一个独立会话，用完自动关闭
# expire_on_commit=False 提交后对象仍然可用，不用重新查
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── 模型基类 ──────────────────────────────────────────────────
# 所有数据模型都要继承这个 Base
class Base(DeclarativeBase):
    """所有数据库模型的基类。"""
    pass


# ── 获取数据库会话（依赖注入） ────────────────────────────────
# FastAPI 路由通过 Depends(get_db) 获取数据库会话
# 请求期间：yield session → 路由里操作数据库
# 请求结束：成功则 commit，失败则 rollback，最后关闭会话
async def get_db() -> AsyncSession:
    """提供给 FastAPI 路由的数据库会话依赖。

    用法：
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session  # 路由里 await db.execute(...) 就在这个会话里执行
            await session.commit()  # 路由正常执行完 → 自动提交
        except Exception:
            await session.rollback()  # 路由抛出异常 → 自动回滚
            raise
        finally:
            await session.close()  # 归还连接到连接池


# ── 建表 ──────────────────────────────────────────────────────
# SQLite 开发模式下，项目启动时自动创建所有表
# PostgreSQL 生产模式下，通过 Alembic 迁移管理表结构
async def init_db():
    """项目启动时调用，自动创建所有表（仅开发模式）。

    生产环境请改用 Alembic 迁移：
        alembic revision --autogenerate -m "描述"
        alembic upgrade head
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
