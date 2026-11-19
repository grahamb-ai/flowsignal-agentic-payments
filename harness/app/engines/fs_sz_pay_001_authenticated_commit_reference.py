"""FS-SZ-PAY-001 replacement authenticated PostgreSQL reference candidate.

This independently checks the institutional Ed25519 instruction before invoking
an atomic database function under a dedicated service login. IMPORTANT: direct
possession of that login still bypasses signature verification. This is a
deliberately bounded integration candidate, NOT BOUNDARY-02 closure.
"""
from __future__ import annotations

from decimal import Decimal
from app.engines.fs_sz_pay_001_isolated_commitment_candidate import IsolatedCommitmentBoundaryCandidate
from app.engines.provider_instruction_verifier import canonical_instruction


class AuthenticatedCommitmentReference:
    def __init__(self, *, connect, verification_key, mandate_id, expected_source_account=None):
        self._connect = connect
        self._verifier = IsolatedCommitmentBoundaryCandidate(
            verification_key=verification_key, mandate_id=mandate_id,
            expected_source_account=expected_source_account,
        )

    def transfer(self, payload):
        status, decision = self._verifier.assess(payload)
        if status != 202:
            return status, decision
        instruction = canonical_instruction(payload)
        if instruction is None:
            return 403, {"status": "REFUSED_INVALID_BINDING"}
        try:
            with self._connect() as db:
                with db.cursor() as cur:
                    cur.execute("SELECT current_user")
                    if cur.fetchone()[0] != "fs_commit_service":
                        raise PermissionError("unqualified commitment service login")
                    cur.execute(
                        "SELECT fs_provider.commit_if_current(%s,%s,%s,%s,%s)",
                        (instruction["payment_intent_id"], instruction["mandate_id"],
                         instruction["authority_epoch"], instruction["amount_minor"],
                         instruction["beneficiary"]),
                    )
                    outcome = cur.fetchone()[0]
            if outcome == "COMMITTED":
                return 201, {"status": "TRANSFER_RECORDED"}
            if outcome == "REFUSED_DUPLICATE_INTENT":
                return 409, {"status": outcome}
            return 403, {"status": outcome}
        except PermissionError:
            return 503, {"status": "REFUSED_UNQUALIFIED_COMMIT_IDENTITY"}
        except Exception:
            return 503, {"status": "OUTCOME_UNKNOWN_RECONCILIATION_REQUIRED"}
