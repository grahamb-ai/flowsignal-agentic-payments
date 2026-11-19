"""Bounded full-path institutional authorization: gateway -> adapter -> provider."""
from pathlib import Path
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from app.engines.external_consequence_adapter import execute_external_payment, _external_payload
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
from external_targets.cbp002_consequence_service import ExternalLedger
from harness.runner import load_scenario
from tests.provider_signed_fixture import issuer, signed_payment


def test_signed_institutional_instruction_crosses_actual_adapter(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE", str(tmp_path / "permits.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE", str(tmp_path / "outcomes.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_ROLLBACK_ANCHOR_STORE", str(tmp_path / "anchors.sqlite3"))
    req = load_scenario(Path("harness/scenarios/AP-001_allow.json"))
    decision, receipt = evaluate_financial(req)
    assert decision.decision == "ALLOW"
    attempt = ExecutionAttempt(
        actor_id=req.actor_id, principal_id=req.principal_id,
        action=req.action, target=req.target, amount=req.amount,
        currency=req.currency, source_account=req.source_account,
        beneficiary=req.beneficiary, purpose=req.purpose,
        mandate_id=req.mandate_id, attempted_at=req.requested_execution_time)
    permit_result = validate_execution(
        receipt, attempt, payment_intent_id="institution-signed-intent-001",
        provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert permit_result.status == "PERMITTED"
    permit = permit_result.execution_permit
    key = issuer()
    fence = ProviderCommitFence(tmp_path / "provider.sqlite3")
    fence.establish(attempt.mandate_id, epoch=1)
    provider = ExternalLedger(fence=fence, mandate_id=attempt.mandate_id,
                              authority_epoch=1, authorization_public_key=key.public_key())
    instruction = signed_payment(key, _external_payload(attempt, permit))
    observed = []
    def post(url, payload, timeout_seconds):
        observed.append(payload)
        status, result = provider.transfer(payload)
        return result
    from app.engines import external_consequence_adapter
    monkeypatch.setattr(external_consequence_adapter, "_post_json", post)
    result, _ = execute_external_payment(
        permit=permit, attempt=attempt, payments_url="http://reference-provider.invalid/payments",
        institutional_authorization=instruction["institutional_authorization"])
    assert result == "CONSEQUENCE_FORMED"
    assert len(observed) == 1
    assert fence.transfer_count() == 1
    assert observed[0]["institutional_authorization"] == instruction["institutional_authorization"]
