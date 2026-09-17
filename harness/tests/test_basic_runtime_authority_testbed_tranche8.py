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
@pytest.mark.parametrize("seconds_ahead",[1,60,3600,86400])
def test_future_dated_screening_evidence_never_allows(seconds_ahead):
    req=_base(); assert _decision(screening_captured_at=req.requested_execution_time+timedelta(seconds=seconds_ahead)) != "ALLOW"
@pytest.mark.parametrize("max_age",[-1,-60,-86400])
def test_negative_screening_max_age_never_allows(max_age): assert _decision(screening_max_age_seconds=max_age) != "ALLOW"
@pytest.mark.parametrize("mandate_id",[""," ","UNKNOWN","MANDATE-TREASURY-001 ","mandate-treasury-001"])
def test_mandate_identifier_must_resolve_exactly_to_authoritative_record(mandate_id): assert _decision(mandate_id=mandate_id) != "ALLOW"
@pytest.mark.parametrize("presented_limit",[1_000_000.01,2_000_000.0,1e12])
def test_presented_limit_cannot_expand_known_authoritative_limit(presented_limit): assert _decision(mandate_max_amount=presented_limit,amount=1_000_000.01) != "ALLOW"
@pytest.mark.parametrize("presented_limit",[0.0,1.0,999_999.0])
def test_presented_limit_cannot_reduce_known_authoritative_limit(presented_limit): assert _decision(mandate_max_amount=presented_limit,amount=750_000.0)=="ALLOW"
