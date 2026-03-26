from database import db
from logging_config import configure_logging
from settings import get_settings

logger = configure_logging("repository")
settings = get_settings()


class UserPhoneRepository:
    def get_user(self, wxid: str):
        with db.session() as conn:
            return conn.execute(
                "SELECT wxid FROM users WHERE wxid = %s" if settings.db_backend == "mysql" else "SELECT wxid FROM users WHERE wxid = ?",
                (wxid,),
            ).fetchone()

    def create_user_if_missing(self, wxid: str):
        with db.session() as conn:
            select_sql = "SELECT wxid FROM users WHERE wxid = %s" if settings.db_backend == "mysql" else "SELECT wxid FROM users WHERE wxid = ?"
            insert_sql = "INSERT INTO users (wxid) VALUES (%s)" if settings.db_backend == "mysql" else "INSERT INTO users (wxid) VALUES (?)"
            row = conn.execute(select_sql, (wxid,)).fetchone()
            if row:
                return False
            conn.execute(insert_sql, (wxid,))
            return True

    def get_phone_rows(self, wxid: str):
        with db.session() as conn:
            return conn.execute(
                "SELECT phone FROM user_phones WHERE wxid = %s ORDER BY id ASC" if settings.db_backend == "mysql" else "SELECT phone FROM user_phones WHERE wxid = ? ORDER BY id ASC",
                (wxid,),
            ).fetchall()

    def replace_phones(self, wxid: str, phones: list[str]):
        with db.session() as conn:
            delete_sql = "DELETE FROM user_phones WHERE wxid = %s" if settings.db_backend == "mysql" else "DELETE FROM user_phones WHERE wxid = ?"
            insert_sql = "INSERT INTO user_phones (wxid, phone) VALUES (%s, %s)" if settings.db_backend == "mysql" else "INSERT INTO user_phones (wxid, phone) VALUES (?, ?)"
            conn.execute(delete_sql, (wxid,))
            for phone in phones:
                conn.execute(insert_sql, (wxid, phone))

    def ensure_schema(self):
        from init_db import init_db

        init_db()
