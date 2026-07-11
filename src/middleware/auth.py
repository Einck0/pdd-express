"""
认证中间件
提供 Token 认证装饰器，从 Authorization 请求头解析 wxid。
"""

from functools import wraps
from flask import request
from utils.response import error_response


def require_token(f):
    """认证装饰器，要求请求携带有效的 Bearer token（即 wxid）

    认证成功后将 wxid 存入 request.wxid。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return error_response(401, "未认证")
        wxid = auth[7:].strip()
        if not wxid:
            return error_response(401, "无效token")
        request.wxid = wxid
        return f(*args, **kwargs)
    return decorated
