"""CBP-002 — adversarial consequence attack challenge.

The proposition was frozen before this executable test. The first CI run failed
at collection because this test initially referenced obsolete module/API names.
That run is preserved. This commit repairs only the test harness; it does not
modify the protected-consequence implementation being challenged.
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


def test_cbp002_adversarial_consequence_attacks(tmp_path, monkeypatch):
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

    # Positive control: the primitive genuinely forms a represented consequence.
    _, first_receipt, _, first_binding, first_permit = _fresh_allow_and_permit()
    first_outcome = execute_protected_consequence(
        permit=first_permit,
        attempted_action_binding_hash=first_binding,
    )
    assert first_outcome == "CONSEQUENCE_FORMED"

    # Attack 1 — duplicate execution / consumed-permit replay.
    replay_outcome, replay_receipt = execute_protected_consequence_with_receipt(
        permit=first_permit,
        attempted_action_binding_hash=first_binding,
    )
    assert replay_outcome == "DENIED_EXECUTION_PERMIT_REPLAY", (
        "CBP-002 FAILURE — CONSUMED PERMIT FORMED CONSEQUENCE AGAIN"
    )
    assert replay_receipt.consequence_formed is False
    assert replay_receipt.authority_receipt_id == first_receipt.id
    assert replay_receipt.action_binding_hash == first_binding
    assert verify_consequence_outcome_receipt(replay_receipt)

    # Prepare a second valid permit under the current authority state.
    _, stale_receipt, stale_attempt, stale_binding, stale_permit = _fresh_allow_and_permit()
    old_version = stale_permit.authority_state_version
    assert stale_receipt.authority_state_version == old_version

    # Attack 2 — change authoritative state after permit issuance but before bind.
    new_version = advance_authority_state_version()
    assert new_version != old_version

    stale_outcome, stale_outcome_receipt = execute_protected_consequence_with_receipt(
        permit=stale_permit,
        attempted_action_binding_hash=stale_binding,
    )
    assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE", (
        "CBP-002 FAILURE — STALE PERMIT FORMED CONSEQUENCE"
    )
    assert stale_outcome_receipt.consequence_formed is False
    assert stale_outcome_receipt.authority_receipt_id == stale_receipt.id
    assert stale_outcome_receipt.action_binding_hash == stale_binding
    assert verify_consequence_outcome_receipt(stale_outcome_receipt)

    # Attack 3 — direct invocation cannot bypass current-state standing.
    direct_stale = execute_protected_consequence(
        permit=stale_permit,
        attempted_action_binding_hash=stale_binding,
    )
    assert direct_stale == "DENIED_AUTHORITY_STATE_STALE", (
        "CBP-002 FAILURE — DIRECT INVOCATION BYPASSED STALE-STATE CHECK"
    )

    # Attack 4a — beneficiary substitution against the historical permit.
    substituted_beneficiary = replace(
        stale_attempt,
        beneficiary="ATTACKER-BENEFICIARY",
    )
    beneficiary_binding = action_binding_hash(substituted_beneficiary)
    assert beneficiary_binding != stale_binding
    beneficiary_outcome = execute_protected_consequence(
        permit=stale_permit,
        attempted_action_binding_hash=beneficiary_binding,
    )
    assert beneficiary_outcome == "DENIED_ACTION_BINDING_MISMATCH", (
        "CBP-002 FAILURE — BENEFICIARY SUBSTITUTION FORMED CONSEQUENCE"
    )

    # Attack 4b — amount substitution against the same historical permit.
    substituted_amount = replace(
        stale_attempt,
        amount=stale_attempt.amount + 1.00,
    )
    amount_binding = action_binding_hash(substituted_amount)
    assert amount_binding != stale_binding
    amount_outcome = execute_protected_consequence(
        permit=stale_permit,
        attempted_action_binding_hash=amount_binding,
    )
    assert amount_outcome == "DENIED_ACTION_BINDING_MISMATCH", (
        "CBP-002 FAILURE — AMOUNT SUBSTITUTION FORMED CONSEQUENCE"
    )

    # Reacquire authority for the exact same attempted consequence under the new state.
    _, fresh_receipt, _, fresh_binding, fresh_permit = _fresh_allow_and_permit()
    assert fresh_binding == stale_binding
    assert fresh_receipt.id != stale_receipt.id
    assert fresh_permit.signature != stale_permit.signature
    assert fresh_permit.authority_state_version == new_version

    # Attack 5 — fresh authority must not resurrect the historical stale permit.
    historical_replay = execute_protected_consequence(
        permit=stale_permit,
        attempted_action_binding_hash=stale_binding,
    )
    assert historical_replay == "DENIED_AUTHORITY_STATE_STALE", (
        "CBP-002 FAILURE — HISTORICAL STALE PERMIT RESURRECTED"
    )

    # Final positive control: current exact-action authority still forms consequence.
    final_outcome, final_receipt = execute_protected_consequence_with_receipt(
        permit=fresh_permit,
        attempted_action_binding_hash=fresh_binding,
    )
    assert final_outcome == "CONSEQUENCE_FORMED"
    assert final_receipt.consequence_formed is True
    assert final_receipt.authority_receipt_id == fresh_receipt.id
    assert final_receipt.action_binding_hash == fresh_binding
    assert verify_consequence_outcome_receipt(final_receipt)
