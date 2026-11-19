"""T21 bounded reference: durable exclusive payment-intent claim, not a provider fence.

The caller must supply a stable, authenticated business payment_intent_id.
This store does not establish that authenticity or bind to permits. Integration
at the protected consequence boundary remains NOT IMPLEMENTED.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

def _path() -> Path:
    value = os.environ.get("FLOWSIGNAL_PAYMENT_INTENT_STORE")
    return Path(value) if value else Path(".flowsignal-runtime/payment_intents.sqlite3")

def reserve_intent(payment_intent_id: str, permit_signature: str) -> bool:
    if not payment_intent_id or not payment_intent_id.strip():
        raise ValueError("payment_intent_id is required")
    if not permit_signature:
        raise ValueError("permit_signature is required")
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=10.0) as conn:
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("""CREATE TABLE IF NOT EXISTS payment_intent_claims (
            payment_intent_id TEXT PRIMARY KEY,
            permit_signature TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'RESERVED',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.execute(
            "INSERT OR IGNORE INTO payment_intent_claims(payment_intent_id, permit_signature) VALUES (?,?)",
            (payment_intent_id, permit_signature),
        )
        return cursor.rowcount == 1

def claim_status(payment_intent_id: str):
    path = _path()
    if not path.exists():
        return None
    with sqlite3.connect(path) as conn:
        row = conn.execute(
            "SELECT permit_signature,status FROM payment_intent_claims WHERE payment_intent_id=?",
            (payment_intent_id,),
        ).fetchone()
    return row
