import argparse
import os
import sqlite3
from pathlib import Path

import psycopg


def normalize_database_url(url: str) -> str:
    value = (url or "").strip()
    if value.startswith("postgres://"):
        return "postgresql://" + value[len("postgres://") :]
    return value


def read_sqlite_rows(db_path: Path, query: str) -> list[sqlite3.Row]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(query).fetchall()
    finally:
        conn.close()


def ensure_postgres_tables(conn: psycopg.Connection) -> None:
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
        cur.execute(
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
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_imports_brain_id ON chat_imports(brain_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_imports_created_at ON chat_imports(created_at DESC)")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_messages_brain_id ON conversation_messages(brain_id)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at ON conversation_messages(created_at DESC, message_id DESC)"
        )


def migrate_brain_states(conn: psycopg.Connection, data_dir: Path) -> int:
    rows = read_sqlite_rows(
        data_dir / "brain_states.db",
        "SELECT brain_id, brain_state, created_at, updated_at FROM brain_states",
    )
    if not rows:
        return 0

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO brain_states (brain_id, brain_state, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (brain_id) DO UPDATE SET
                brain_state = EXCLUDED.brain_state,
                updated_at = EXCLUDED.updated_at
            """,
            [
                (
                    row["brain_id"],
                    row["brain_state"],
                    row["created_at"],
                    row["updated_at"],
                )
                for row in rows
            ],
        )
    return len(rows)


def migrate_chat_imports(conn: psycopg.Connection, data_dir: Path) -> int:
    rows = read_sqlite_rows(
        data_dir / "chat_imports.db",
        """
        SELECT import_id, brain_id, mode, chat_log, relationship_context,
               user_preference, goal, chat_length, created_at
        FROM chat_imports
        """,
    )
    if not rows:
        return 0

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO chat_imports (
                import_id, brain_id, mode, chat_log, relationship_context,
                user_preference, goal, chat_length, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (import_id) DO UPDATE SET
                brain_id = EXCLUDED.brain_id,
                mode = EXCLUDED.mode,
                chat_log = EXCLUDED.chat_log,
                relationship_context = EXCLUDED.relationship_context,
                user_preference = EXCLUDED.user_preference,
                goal = EXCLUDED.goal,
                chat_length = EXCLUDED.chat_length,
                created_at = EXCLUDED.created_at
            """,
            [
                (
                    row["import_id"],
                    row["brain_id"],
                    row["mode"],
                    row["chat_log"],
                    row["relationship_context"],
                    row["user_preference"],
                    row["goal"],
                    row["chat_length"],
                    row["created_at"],
                )
                for row in rows
            ],
        )
    return len(rows)


def migrate_conversation_messages(conn: psycopg.Connection, data_dir: Path) -> int:
    rows = read_sqlite_rows(
        data_dir / "conversation.db",
        "SELECT message_id, brain_id, role, content, created_at FROM conversation_messages",
    )
    if not rows:
        return 0

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO conversation_messages (message_id, brain_id, role, content, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING
            """,
            [
                (
                    row["message_id"],
                    row["brain_id"],
                    row["role"],
                    row["content"],
                    row["created_at"],
                )
                for row in rows
            ],
        )
        cur.execute(
            """
            SELECT setval(
                pg_get_serial_sequence('conversation_messages', 'message_id'),
                COALESCE((SELECT MAX(message_id) FROM conversation_messages), 1),
                true
            )
            """
        )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate local SQLite data to PostgreSQL")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="PostgreSQL connection string, default reads DATABASE_URL env",
    )
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).resolve().parents[1] / "data"),
        help="Directory that contains brain_states.db/chat_imports.db/conversation.db",
    )
    args = parser.parse_args()

    database_url = normalize_database_url(args.database_url)
    if not database_url:
        print("ERROR: missing DATABASE_URL. Pass --database-url or set env DATABASE_URL.")
        return 1

    data_dir = Path(args.data_dir)

    with psycopg.connect(database_url) as conn:
        ensure_postgres_tables(conn)
        brain_count = migrate_brain_states(conn, data_dir)
        import_count = migrate_chat_imports(conn, data_dir)
        msg_count = migrate_conversation_messages(conn, data_dir)
        conn.commit()

    print("Migration done.")
    print(f"brain_states: {brain_count}")
    print(f"chat_imports: {import_count}")
    print(f"conversation_messages: {msg_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
