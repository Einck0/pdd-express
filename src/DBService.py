import sqlite3

from database import db
from logging_config import configure_logging

logger = configure_logging("db_service")


class DBService:
    def fetch_one(self, sql, params=None):
        with db.session() as conn:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchone()

    def fetch_all(self, sql, params=None):
        with db.session() as conn:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchall()

    def execute(self, sql, params=None):
        with db.session() as conn:
            conn.execute(sql, params or ())
        return True

    def get_sub_pass_id(self):
        row = self.fetch_one(
            "SELECT value FROM cookies WHERE name = 'SUB_PASS_ID' LIMIT 1"
        )
        if row:
            return row["value"]
        logger.error("Failed to fetch SUB_PASS_ID from database.")
        raise Exception("Failed to fetch SUB_PASS_ID from database.")
