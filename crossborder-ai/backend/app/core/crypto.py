"""VeyaShip - 服务商密钥加密工具

Onebound 等平台级 API Key 在数据库中密文存储（Fernet 对称加密），
避免 DB 泄漏时服务商密钥直接暴露。

- 加密密钥由 JWT_SECRET_KEY 派生（SHA-256 → Fernet key）；
  本地开发无密钥时降级为明文存储，避免阻塞开箱即用。
- 存储格式：``enc:<base64 密文>`` —— ``enc:`` 前缀标记已加密；
  无前缀的旧数据按明文原样返回，兼容存量行。
"""

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings

PREFIX = "enc:"


def _fernet_key() -> bytes | None:
    """由 JWT_SECRET_KEY 派生 Fernet 密钥；未配置时返回 None（本地开发降级）。"""
    secret = settings.JWT_SECRET_KEY or settings.SECRET_KEY
    if not secret:
        return None
    return base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())


def encrypt_value(plain: str | None) -> str:
    """加密。无可用密钥（本地开发）时原样返回明文。"""
    if not plain:
        return plain or ""
    key = _fernet_key()
    if not key:
        return plain
    return PREFIX + Fernet(key).encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_value(stored: str | None) -> str:
    """解密。``enc:`` 前缀 → 解密；失败或无前缀 → 按原样返回（兼容存量明文）。"""
    if not stored:
        return stored or ""
    if not stored.startswith(PREFIX):
        return stored
    key = _fernet_key()
    if not key:
        return stored
    try:
        return Fernet(key).decrypt(stored[len(PREFIX):].encode("utf-8")).decode("utf-8")
    except Exception:
        # 密文损坏或密钥变更时按原样返回，避免抓取功能整体不可用
        return stored


def mask_secret(value: str | None) -> str:
    """回显掩码：保留前 4 + 后 4，中间 ****，避免 API Key 明文暴露在前端。"""
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"
