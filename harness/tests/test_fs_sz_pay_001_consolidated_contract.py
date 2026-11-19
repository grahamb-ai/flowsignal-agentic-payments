"""Consolidated contract acceptance: actual adapter must carry authenticated intent/epoch.

Failure-first tests are deliberately retained until issuer, gateway and provider
implement one coherent binding. Do not replace business intent with permit signature
or provider epoch with FlowSignal's local authority_state_version.
"""
from dataclasses import replace
from pathlib import Path

from app.engines.external_consequence_adapter import _external_payload
from app.engines.execution_gateway import ExecutionAttempt, validate_execution
from app.engines.financial_runtime import evaluate_financial
from harness.runner import load_scenario


def _issued_payment():
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
    gateway = validate_execution(receipt, attempt, payment_intent_id='institution-intent-001', provider_authority_epoch=1, provider_mandate_id=attempt.mandate_id)
    assert gateway.status == "PERMITTED"
    return attempt, gateway.execution_permit


def test_adapter_payment_contains_explicit_mandate_and_provider_epoch():
    attempt, permit = _issued_payment()
    payload = _external_payload(attempt, permit)
    assert payload.get("mandate_id") == attempt.mandate_id
    assert isinstance(payload.get("authority_epoch"), int)
    assert payload["authority_epoch"] > 0


def test_payment_intent_is_not_permit_signature_and_survives_new_permit():
    attempt, permit = _issued_payment()
    payload = _external_payload(attempt, permit)
    assert payload.get("payment_intent_id")
    assert payload["payment_intent_id"] != permit.signature
    # Issuer must bind the identity, not derive it from mutable HTTP parameters.
    assert getattr(permit, "payment_intent_id", None) == payload["payment_intent_id"]
    assert getattr(permit, "provider_authority_epoch", None) == payload["authority_epoch"]


def test_signed_intent_and_epoch_tampering_invalidates_permit():
    from app.engines.permit_authority import verify_execution_permit
    attempt, permit = _issued_payment()
    assert verify_execution_permit(permit)
    assert not verify_execution_permit(replace(permit, payment_intent_id="attacker-intent"))
    assert not verify_execution_permit(replace(permit, provider_authority_epoch=2))
    assert not verify_execution_permit(replace(permit, provider_mandate_id="OTHER-MANDATE"))
