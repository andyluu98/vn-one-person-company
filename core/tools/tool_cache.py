"""SQLite cache cho tool results (24h default TTL)."""
from __future__ import annotations
from pathlib import Path
import sqlite3
import json
import time


class ToolCache:
    def __init__(self, db_path: Path, ttl_seconds: int = 86400):
        self.db_path = Path(db_path)
        self.ttl = ttl_seconds
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    source TEXT,
                    data TEXT,
                    timestamp INTEGER
                )
            """)

    def get(self, query: str, source: str) -> dict | None:
        key = f"{source}::{query}"
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT data, timestamp FROM cache WHERE key = ?", (key,)
            ).fetchone()
        if not row:
            return None
        data, ts = row
        if time.time() - ts > self.ttl:
            return None
        return json.loads(data)

    def set(self, query: str, data: dict, source: str):
        key = f"{source}::{query}"
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)",
                (key, source, json.dumps(data), int(time.time())),
            )
            conn.commit()
