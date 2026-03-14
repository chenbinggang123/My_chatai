import json
import sqlite3
from pathlib import Path
from uuid import uuid4

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

DB_PATH = DATA_DIR / "brain_states.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_brain_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS brain_states (
                brain_id   TEXT PRIMARY KEY,
                brain_state TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_brain_state(brain_state: dict) -> str:
    brain_id = str(uuid4())
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO brain_states (brain_id, brain_state) VALUES (?, ?)",
            (brain_id, json.dumps(brain_state, ensure_ascii=False)),
        )
    return brain_id


def load_brain_state(brain_id: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT brain_id, brain_state FROM brain_states WHERE brain_id = ?",
            (brain_id,),
        ).fetchone()
    if row is None:
        return None
    return {"brain_id": row["brain_id"], "brain_state": json.loads(row["brain_state"])}


def update_brain_state(brain_id: str, brain_state: dict) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE brain_states
            SET brain_state = ?, updated_at = CURRENT_TIMESTAMP
            WHERE brain_id = ?
            """,
            (json.dumps(brain_state, ensure_ascii=False), brain_id),
        )
