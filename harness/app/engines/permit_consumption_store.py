from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path


_DEFAULT_STORE_PATH = Path(".flowsignal-runtime/permit_consumption.sqlite3")
_BUSY_RETRY_ATTEMPTS = 100
_BUSY_RETRY_DELAY_SECONDS = 0.05


def _store_path() -> Path:
    configured = os.environ.get("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE")
    return Path(configured) if configured else _DEFAULT_STORE_PATH


def _execute_with_busy_retry(connection: sqlite3.Connection, statement: str) -> None:
    """Execute store-initialization SQL while tolerating bounded SQLite lock races."""
    for attempt in range(_BUSY_RETRY_ATTEMPTS):
        try:
            connection.execute(statement)
            return
        except sqlite3.OperationalError as exc:
            message = str(exc).lower()
            if "locked" not in message and "busy" not in message:
                raise
            if attempt == _BUSY_RETRY_ATTEMPTS - 1:
                raise
            time.sleep(_BUSY_RETRY_DELAY_SECONDS)


def _connect() -> sqlite3.Connection:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5.0, isolation_level=None)
    connection.execute("PRAGMA busy_timeout=5000")
    _execute_with_busy_retry(connection, "PRAGMA journal_mode=WAL")
    _execute_with_busy_retry(
        connection,
        """
        CREATE TABLE IF NOT EXISTS consumed_execution_permits (
            signature TEXT PRIMARY KEY,
            consumed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
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
