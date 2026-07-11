"""
用户手机号服务
管理用户的手机号绑定关系，包含用户创建、手机号 CRUD 操作。
"""

from typing import Optional

from models.database import db
from config import get_settings
from logging_config import configure_logging

logger = configure_logging("user_service")
settings = get_settings()

# 根据数据库类型选择占位符
_PH = "%s" if settings.db_backend in ("mysql", "postgresql") else "?"


class UserPhoneService:
    """用户手机号管理服务"""

    def __init__(self):
        """初始化并确保数据库表结构存在"""
        self._ensure_schema()

    def _ensure_schema(self):
        """确保 users 和 user_phones 表存在"""
        from init_db import init_db
        init_db()

    def get_user(self, wxid: str):
        """查询用户是否存在"""
        with db.session() as conn:
            sql = f"SELECT wxid FROM users WHERE wxid = {_PH}"
            return conn.execute(sql, (wxid,)).fetchone()

    def create_user_if_missing(self, wxid: str):
        """用户不存在时创建"""
        with db.session() as conn:
            select_sql = f"SELECT wxid FROM users WHERE wxid = {_PH}"
            insert_sql = f"INSERT INTO users (wxid) VALUES ({_PH})"
            row = conn.execute(select_sql, (wxid,)).fetchone()
            if row:
                return False
            conn.execute(insert_sql, (wxid,))
            return True

    def get_phones(self, wxid: str) -> list:
        """获取用户的所有手机号"""
        with db.session() as conn:
            sql = f"SELECT phone FROM user_phones WHERE wxid = {_PH} ORDER BY id ASC"
            return [row["phone"] for row in conn.execute(sql, (wxid,)).fetchall()]

    def save_phones(self, wxid: str, phones: list):
        """替换用户的所有手机号"""
        with db.session() as conn:
            delete_sql = f"DELETE FROM user_phones WHERE wxid = {_PH}"
            insert_sql = f"INSERT INTO user_phones (wxid, phone) VALUES ({_PH}, {_PH})"
            conn.execute(delete_sql, (wxid,))
            for phone in phones:
                conn.execute(insert_sql, (wxid, phone))

    def add_phone(self, wxid: str, phone: str):
        """添加手机号

        Returns:
            tuple: (data_dict, status_code)
        """
        user = self.get_user(wxid)
        if not user:
            return {"error": "wxid not found"}, 404

        phones = self.get_phones(wxid)
        if len(phones) >= 5:
            return {"error": "手机号数量已达上限"}, 429
        if phone in phones:
            return {"error": "手机号已存在"}, 409

        phones.append(phone)
        self.save_phones(wxid, phones)
        return {"phone": phone}, 200

    def delete_phone(self, wxid: str, phone: str):
        """删除手机号

        Returns:
            tuple: (data_dict, status_code)
        """
        user = self.get_user(wxid)
        if not user:
            return {"error": "wxid not found"}, 404

        phones = self.get_phones(wxid)
        if phone not in phones:
            return {"error": "手机号不存在"}, 404

        phones.remove(phone)
        self.save_phones(wxid, phones)
        return {"phone": phone}, 200
