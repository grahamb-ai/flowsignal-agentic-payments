from contextlib import contextmanager
from threading import RLock

AUTHORITATIVE_MANDATE_LIMITS = {
    "MANDATE-TREASURY-001": 1000000.0,
}

_AUTHORITY_STATE_VERSION = 1
_AUTHORITY_STATE_LOCK = RLock()


def get_authoritative_mandate_limit(mandate_id: str) -> float | None:
    return AUTHORITATIVE_MANDATE_LIMITS.get(mandate_id)


def get_authority_state_version() -> int:
    with _AUTHORITY_STATE_LOCK:
        return _AUTHORITY_STATE_VERSION


@contextmanager
def authority_state_guard():
    """Serialize final standing validation and represented consequence formation.

    The guard is intentionally in-process and reference-harness scoped. It does
    not claim distributed transaction semantics across external systems.
    """
    with _AUTHORITY_STATE_LOCK:
        yield


def get_authority_state_version_unlocked() -> int:
    """Read state while the caller already holds authority_state_guard()."""
    return _AUTHORITY_STATE_VERSION


def advance_authority_state_version() -> int:
    global _AUTHORITY_STATE_VERSION
    with _AUTHORITY_STATE_LOCK:
        _AUTHORITY_STATE_VERSION += 1
        return _AUTHORITY_STATE_VERSION
