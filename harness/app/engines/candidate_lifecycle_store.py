from __future__ import annotations

import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from threading import RLock


_DEFAULT_PATH = Path(".flowsignal-runtime/candidate-lifecycle.sqlite3")
_LOCK = RLock()
_GENERATION_ISSUANCE_CAPABILITY = object()


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
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS authority_issued_candidate_generations (
            candidate_generation_id TEXT PRIMARY KEY,
            scenario_id TEXT NOT NULL,
            action_binding_hash TEXT NOT NULL,
            parent_candidate_generation_id TEXT,
            issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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


def _require_issuance_capability(capability: object) -> None:
    if capability is not _GENERATION_ISSUANCE_CAPABILITY:
        raise PermissionError("candidate generation issuance is authority-owned")


def issue_initial_candidate_generation(
    scenario_id: str,
    action_hash: str,
    *,
    issuance_capability: object,
) -> str:
    """Mint and register a root generation inside the authority boundary."""
    _require_issuance_capability(issuance_capability)
    candidate_generation_id = str(uuid.uuid4())
    with _LOCK, _connect() as connection:
        connection.execute(
            """
            INSERT INTO authority_issued_candidate_generations(
                candidate_generation_id, scenario_id, action_binding_hash,
                parent_candidate_generation_id
            ) VALUES (?, ?, ?, NULL)
            """,
            (candidate_generation_id, scenario_id, action_hash),
        )
    return candidate_generation_id


def issue_successor_candidate_generation(
    parent_candidate_generation_id: str,
    scenario_id: str,
    action_hash: str,
    *,
    issuance_capability: object,
) -> str:
    """Mint a successor only for an invalidated, identically bound parent."""
    _require_issuance_capability(issuance_capability)
    candidate_generation_id = str(uuid.uuid4())
    with _LOCK, _connect() as connection:
        parent = connection.execute(
            """
            SELECT scenario_id, action_binding_hash
            FROM authority_issued_candidate_generations
            WHERE candidate_generation_id = ?
            """,
            (parent_candidate_generation_id,),
        ).fetchone()
        invalidated = connection.execute(
            """
            SELECT 1 FROM invalidated_candidate_generations
            WHERE candidate_generation_id = ?
            """,
            (parent_candidate_generation_id,),
        ).fetchone()
        if parent is None or invalidated is None:
            raise ValueError("successor requires an authority-issued invalidated parent")
        if parent != (scenario_id, action_hash):
            raise ValueError("successor must preserve parent scenario and action binding")
        connection.execute(
            """
            INSERT INTO authority_issued_candidate_generations(
                candidate_generation_id, scenario_id, action_binding_hash,
                parent_candidate_generation_id
            ) VALUES (?, ?, ?, ?)
            """,
            (
                candidate_generation_id,
                scenario_id,
                action_hash,
                parent_candidate_generation_id,
            ),
        )
    return candidate_generation_id


def is_authority_issued_candidate_generation(
    candidate_generation_id: str,
    scenario_id: str,
    action_hash: str,
) -> bool:
    """Verify issuance and immutable binding, not merely identifier presence."""
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT 1 FROM authority_issued_candidate_generations
            WHERE candidate_generation_id = ?
              AND scenario_id = ?
              AND action_binding_hash = ?
            """,
            (candidate_generation_id, scenario_id, action_hash),
        ).fetchone()
    return row is not None
