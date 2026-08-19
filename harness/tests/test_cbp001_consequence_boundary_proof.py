"""CBP-001 — frozen consequence-boundary proof challenge.

Frozen external seam:
real represented protected consequence -> current standing -> changed condition
-> attempted bind -> NO_BIND -> bypass failure -> receipt -> replay/current-state separation

The challenge definition was committed before this executable test.
"""

from dataclasses import replace
from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.consequence_receipt import verify_consequence_outcome_receipt
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import (
    execute_protected_consequence,
    execute_protected_consequence_with_receipt,
)
from harness.runner import load_scenario


def _fresh_allow_and_permit():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    response, receipt = evaluate_financial(req)
    assert response.decision == "ALLOW"

    attempt = ExecutionAttempt(
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
    binding = action_binding_hash(attempt)
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    return req, receipt, attempt, binding, gateway.execution_permit


def test_cbp001_consequence_boundary_seam(tmp_path, monkeypatch):
    # Isolate represented durable execution state for this frozen qualification.
    monkeypatch.setenv(
        "FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",
        str(tmp_path / "permit-consumption.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",
        str(tmp_path / "consequence-outcomes.sqlite3"),
    )
    monkeypatch.setenv(
        "FLOWSIGNAL_ROLLBACK_ANCHOR_STORE",
        str(tmp_path / "rollback-anchor.sqlite3"),
    )

    # 1. CONTROL: prove the challenged primitive is genuinely consequence-producing
    # under current standing and exact action binding. This prevents a vacuous
    # NO_BIND result against a primitive that never forms consequences.
    _, control_receipt, _, control_binding, control_permit = _fresh_allow_and_permit()
    control_outcome, control_consequence_receipt = execute_protected_consequence_with_receipt(
        permit=control_permit,
        attempted_action_binding_hash=control_binding,
    )
    assert control_outcome == "CONSEQUENCE_FORMED"
    assert control_consequence_receipt.consequence_formed is True
    assert verify_consequence_outcome_receipt(control_consequence_receipt)

    # 2. Obtain a second valid exact-action permit while the same authority state
    # is current. This is the historical standing that will be attacked.
    _, historical_receipt, historical_attempt, historical_binding, historical_permit = (
        _fresh_allow_and_permit()
    )
    assert historical_permit.authority_receipt_id == historical_receipt.id

    # 3. CHANGED WORLD: authoritative runtime state commits a newer version after
    # permit issuance but before the represented consequence attempts to bind.
    new_authority_state_version = advance_authority_state_version()
    assert new_authority_state_version != historical_permit.authority_state_version

    # 4. ATTEMPTED BIND / NO_BIND: call the protected consequence primitive
    # directly with the formerly valid permit. PASS only if current standing is
    # reacquired at this boundary and stale authority cannot form consequence.
    stale_outcome, stale_consequence_receipt = execute_protected_consequence_with_receipt(
        permit=historical_permit,
        attempted_action_binding_hash=historical_binding,
    )
    assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE", (
        "CBP-001 FAILURE — STALE AUTHORITY FORMED CONSEQUENCE OR FAILED TO DENY "
        "AT THE PROTECTED CONSEQUENCE BOUNDARY"
    )
    assert stale_outcome != "CONSEQUENCE_FORMED"

    # 5. RECEIPT: the denial evidence is bound to the same attempted action and
    # explicitly records non-formation.
    assert stale_consequence_receipt.authority_receipt_id == historical_receipt.id
    assert stale_consequence_receipt.action_binding_hash == historical_binding
    assert stale_consequence_receipt.outcome == "DENIED_AUTHORITY_STATE_STALE"
    assert stale_consequence_receipt.consequence_formed is False
    assert verify_consequence_outcome_receipt(stale_consequence_receipt)

    # 6. BYPASS / ACTION SUBSTITUTION: alter the attempted consequence while
    # presenting the same historical permit directly to the protected primitive.
    substituted_attempt = replace(
        historical_attempt,
        beneficiary="SUBSTITUTED-BENEFICIARY",
        amount=historical_attempt.amount + 1.00,
    )
    substituted_binding = action_binding_hash(substituted_attempt)
    assert substituted_binding != historical_binding

    substitution_outcome = execute_protected_consequence(
        permit=historical_permit,
        attempted_action_binding_hash=substituted_binding,
    )
    assert substitution_outcome == "DENIED_ACTION_BINDING_MISMATCH", (
        "CBP-001 FAILURE — ACTION SUBSTITUTION FORMED CONSEQUENCE"
    )
    assert substitution_outcome != "CONSEQUENCE_FORMED"

    # 7. CURRENT-STATE REACQUISITION: reevaluate the same business action under
    # the changed authoritative state. If execution is permitted, it must be a
    # newly issued authority receipt/permit bound to the new state — never a
    # resurrection of the historical permit.
    _, fresh_receipt, _, fresh_binding, fresh_permit = _fresh_allow_and_permit()
    assert fresh_receipt.id != historical_receipt.id
    assert fresh_permit.signature != historical_permit.signature
    assert fresh_permit.authority_state_version == new_authority_state_version
    assert fresh_permit.authority_state_version != historical_permit.authority_state_version
    assert fresh_binding == historical_binding

    # 8. HISTORICAL REPLAY AFTER FRESH EVALUATION: the old permit remains stale
    # even though a new current-state permit for the same exact action now exists.
    historical_replay = execute_protected_consequence(
        permit=historical_permit,
        attempted_action_binding_hash=historical_binding,
    )
    assert historical_replay == "DENIED_AUTHORITY_STATE_STALE", (
        "CBP-001 FAILURE — HISTORICAL PERMIT RESURRECTED AFTER REEVALUATION"
    )
    assert historical_replay != "CONSEQUENCE_FORMED"

    # 9. POSITIVE CURRENT-STATE CONTROL: the newly reacquired authority can reach
    # the same protected consequence primitive, proving that stale denial above
    # was caused by standing/action state rather than a dead execution surface.
    fresh_outcome = execute_protected_consequence(
        permit=fresh_permit,
        attempted_action_binding_hash=fresh_binding,
    )
    assert fresh_outcome == "CONSEQUENCE_FORMED"
