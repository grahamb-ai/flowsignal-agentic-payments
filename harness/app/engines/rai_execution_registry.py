from __future__ import annotations

"""Reference registry for RAI-bound execution capabilities.

This is deliberately narrow reference-harness state. It lets the protected
execution boundary establish that signed RAI identifiers on a permit correspond
to a capability actually issued after successful final-bind, rather than merely
being non-empty attacker-chosen fields.
"""

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class RAIExecutionBinding:
    permit_signature: str
    determination_id: str
    constraint_id: str
    protected_operation_id: str
    authority_exercise_id: str
    execution_attempt_id: str
    action_binding_hash: str


_LOCK = RLock()
_BINDINGS: dict[str, RAIExecutionBinding] = {}


def register_rai_execution_binding(
    *,
    permit_signature: str,
    determination_id: str,
    constraint_id: str,
    protected_operation_id: str,
    authority_exercise_id: str,
    execution_attempt_id: str,
    action_binding_hash: str,
) -> RAIExecutionBinding:
    proposed = RAIExecutionBinding(
        permit_signature=permit_signature,
        determination_id=determination_id,
        constraint_id=constraint_id,
        protected_operation_id=protected_operation_id,
        authority_exercise_id=authority_exercise_id,
        execution_attempt_id=execution_attempt_id,
        action_binding_hash=action_binding_hash,
    )
    with _LOCK:
        existing = _BINDINGS.get(permit_signature)
        if existing is not None and existing != proposed:
            raise ValueError("RAI execution capability already registered differently")
        _BINDINGS[permit_signature] = proposed
    return proposed


def verify_rai_execution_binding(
    *,
    permit_signature: str,
    determination_id: str | None,
    constraint_id: str | None,
    protected_operation_id: str | None,
    authority_exercise_id: str | None,
    execution_attempt_id: str | None,
    action_binding_hash: str,
) -> bool:
    if None in (
        determination_id,
        constraint_id,
        protected_operation_id,
        authority_exercise_id,
        execution_attempt_id,
    ):
        return False
    with _LOCK:
        binding = _BINDINGS.get(permit_signature)
        return bool(
            binding
            and binding.determination_id == determination_id
            and binding.constraint_id == constraint_id
            and binding.protected_operation_id == protected_operation_id
            and binding.authority_exercise_id == authority_exercise_id
            and binding.execution_attempt_id == execution_attempt_id
            and binding.action_binding_hash == action_binding_hash
        )
