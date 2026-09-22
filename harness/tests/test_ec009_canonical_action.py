from dataclasses import replace
from datetime import timedelta
import hashlib
import json
from pathlib import Path

import pytest

from app.engines.action_binding import action_binding_hash, canonical_action_object
from app.engines.ec009_projection import cap_downstream_expiry, stripe_payment_intent_projection
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/EC-009_stripe_usd_collection.json"
FROZEN = REPOSITORY_ROOT / "evidence/EC-009/EC-009_CANONICAL_ACTION.json"
FROZEN_HASH = REPOSITORY_ROOT / "evidence/EC-009/EC-009_CANONICAL_ACTION.sha256"


def _request():
    return load_scenario(SCENARIO)


def _attempt(req):
    return ExecutionAttempt(
        actor_id=req.actor_id,
        principal_id=req.principal_id,
        action=req.action,
        target=req.target,
        amount=req.amount,
        currency=req.currency,
        source_account=req.source_account,
        beneficiary=req.beneficiary,
        purpose=req.purpose,
        mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )


def test_ec009_frozen_object_is_exact_runtime_action():
    req = _request()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert canonical_action_object(req) == frozen
    canonical = json.dumps(frozen, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert action_binding_hash(req) == hashlib.sha256(canonical).hexdigest()
    assert FROZEN_HASH.read_text(encoding="ascii").split()[0] == action_binding_hash(req)


def test_ec009_authority_and_gateway_permit_exact_action():
    req = _request()
    response, receipt = evaluate_financial(req)
    assert response.decision == "ALLOW"
    result = validate_execution(receipt, _attempt(req))
    assert result.status == "PERMITTED"
    assert result.execution_permit is not None
    assert result.execution_permit.action_binding_hash == action_binding_hash(req)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("amount", 1.01),
        ("currency", "GBP"),
        ("target", "stripe:test:acct_ATTACKER:payment_intent.create"),
        ("beneficiary", "acct_ATTACKER"),
        ("source_account", "pm_card_mastercard"),
        ("action", "payment.release"),
        ("mandate_currency", "GBP"),
        ("permitted_source_accounts", ["pm_card_mastercard"]),
        ("permitted_counterparty_class", "APPROVED_SUPPLIERS"),
    ],
)
def test_ec009_authority_refuses_materially_different_action(field, value):
    response, _ = evaluate_financial(replace(_request(), **{field: value}))
    assert response.decision != "ALLOW"


def test_ec009_gateway_blocks_post_allow_substitution():
    req = _request()
    _, receipt = evaluate_financial(req)
    changed = replace(_attempt(req), beneficiary="acct_ATTACKER")
    result = validate_execution(receipt, changed)
    assert result.status == "BLOCKED"
    assert result.reason_code == "ACTION_BINDING_MISMATCH"


def test_ec009_stripe_projection_is_exact_and_minor_unit_safe():
    req = _request()
    params = stripe_payment_intent_projection(req)
    assert params["amount"] == 100
    assert params["currency"] == "usd"
    assert params["payment_method"] == "pm_card_visa"
    assert params["metadata"]["flowsignal_beneficiary"] == "acct_1U06JYL6P3J1guFB"
    assert params["metadata"]["flowsignal_action_binding_hash"] == action_binding_hash(req)


def test_ec009_downstream_expiry_cannot_outlive_upstream():
    req = _request()
    response, _ = evaluate_financial(req)
    downstream = cap_downstream_expiry(response.valid_until, 300, now=req.requested_execution_time)
    assert downstream == response.valid_until
    assert downstream <= response.valid_until
