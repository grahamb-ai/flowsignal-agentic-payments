"""Integrated concurrent revocation/commit qualification (cooperating reference provider).

The provider's SQLite transaction defines the linearisation order. The
independent revocation actor does NOT update FlowSignal's process-local guard.
"""
import threading
from pathlib import Path

from app.engines import external_consequence_adapter
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from harness.runner import load_scenario


def _attempt_and_permit():
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision, receipt = evaluate_financial(req)
    assert decision.decision == "ALLOW"
    attempt = ExecutionAttempt(
        actor_id=req.actor_id, principal_id=req.principal_id,
        action=req.action, target=req.target, amount=req.amount,
        currency=req.currency, source_account=req.source_account,
        beneficiary=req.beneficiary, purpose=req.purpose,
        mandate_id=req.mandate_id, attempted_at=req.requested_execution_time,
    )
    gateway = validate_execution(receipt, attempt, payment_intent_id='institution-payment-intent-001', provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert gateway.status == "PERMITTED"
    assert gateway.execution_permit is not None
    return attempt, gateway.execution_permit


def test_integrated_concurrent_revocation_commit_has_valid_order(tmp_path, monkeypatch):
    # Multiple independent rounds, each with separate durable provider state.
    # This is a bounded race test, not exhaustive scheduling verification.
    for i in range(20):
        root = tmp_path / str(i)
        root.mkdir()
        monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(root / "permits.sqlite3"))
        monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(root / "outcomes.sqlite3"))
        monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(root / "anchors.sqlite3"))
        attempt, permit = _attempt_and_permit()
        provider = ProviderCommitFence(root / "provider.sqlite3")
        provider.establish(attempt.mandate_id, epoch=1)

        barrier = threading.Barrier(2, timeout=5)
        seen = {}
        errors = []

        def post(url, payload, timeout_seconds):
            barrier.wait()
            status = provider.commit(attempt.mandate_id, 1, payload["transaction_id"])
            seen["provider_status"] = status
            return {"status": status}

        monkeypatch.setattr(external_consequence_adapter, "_post_json", post)

        def execute():
            try:
                result, _ = external_consequence_adapter.execute_external_payment(
                    permit=permit, attempt=attempt,
                    payments_url="http://cooperating-provider.invalid/payments",
                )
                seen["flowsignal_outcome"] = result
            except Exception as exc:
                errors.append(repr(exc))

        def revoke():
            try:
                barrier.wait()
                provider.revoke(attempt.mandate_id)
            except Exception as exc:
                errors.append(repr(exc))

        threads = [threading.Thread(target=execute), threading.Thread(target=revoke)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
            assert not thread.is_alive()
        assert not errors, errors

        status = seen["provider_status"]
        assert status in ("COMMITTED", "REFUSED_AUTHORITY")
        assert seen["flowsignal_outcome"] == (
            "CONSEQUENCE_FORMED" if status == "COMMITTED"
            else "DENIED_PROVIDER_COMMIT_REFUSED"
        )
        assert provider.count() == (1 if status == "COMMITTED" else 0)
        assert provider.commit(attempt.mandate_id, 1, "later-intent") == "REFUSED_AUTHORITY"
