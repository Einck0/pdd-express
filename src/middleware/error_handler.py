"""
全局错误处理中间件
捕获未处理的异常，统一返回标准错误响应格式。
"""

import logging
from flask import jsonify


def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"code": 404, "message": "资源不存在"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"code": 405, "message": "请求方法不允许"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"code": 500, "message": "服务器内部错误"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger = logging.getLogger("error_handler")
        logger.exception("未捕获的异常: %s", e)
        return jsonify({"code": 500, "message": "服务器内部错误"}), 500
