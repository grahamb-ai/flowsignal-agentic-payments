from __future__ import annotations

import os
import sqlite3
from pathlib import Path


_DEFAULT_STORE_PATH = Path(".flowsignal-runtime/permit_consumption.sqlite3")


def _store_path() -> Path:
    configured = os.environ.get("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE")
    return Path(configured) if configured else _DEFAULT_STORE_PATH


def _connect() -> sqlite3.Connection:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5.0, isolation_level=None)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS consumed_execution_permits (
            signature TEXT PRIMARY KEY,
            consumed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


def consume_execution_permit_once(signature: str) -> bool:
    """Atomically record one permit signature in the reference durable store.

    Returns True only for the first successful insertion of a signature. A
    duplicate signature returns False, including after a Python component
    reload or a new process using the same SQLite store path.

    This is a reference-MVP durability mechanism. It does not establish
    production database availability, replication, multi-region consensus,
    external payment idempotency or infrastructure trust isolation.
    """
    connection = _connect()
    try:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO consumed_execution_permits(signature) VALUES (?)",
            (signature,),
        )
        return cursor.rowcount == 1
    finally:
        connection.close()
