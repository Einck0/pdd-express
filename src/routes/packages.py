"""
包裹查询路由
提供包裹查询和搜索接口。
"""

import logging
from flask import Blueprint, request, current_app

from middleware.auth import require_token
from utils.response import success_response, error_response
from utils.validators import validate_keyword

logger = logging.getLogger("routes.packages")
packages_bp = Blueprint("packages", __name__)


@packages_bp.route("/package", methods=["GET"])
@require_token
def get_packages_by_user():
    """根据用户绑定的手机号查询所有包裹"""
    wxid = request.wxid
    user_service = current_app.user_phone_service
    package_service = current_app.package_service

    user = user_service.get_user(wxid)
    if not user:
        return error_response(404, "用户不存在")

    phones = user_service.get_phones(wxid)
    packages = []
    try:
        for phone in phones:
            packages.extend(package_service.get_packages(phone))
        return success_response(
            data={"phones": phones, "packages": packages}
        )
    except Exception as e:
        logger.exception("查询包裹失败 wxid=%s: %s", wxid, e)
        return error_response(500, "查询包裹失败")


@packages_bp.route("/package", methods=["POST"])
@require_token
def search_packages():
    """按关键词搜索包裹"""
    wxid = request.wxid
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    keyword = str(data.get("keyword", "")).strip()

    if not validate_keyword(keyword):
        return error_response(400, "关键词长度不能少于4个字符")

    package_service = current_app.package_service
    try:
        packages = package_service.get_packages(keyword)
        return success_response(data={"packages": packages})
    except Exception as e:
        logger.exception("搜索包裹失败 wxid=%s: %s", wxid, e)
        return error_response(500, "搜索包裹失败")
