import json
from uuid import uuid4

from app.services.storage.db import DATA_DIR, DATABASE_URL, is_postgres_enabled, sqlite_connect

DB_PATH = DATA_DIR / "brain_states.db"


def _get_conn():
    return sqlite_connect(DB_PATH)


def init_brain_store() -> None:
    if is_postgres_enabled():
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS brain_states (
                        brain_id TEXT PRIMARY KEY,
                        brain_state TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()
        return

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

    if is_postgres_enabled():
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO brain_states (brain_id, brain_state) VALUES (%s, %s)",
                    (brain_id, json.dumps(brain_state, ensure_ascii=False)),
                )
            conn.commit()
        return brain_id

    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO brain_states (brain_id, brain_state) VALUES (?, ?)",
            (brain_id, json.dumps(brain_state, ensure_ascii=False)),
        )
    return brain_id


def load_brain_state(brain_id: str) -> dict | None:
    if is_postgres_enabled():
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT brain_id, brain_state FROM brain_states WHERE brain_id = %s",
                    (brain_id,),
                )
                row = cur.fetchone()
        if row is None:
            return None
        return {"brain_id": row["brain_id"], "brain_state": json.loads(row["brain_state"])}

    with _get_conn() as conn:
        row = conn.execute(
            "SELECT brain_id, brain_state FROM brain_states WHERE brain_id = ?",
            (brain_id,),
        ).fetchone()
    if row is None:
        return None
    return {"brain_id": row["brain_id"], "brain_state": json.loads(row["brain_state"])}


def update_brain_state(brain_id: str, brain_state: dict) -> None:
    if is_postgres_enabled():
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE brain_states
                    SET brain_state = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE brain_id = %s
                    """,
                    (json.dumps(brain_state, ensure_ascii=False), brain_id),
                )
            conn.commit()
        return

    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE brain_states
            SET brain_state = ?, updated_at = CURRENT_TIMESTAMP
            WHERE brain_id = ?
            """,
            (json.dumps(brain_state, ensure_ascii=False), brain_id),
        )


def delete_brain_state(brain_id: str) -> int:
    if is_postgres_enabled():
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("DATABASE_URL is set but psycopg is not installed") from exc

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM brain_states WHERE brain_id = %s", (brain_id,))
                deleted = int(cur.rowcount)
            conn.commit()
        return deleted

    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM brain_states WHERE brain_id = ?", (brain_id,))
    return int(cur.rowcount)
