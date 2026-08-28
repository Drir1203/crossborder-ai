"""VeyaShip - 安全修复回归测试

覆盖四类修复：
1. SSRF：1688 URL 白名单校验（拒绝伪装域名 / IP 直连 / 私网环回）
2. API Key：Fernet 加密 / 解密 / 回显掩码
3. JWT：生产环境空密钥拒绝启动
4. 积分不足：InsufficientCreditsError 类型 + 全局 402 处理器已注册
"""

import pytest

from app.core import crypto
from app.core.crypto import decrypt_value, encrypt_value, mask_secret
from app.services.scraper import _validate_1688_url


# ── SSRF：URL 校验 ─────────────────────────────────────────────

def test_validate_1688_url_accepts_real_links():
    _validate_1688_url("https://detail.1688.com/offer/123456789.html")
    _validate_1688_url("https://detail.1688.com/offer/123456789.html?spm=a123.456")
    _validate_1688_url("https://m.1688.com/offer/123456789.html")
    _validate_1688_url("http://1688.com/offer/123456789.html")


def test_validate_1688_url_rejects_ssrf_vectors():
    bad = [
        "https://127.0.0.1/offer/123.html",              # 环回 IP
        "https://169.254.169.254/offer/123.html",        # 云元数据
        "https://192.168.1.1/offer/123.html",            # 私网 IP
        "https://evil.com/1688.com/offer/123.html",      # 伪装路径
        "https://1688.com.evil.com/offer/123.html",      # 伪装子域
        "https://detail.1688.com@127.0.0.1/offer/1.html",  # userinfo 绕过
        "ftp://detail.1688.com/offer/1.html",            # 非 http(s)
        "file:///etc/passwd",                            # 本地文件
        "",                                              # 空
    ]
    for url in bad:
        with pytest.raises(ValueError):
            _validate_1688_url(url)


@pytest.mark.asyncio
async def test_scrape_1688_rejects_non_1688_url():
    # 校验发生在任何网络请求之前，坏 URL 直接抛 ValueError
    from app.services.scraper import scrape_1688
    with pytest.raises(ValueError):
        await scrape_1688("https://taobao.com/item/123.html")


# ── API Key 加密 / 掩码 ───────────────────────────────────────

@pytest.fixture
def secret_key(monkeypatch):
    """测试期间注入 JWT_SECRET_KEY，让加密真正生效。"""
    monkeypatch.setattr(crypto.settings, "JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setattr(crypto.settings, "SECRET_KEY", "test-secret-key")
    return "test-jwt-secret"


def test_encrypt_decrypt_roundtrip(secret_key):
    plain = "sk-abc1234567890xyz"
    enc = encrypt_value(plain)
    assert enc.startswith("enc:")
    assert enc != plain
    assert decrypt_value(enc) == plain


def test_decrypt_backward_compat_plaintext():
    # 存量明文（无 enc: 前缀）原样返回
    assert decrypt_value("sk-plain-old-value") == "sk-plain-old-value"
    assert decrypt_value("") == ""
    assert decrypt_value(None) == ""


def test_mask_secret():
    assert mask_secret("sk-abcdefghijkl1234") == "sk-a****1234"
    assert mask_secret("short") == "****"
    assert mask_secret("") == ""
    assert mask_secret(None) == ""


# ── JWT 空密钥拒启 ────────────────────────────────────────────

def test_config_requires_jwt_secret_in_production():
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(USE_SQLITE=False, JWT_SECRET_KEY="")
    # 开发模式（SQLite）允许空密钥
    Settings(USE_SQLITE=True, JWT_SECRET_KEY="")


# ── 积分不足异常 ───────────────────────────────────────────────

def test_insufficient_credits_error_is_valueerror_subclass():
    """ValueError 子类 → users.py 的 except ValueError（400）仍然兼容。"""
    from app.models.user import InsufficientCreditsError

    assert issubclass(InsufficientCreditsError, ValueError)


def test_insufficient_credits_handler_registered():
    """全局 402 处理器已注册，并发扣分不再 500。"""
    from app.main import app
    from app.models.user import InsufficientCreditsError

    assert InsufficientCreditsError in app.exception_handlers
