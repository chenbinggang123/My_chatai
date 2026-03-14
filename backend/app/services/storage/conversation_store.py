import sqlite3
from pathlib import Path

from app.services.storage.store import DATA_DIR

DB_PATH = Path(DATA_DIR) / "conversation.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_conversation_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                brain_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_messages_brain_id ON conversation_messages(brain_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at ON conversation_messages(created_at DESC, message_id DESC)"
        )


def save_conversation_message(*, brain_id: str, role: str, content: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO conversation_messages (brain_id, role, content)
            VALUES (?, ?, ?)
            """,
            (brain_id, role, content),
        )


def get_recent_conversation_messages(brain_id: str, limit: int = 20) -> list[dict[str, str]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM conversation_messages
            WHERE brain_id = ?
            ORDER BY message_id DESC
            LIMIT ?
            """,
            (brain_id, max(1, min(limit, 100))),
        ).fetchall()

    ordered_rows = reversed(rows)
    return [
        {"role": row["role"], "content": row["content"]}
        for row in ordered_rows
    ]


def delete_conversation_messages(brain_id: str) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM conversation_messages WHERE brain_id = ?",
            (brain_id,),
        )
    return int(cur.rowcount)