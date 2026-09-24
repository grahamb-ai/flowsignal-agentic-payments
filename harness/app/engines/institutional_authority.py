from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from threading import RLock


@dataclass(frozen=True)
class AuthoritativeMandate:
    mandate_id: str
    status: str
    max_amount: Decimal
    currency: str
    source_accounts: tuple[str, ...]
    principal_id: str
    action: str


@dataclass(frozen=True)
class AuthoritySemantics:
    version: str
    definition_id: str
    source_id: str
    source_competence_root_id: str


@dataclass(frozen=True)
class AuthoritySnapshot:
    snapshot_id: str
    authority_epoch_id: str
    authority_fence_scope_key: str
    authority_fence: int
    authoritative_source_id: str
    source_competence_root_id: str
    semantics: AuthoritySemantics
    mandate: AuthoritativeMandate


_LOCK = RLock()
_EPOCH_ID = "AUTH-EPOCH-001"
_SOURCE_ID = "INSTITUTIONAL-AUTHORITY-STORE-001"
_COMPETENCE_ROOT = "INSTITUTIONAL-COMPETENCE-ROOT-001"
_SEMANTICS = AuthoritySemantics(
    version="NORM-PAY-001-v1.2",
    definition_id="FS-RAI-FX-001:NORM-PAY-001:v1.2",
    source_id="FS-RAI-FX-001-v1.0",
    source_competence_root_id=_COMPETENCE_ROOT,
)
_FENCE = 1
_MANDATES = {
    "MANDATE-TREASURY-001": AuthoritativeMandate(
        mandate_id="MANDATE-TREASURY-001",
        status="ACTIVE",
        max_amount=Decimal("1000000.00"),
        currency="GBP",
        source_accounts=("TREASURY-001",),
        principal_id="institution-001",
        action="payment.release",
    )
}


def _snapshot_id(mandate: AuthoritativeMandate, fence: int) -> str:
    payload = {
        "authority_epoch_id": _EPOCH_ID,
        "authority_fence": fence,
        "authoritative_source_id": _SOURCE_ID,
        "source_competence_root_id": _COMPETENCE_ROOT,
        "semantics": asdict(_SEMANTICS),
        "mandate": {
            **asdict(mandate),
            "max_amount": format(mandate.max_amount, ".2f"),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def get_authority_snapshot(mandate_id: str) -> AuthoritySnapshot | None:
    """Return one coherent immutable reference-state cut.

    Unknown mandates return None. Request-presented values are never promoted
    into authoritative state.
    """
    with _LOCK:
        mandate = _MANDATES.get(mandate_id)
        if mandate is None:
            return None
        fence = _FENCE
        return AuthoritySnapshot(
            snapshot_id=_snapshot_id(mandate, fence),
            authority_epoch_id=_EPOCH_ID,
            authority_fence_scope_key=f"{mandate.principal_id}:{mandate.mandate_id}",
            authority_fence=fence,
            authoritative_source_id=_SOURCE_ID,
            source_competence_root_id=_COMPETENCE_ROOT,
            semantics=_SEMANTICS,
            mandate=mandate,
        )


def advance_authority_fence() -> int:
    global _FENCE
    with _LOCK:
        _FENCE += 1
        return _FENCE


def advance_authority_epoch_for_test() -> str:
    """Advance the synthetic authority epoch without changing mandate economics.

    Test/reference-harness support only. A new authority-state epoch must not,
    by itself, imply replenishment of an aggregate mandate amount.
    """
    global _EPOCH_ID, _FENCE
    with _LOCK:
        try:
            prefix, raw = _EPOCH_ID.rsplit("-", 1)
            _EPOCH_ID = f"{prefix}-{int(raw) + 1:03d}"
        except (ValueError, TypeError):
            _EPOCH_ID = f"{_EPOCH_ID}-NEXT"
        _FENCE += 1
        return _EPOCH_ID
