import sqlite3

from database import db


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
