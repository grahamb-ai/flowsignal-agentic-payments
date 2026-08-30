"""VPC-001.3 — Cross-Department Resource Collision Loop.

Frozen challenge derived from Vadym Partasyuk's public scenario:
Department A needs X, treats Y as surplus and proposes disposing Y to acquire X.
Department B needs Y, treats X as surplus and proposes disposing X to acquire Y.
Each action can be locally authorised in isolation while the pair is globally
contradictory.

This test deliberately separates two propositions:
1. WITHOUT a represented shared/correlated-conflict condition, the existing
   runtime is not credited with discovering the semantic contradiction itself.
2. ONCE that material conflict is represented as a newer authoritative state,
   a permit issued against the previous state MUST NOT form its protected
   consequence.

It does not claim universal semantic reasoning or cross-workflow discovery.
"""

from pathlib import Path

from app.engines.authority_store import advance_authority_state_version
from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
from harness.runner import load_scenario


def _fresh_permit():
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
    gateway = validate_execution(receipt, attempt)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    return gateway.execution_permit, action_binding_hash(attempt)


def test_vpc001_3_cross_workflow_conflict_requires_authoritative_signal_then_stale_permit_is_denied():
    # Department A and Department B can each obtain a locally valid permit while
    # no shared semantic/collision condition is represented in authoritative state.
    permit_a, binding_a = _fresh_permit()
    permit_b, binding_b = _fresh_permit()
    assert permit_a.authority_state_version == permit_b.authority_state_version

    # The current implementation is NOT credited with autonomously inferring that
    # the two business intents form a circular semantic contradiction.  The
    # conflict becomes enforceable only when represented as authoritative state.
    result_a = execute_protected_consequence(
        permit=permit_a,
        attempted_action_binding_hash=binding_a,
    )
    assert result_a == "CONSEQUENCE_FORMED"

    # Represent discovery/commit of the cross-department collision as a material
    # authoritative-state change before Department B reaches its protected bind.
    new_version = advance_authority_state_version()
    assert new_version != permit_b.authority_state_version

    result_b = execute_protected_consequence(
        permit=permit_b,
        attempted_action_binding_hash=binding_b,
    )
    assert result_b == "DENIED_AUTHORITY_STATE_STALE", (
        "VPC-001.3 FAILURE: a locally valid but now-conflicting second action "
        "formed a consequence after the cross-workflow conflict was represented "
        "as newer authoritative state"
    )
