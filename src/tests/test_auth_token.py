import pytest
import time
from utils.token import generate_token, verify_token


def test_generate_and_verify_token():
    openid = "test_openid_12345"
    token = generate_token(openid)
    assert token is not None
    assert "." in token

    extracted = verify_token(token)
    assert extracted == openid


def test_verify_tampered_token():
    openid = "test_openid_12345"
    token = generate_token(openid)
    # 篡改签名部分
    tampered = token[:-4] + "abcd"
    assert verify_token(tampered) is None


def test_verify_legacy_openid_fallback():
    openid = "oABC123456789"
    # 旧版本客户端可能直传 openid
    assert verify_token(openid) == openid


def test_verify_invalid_token():
    assert verify_token("") is None
    assert verify_token("short") is None
    assert verify_token("invalid.token.structure") is None
