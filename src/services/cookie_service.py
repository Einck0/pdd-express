"""
Cookie 管理服务
封装 cookie 的设置、获取和持久化逻辑。
"""

from flask import current_app
from logging_config import configure_logging

logger = configure_logging("cookie_service")


def get_package_service():
    """获取 PackageService 实例（通过 Flask app）"""
    return current_app.package_service


def set_cookies(cookie_string=None, cookies=None):
    """设置 cookie

    Args:
        cookie_string: 完整的 cookie 字符串
        cookies: 单个 cookie 键值对字典

    Returns:
        tuple: (data_dict, status_code)
    """
    ps = get_package_service()

    if cookie_string:
        ps.set_cookies(cookie_string)
    elif cookies and isinstance(cookies, dict):
        ps.merge_cookies(cookies)

    # 持久化到 .env
    if not ps.persist_cookies_to_env():
        return {"error": "cookie 已更新但持久化失败"}, 500

    return {"keys": ps.get_cookie_keys()}, 200


def get_cookies():
    """获取当前 cookie 的 key 列表

    Returns:
        tuple: (data_dict, status_code)
    """
    ps = get_package_service()
    return {"keys": ps.get_cookie_keys()}, 200
