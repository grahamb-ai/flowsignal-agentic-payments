from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE=Path("harness/scenarios/AP-001_allow.json")
def _base(): return load_scenario(BASE)
def _decision(**changes):
    response,_=evaluate_financial(replace(_base(),**changes)); return response.decision
def test_expired_mandate_refuses():
    req=_base(); assert _decision(mandate_valid_until=req.requested_execution_time-timedelta(seconds=1)) != "ALLOW"
def test_screening_just_beyond_freshness_window_does_not_allow():
    req=_base(); assert _decision(screening_captured_at=req.requested_execution_time-timedelta(seconds=req.screening_max_age_seconds+1)) != "ALLOW"
@pytest.mark.parametrize("age",[0,1,30,60])
def test_future_screening_evidence_cannot_be_treated_as_fresh(age):
    req=_base(); assert _decision(screening_captured_at=req.requested_execution_time+timedelta(seconds=age+1)) != "ALLOW"
@pytest.mark.parametrize("max_age",[-1,-60,-3600])
def test_negative_screening_freshness_policy_never_allows(max_age): assert _decision(screening_max_age_seconds=max_age) != "ALLOW"
@pytest.mark.parametrize("value",[""," ","GBP "," GBP","ZZZ"])
def test_invalid_mandate_currency_never_allows(value): assert _decision(mandate_currency=value) != "ALLOW"
# For a resolved mandate, finite request-presented limits do not override the authoritative store.
# Nonfinite numeric material is malformed at the request boundary and must fail closed.
@pytest.mark.parametrize("limit",[-1.0,0.0])
def test_finite_presented_limit_cannot_override_resolved_authoritative_mandate(limit): assert _decision(mandate_max_amount=limit) == "ALLOW"
@pytest.mark.parametrize("limit",[float("nan"),float("inf"),float("-inf")])
def test_nonfinite_presented_limit_is_malformed_even_for_resolved_mandate(limit): assert _decision(mandate_max_amount=limit) != "ALLOW"
# These are descriptive/correlation fields in the MVP, not authority-establishing inputs.
@pytest.mark.parametrize("field",["scenario_id","actor_type","actor_role","principal_name","screening_source"])
@pytest.mark.parametrize("bad",[" ","\t","\n"])
def test_descriptive_metadata_whitespace_does_not_change_authority(field,bad): assert _decision(**{field:bad}) == "ALLOW"
