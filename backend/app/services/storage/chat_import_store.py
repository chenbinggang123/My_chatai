import sqlite3
from pathlib import Path
from uuid import uuid4

from app.services.storage.store import DATA_DIR

DB_PATH = Path(DATA_DIR) / "chat_imports.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_chat_import_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_imports (
                import_id TEXT PRIMARY KEY,
                brain_id TEXT,
                mode TEXT NOT NULL,
                chat_log TEXT NOT NULL,
                relationship_context TEXT,
                user_preference TEXT,
                goal TEXT,
                chat_length INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_imports_brain_id ON chat_imports(brain_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_imports_created_at ON chat_imports(created_at DESC)"
        )


def save_chat_import(
    *,
    mode: str,
    chat_log: str,
    brain_id: str | None = None,
    relationship_context: str | None = None,
    user_preference: str | None = None,
    goal: str | None = None,
) -> str:
    import_id = str(uuid4())
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chat_imports (
                import_id, brain_id, mode, chat_log, relationship_context,
                user_preference, goal, chat_length
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                import_id,
                brain_id,
                mode,
                chat_log,
                relationship_context,
                user_preference,
                goal,
                len(chat_log),
            ),
        )
    return import_id


def get_recent_chat_logs(brain_id: str, limit: int = 3) -> list[str]:
    """返回该 brain_id 最近几条原始聊天记录，用于喂给 AI 作为上下文。"""
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT chat_log FROM chat_imports
            WHERE brain_id = ?
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (brain_id, max(1, min(limit, 10))),
        ).fetchall()
    return [row["chat_log"] for row in rows]


def query_chat_imports(
    *,
    brain_id: str | None = None,
    mode: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    where_parts: list[str] = []
    params: list[object] = []

    if brain_id:
        where_parts.append("brain_id = ?")
        params.append(brain_id)
    if mode:
        where_parts.append("mode = ?")
        params.append(mode)
    if keyword:
        where_parts.append("chat_log LIKE ?")
        params.append(f"%{keyword}%")

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    with _get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM chat_imports {where_sql}",
            params,
        ).fetchone()["c"]

        rows = conn.execute(
            f"""
            SELECT
                import_id,
                brain_id,
                mode,
                chat_length,
                created_at,
                substr(chat_log, 1, 120) AS excerpt
            FROM chat_imports
            {where_sql}
            ORDER BY datetime(created_at) DESC
            LIMIT ? OFFSET ?
            """,
            [*params, max(1, min(limit, 200)), max(0, offset)],
        ).fetchall()

    items = [dict(row) for row in rows]
    return items, int(total)
