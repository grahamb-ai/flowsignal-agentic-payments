from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE=Path("harness/scenarios/AP-001_allow.json")
def _base(): return load_scenario(BASE)
def _decision(**changes):
    response,_=evaluate_financial(replace(_base(),**changes)); return response.decision
def test_amount_exactly_at_authoritative_limit_may_allow():
    req=_base(); assert _decision(amount=req.mandate_max_amount)=="ALLOW"
def test_amount_just_over_authoritative_limit_does_not_allow():
    req=_base(); assert _decision(amount=req.mandate_max_amount+0.01)!="ALLOW"
@pytest.mark.parametrize("value",["\x00","\r","\r\n","\u200b"])
@pytest.mark.parametrize("field",["actor_id","principal_id","mandate_id","target","beneficiary","purpose"])
def test_control_or_invisible_only_required_text_never_allows(field,value): assert _decision(**{field:value}) != "ALLOW"
# scenario_id is a test/correlation identifier and is deliberately not an authority-establishing field.
@pytest.mark.parametrize("value",["\x00","\r","\r\n","\u200b"])
def test_scenario_id_cannot_change_authority_decision(value): assert _decision(scenario_id=value) == "ALLOW"
def test_approval_required_true_never_allows_autonomous_execution(): assert _decision(approval_required=True) != "ALLOW"
@pytest.mark.parametrize("presented_limit",[0.01,1.0,1_000_000.0,999_999_999.0])
def test_unknown_mandate_never_bootstraps_authority_from_presented_limit(presented_limit): assert _decision(mandate_id="UNKNOWN-MANDATE",mandate_max_amount=presented_limit,amount=0.01) != "ALLOW"
@pytest.mark.parametrize("target",["UNKNOWN","PAYMENT_GATEWAY","TREASURY_PAYMENT_GATEWAY "," treasury_payment_gateway"])
def test_non_exact_or_unknown_target_never_allows(target): assert _decision(target=target) != "ALLOW"
