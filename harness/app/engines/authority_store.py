from contextlib import contextmanager
from dataclasses import dataclass
from threading import RLock

@dataclass(frozen=True)
class AuthoritativeMandate:
    max_amount: float
    currency: str
    actions: tuple[str, ...]
    targets: tuple[str, ...]
    source_accounts: tuple[str, ...]
    counterparty_class: str
    beneficiaries: tuple[str, ...] = ()


AUTHORITATIVE_MANDATES = {
    "MANDATE-TREASURY-001": AuthoritativeMandate(
        max_amount=1000000.0,
        currency="GBP",
        actions=("payment.release",),
        targets=("TREASURY_PAYMENT_GATEWAY",),
        source_accounts=("TREASURY-001",),
        counterparty_class="APPROVED_SUPPLIERS",
    ),
    "MANDATE-EC009-STRIPE-USD-001": AuthoritativeMandate(
        max_amount=1.0,
        currency="USD",
        actions=("payment.collect",),
        targets=("stripe:test:acct_1U06JYL6P3J1guFB:payment_intent.create",),
        source_accounts=("pm_card_visa",),
        counterparty_class="STRIPE_TEST_ACCOUNTS",
        beneficiaries=("acct_1U06JYL6P3J1guFB",),
    ),
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
    mandate = AUTHORITATIVE_MANDATES.get(mandate_id)
    return mandate.max_amount if mandate is not None else None


def get_authoritative_mandate(mandate_id: str) -> AuthoritativeMandate | None:
    return AUTHORITATIVE_MANDATES.get(mandate_id)


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
