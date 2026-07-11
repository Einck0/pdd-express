"""
认证路由
处理微信登录和用户注册。
"""

import requests as http_requests
from flask import Blueprint, request, current_app

from config import get_settings
from utils.response import success_response, error_response

auth_bp = Blueprint("auth", __name__)
settings = get_settings()


@auth_bp.route("/wxlogin", methods=["POST"])
def wx_login():
    """微信登录，获取 openid 并注册/返回 token"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    code = data.get("code")
    if not code:
        return error_response(400, "缺少登录 code")

    response = http_requests.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={
            "appid": settings.appid,
            "secret": settings.secret,
            "js_code": code,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if response.status_code != 200:
        return error_response(500, "微信 API 请求失败")

    res_data = response.json()
    if "openid" not in res_data:
        return error_response(400, "获取 openid 失败", status=400)

    openid = res_data["openid"]
    user_service = current_app.user_phone_service
    existing = user_service.get_user(openid)
    if not existing:
        user_service.create_user_if_missing(openid)

    return success_response(data={"token": openid}, message="登录成功")
