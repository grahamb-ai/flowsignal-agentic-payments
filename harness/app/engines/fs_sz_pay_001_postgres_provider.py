"""FS-SZ-PAY-001 integrated PostgreSQL-backed provider reference.

Only a separately provisioned payment-executor DB identity may be used here.
Institutional signing private keys and authority-writer credentials are excluded.
This is not a production rail or deployment-IAM qualification.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.engines.provider_instruction_verifier import verify_instruction


class PostgreSQLProtectedLedger:
    def __init__(self, *, connect, verification_key, mandate_id: str):
        if verification_key is None or not mandate_id:
            raise ValueError("institutional verifier and mandate required")
        self._connect = connect
        self._verification_key = verification_key
        self._mandate_id = mandate_id

    def transfer(self, payload: dict) -> tuple[int, dict]:
        if not verify_instruction(payload, self._verification_key):
            return 403, {"status": "REFUSED_UNAUTHENTICATED_INSTRUCTION"}
        if payload.get("mandate_id") != self._mandate_id:
            return 403, {"status": "REFUSED_AUTHORITY"}
        if payload.get("currency") != "GBP":
            return 403, {"status": "REFUSED_INVALID_BINDING"}
        try:
            amount = Decimal(str(payload["amount"]))
            minor = amount * 100
            if not amount.is_finite() or amount <= 0 or minor != minor.to_integral_value():
                return 403, {"status": "REFUSED_INVALID_AMOUNT"}
            amount_minor = int(minor)
        except (KeyError, InvalidOperation, ValueError, TypeError, OverflowError):
            return 403, {"status": "REFUSED_INVALID_AMOUNT"}
        try:
            with self._connect() as db:
                # The connection must already be authenticated as the
                # restricted executor role; do not SET ROLE from HTTP input.
                with db.cursor() as cur:
                    cur.execute("SELECT current_user")
                    if cur.fetchone()[0] != "fs_payment_executor":
                        raise PermissionError("provider DB identity is not restricted executor")
                    cur.execute(
                        "SELECT fs_provider.commit_if_current(%s,%s,%s,%s,%s)",
                        (payload["payment_intent_id"], self._mandate_id,
                         payload["authority_epoch"], amount_minor, payload["beneficiary"]),
                    )
                    outcome = cur.fetchone()[0]
            if outcome == "COMMITTED":
                return 201, {"status": "TRANSFER_RECORDED"}
            if outcome in ("REFUSED_AUTHORITY", "REFUSED_DUPLICATE_INTENT"):
                return (403 if outcome == "REFUSED_AUTHORITY" else 409), {"status": outcome}
            return 403, {"status": outcome}
        except PermissionError:
            return 503, {"status": "REFUSED_UNQUALIFIED_PROVIDER_IDENTITY"}
        except Exception:
            # Do not infer non-commitment from an ambiguous DB failure.
            return 503, {"status": "OUTCOME_UNKNOWN_RECONCILIATION_REQUIRED"}
