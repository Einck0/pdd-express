"""
Flask 应用工厂
创建并配置 Flask 应用实例，注册蓝图和中间件。
"""

from flask import Flask, jsonify

from config import get_settings
from middleware.error_handler import register_error_handlers
from services.package_service import PackageService
from services.user_service import UserPhoneService
from routes import register_blueprints
from logging_config import configure_logging

logger = configure_logging("app")


def create_app(package_service=None):
    """创建 Flask 应用实例

    Args:
        package_service: 可选的 PackageService 实例（用于测试注入）

    Returns:
        Flask: 配置完成的 Flask 应用
    """
    settings = get_settings()
    app = Flask(__name__)

    # 初始化服务（存储在 app 上，路由中通过 current_app 访问）
    app.package_service = package_service or PackageService()
    app.user_phone_service = UserPhoneService()

    # 注册全局错误处理
    register_error_handlers(app)

    # 注册路由蓝图
    register_blueprints(app, settings.api_prefix)

    # 健康检查（不属于任何蓝图）
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "code": 0,
            "message": "ok",
            "data": {
                "service": "pdd-express",
                "api_prefix": settings.api_prefix,
                "port": settings.port,
            },
        })

    logger.info(
        "应用初始化完成 | backend=%s | prefix=%s | port=%s",
        settings.db_backend, settings.api_prefix, settings.port,
    )

    return app
