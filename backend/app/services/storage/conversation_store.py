import sqlite3
from pathlib import Path

from app.services.storage.db import DATA_DIR, DATABASE_URL

DB_PATH = Path(DATA_DIR) / "conversation.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_conversation_store() -> None:
    if DATABASE_URL:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        message_id BIGSERIAL PRIMARY KEY,
                        brain_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversation_messages_brain_id ON conversation_messages(brain_id)"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at ON conversation_messages(created_at DESC, message_id DESC)"
                )
            conn.commit()
        return

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
    if DATABASE_URL:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversation_messages (brain_id, role, content)
                    VALUES (%s, %s, %s)
                    """,
                    (brain_id, role, content),
                )
            conn.commit()
        return

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO conversation_messages (brain_id, role, content)
            VALUES (?, ?, ?)
            """,
            (brain_id, role, content),
        )


def get_recent_conversation_messages(brain_id: str, limit: int = 20) -> list[dict[str, str]]:
    if DATABASE_URL:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT role, content
                    FROM conversation_messages
                    WHERE brain_id = %s
                    ORDER BY message_id DESC
                    LIMIT %s
                    """,
                    (brain_id, max(1, min(limit, 100))),
                )
                rows = cur.fetchall()

        ordered_rows = reversed(rows)
        return [
            {"role": row["role"], "content": row["content"]}
            for row in ordered_rows
        ]

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
    if DATABASE_URL:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM conversation_messages WHERE brain_id = %s",
                    (brain_id,),
                )
                deleted = int(cur.rowcount)
            conn.commit()
        return deleted

    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM conversation_messages WHERE brain_id = ?",
            (brain_id,),
        )
    return int(cur.rowcount)