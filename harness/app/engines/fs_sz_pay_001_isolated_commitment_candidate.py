"""Fail-closed replacement commitment boundary, initial candidate.

This is intentionally NOT wired to a database commitment credential.
An independent signer check is necessary but insufficient: the replacement
must not become payment-capable until credential isolation and atomic
authority/commit enforcement are qualified.
"""
from __future__ import annotations

from app.engines.provider_instruction_verifier import (
    canonical_instruction, verify_instruction,
)


class ReplacementBoundaryNotQualified(RuntimeError):
    pass


class IsolatedCommitmentBoundaryCandidate:
    """Independent instruction verifier with a hard-disabled commit operation."""

    def __init__(self, *, verification_key, mandate_id: str,
                 expected_action: str = "transfer",
                 expected_target: str = "protected-provider",
                 expected_source_account: str | None = None):
        if verification_key is None or not mandate_id or not expected_action or not expected_target:
            raise ValueError("pinned institutional verifier and mandate required")
        self._verification_key = verification_key
        self._mandate_id = mandate_id
        self._expected_action = expected_action
        self._expected_target = expected_target
        self._expected_source_account = expected_source_account

    def assess(self, payload: dict) -> tuple[int, dict]:
        if not isinstance(payload, dict):
            return 403, {"status": "REFUSED_INVALID_INSTRUCTION"}
        if not verify_instruction(payload, self._verification_key):
            return 403, {"status": "REFUSED_UNAUTHENTICATED_INSTRUCTION"}
        instruction = canonical_instruction(payload)
        if instruction is None or instruction["mandate_id"] != self._mandate_id:
            return 403, {"status": "REFUSED_AUTHORITY"}
        if (instruction["currency"] != "GBP"
                or instruction["action"] != self._expected_action
                or instruction["target"] != self._expected_target
                or (self._expected_source_account is not None
                    and instruction["source_account"] != self._expected_source_account)):
            return 403, {"status": "REFUSED_INVALID_BINDING"}
        return 202, {"status": "INSTRUCTION_AUTHENTICATED_NOT_COMMITTED"}

    def commit(self, payload: dict) -> tuple[int, dict]:
        # No database connection, privileged role or old SQL function may be
        # reachable from this candidate. Fail closed even for valid signatures.
        status, decision = self.assess(payload)
        if status != 202:
            return status, decision
        return 503, {"status": "REFUSED_FINAL_BOUNDARY_NOT_QUALIFIED"}
