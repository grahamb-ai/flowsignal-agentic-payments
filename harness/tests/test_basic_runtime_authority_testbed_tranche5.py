from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE=Path("harness/scenarios/AP-001_allow.json")
def _decision(**changes):
    response,_=evaluate_financial(replace(load_scenario(BASE),**changes)); return response.decision
@pytest.mark.parametrize("amount",[float("nan"),float("inf"),float("-inf")])
def test_non_finite_payment_amount_never_allows(amount): assert _decision(amount=amount) != "ALLOW"
@pytest.mark.parametrize("limit",[float("nan"),float("inf"),float("-inf")])
def test_unknown_mandate_cannot_use_non_finite_presented_limit(limit): assert _decision(mandate_id="UNKNOWN-MANDATE",mandate_max_amount=limit) != "ALLOW"
def test_negative_screening_freshness_window_cannot_allow(): assert _decision(screening_max_age_seconds=-1) != "ALLOW"
@pytest.mark.parametrize("field",["actor_type","actor_role","principal_name","screening_source"])
def test_identity_and_evidence_descriptor_fields_cannot_be_blank(field): assert _decision(**{field:""}) != "ALLOW"
def test_empty_permitted_source_accounts_cannot_allow(): assert _decision(permitted_source_accounts=[]) != "ALLOW"
def test_blank_permitted_counterparty_class_cannot_allow(): assert _decision(permitted_counterparty_class="") != "ALLOW"
