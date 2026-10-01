from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock


_DEFAULT_PATH = Path(".flowsignal-runtime/candidate-lifecycle.sqlite3")
_LOCK = RLock()


def _store_path() -> Path:
    configured = os.environ.get("FLOWSIGNAL_CANDIDATE_LIFECYCLE_STORE")
    return Path(configured) if configured else _DEFAULT_PATH


def _connect() -> sqlite3.Connection:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS invalidated_candidate_generations (
            candidate_generation_id TEXT PRIMARY KEY,
            invalidated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


@contextmanager
def candidate_lifecycle_guard():
    """Serialize reference-MVP candidate lifecycle decisions."""
    with _LOCK:
        yield


def is_candidate_generation_invalidated(candidate_generation_id: str) -> bool:
    with _connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM invalidated_candidate_generations WHERE candidate_generation_id = ?",
            (candidate_generation_id,),
        ).fetchone()
    return row is not None


def invalidate_candidate_generation(candidate_generation_id: str) -> None:
    with _connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO invalidated_candidate_generations(candidate_generation_id) VALUES (?)",
            (candidate_generation_id,),
        )
