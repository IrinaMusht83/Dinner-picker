import sqlite3
from pathlib import Path

DB_PATH = Path("db/profiles.sqlite")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id         INTEGER PRIMARY KEY,
                store_id        TEXT NOT NULL,
                default_persons INTEGER NOT NULL CHECK (default_persons BETWEEN 1 AND 20),
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def get_profile(user_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT user_id, store_id, default_persons FROM profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def save_profile(user_id: int, store_id: str, default_persons: int) -> None:
    if not 1 <= default_persons <= 20:
        raise ValueError("default_persons must be 1..20")
    with _connect() as conn:
        conn.execute("""
            INSERT INTO profiles (user_id, store_id, default_persons)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                store_id = excluded.store_id,
                default_persons = excluded.default_persons,
                updated_at = datetime('now')
        """, (user_id, store_id, default_persons))