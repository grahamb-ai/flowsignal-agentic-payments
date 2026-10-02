"""SCB-002 frozen known-invalid consequence-unreachability challenge.

This challenge is intentionally separate from SCB-001.

SCB-001 asks the stronger structural question: should an authority-bearing
candidate identity be issued at all when invalidity is already knowable?

SCB-002 assumes that such a candidate exists and tests the narrower claim:
within the declared reference-MVP transition surface, no supported sequence
may convert that known-invalid candidate, its receipt, a substituted valid
receipt, a successor generation, retry, replay, or condition restoration into
an execution permit or protected consequence.

The paired liveness assertion requires a valid candidate to retain a route to
exactly one protected consequence.  This prevents route closure being claimed
by disabling consequence formation altogether.
"""

from dataclasses import replace
from pathlib import Path

from app.engines.action_binding import action_binding_hash
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.permit_authority import issue_execution_permit
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import (
    issue_initial_generation,
    issue_successor_generation,
    load_scenario,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCENARIO = REPOSITORY_ROOT / "harness/harness/scenarios/AP-001_allow.json"


def _attempt(req, *, action: str | None = None) -> ExecutionAttempt:
    return ExecutionAttempt(
        actor_id=req.actor_id,
        principal_id=req.principal_id,
        action=action or req.action,
        target=req.target,
        amount=req.amount,
        currency=req.currency,
        source_account=req.source_account,
        beneficiary=req.beneficiary,
        purpose=req.purpose,
        mandate_id=req.mandate_id,
        attempted_at=req.requested_execution_time,
    )


def _isolated_runtime_stores(tmp_path, monkeypatch) -> None:
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


def test_known_invalid_candidate_has_no_supported_route_to_consequence(
    tmp_path,
    monkeypatch,
):
    _isolated_runtime_stores(tmp_path, monkeypatch)

    # Establish an authority-issued candidate whose action is already known to
    # be outside the authoritative payment mandate.  SCB-001 separately records
    # that issuing this identity is itself a structural-closure failure.
    template = load_scenario(SCENARIO)
    known_invalid = issue_initial_generation(
        replace(
            template,
            candidate_generation_id="PENDING_AUTHORITY_ISSUANCE",
            action="DELETE_ACCOUNT",
        )
    )
    invalid_hash = action_binding_hash(known_invalid)

    # Route 1: ordinary evaluation cannot create ALLOW or a usable gateway path.
    invalid_response, invalid_receipt = evaluate_financial(known_invalid)
    assert invalid_response.decision == "REFUSE"
    assert invalid_receipt is not None
    invalid_gateway = validate_execution(invalid_receipt, _attempt(known_invalid))
    assert invalid_gateway.status == "BLOCKED"
    assert invalid_gateway.execution_permit is None

    # Route 2: the public permit issuer cannot be used without the private
    # gateway capability, even when all permit fields are supplied.
    caller_minted = issue_execution_permit(
        authority_receipt_id=invalid_receipt.id,
        candidate_generation_id=known_invalid.candidate_generation_id,
        action_binding_hash=invalid_hash,
        authority_state_version=invalid_receipt.authority_state_version,
        valid_until=known_invalid.requested_execution_time.isoformat(),
        mint_capability=object(),
    )
    assert caller_minted is None
    assert (
        execute_protected_consequence(caller_minted, invalid_hash)
        == "DENIED_NO_EXECUTION_PERMIT"
    )

    # Route 3: a genuine ALLOW receipt for a valid movement cannot be
    # transplanted onto the known-invalid action at the execution boundary.
    valid = load_scenario(SCENARIO)
    valid_response, valid_receipt = evaluate_financial(valid)
    assert valid_response.decision == "ALLOW"
    assert valid_receipt is not None

    substituted_attempt = _attempt(valid, action="DELETE_ACCOUNT")
    substituted_gateway = validate_execution(valid_receipt, substituted_attempt)
    assert substituted_gateway.status == "BLOCKED"
    assert substituted_gateway.reason_code == "ACTION_BINDING_MISMATCH"
    assert substituted_gateway.execution_permit is None

    # Route 4: even a genuine permit for the valid action cannot be replayed as
    # the invalid action at protected consequence formation.
    valid_gateway = validate_execution(valid_receipt, _attempt(valid))
    assert valid_gateway.status == "PERMITTED"
    assert valid_gateway.execution_permit is not None
    assert (
        execute_protected_consequence(
            valid_gateway.execution_permit,
            action_binding_hash(substituted_attempt),
        )
        == "DENIED_ACTION_BINDING_MISMATCH"
    )

    # Route 5: retrying through an authority-issued successor preserves the
    # same invalid action binding and remains unable to acquire ALLOW/permit.
    invalid_successor = issue_successor_generation(known_invalid)
    successor_response, successor_receipt = evaluate_financial(invalid_successor)
    assert successor_response.decision == "REFUSE"
    assert successor_receipt is not None
    successor_gateway = validate_execution(
        successor_receipt,
        _attempt(invalid_successor),
    )
    assert successor_gateway.status == "BLOCKED"
    assert successor_gateway.execution_permit is None

    # Route 6: changing the successor into a valid-looking action changes its
    # binding.  Its existing candidate identity was never authority-issued for
    # that new binding, so "restoration" cannot manufacture ALLOW.
    rebound_successor = replace(invalid_successor, action=valid.action)
    rebound_response, rebound_receipt = evaluate_financial(rebound_successor)
    assert rebound_response.decision == "REFUSE"
    assert rebound_receipt is not None
    rebound_gateway = validate_execution(
        rebound_receipt,
        _attempt(rebound_successor),
    )
    assert rebound_gateway.status == "BLOCKED"
    assert rebound_gateway.execution_permit is None


def test_valid_candidate_retains_exactly_bound_consequence_route(
    tmp_path,
    monkeypatch,
):
    _isolated_runtime_stores(tmp_path, monkeypatch)

    valid = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(valid)
    assert response.decision == "ALLOW"
    assert receipt is not None

    attempt = _attempt(valid)
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    assert (
        execute_protected_consequence(
            gateway.execution_permit,
            action_binding_hash(attempt),
        )
        == "CONSEQUENCE_FORMED"
    )

    # The same exact route is one-shot rather than a reusable consequential edge.
    assert (
        execute_protected_consequence(
            gateway.execution_permit,
            action_binding_hash(attempt),
        )
        == "DENIED_EXECUTION_PERMIT_REPLAY"
    )
