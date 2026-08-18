from __future__ import annotations

import os
import sqlite3
from pathlib import Path


_DEFAULT_ANCHOR_PATH = Path(".flowsignal-runtime/execution_rollback_anchor.sqlite3")


def _anchor_path() -> Path:
    configured = os.environ.get("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE")
    if configured:
        return Path(configured)

    # Keep test/reference instances isolated when the permit store is redirected,
    # while deliberately keeping the rollback anchor outside the two stores that
    # PMQ-002.10 restores.
    permit_store = os.environ.get("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE")
    if permit_store:
        return Path(permit_store).with_name("execution-rollback-anchor.sqlite3")
    return _DEFAULT_ANCHOR_PATH


def _connect() -> sqlite3.Connection:
    path = _anchor_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5.0, isolation_level=None)
    connection.execute("PRAGMA busy_timeout=5000")
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS execution_rollback_anchors (
            permit_signature TEXT PRIMARY KEY,
            action_binding_hash TEXT NOT NULL,
            anchored_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return connection


def claim_execution_anchor_once(*, permit_signature: str, action_binding_hash: str) -> bool:
    """Claim a surviving reference rollback anchor for one execution permit.

    The anchor is intentionally separate from the permit-consumption and
    consequence-outcome stores restored by PMQ-002.10. If those stores are moved
    backwards while this anchor survives, re-presentation of the same permit is
    detected before represented consequence formation.

    This is only a local reference-MVP rollback-detection mechanism. It does not
    establish resistance to rollback of all local state, privileged storage
    compromise, production backup/restore, immutable audit, external monotonic
    counters, replicated storage or distributed consensus.
    """
    connection = _connect()
    try:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO execution_rollback_anchors(
                permit_signature,
                action_binding_hash
            ) VALUES (?, ?)
            """,
            (permit_signature, action_binding_hash),
        )
        return cursor.rowcount == 1
    finally:
        connection.close()
