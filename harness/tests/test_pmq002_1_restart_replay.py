"""PMQ-002.1 failure-first restart replay challenge.

Frozen proposition:
An execution permit that has already been consumed MUST NOT be capable of
forming a second represented consequence after process restart.

Challenge record:
`evidence/PMQ-002/PMQ-002.1_RESTART_REPLAY_CHALLENGE.md`

If this test fails because process-local replay state is lost on restart,
preserve the failure before remediation. Do not weaken the proposition or
change the test semantics to make the current implementation pass.
"""

import importlib
from pathlib import Path

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
import app.engines.protected_consequence as protected_consequence
from harness.runner import load_scenario


def _valid_permit_and_binding():
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


def test_pmq002_1_consumed_permit_cannot_form_second_consequence_after_restart():
    permit, binding = _valid_permit_and_binding()

    first = protected_consequence.execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    assert first == "CONSEQUENCE_FORMED"

    # Represent restart by reloading the execution component. This deliberately
    # discards module-local memory while retaining the exact previously issued
    # permit and exact action binding presented by the caller.
    restarted_component = importlib.reload(protected_consequence)

    second = restarted_component.execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )

    assert second != "CONSEQUENCE_FORMED", (
        "PMQ-002.1 FAILURE: an execution permit already consumed before the "
        "represented restart formed a second represented consequence after "
        "process-local replay state was lost"
    )
