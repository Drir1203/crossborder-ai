"""VeyaShip - 安全工具模块

【全栈学习者必读】
这个模块做了两件事，几乎所有后端项目都需要：
1. JWT 令牌（Token）的创建和验证 —— 相当于"临时通行证"
2. 密码的哈希存储和校验 —— 绝不存明文密码

理解 JSON Web Token (JWT)：
- JWT 是一个字符串，分三部分：header.payload.signature
- 服务器用 SECRET_KEY 签名，客户端持有 token
- token 里包含用户 ID（sub字段）和过期时间（exp字段）
- 客户端每次请求把 token 放在 HTTP Header 里
- 服务器验签通过即认为已认证，不需要查数据库

JWT vs Session：
- Session：用户信息存在服务器内存/Redis，客户端只存 session_id
- JWT：用户信息存在 token 本身，服务器无状态（stateless）
- JWT 适合分布式系统，但 token 一旦签发，过期前无法主动撤销
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── 密码加密上下文 ──────────────────────────────────────────────
# CryptContext 是 passlib 库的核心，支持多种哈希算法
# "bcrypt" 是目前最流行的密码哈希算法
# "deprecated" 参数指定旧算法升级策略
# 如果以后 bcrypt 不再安全，加新算法名即可，旧密码自动升级
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对明文密码做 bcrypt 哈希。

    哈希是单向的：从哈希值无法反推原始密码。
    bcrypt 会自动加盐（salt），同一密码每次哈希结果都不同。

    Args:
        password: 用户注册时输入的明文密码

    Returns:
        哈希后的密文字符串（约 60 字符）
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码是否匹配哈希值。

    用户登录时调用：输入明文密码 vs 数据库存的哈希值。
    即使哈希值泄漏，攻击者也无法反推密码。

    Args:
        plain_password: 用户登录时输入的明文密码
        hashed_password: 数据库里存的哈希值

    Returns:
        True=密码正确, False=密码错误
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """签发 JWT 访问令牌（Access Token）。

    流程：
    1. 设置过期时间（默认 7 天，通过 settings.ACCESS_TOKEN_EXPIRE_MINUTES 配置）
    2. 把用户 ID 放入 sub（subject）字段
    3. 用 JWT_SECRET_KEY 签名 → 生成一个不可篡改的 token 字符串

    Args:
        subject: 用户标识（用户 ID 的字符串形式）
        extra_claims: 额外的声明字段（如用户角色）
        expires_delta: 自定义过期时间，默认用配置的 7 天

    Returns:
        JWT 字符串（如 "eyJhbGciOiJIUzI1NiI9.eyJzdWIiOiIxIiw...")
    """
    # 计算过期时间：当前UTC时间 + 有效期
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # JWT Payload（载荷）：存放要传递的用户信息
    payload = {
        "sub": subject,             # subject = 用户ID，标准字段
        "exp": expire,              # expiration time，到期时间
        "iat": datetime.now(timezone.utc),  # issued at，签发时间
        "type": "access",           # 自定义：标记这是 access token
    }
    if extra_claims:
        payload.update(extra_claims)

    # jwt.encode 做三件事：
    # 1. payload → JSON 字符串
    # 2. Base64 编码 header 和 payload
    # 3. 用密钥对 header.payload 做 HMAC-SHA256 签名
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """解码并验证 JWT 令牌。

    验证包括：签名是否有效、是否过期。
    如果 token 被篡改或已过期，抛出 JWTError。

    Args:
        token: JWT 字符串

    Returns:
        payload 字典（包含 sub、exp 等字段）

    Raises:
        JWTError: token 无效或已过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise


def decode_token_safe(token: str) -> Dict[str, Any] | None:
    """安全解码 JWT（不抛异常，失败返回 None）。

    某些场景需要不会阻断流程的令牌检查，比如"有 token 就个性化，没有也正常显示"。

    Args:
        token: JWT 字符串

    Returns:
        payload 字典，或 None（无效/过期时）
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
