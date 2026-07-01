"""VeyaShip - 认证路由

演示了数据库的三种基本操作：
1. 查询（select）：注册时检查邮箱是否已存在
2. 写入（add）：创建用户
3. 更新（赋值 + flush）：更新登录时间
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """注册新用户

    数据库操作流程：
    1. SELECT：查邮箱是否已注册
    2. INSERT：写入新用户
    3. flush：立即获取生成的 UUID
    4. get_db 自动 commit
    """
    # ── SELECT 查询 ─────────────────────────────────────────
    # select(User) = "SELECT * FROM users"
    # .where(User.email == payload.email) = "WHERE email=?"
    # .scalar_one_or_none() = 取第一行，没有则返回 None
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # ── INSERT 写入 ─────────────────────────────────────────
    # 创建一个 User 对象 → 相当于 INSERT 的一行数据
    # password_hash 存的是 bcrypt 哈希，不是明文
    user = User(
        email=payload.email,
        username=payload.username or payload.email.split("@")[0],
        password_hash=hash_password(payload.password),
    )
    db.add(user)  # 加入会话（还没写入数据库）
    await db.flush()  # 写入数据库，此时 user.id 才生成

    # 签发 JWT
    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。

    这里没有直接查数据库，而是通过 JWT token 解析出用户 ID，
    由 get_current_user 依赖帮我们查好了。
    """
    return current_user
