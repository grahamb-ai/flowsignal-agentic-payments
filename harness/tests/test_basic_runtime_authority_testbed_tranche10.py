from dataclasses import replace
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


@pytest.mark.parametrize("field", [
    "actor_id", "principal_id", "mandate_id", "action", "target",
    "source_account", "beneficiary", "currency", "purpose",
])
@pytest.mark.parametrize("bad", [
    "x\x00y", "x\x01y", "x\x1fy", "x\x7fy", "x\u200by",
    "\x00visible", "visible\x00", "\u200bvisible", "visible\u200b",
])
def test_authority_text_with_embedded_control_or_zero_width_never_allows(field, bad):
    assert _decision(**{field: bad}) != "ALLOW"


@pytest.mark.parametrize("field", [
    "kya_status", "mandate_status", "mandate_currency", "counterparty_status",
    "account_status", "risk_state", "screening_status",
])
@pytest.mark.parametrize("bad", [
    "VERIFIED\x00", "\x00VERIFIED", "ACTIVE\x00", "GBP\x00", "CLEAR\u200b",
])
def test_semantic_status_text_with_embedded_controls_never_allows(field, bad):
    assert _decision(**{field: bad}) != "ALLOW"


# The current authority contract requires a finite amount greater than zero and within
# the authoritative mandate limit. It does not define a currency minimum-unit rule.
@pytest.mark.parametrize("amount", [5e-324, 1e-300])
def test_tiny_positive_finite_amounts_follow_defined_amount_policy(amount):
    assert _decision(amount=amount) == "ALLOW"

@pytest.mark.parametrize("bad", [-5e-324, -1e-300, 1e308, -1e308])
def test_extreme_amounts_outside_defined_policy_never_allow(bad):
    assert _decision(amount=bad) != "ALLOW"


@pytest.mark.parametrize("bad", [
    float("nan"), float("inf"), float("-inf"), True, False, "1000000", None,
])
def test_presented_mandate_limit_malformed_numeric_material_never_allows(bad):
    assert _decision(mandate_max_amount=bad) != "ALLOW"


@pytest.mark.parametrize("bad", [
    float("nan"), float("inf"), float("-inf"), 0.5, 1.5,
])
def test_screening_max_age_noninteger_or_nonfinite_never_allows(bad):
    assert _decision(screening_max_age_seconds=bad) != "ALLOW"


@pytest.mark.parametrize("bad", [
    [], [""], [" "], ["\t"], ["\u200b"], ["TREASURY-001", ""],
    ["TREASURY-001", "\x00"], ["TREASURY-001", 1], ["TREASURY-001", False],
])
def test_permitted_source_accounts_structural_garbage_never_allows(bad):
    assert _decision(permitted_source_accounts=bad) != "ALLOW"
