"""PMQ-001 failure-first duplicate/retry/concurrency challenge.

The frozen challenge is recorded in:
`evidence/PMQ-001/PMQ-001_DUPLICATE_RETRY_CHALLENGE.md`

If either test fails because the same permit can form more than one represented
consequence, preserve that failure before remediation. Do not weaken the tests.
"""

from pathlib import Path
from threading import Barrier, Lock, Thread

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.protected_consequence import execute_protected_consequence
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


def test_pmq001_same_execution_permit_cannot_form_consequence_twice_sequentially():
    permit, binding = _valid_permit_and_binding()

    first = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    second = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )

    assert first == "CONSEQUENCE_FORMED"
    assert second != "CONSEQUENCE_FORMED", (
        "PMQ-001 FAILURE: exact same execution permit formed the represented "
        "consequence more than once under sequential replay"
    )


def test_pmq001_same_execution_permit_cannot_form_multiple_consequences_concurrently():
    permit, binding = _valid_permit_and_binding()
    start = Barrier(3)
    results = []
    results_lock = Lock()

    def execute_once():
        start.wait(timeout=2.0)
        result = execute_protected_consequence(
            permit=permit,
            attempted_action_binding_hash=binding,
        )
        with results_lock:
            results.append(result)

    threads = [Thread(target=execute_once), Thread(target=execute_once)]
    for thread in threads:
        thread.start()

    start.wait(timeout=2.0)
    for thread in threads:
        thread.join(timeout=2.0)

    assert len(results) == 2
    assert results.count("CONSEQUENCE_FORMED") == 1, (
        "PMQ-001 FAILURE: concurrent replay of one execution permit formed "
        "more than one represented consequence"
    )
