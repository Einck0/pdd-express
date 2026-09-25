"""
Cookie 管理路由
提供 cookie 的设置和查询接口，用于维护拼多多 API 认证状态。
"""

from flask import Blueprint, request

from middleware.auth import require_token
from utils.response import success_response, error_response
from services import cookie_service

cookies_bp = Blueprint("cookies", __name__)


@cookies_bp.route("/cookies", methods=["PUT"])
@require_token
def set_cookies():
    """设置 cookie（完整字符串或单个键值对），需要管理凭据校验。"""
    from config import get_settings
    settings = get_settings()
    admin_key = getattr(settings, "admin_key", None) or settings.secret
    req_key = request.headers.get("X-Admin-Key")
    if admin_key and req_key != admin_key:
        return error_response(403, "需要有效的管理密钥 (X-Admin-Key)")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}

    cookie_string = data.get("cookie_string")
    cookies = data.get("cookies")

    if not cookie_string and not cookies:
        return error_response(400, "需要提供 cookie_string 或 cookies")

    result, status = cookie_service.set_cookies(
        cookie_string=cookie_string,
        cookies=cookies,
    )

    if status >= 400:
        return error_response(500, result.get("error", "cookie 更新失败"))

    return success_response(data=result, message="cookie 已更新并持久化")


@cookies_bp.route("/cookies", methods=["GET"])
@require_token
def get_cookies():
    """获取当前 cookie 的 key 列表（不返回值，用于调试）"""
    result, status = cookie_service.get_cookies()
    return success_response(data=result)
