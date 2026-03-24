import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    log_dir: Path
    api_prefix: str
    appid: str
    secret: str
    sqlite_db_path: Path
    pdd_mobile: str
    pdd_encrypted_password: str
    pdd_cookie_string: str
    pdd_user_agent: str
    host: str
    port: int
    debug: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    base_dir = BASE_DIR
    log_dir = Path(os.getenv("PDD_LOG_DIR", str(base_dir / "logs")))
    db_dir = Path(os.getenv("PDD_SQLITE_DATABASE_DIR", str(base_dir)))
    if not db_dir.is_absolute():
        db_dir = (base_dir / db_dir).resolve()
    db_name = os.getenv("PDD_SQLITE_DATABASE_NAME", "pdd.db")

    return Settings(
        base_dir=base_dir,
        log_dir=log_dir,
        api_prefix=os.getenv("PDD_API_PREFIX", "/express"),
        appid=os.getenv("PDD_WECHAT_APPID", ""),
        secret=os.getenv("PDD_WECHAT_SECRET", ""),
        sqlite_db_path=db_dir / db_name,
        pdd_mobile=os.getenv("PDD_MOBILE", ""),
        pdd_encrypted_password=os.getenv("PDD_ENCRYPTED_PASSWORD", ""),
        pdd_cookie_string=os.getenv("PDD_COOKIE_STRING", ""),
        pdd_user_agent=os.getenv(
            "PDD_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        ),
        host=os.getenv("PDD_APP_HOST", "0.0.0.0"),
        port=int(os.getenv("PDD_APP_PORT", "15000")),
        debug=os.getenv("PDD_APP_DEBUG", "false").lower() == "true",
    )
