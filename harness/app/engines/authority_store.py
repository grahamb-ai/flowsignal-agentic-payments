from contextlib import contextmanager
from threading import RLock

AUTHORITATIVE_MANDATE_LIMITS = {
    "MANDATE-TREASURY-001": 1000000.0,
}

# The represented authority state is held in a private monotonic holder rather
# than exposed as a directly assignable module-level integer. Mutation is only
# available through the forward-only advance operation below.
class _MonotonicAuthorityState:
    __slots__ = ("__version",)

    def __init__(self, initial_version: int) -> None:
        object.__setattr__(self, "_MonotonicAuthorityState__version", initial_version)

    @property
    def version(self) -> int:
        return self.__version

    def advance(self) -> int:
        object.__setattr__(
            self,
            "_MonotonicAuthorityState__version",
            self.__version + 1,
        )
        return self.__version


_AUTHORITY_STATE = _MonotonicAuthorityState(1)
_AUTHORITY_STATE_LOCK = RLock()


def get_authoritative_mandate_limit(mandate_id: str) -> float | None:
    return AUTHORITATIVE_MANDATE_LIMITS.get(mandate_id)


def get_authority_state_version() -> int:
    with _AUTHORITY_STATE_LOCK:
        return _AUTHORITY_STATE.version


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
    return _AUTHORITY_STATE.version


def advance_authority_state_version() -> int:
    with _AUTHORITY_STATE_LOCK:
        return _AUTHORITY_STATE.advance()
