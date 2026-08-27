import base64
import hashlib
import hmac
import json
import time

from config import get_settings

TOKEN_EXPIRY_SECONDS = 30 * 24 * 3600  # 30天有效


def generate_token(openid: str) -> str:
    """基于 HMAC-SHA256 签发带时效的 Token。"""
    settings = get_settings()
    secret = settings.secret.encode("utf-8") if settings.secret else b"default-pdd-secret-key"
    payload = {
        "sub": openid,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    sig = hmac.new(secret, payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def verify_token(token_str: str) -> str | None:
    """校验 Token 签名和过期时间，通过返回 openid (sub)，失败返回 None。

    同时兼容过渡期原始 openid 格式（若长度>10且无点号）。
    """
    if not token_str:
        return None

    settings = get_settings()
    secret = settings.secret.encode("utf-8") if settings.secret else b"default-pdd-secret-key"

    parts = token_str.split(".")
    if len(parts) == 2:
        payload_b64, sig_b64 = parts
        try:
            # 补齐 base64 padding
            pad_len = 4 - (len(sig_b64) % 4)
            sig_raw = base64.urlsafe_b64decode(sig_b64 + ("=" * (pad_len % 4)))

            expected_sig = hmac.new(secret, payload_b64.encode("utf-8"), hashlib.sha256).digest()
            if not hmac.compare_digest(sig_raw, expected_sig):
                return None

            pad_len_p = 4 - (len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64 + ("=" * (pad_len_p % 4))).decode("utf-8")
            payload = json.loads(payload_json)

            if int(payload.get("exp", 0)) < int(time.time()):
                return None  # 已过期

            return payload.get("sub")
        except Exception:
            return None

    # 向后兼容：旧客户端缓存的原生 openid 字符串
    if "." not in token_str and len(token_str) >= 10:
        return token_str

    return None
