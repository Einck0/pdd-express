"""
请求参数校验模块
提供各接口常用的参数校验函数。
"""

import re


def validate_phone(phone: str) -> bool:
    """校验手机号格式（1开头的11位数字）"""
    if not phone or not re.match(r'^1\d{10}$', phone):
        return False
    return True


def validate_keyword(keyword: str) -> bool:
    """校验搜索关键词（至少4个字符）"""
    if not keyword or len(keyword) < 4:
        return False
    return True


def format_phone(phone: str) -> str:
    """格式化手机号为 138****8888 格式"""
    if not phone or len(phone) != 11:
        return phone
    return phone[:3] + "****" + phone[7:]
