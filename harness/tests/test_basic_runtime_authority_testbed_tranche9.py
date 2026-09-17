from dataclasses import replace
from pathlib import Path
import pytest

from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario

BASE = Path("harness/scenarios/AP-001_allow.json")


def _base():
    return load_scenario(BASE)


def _never_allow(**changes):
    """Malformed front-door values must fail closed, not crash or ALLOW."""
    try:
        response, _ = evaluate_financial(replace(_base(), **changes))
    except Exception as exc:  # a crash is itself a failed boundary contract
        pytest.fail(f"malformed request escaped authority boundary: {type(exc).__name__}: {exc}")
    assert response.decision != "ALLOW"


@pytest.mark.parametrize("field", [
    "actor_id", "principal_id", "mandate_id", "action", "target",
    "source_account", "beneficiary", "currency", "purpose",
])
@pytest.mark.parametrize("bad", [None, 0, False, [], {}])
def test_required_authority_text_wrong_types_fail_closed(field, bad):
    _never_allow(**{field: bad})


@pytest.mark.parametrize("field", [
    "kya_status", "mandate_status", "counterparty_status", "account_status",
    "risk_state", "screening_status", "mandate_currency",
])
@pytest.mark.parametrize("bad", [None, 0, False, [], {}])
def test_status_and_currency_wrong_types_fail_closed(field, bad):
    _never_allow(**{field: bad})


@pytest.mark.parametrize("bad", [None, "750000", True, False, [], {}])
def test_amount_wrong_types_fail_closed(bad):
    _never_allow(amount=bad)


@pytest.mark.parametrize("bad", [None, "3600", True, False, [], {}])
def test_screening_max_age_wrong_types_fail_closed(bad):
    _never_allow(screening_max_age_seconds=bad)


@pytest.mark.parametrize("bad", [None, "2026-08-10T09:00:00Z", 0, False, [], {}])
def test_screening_timestamp_wrong_types_fail_closed(bad):
    _never_allow(screening_captured_at=bad)


@pytest.mark.parametrize("bad", [None, "2026-12-31T23:59:59Z", 0, False, [], {}])
def test_mandate_expiry_wrong_types_fail_closed(bad):
    _never_allow(mandate_valid_until=bad)


@pytest.mark.parametrize("bad", [None, "2026-08-10T09:15:00Z", 0, False, [], {}])
def test_requested_execution_time_wrong_types_fail_closed(bad):
    _never_allow(requested_execution_time=bad)


@pytest.mark.parametrize("bad", [None, "TREASURY-001", 0, False, {}, ["TREASURY-001", None]])
def test_permitted_source_accounts_malformed_values_fail_closed(bad):
    _never_allow(permitted_source_accounts=bad)


@pytest.mark.parametrize("bad", [None, 0, 1, "true", "false", [], {}])
def test_actor_authenticated_must_be_literal_boolean_true(bad):
    _never_allow(actor_authenticated=bad)


@pytest.mark.parametrize("bad", [None, 0, 1, "false", "true", [], {}])
def test_approval_required_malformed_values_fail_closed(bad):
    _never_allow(approval_required=bad)
