from dataclasses import replace
from pathlib import Path
import pytest
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario
BASE=Path("harness/scenarios/AP-001_allow.json")
def _decision(**changes):
    response,_=evaluate_financial(replace(load_scenario(BASE),**changes)); return response.decision
@pytest.mark.parametrize("field,value",[("kya_status",""),("mandate_status",""),("counterparty_status",""),("account_status",""),("risk_state",""),("screening_status","")])
def test_blank_status_fields_never_allow(field,value): assert _decision(**{field:value}) != "ALLOW"
@pytest.mark.parametrize("field,value",[("kya_status"," verified "),("mandate_status"," active "),("counterparty_status"," approved "),("account_status"," active "),("risk_state"," normal "),("screening_status"," clear ")])
def test_untrimmed_status_values_do_not_silently_normalise_to_allow(field,value): assert _decision(**{field:value}) != "ALLOW"
@pytest.mark.parametrize("currency",[""," ","ZZZ","GBP "," GBP"])
def test_invalid_or_untrimmed_currency_never_allows(currency): assert _decision(currency=currency) != "ALLOW"
@pytest.mark.parametrize("account",[""," ","UNKNOWN-ACCOUNT","TREASURY-001 "])
def test_invalid_source_account_never_allows(account): assert _decision(source_account=account) != "ALLOW"
@pytest.mark.parametrize("action",[""," ","payment.Release","payment.release ","payment.refund"])
def test_non_exact_action_never_allows(action): assert _decision(action=action) != "ALLOW"
def test_presented_limit_cannot_expand_known_authoritative_mandate(): assert _decision(mandate_max_amount=999_999_999.0,amount=1_000_001.0) != "ALLOW"
