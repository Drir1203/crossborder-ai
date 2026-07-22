"""VeyaShip - FastAPI 依赖注入

【全栈学习者必读】
"依赖注入"（Dependency Injection）是 FastAPI 最核心的概念。
理解它，就理解了 FastAPI 的架构精髓。

什么是依赖注入？
- 路由函数需要的"东西"，不自己创建，而是声明"我需要什么"
- FastAPI 自动把需要的东西传进来
- 就像去餐厅：你不自己种菜做饭，你点菜（声明依赖），服务员（FastAPI）给你端上来

常见的依赖：
- get_db: 给路由一个数据库会话
- get_current_user: 从 JWT token 解析出当前登录用户
- RateLimit: 检查请求是否超过频率限制

依赖注入的好处：
- 解耦：路由函数不需要知道如何创建数据库连接
- 复用：多个路由共享同一个依赖
- 测试：可以替换依赖（如用测试数据库代替真实数据库）
- 可维护：修改依赖实现，所有路由自动生效
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# ── OAuth2 密码流配置 ──────────────────────────────────────────
# OAuth2PasswordBearer 告诉 FastAPI：
# "客户端应该把 token 放在 HTTP Header 里：
#   Authorization: Bearer <token>"
#
# tokenUrl 指定了获取 token 的 API 路径（用户登录的接口）
# auto_error=False 表示如果没有 token，不自动报错，而是传 None
# 这样有些接口可以"有 token 就认证，没有也允许访问"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """【核心】从 JWT token 解析出当前登录用户。

    这是最常用的依赖，几乎所有需要登录的接口都用它。

    执行流程：
    1. FastAPI 从 HTTP Header 提取 Bearer token
    2. decode_token() 验证 JWT 签名和过期时间
    3. 取出 payload.sub 里的用户 ID
    4. 查数据库找到对应的 User 对象
    5. 返回 User 对象给路由函数

    路由中使用：
        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"username": current_user.username}
        # 不需要手动解析 token！不需要自己查数据库！
        # FastAPI 自动搞定这一切

    Args:
        token: JWT 令牌（自动从请求头提取）
        db: 数据库会话（自动创建和释放）

    Returns:
        当前登录的 User 对象

    Raises:
        HTTPException 401: 未提供 token / token 无效 / 用户不存在
    """
    # 第一步：检查是否有 token
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
        )

    # 第二步：解码 token，提取用户 ID
    try:
        payload = decode_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的登录令牌",
            )
        # 把字符串 ID 转成 UUID 对象（数据库用 UUID 做主键）
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        # JWTError = 签名无效或已过期
        # ValueError = UUID 格式不对
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )

    # 第三步：查数据库，确认用户还存在
    # 这一步不是必须的（JWT 本身已经够安全），
    # 但可以拦截"用户已被删除"的情况
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user
