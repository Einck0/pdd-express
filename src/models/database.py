"""
数据库连接管理模块
支持 SQLite、MySQL、PostgreSQL 三种后端，通过配置自动选择。
"""

from contextlib import contextmanager
from typing import Iterator

from logging_config import configure_logging
from config import get_settings

logger = configure_logging("database")

# 延迟导入可选数据库驱动，避免未安装时报错
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

import sqlite3


class Database:
    """数据库连接管理器"""

    def __init__(self):
        self.settings = get_settings()
        if self.settings.db_backend == "sqlite":
            self.settings.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """创建数据库连接"""
        if self.settings.db_backend == "postgresql":
            if psycopg2 is None:
                raise RuntimeError("PostgreSQL 驱动未安装，请安装 psycopg2")
            return psycopg2.connect(
                host=self.settings.postgres_host,
                port=self.settings.postgres_port,
                user=self.settings.postgres_user,
                password=self.settings.postgres_password,
                dbname=self.settings.postgres_database,
            )

        if self.settings.db_backend == "mysql":
            if pymysql is None:
                raise RuntimeError("MySQL 驱动未安装，请安装 pymysql")
            return pymysql.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                database=self.settings.mysql_database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )

        # 默认 SQLite
        conn = sqlite3.connect(self.settings.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def session(self) -> Iterator:
        """获取数据库会话（上下文管理器，自动提交/回滚）"""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error("数据库错误: %s", exc)
            raise
        finally:
            conn.close()


db = Database()
