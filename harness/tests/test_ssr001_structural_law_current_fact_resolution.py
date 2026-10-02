"""SSR-001: fixed structural law, current fact resolution, path reachability."""

from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from app.engines.action_binding import action_binding_hash
from app.engines.authority_store import (
    AUTHORITATIVE_MANDATES,
    advance_authority_state_version,
)
from app.engines.consequence_receipt import verify_consequence_outcome_receipt
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import (
    execute_protected_consequence,
    execute_protected_consequence_with_receipt,
)
from harness.runner import issue_initial_generation, load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"


def _isolate_stores(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "FLOWSIGNAL_CANDIDATE_LIFECYCLE_STORE",
        str(tmp_path / "candidate-lifecycle.sqlite3"),
    )
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


def _resolve_path(req):
    response, receipt = evaluate_financial(req)
    attempt = _attempt(req)
    gateway = validate_execution(receipt, attempt)
    return response, receipt, attempt, gateway


def test_fixed_structure_excludes_known_invalid_but_preserves_valid_liveness(
    tmp_path,
    monkeypatch,
):
    _isolate_stores(tmp_path, monkeypatch)

    structural_law = AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"]
    assert structural_law.actions == ("payment.release",)

    template = load_scenario(SCENARIO)
    known_invalid = issue_initial_generation(
        replace(
            template,
            candidate_generation_id="PENDING_AUTHORITY_ISSUANCE",
            action="DELETE_ACCOUNT",
        )
    )
    invalid_response, invalid_receipt, _, invalid_gateway = _resolve_path(known_invalid)
    assert invalid_response.decision == "REFUSE"
    assert any(
        check.name == "action_permitted" and check.passed is False
        for check in invalid_receipt.checks
    )
    assert invalid_gateway.status == "BLOCKED"
    assert invalid_gateway.execution_permit is None

    valid = load_scenario(SCENARIO)
    valid_response, _, valid_attempt, valid_gateway = _resolve_path(valid)
    assert valid_response.decision == "ALLOW"
    assert valid_gateway.status == "PERMITTED"
    assert valid_gateway.execution_permit is not None
    assert (
        execute_protected_consequence(
            valid_gateway.execution_permit,
            action_binding_hash(valid_attempt),
        )
        == "CONSEQUENCE_FORMED"
    )

    # Runtime resolution did not rewrite what the mandate means.
    assert AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"] == structural_law


def test_current_fact_change_removes_old_path_and_fresh_resolution_can_restore_it(
    tmp_path,
    monkeypatch,
):
    _isolate_stores(tmp_path, monkeypatch)

    structural_law = AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"]
    historical = load_scenario(SCENARIO)
    historical_response, historical_receipt, historical_attempt, historical_gateway = (
        _resolve_path(historical)
    )
    assert historical_response.decision == "ALLOW"
    assert historical_gateway.execution_permit is not None
    historical_permit = historical_gateway.execution_permit
    historical_binding = action_binding_hash(historical_attempt)

    new_state = advance_authority_state_version()
    assert new_state != historical_permit.authority_state_version

    stale_outcome, stale_receipt = execute_protected_consequence_with_receipt(
        historical_permit,
        historical_binding,
    )
    assert stale_outcome == "DENIED_AUTHORITY_STATE_STALE"
    assert stale_receipt.consequence_formed is False
    assert stale_receipt.authority_receipt_id == historical_receipt.id
    assert verify_consequence_outcome_receipt(stale_receipt)

    fresh = load_scenario(SCENARIO)
    fresh_response, fresh_receipt, fresh_attempt, fresh_gateway = _resolve_path(fresh)
    assert fresh_response.decision == "ALLOW"
    assert fresh_gateway.execution_permit is not None
    fresh_permit = fresh_gateway.execution_permit
    assert fresh_receipt.id != historical_receipt.id
    assert fresh_permit.authority_state_version == new_state
    assert fresh_permit.signature != historical_permit.signature
    assert action_binding_hash(fresh_attempt) == historical_binding
    assert (
        execute_protected_consequence(fresh_permit, historical_binding)
        == "CONSEQUENCE_FORMED"
    )

    # The historical edge remains absent after a fresh current-state edge exists.
    assert (
        execute_protected_consequence(historical_permit, historical_binding)
        == "DENIED_AUTHORITY_STATE_STALE"
    )
    assert AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"] == structural_law


def test_expiry_and_consumption_remove_path_under_fixed_rules(tmp_path, monkeypatch):
    _isolate_stores(tmp_path, monkeypatch)

    structural_law = AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"]
    template = load_scenario(SCENARIO)
    expired = issue_initial_generation(
        replace(
            template,
            candidate_generation_id="PENDING_AUTHORITY_ISSUANCE",
            mandate_valid_until=template.requested_execution_time - timedelta(microseconds=1),
        )
    )
    expired_response, expired_receipt, _, expired_gateway = _resolve_path(expired)
    assert expired_response.decision == "REFUSE"
    assert any(
        check.name == "mandate_not_expired" and check.passed is False
        for check in expired_receipt.checks
    )
    assert expired_gateway.execution_permit is None

    valid = load_scenario(SCENARIO)
    valid_response, _, valid_attempt, valid_gateway = _resolve_path(valid)
    assert valid_response.decision == "ALLOW"
    permit = valid_gateway.execution_permit
    binding = action_binding_hash(valid_attempt)
    assert execute_protected_consequence(permit, binding) == "CONSEQUENCE_FORMED"
    assert (
        execute_protected_consequence(permit, binding)
        == "DENIED_EXECUTION_PERMIT_REPLAY"
    )
    assert AUTHORITATIVE_MANDATES["MANDATE-TREASURY-001"] == structural_law
