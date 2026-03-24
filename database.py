import sqlite3
from contextlib import contextmanager
from typing import Iterator

from logging_config import configure_logging
from settings import get_settings

logger = configure_logging("database")


class Database:
    def __init__(self):
        self.settings = get_settings()
        self.settings.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.settings.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            logger.error("Database error: %s", exc)
            raise
        finally:
            conn.close()


db = Database()
