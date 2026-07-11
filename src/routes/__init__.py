"""
路由注册模块
将所有蓝图统一注册到 Flask app。
"""

from routes.auth import auth_bp
from routes.phones import phones_bp
from routes.packages import packages_bp
from routes.cookies import cookies_bp


def register_blueprints(app, api_prefix):
    """注册所有路由蓝图"""
    app.register_blueprint(auth_bp, url_prefix=api_prefix)
    app.register_blueprint(phones_bp, url_prefix=api_prefix)
    app.register_blueprint(packages_bp, url_prefix=api_prefix)
    app.register_blueprint(cookies_bp, url_prefix=api_prefix)
