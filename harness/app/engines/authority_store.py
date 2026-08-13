AUTHORITATIVE_MANDATE_LIMITS = {
    "MANDATE-TREASURY-001": 1000000.0,
}

_AUTHORITY_STATE_VERSION = 1


def get_authoritative_mandate_limit(mandate_id: str) -> float | None:
    return AUTHORITATIVE_MANDATE_LIMITS.get(mandate_id)


def get_authority_state_version() -> int:
    return _AUTHORITY_STATE_VERSION


def advance_authority_state_version() -> int:
    global _AUTHORITY_STATE_VERSION
    _AUTHORITY_STATE_VERSION += 1
    return _AUTHORITY_STATE_VERSION