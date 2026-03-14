import os
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def normalize_database_url(url: str) -> str:
    value = (url or "").strip()
    if value.startswith("postgres://"):
        return "postgresql://" + value[len("postgres://") :]
    return value


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", ""))


def is_postgres_enabled() -> bool:
    return bool(DATABASE_URL)


def sqlite_connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
