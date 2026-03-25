from database import db
from logging_config import configure_logging

logger = configure_logging("repository")


class UserPhoneRepository:
    def get_user(self, wxid: str):
        with db.session() as conn:
            return conn.execute(
                "SELECT wxid FROM users WHERE wxid = ?",
                (wxid,),
            ).fetchone()

    def create_user_if_missing(self, wxid: str):
        with db.session() as conn:
            row = conn.execute(
                "SELECT wxid FROM users WHERE wxid = ?",
                (wxid,),
            ).fetchone()
            if row:
                return False
            conn.execute("INSERT INTO users (wxid) VALUES (?)", (wxid,))
            return True

    def get_phone_rows(self, wxid: str):
        with db.session() as conn:
            return conn.execute(
                "SELECT phone FROM user_phones WHERE wxid = ? ORDER BY id ASC",
                (wxid,),
            ).fetchall()

    def replace_phones(self, wxid: str, phones: list[str]):
        with db.session() as conn:
            conn.execute("DELETE FROM user_phones WHERE wxid = ?", (wxid,))
            for phone in phones:
                conn.execute(
                    "INSERT INTO user_phones (wxid, phone) VALUES (?, ?)",
                    (wxid, phone),
                )

    def ensure_schema(self):
        with db.session() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    wxid TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_phones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wxid TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(wxid, phone),
                    FOREIGN KEY (wxid) REFERENCES users(wxid)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cookies (
                    name TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_phones_wxid ON user_phones(wxid)"
            )
