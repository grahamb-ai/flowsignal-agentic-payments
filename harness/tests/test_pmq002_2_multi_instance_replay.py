"""PMQ-002.2 failure-first multi-instance replay challenge.

Frozen proposition:
When two represented executor instances share the same durable permit-consumption
store, the exact same valid execution permit MUST NOT form more than one
represented consequence under concurrent presentation.

If more than one worker returns CONSEQUENCE_FORMED, preserve the failure before
remediation and do not weaken the test semantics.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
from pathlib import Path

from app.engines.execution_gateway import ExecutionAttempt, action_binding_hash, validate_execution
from app.engines.financial_runtime import evaluate_financial
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


def _worker(start_event, result_queue, permit_payload, binding, store_path):
    os.environ["FLOWSIGNAL_PERMIT_CONSUMPTION_STORE"] = store_path

    # Import inside each worker so each process owns an independent Python
    # execution component while sharing only the configured durable store.
    from app.engines.permit_authority import ExecutionPermit
    from app.engines.protected_consequence import execute_protected_consequence

    permit = ExecutionPermit(**json.loads(permit_payload))
    start_event.wait(timeout=5.0)
    outcome = execute_protected_consequence(
        permit=permit,
        attempted_action_binding_hash=binding,
    )
    result_queue.put(outcome)


def test_pmq002_2_same_permit_cannot_form_multiple_consequences_across_two_processes(tmp_path):
    permit, binding = _valid_permit_and_binding()
    store_path = str(tmp_path / "shared-permit-consumption.sqlite3")

    permit_payload = json.dumps(
        {
            "authority_receipt_id": permit.authority_receipt_id,
            "action_binding_hash": permit.action_binding_hash,
            "authority_state_version": permit.authority_state_version,
            "issued_at": permit.issued_at,
            "signature": permit.signature,
            "valid_until": permit.valid_until,
        }
    )

    ctx = mp.get_context("spawn")
    start_event = ctx.Event()
    result_queue = ctx.Queue()

    workers = [
        ctx.Process(
            target=_worker,
            args=(start_event, result_queue, permit_payload, binding, store_path),
        )
        for _ in range(2)
    ]

    for worker in workers:
        worker.start()

    start_event.set()

    results = [result_queue.get(timeout=10.0) for _ in workers]

    for worker in workers:
        worker.join(timeout=10.0)
        assert worker.exitcode == 0

    assert results.count("CONSEQUENCE_FORMED") == 1, (
        "PMQ-002.2 FAILURE: the exact same execution permit formed more than "
        "one represented consequence when raced across two executor processes"
    )
