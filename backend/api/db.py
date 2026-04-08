"""SQLite persistence for daily WhatsApp sync results."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "smarthome.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS daily_logs (
                date          TEXT PRIMARY KEY,        -- YYYY-MM-DD
                food_log      TEXT NOT NULL,
                behavior_log  TEXT NOT NULL,
                generated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS raw_entries (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                date         TEXT NOT NULL,
                idx          INTEGER NOT NULL,         -- order within the day
                content      TEXT NOT NULL,
                FOREIGN KEY (date) REFERENCES daily_logs(date) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_raw_entries_date ON raw_entries(date);
            """
        )


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_daily_log(
    date_str: str,
    food_log: str,
    behavior_log: str,
    generated_at: str,
    entries: list[str],
) -> None:
    with _conn() as c:
        c.execute(
            """
            INSERT INTO daily_logs(date, food_log, behavior_log, generated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                food_log = excluded.food_log,
                behavior_log = excluded.behavior_log,
                generated_at = excluded.generated_at
            """,
            (date_str, food_log, behavior_log, generated_at),
        )
        c.execute("DELETE FROM raw_entries WHERE date = ?", (date_str,))
        c.executemany(
            "INSERT INTO raw_entries(date, idx, content) VALUES (?, ?, ?)",
            [(date_str, i, e) for i, e in enumerate(entries)],
        )


def get_daily_log(date_str: str) -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT date, food_log, behavior_log, generated_at FROM daily_logs WHERE date = ?",
            (date_str,),
        ).fetchone()
        if not row:
            return None
        entries = [
            r["content"]
            for r in c.execute(
                "SELECT content FROM raw_entries WHERE date = ? ORDER BY idx",
                (date_str,),
            ).fetchall()
        ]
        return {**dict(row), "entries": entries}


def list_daily_logs() -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT date, generated_at FROM daily_logs ORDER BY date DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_latest_daily_log() -> dict | None:
    logs = list_daily_logs()
    if not logs:
        return None
    return get_daily_log(logs[0]["date"])
