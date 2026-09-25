from __future__ import annotations

"""Bounded reference provenance for successful RAI final-bind.

This process-local registry is a conformance-harness mechanism, not a production
credential, IAM, KMS, HSM, distributed-consensus or durable provenance claim.
"""

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4


@dataclass(frozen=True)
class FinalBindProvenance:
    provenance_id: str
    determination_id: str
    constraint_id: str
    protected_operation_id: str
    authority_exercise_id: str
    execution_attempt_id: str
    action_binding_hash: str
    usage_reservation_id: str


_LOCK = RLock()
_PROVENANCE: dict[str, FinalBindProvenance] = {}
_FINAL_BIND_PROVENANCE_ISSUANCE_CAPABILITY = object()


def establish_final_bind_provenance(
    *,
    determination_id: str,
    constraint_id: str,
    protected_operation_id: str,
    authority_exercise_id: str,
    execution_attempt_id: str,
    action_binding_hash: str,
    usage_reservation_id: str,
    issuance_capability: object | None = None,
) -> FinalBindProvenance:
    if issuance_capability is not _FINAL_BIND_PROVENANCE_ISSUANCE_CAPABILITY:
        raise ValueError("successful final-bind provenance required")
    item = FinalBindProvenance(
        provenance_id=f"FBP:{uuid4()}",
        determination_id=determination_id,
        constraint_id=constraint_id,
        protected_operation_id=protected_operation_id,
        authority_exercise_id=authority_exercise_id,
        execution_attempt_id=execution_attempt_id,
        action_binding_hash=action_binding_hash,
        usage_reservation_id=usage_reservation_id,
    )
    with _LOCK:
        _PROVENANCE[item.provenance_id] = item
    return item


def verify_final_bind_provenance(
    provenance_id: str,
    *,
    determination_id: str,
    constraint_id: str,
    protected_operation_id: str,
    authority_exercise_id: str,
    execution_attempt_id: str,
    action_binding_hash: str,
    usage_reservation_id: str,
) -> bool:
    with _LOCK:
        item = _PROVENANCE.get(provenance_id)
        return bool(
            item
            and item.determination_id == determination_id
            and item.constraint_id == constraint_id
            and item.protected_operation_id == protected_operation_id
            and item.authority_exercise_id == authority_exercise_id
            and item.execution_attempt_id == execution_attempt_id
            and item.action_binding_hash == action_binding_hash
            and item.usage_reservation_id == usage_reservation_id
        )
