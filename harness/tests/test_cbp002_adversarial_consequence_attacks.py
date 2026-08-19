from dataclasses import replace

from app.engines.authority_store import advance_authority_state_version, get_authority_state_version
from app.engines.consequence_receipt import verify_consequence_outcome_receipt
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial import evaluate_financial
from app.engines.protected_consequence import (
    execute_protected_consequence,
    execute_protected_consequence_with_receipt,
)
from app.scenarios import load_scenario


def _attempt_from_request(req):
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
        attempted_at=req.attempted_at,
    )


def _fresh_allow_and_permit():
    req = load_scenario("AP-001")
    receipt = evaluate_financial(req)
    assert receipt.decision == "ALLOW"

    attempt = _attempt_from_request(req)
    gateway = validate_execution(receipt, attempt)
    assert gateway.result == "PERMITTED"
    assert gateway.permit is not None

    return req, receipt, attempt, gateway.permit, action_binding_hash(attempt)


def test_cbp002_adversarial_consequence_attacks(tmp_path, monkeypatch):
    # Isolate durable reference stores for this frozen challenge.
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_STORE", str(tmp_path / "permit.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(tmp_path / "outcome.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(tmp_path / "anchor.sqlite3"))

    # Positive control: a fresh exact-action permit can form the represented consequence.
    _, first_receipt, first_attempt, first_permit, first_binding = _fresh_allow_and_permit()
    formed = execute_protected_consequence(first_permit, first_binding)
    assert formed == "CONSEQUENCE_FORMED"

    # Attack 1 — duplicate/replay of already-consumed permit must not form again.
    replay_outcome, replay_receipt = execute_protected_consequence_with_receipt(
        first_permit, first_binding
    )
    assert replay_outcome != "CONSEQUENCE_FORMED"
    assert replay_receipt.consequence_formed is False
    assert replay_receipt.authority_receipt_id == first_receipt.receipt_id
    assert replay_receipt.action_binding_hash == first_binding
    assert verify_consequence_outcome_receipt(replay_receipt)

    # Prepare a second valid permit under current authority, but do not consume it yet.
    _, stale_receipt, stale_attempt, stale_permit, stale_binding = _fresh_allow_and_permit()
    old_version = get_authority_state_version()
    assert stale_receipt.authority_state_version == old_version
    assert stale_permit.authority_state_version == old_version

    # Attack 2 — authority changes after permit issuance.
    new_version = advance_authority_state_version()
    assert new_version == old_version + 1

    stale_outcome, stale_outcome_receipt = execute_protected_consequence_with_receipt(
        stale_permit, stale_binding
    )
    assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE"
    assert stale_outcome_receipt.consequence_formed is False
    assert stale_outcome_receipt.authority_receipt_id == stale_receipt.receipt_id
    assert stale_outcome_receipt.action_binding_hash == stale_binding
    assert verify_consequence_outcome_receipt(stale_outcome_receipt)

    # Attack 3 — direct invocation does not bypass the stale-state check.
    direct_stale = execute_protected_consequence(stale_permit, stale_binding)
    assert direct_stale == "DENIED_AUTHORITY_STATE_STALE"

    # Attack 4 — exact-action substitution at consequence formation.
    substituted_beneficiary = replace(stale_attempt, beneficiary="ATTACKER-BENEFICIARY")
    beneficiary_binding = action_binding_hash(substituted_beneficiary)
    assert beneficiary_binding != stale_binding
    beneficiary_outcome = execute_protected_consequence(stale_permit, beneficiary_binding)
    assert beneficiary_outcome == "DENIED_ACTION_BINDING_MISMATCH"

    substituted_amount = replace(stale_attempt, amount=stale_attempt.amount + 1)
    amount_binding = action_binding_hash(substituted_amount)
    assert amount_binding != stale_binding
    amount_outcome = execute_protected_consequence(stale_permit, amount_binding)
    assert amount_outcome == "DENIED_ACTION_BINDING_MISMATCH"

    # Fresh current-state re-authorisation for the same attempted consequence.
    _, fresh_receipt, fresh_attempt, fresh_permit, fresh_binding = _fresh_allow_and_permit()
    assert fresh_binding == stale_binding
    assert fresh_receipt.receipt_id != stale_receipt.receipt_id
    assert fresh_receipt.authority_state_version == new_version
    assert fresh_permit.authority_state_version == new_version
    assert fresh_permit.signature != stale_permit.signature

    # Attack 5 — historical stale permit remains dead even after fresh authority exists.
    historical_replay = execute_protected_consequence(stale_permit, stale_binding)
    assert historical_replay == "DENIED_AUTHORITY_STATE_STALE"

    # Positive control after attacks: current exact-action permit still forms.
    final_outcome, final_receipt = execute_protected_consequence_with_receipt(
        fresh_permit, fresh_binding
    )
    assert final_outcome == "CONSEQUENCE_FORMED"
    assert final_receipt.consequence_formed is True
    assert final_receipt.authority_receipt_id == fresh_receipt.receipt_id
    assert final_receipt.action_binding_hash == fresh_binding
    assert verify_consequence_outcome_receipt(final_receipt)
