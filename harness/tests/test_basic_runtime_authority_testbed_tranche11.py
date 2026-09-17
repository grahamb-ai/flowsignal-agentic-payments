from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import pytest

from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario

BASE = Path("harness/scenarios/AP-001_allow.json")


def _base():
    return load_scenario(BASE)


def _decision(**changes):
    response, _ = evaluate_financial(replace(_base(), **changes))
    return response.decision


# Additional Unicode format/control characters that can visually disguise authority text.
@pytest.mark.parametrize("field", ["actor_id", "principal_id", "mandate_id", "beneficiary", "purpose"])
@pytest.mark.parametrize("bad", [
    "good\u200cvalue",  # zero-width non-joiner
    "good\u200dvalue",  # zero-width joiner
    "good\u2060value",  # word joiner
    "good\ufeffvalue",  # BOM / zero-width no-break space
])
def test_additional_unicode_format_characters_fail_closed(field, bad):
    assert _decision(**{field: bad}) != "ALLOW"


# Exact policy identifiers must not be normalized or trimmed into authority.
@pytest.mark.parametrize("field,value", [
    ("action", "payment.release "),
    ("action", " payment.release"),
    ("action", "PAYMENT.RELEASE"),
    ("target", "TREASURY_PAYMENT_GATEWAY "),
    ("target", " TREASURY_PAYMENT_GATEWAY"),
    ("target", "treasury_payment_gateway"),
    ("source_account", "TREASURY-001 "),
    ("source_account", " TREASURY-001"),
    ("mandate_id", "MANDATE-TREASURY-001 "),
    ("mandate_id", " MANDATE-TREASURY-001"),
])
def test_exact_authority_identifiers_are_not_silently_normalized(field, value):
    assert _decision(**{field: value}) != "ALLOW"


# Status values may be case-insensitive today, but whitespace must not be silently accepted.
@pytest.mark.parametrize("field,value", [
    ("kya_status", "VERIFIED "),
    ("mandate_status", "ACTIVE "),
    ("mandate_currency", "GBP "),
    ("counterparty_status", "APPROVED "),
    ("account_status", "ACTIVE "),
    ("risk_state", "NORMAL "),
    ("screening_status", "CLEAR "),
])
def test_semantic_status_trailing_whitespace_never_allows(field, value):
    assert _decision(**{field: value}) != "ALLOW"


# Boundary clock checks use the request's own fixed execution time, avoiding wall-clock flakiness.
def test_mandate_expiring_exactly_at_execution_time_is_still_current():
    req = _base()
    assert _decision(mandate_valid_until=req.requested_execution_time) == "ALLOW"


def test_mandate_expired_one_microsecond_before_execution_never_allows():
    req = _base()
    assert _decision(mandate_valid_until=req.requested_execution_time - timedelta(microseconds=1)) != "ALLOW"


def test_screening_exactly_at_freshness_limit_is_accepted():
    req = _base()
    captured = req.requested_execution_time - timedelta(seconds=req.screening_max_age_seconds)
    assert _decision(screening_captured_at=captured) == "ALLOW"


def test_screening_one_microsecond_beyond_freshness_limit_never_allows():
    req = _base()
    captured = req.requested_execution_time - timedelta(seconds=req.screening_max_age_seconds, microseconds=1)
    assert _decision(screening_captured_at=captured) != "ALLOW"


# Boolean values are integers in Python; authority numeric fields must not inherit that coercion.
@pytest.mark.parametrize("field", ["amount", "mandate_max_amount", "screening_max_age_seconds"])
@pytest.mark.parametrize("bad", [True, False])
def test_boolean_numeric_coercion_fails_closed(field, bad):
    assert _decision(**{field: bad}) != "ALLOW"
