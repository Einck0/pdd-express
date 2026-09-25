from functools import wraps
from flask import request
from utils.response import error_response
from utils.token import verify_token


def require_token(f):
    """认证装饰器，要求请求携带有效的 Bearer token。

    认证成功后将解析出的真实 openid 存入 request.wxid。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return error_response(401, "未认证")
        raw_token = auth[7:].strip()
        if not raw_token:
            return error_response(401, "无效token")

        wxid = verify_token(raw_token)
        if not wxid:
            return error_response(401, "Token 无效或已过期")

        request.wxid = wxid
        return f(*args, **kwargs)
    return decorated
