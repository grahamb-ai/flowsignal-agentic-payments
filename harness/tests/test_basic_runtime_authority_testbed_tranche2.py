from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
def _request(**changes): return replace(load_scenario(Path("harness/scenarios/AP-001_allow.json")), **changes)
def _decision(**changes):
    response,_=evaluate_financial(_request(**changes)); return response.decision
@pytest.mark.parametrize("field", ["action","target","source_account","currency","purpose"])
def test_basic_bound_action_fields_cannot_be_blank(field): assert _decision(**{field:""}) != "ALLOW"
def test_basic_zero_payment_amount_cannot_be_allowed(): assert _decision(amount=0.0) != "ALLOW"
def test_basic_unknown_currency_cannot_be_allowed(): assert _decision(currency="ZZZ") != "ALLOW"
def test_basic_unknown_action_cannot_be_allowed(): assert _decision(action="unrecognised.action") != "ALLOW"
def test_basic_blank_source_account_cannot_be_allowed(): assert _decision(source_account="") != "ALLOW"
