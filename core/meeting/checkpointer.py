"""SQLite checkpointer cho LangGraph state persistence.

Adapted from TradingAgents/graph/checkpointer.py.
"""
from __future__ import annotations
from pathlib import Path
import sqlite3


def make_checkpointer(db_path: Path | None = None):
    """Create SqliteSaver. Lazy import to avoid hard dep at module level."""
    from langgraph.checkpoint.sqlite import SqliteSaver

    if db_path is None:
        db_path = Path.home() / ".vn-business-os" / "checkpoints.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return SqliteSaver(conn)
