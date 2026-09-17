"""Basic Runtime Authority Test Bed — failure-first tranche 1."""
from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE = Path("harness/scenarios/AP-001_allow.json")
def _base(): return load_scenario(BASE)
def _decision(**changes):
    response, _ = evaluate_financial(replace(_base(), **changes)); return response.decision
@pytest.mark.parametrize("field", ["actor_id", "principal_id", "mandate_id"])
def test_basic_required_authority_identifiers_cannot_be_blank(field): assert _decision(**{field:""}) != "ALLOW"
def test_basic_unknown_mandate_cannot_self_assert_its_limit(): assert _decision(mandate_id="UNKNOWN-MANDATE", mandate_max_amount=999_999_999.0) != "ALLOW"
@pytest.mark.parametrize("amount", [-1.0, -0.01])
def test_basic_negative_payment_amount_cannot_be_allowed(amount): assert _decision(amount=amount) != "ALLOW"
def test_basic_unknown_execution_target_cannot_be_allowed(): assert _decision(target="UNRECOGNISED_EXECUTION_TARGET") != "ALLOW"
def test_basic_explicit_approval_required_cannot_return_autonomous_allow(): assert _decision(approval_required=True) != "ALLOW"
def test_basic_blank_beneficiary_cannot_be_allowed(): assert _decision(beneficiary="") != "ALLOW"
