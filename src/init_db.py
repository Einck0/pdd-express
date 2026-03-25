from database import db


def init_db():
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
            "CREATE INDEX IF NOT EXISTS idx_user_phones_wxid ON user_phones(wxid)"
        )
    print("Database schema initialized.")


if __name__ == "__main__":
    init_db()
