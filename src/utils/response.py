"""
统一响应格式模块
所有接口返回统一的 JSON 结构：{"code": 0, "message": "ok", "data": {...}}
"""

from flask import jsonify


def success_response(data=None, message="ok"):
    """成功响应"""
    payload = {"code": 0, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), 200


def error_response(code, message, status=None):
    """错误响应

    Args:
        code: 业务错误码（400/401/404/409/429/500）
        message: 错误描述
        status: HTTP 状态码，默认根据 code 自动映射
    """
    if status is None:
        status_map = {
            400: 400,
            401: 401,
            404: 404,
            409: 409,
            429: 429,
            500: 500,
        }
        status = status_map.get(code, 500)
    payload = {"code": code, "message": message}
    return jsonify(payload), status
