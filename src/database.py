from contextlib import contextmanager
from typing import Iterator

import pymysql
import sqlite3

from logging_config import configure_logging
from settings import get_settings

logger = configure_logging("database")


class Database:
    def __init__(self):
        self.settings = get_settings()
        if self.settings.db_backend == "sqlite":
            self.settings.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        if self.settings.db_backend == "mysql":
            conn = pymysql.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                database=self.settings.mysql_database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
            return conn

        conn = sqlite3.connect(self.settings.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def session(self) -> Iterator:
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except (sqlite3.Error, pymysql.MySQLError) as exc:
            conn.rollback()
            logger.error("Database error: %s", exc)
            raise
        finally:
            conn.close()

db = Database()
