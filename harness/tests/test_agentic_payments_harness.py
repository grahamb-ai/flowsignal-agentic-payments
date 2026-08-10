from pathlib import Path
from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "harness" / "scenarios" / "AP-001_allow.json"

def test_ap001_all_required_conditions_are_evaluated_and_allow():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "ALLOW"
    assert response.reason_code == "AUTHORITY_ESTABLISHED"
    assert response.authority_receipt_id == receipt.id
    assert receipt.action_binding_hash
    assert receipt.valid_until is not None

    expected = {
        "actor_authenticated","kya_verified","mandate_active","mandate_not_expired",
        "action_permitted","amount_within_limit","currency_permitted",
        "source_account_permitted","counterparty_approved","account_active",
        "risk_state_permits_execution","screening_clear","screening_fresh",
    }
    assert {c.name for c in receipt.checks} == expected
    assert all(c.passed for c in receipt.checks)

def test_execution_response_is_bounded_relative_to_receipt():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)
    assert not hasattr(response, "checks")
    assert not hasattr(response, "request_snapshot")
    assert not hasattr(response, "evidence_references")
    assert receipt.checks and receipt.request_snapshot and receipt.evidence_references


AP002 = ROOT / "harness" / "scenarios" / "AP-002_limit_escalate.json"

def test_ap002_same_trusted_agent_limit_exceeded_escalates():
    request = load_scenario(AP002)
    response, receipt = evaluate_financial(request)

    assert request.actor_id == "agent-treasury-01"
    assert request.actor_authenticated is True
    assert request.kya_status == "VERIFIED"

    assert response.decision == "ESCALATE"
    assert response.reason_code == "ADDITIONAL_AUTHORITY_OR_EVIDENCE_REQUIRED"
    assert response.valid_until is None
    assert receipt.decision == "ESCALATE"

    failed = [c for c in receipt.checks if not c.passed]
    assert len(failed) == 1
    assert failed[0].name == "amount_within_limit"
    assert failed[0].outcome_on_failure == "ESCALATE"

    passed = {c.name for c in receipt.checks if c.passed}
    assert "actor_authenticated" in passed
    assert "kya_verified" in passed
    assert "mandate_active" in passed
    assert "screening_clear" in passed
    assert "screening_fresh" in passed

def test_ap001_and_ap002_differ_only_in_proposed_amount():
    ap1 = load_scenario(SCENARIO)
    ap2 = load_scenario(AP002)

    # Central proposition: same trusted actor / mandate / context; different action value.
    assert ap1.actor_id == ap2.actor_id
    assert ap1.actor_authenticated == ap2.actor_authenticated
    assert ap1.kya_status == ap2.kya_status
    assert ap1.mandate_id == ap2.mandate_id
    assert ap1.source_account == ap2.source_account
    assert ap1.beneficiary == ap2.beneficiary
    assert ap1.counterparty_status == ap2.counterparty_status
    assert ap1.screening_status == ap2.screening_status

    assert ap1.amount == 750000
    assert ap2.amount == 1400000


AP003 = ROOT / "harness" / "scenarios" / "AP-003_post_approval_counterparty_change.json"

def test_ap003_post_approval_counterparty_change_refuses():
    request = load_scenario(AP003)
    response, receipt = evaluate_financial(request)

    # Same trusted actor and same action value as the positive control.
    assert request.actor_id == "agent-treasury-01"
    assert request.actor_authenticated is True
    assert request.kya_status == "VERIFIED"
    assert request.amount == 750000
    assert request.mandate_id == "MANDATE-TREASURY-001"

    # Current counterparty state is the material change.
    assert request.counterparty_status == "RESTRICTED"

    assert response.decision == "REFUSE"
    assert response.reason_code == "AUTHORITY_NOT_ESTABLISHED"
    assert response.valid_until is None
    assert receipt.decision == "REFUSE"

    failed = [c for c in receipt.checks if not c.passed]
    assert len(failed) == 1
    assert failed[0].name == "counterparty_approved"
    assert failed[0].outcome_on_failure == "REFUSE"

def test_ap001_and_ap003_share_action_but_current_context_changes():
    ap1 = load_scenario(SCENARIO)
    ap3 = load_scenario(AP003)

    assert ap1.actor_id == ap3.actor_id
    assert ap1.actor_authenticated == ap3.actor_authenticated
    assert ap1.kya_status == ap3.kya_status
    assert ap1.mandate_id == ap3.mandate_id
    assert ap1.amount == ap3.amount == 750000
    assert ap1.currency == ap3.currency == "GBP"
    assert ap1.source_account == ap3.source_account
    assert ap1.beneficiary == ap3.beneficiary
    assert ap1.screening_status == ap3.screening_status == "CLEAR"

    assert ap1.counterparty_status == "APPROVED"
    assert ap3.counterparty_status == "RESTRICTED"


AP004 = ROOT / "harness" / "scenarios" / "AP-004_stale_screening_evidence.json"

