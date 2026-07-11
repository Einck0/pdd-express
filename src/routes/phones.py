"""
手机号管理路由
提供手机号的查询、添加、删除接口。
"""

import logging
from flask import Blueprint, request, current_app

from middleware.auth import require_token
from utils.response import success_response, error_response
from utils.validators import validate_phone, format_phone

logger = logging.getLogger("routes.phones")
phones_bp = Blueprint("phones", __name__)


@phones_bp.route("/phones", methods=["GET"])
@require_token
def get_phones():
    """获取当前用户的手机号列表"""
    wxid = request.wxid
    user_service = current_app.user_phone_service

    user = user_service.get_user(wxid)
    if not user:
        user_service.create_user_if_missing(wxid)
        return success_response(data={"phones": []}, message="用户已创建")

    phones = user_service.get_phones(wxid)
    return success_response(data={"phones": phones})


@phones_bp.route("/phones", methods=["POST"])
@require_token
def add_phone():
    """添加手机号"""
    wxid = request.wxid
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    phone = str(data.get("phone", "")).strip()

    if not phone:
        return error_response(400, "缺少手机号")
    if not validate_phone(phone):
        return error_response(400, "手机号格式不正确")

    user_service = current_app.user_phone_service
    result, status = user_service.add_phone(wxid, phone)

    if status >= 400:
        error_code_map = {404: 404, 409: 409, 429: 429}
        return error_response(error_code_map.get(status, 500), result.get("error", "操作失败"))

    return success_response(data={"phone": phone}, message="手机号添加成功")


@phones_bp.route("/phones", methods=["DELETE"])
@require_token
def delete_phone():
    """删除手机号"""
    wxid = request.wxid
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    phone = str(data.get("phone", "")).strip()

    if not phone:
        return error_response(400, "缺少手机号")

    user_service = current_app.user_phone_service
    result, status = user_service.delete_phone(wxid, phone)

    if status >= 400:
        error_code_map = {404: 404, 409: 409}
        return error_response(error_code_map.get(status, 500), result.get("error", "操作失败"))

    return success_response(data={"phone": phone}, message="手机号删除成功")
