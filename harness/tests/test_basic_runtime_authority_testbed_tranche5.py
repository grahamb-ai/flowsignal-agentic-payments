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
# These fields are descriptive evidence/identity metadata in the MVP contract. They do not establish authority.
# Preserve that distinction explicitly rather than inventing a runtime refusal rule for non-authoritative labels.
@pytest.mark.parametrize("field",["actor_type","actor_role","principal_name","screening_source"])
def test_descriptive_metadata_does_not_create_or_remove_authority(field): assert _decision(**{field:""}) == "ALLOW"
def test_empty_permitted_source_accounts_cannot_allow(): assert _decision(permitted_source_accounts=[]) != "ALLOW"
# Counterparty authority is established by counterparty_status in this MVP; the class label is descriptive.
def test_blank_counterparty_class_label_does_not_override_approved_counterparty(): assert _decision(permitted_counterparty_class="") == "ALLOW"
