from database import db
from utils_common import parse_phone_list


def migrate_phones_and_users():
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
        rows = conn.execute("SELECT wxid, phones FROM user_phone_map").fetchall()
        migrated_users = 0
        migrated_phones = 0
        for row in rows:
            wxid = row["wxid"]
            phones = parse_phone_list(row["phones"])
            conn.execute("INSERT OR IGNORE INTO users (wxid) VALUES (?)", (wxid,))
            migrated_users += 1
            for phone in phones:
                conn.execute(
                    "INSERT OR IGNORE INTO user_phones (wxid, phone) VALUES (?, ?)",
                    (wxid, phone),
                )
                migrated_phones += 1
    print(f"Migrated users: {migrated_users}, phones: {migrated_phones}")


if __name__ == "__main__":
    migrate_phones_and_users()
