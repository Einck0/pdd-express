"""
数据库通用服务
提供便捷的查询/执行方法封装。
"""

from models.database import db
from logging_config import configure_logging

logger = configure_logging("db_service")


class DBService:
    """数据库通用操作服务"""

    def fetch_one(self, sql, params=None):
        """查询单条记录"""
        with db.session() as conn:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchone()

    def fetch_all(self, sql, params=None):
        """查询多条记录"""
        with db.session() as conn:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchall()

    def execute(self, sql, params=None):
        """执行 SQL 语句"""
        with db.session() as conn:
            conn.execute(sql, params or ())
        return True
