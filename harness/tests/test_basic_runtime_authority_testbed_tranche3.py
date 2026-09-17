from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE=Path("harness/scenarios/AP-001_allow.json")
def _decision(**changes):
    response,_=evaluate_financial(replace(load_scenario(BASE),**changes)); return response.decision
@pytest.mark.parametrize("field",["actor_id","principal_id","mandate_id","action","target","source_account","beneficiary","currency","purpose"])
@pytest.mark.parametrize("bad",[" ","\t","\n","   "])
def test_required_text_fields_reject_whitespace_only(field,bad): assert _decision(**{field:bad}) != "ALLOW"
@pytest.mark.parametrize("field,bad",[("actor_authenticated",False),("kya_status","UNVERIFIED"),("mandate_status","INACTIVE"),("counterparty_status","UNAPPROVED"),("account_status","INACTIVE"),("risk_state","HIGH"),("screening_status","HIT")])
def test_each_existing_negative_authority_condition_prevents_allow(field,bad): assert _decision(**{field:bad}) != "ALLOW"
@pytest.mark.parametrize("amount",[-1_000_000_000.0,-0.000001,0.0])
def test_non_positive_amounts_never_allow(amount): assert _decision(amount=amount) != "ALLOW"
def test_unknown_mandate_rejected_even_with_small_self_asserted_limit(): assert _decision(mandate_id="DOES-NOT-EXIST",mandate_max_amount=1.0,amount=0.5) != "ALLOW"