def test_ap004_clear_but_stale_screening_escalates():
    request = load_scenario(AP004)
    response, receipt = evaluate_financial(request)

    # Trust facts remain valid.
    assert request.actor_id == "agent-treasury-01"
    assert request.actor_authenticated is True
    assert request.kya_status == "VERIFIED"
    assert request.amount == 750000
    assert request.screening_status == "CLEAR"

    assert response.decision == "ESCALATE"
    assert response.reason_code == "ADDITIONAL_AUTHORITY_OR_EVIDENCE_REQUIRED"
    assert response.valid_until is None
    assert receipt.decision == "ESCALATE"

    failed = [c for c in receipt.checks if not c.passed]
    assert len(failed) == 1
    assert failed[0].name == "screening_fresh"
    assert failed[0].outcome_on_failure == "ESCALATE"

    evidence = receipt.evidence_references[0]
    assert evidence["status"] == "CLEAR"
    assert evidence["age_seconds"] == 8100
    assert evidence["max_age_seconds"] == 3600

def test_ap001_and_ap004_differ_only_in_screening_capture_time():
    ap1 = load_scenario(SCENARIO)
    ap4 = load_scenario(AP004)

    assert ap1.actor_id == ap4.actor_id
    assert ap1.actor_authenticated == ap4.actor_authenticated
    assert ap1.kya_status == ap4.kya_status
    assert ap1.mandate_id == ap4.mandate_id
    assert ap1.amount == ap4.amount == 750000
    assert ap1.currency == ap4.currency
    assert ap1.source_account == ap4.source_account
    assert ap1.beneficiary == ap4.beneficiary
    assert ap1.counterparty_status == ap4.counterparty_status == "APPROVED"
    assert ap1.screening_status == ap4.screening_status == "CLEAR"

    assert ap1.screening_captured_at != ap4.screening_captured_at
    assert ap1.screening_max_age_seconds == ap4.screening_max_age_seconds == 3600


AP005 = ROOT / "harness" / "scenarios" / "AP-005_expired_mandate.json"

def test_ap005_expired_mandate_refuses():
    request = load_scenario(AP005)
    response, receipt = evaluate_financial(request)

    # Trust establishment still succeeds.
    assert request.actor_id == "agent-treasury-01"
    assert request.actor_authenticated is True
    assert request.kya_status == "VERIFIED"
    assert request.amount == 750000
    assert request.counterparty_status == "APPROVED"
    assert request.screening_status == "CLEAR"

    assert response.decision == "REFUSE"
    assert response.reason_code == "AUTHORITY_NOT_ESTABLISHED"
    assert response.valid_until is None
    assert receipt.decision == "REFUSE"

    failed = [c for c in receipt.checks if not c.passed]
    assert len(failed) == 1
    assert failed[0].name == "mandate_not_expired"
    assert failed[0].outcome_on_failure == "REFUSE"

def test_ap001_and_ap005_differ_only_in_mandate_expiry():
    ap1 = load_scenario(SCENARIO)
    ap5 = load_scenario(AP005)

    assert ap1.actor_id == ap5.actor_id
    assert ap1.actor_authenticated == ap5.actor_authenticated
    assert ap1.kya_status == ap5.kya_status
    assert ap1.mandate_id == ap5.mandate_id
    assert ap1.amount == ap5.amount == 750000
    assert ap1.currency == ap5.currency == "GBP"
    assert ap1.source_account == ap5.source_account
    assert ap1.beneficiary == ap5.beneficiary
    assert ap1.counterparty_status == ap5.counterparty_status == "APPROVED"
    assert ap1.screening_status == ap5.screening_status == "CLEAR"

    assert ap1.mandate_valid_until != ap5.mandate_valid_until
    assert ap5.mandate_valid_until < ap5.requested_execution_time


from datetime import datetime
from app.engines.execution_gateway import ExecutionAttempt, validate_execution

def test_ap006_substituted_beneficiary_is_blocked_by_execution_gateway():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)

    # Runtime Authority genuinely allowed Supplier X.
    assert response.decision == "ALLOW"
    assert request.beneficiary == "SUPPLIER-X"

    # Execution path is altered after the authority determination.
    attempt = ExecutionAttempt(
        actor_id=request.actor_id,
        principal_id=request.principal_id,
        action=request.action,
        target=request.target,
        amount=request.amount,
        currency=request.currency,
        source_account=request.source_account,
        beneficiary="SUPPLIER-Y",
        purpose=request.purpose,
        mandate_id=request.mandate_id,
        attempted_at=datetime.fromisoformat("2026-08-10T09:15:30+00:00"),
    )

    result = validate_execution(receipt, attempt)

    assert result.status == "BLOCKED"
    assert result.reason_code == "ACTION_BINDING_MISMATCH"
    assert result.expected_action_binding_hash != result.attempted_action_binding_hash


def test_execution_gateway_permits_exact_action_bound_to_allow():
    request = load_scenario(SCENARIO)
    response, receipt = evaluate_financial(request)
    assert response.decision == "ALLOW"

    attempt = ExecutionAttempt(
        actor_id=request.actor_id,
        principal_id=request.principal_id,
        action=request.action,
        target=request.target,
        amount=request.amount,
        currency=request.currency,
        source_account=request.source_account,
        beneficiary=request.beneficiary,
        purpose=request.purpose,
        mandate_id=request.mandate_id,
        attempted_at=datetime.fromisoformat("2026-08-10T09:15:30+00:00"),
    )

    result = validate_execution(receipt, attempt)

    assert result.status == "PERMITTED"
    assert result.reason_code == "BOUND_ALLOW_VALID"
    assert result.expected_action_binding_hash == result.attempted_action_binding_hash
