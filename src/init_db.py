from settings import get_settings
from database import db

settings = get_settings()


def init_db():
    with db.session() as conn:
        if settings.db_backend == "mysql":
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    wxid VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_phones (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    wxid VARCHAR(255) NOT NULL,
                    phone VARCHAR(32) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uniq_wxid_phone (wxid, phone),
                    KEY idx_user_phones_wxid (wxid),
                    CONSTRAINT fk_user_phones_wxid FOREIGN KEY (wxid) REFERENCES users(wxid)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        else:
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
                "CREATE INDEX IF NOT EXISTS idx_user_phones_wxid ON user_phones(wxid)"
            )
    print(f"Database schema initialized with backend: {settings.db_backend}")


if __name__ == "__main__":
    init_db()
