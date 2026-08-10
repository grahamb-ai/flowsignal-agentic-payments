from __future__ import annotations
import hashlib, json, uuid
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from app.engines.financial_types import AuthorityReceipt, ExecutionResponse, FinancialAuthorityRequest, FinancialCheck

def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _binding(req: FinancialAuthorityRequest) -> str:
    payload = {
        "actor_id": req.actor_id,
        "principal_id": req.principal_id,
        "action": req.action,
        "target": req.target,
        "amount": req.amount,
        "currency": req.currency,
        "source_account": req.source_account,
        "beneficiary": req.beneficiary,
        "purpose": req.purpose,
        "mandate_id": req.mandate_id,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def _check(name, passed, fail_outcome, reason=None, evidence_ref=None):
    return FinancialCheck(
        name=name,
        passed=passed,
        outcome_on_failure=fail_outcome,
        reason=None if passed else reason,
        evidence_ref=evidence_ref,
    )

def evaluate_financial(req: FinancialAuthorityRequest, *, sealed_at: datetime | None = None):
    now = _aware(sealed_at or req.requested_execution_time)
    expiry = _aware(req.mandate_valid_until)
    screening_time = _aware(req.screening_captured_at)
    screening_age = max(0.0, (now - screening_time).total_seconds())

    checks = [
        _check("actor_authenticated", req.actor_authenticated, "REFUSE", "Actor authentication is not established", "authentication"),
        _check("kya_verified", req.kya_status.upper() == "VERIFIED", "REFUSE", f"KYA status is '{req.kya_status}'", "kya"),
        _check("mandate_active", req.mandate_status.upper() == "ACTIVE", "REFUSE", f"Mandate status is '{req.mandate_status}'", req.mandate_id),
        _check("mandate_not_expired", now <= expiry, "REFUSE", "Delegated mandate has expired", req.mandate_id),
        _check("action_permitted", req.action == "payment.release", "REFUSE", f"Action '{req.action}' is not permitted", req.mandate_id),
        _check("amount_within_limit", req.amount <= req.mandate_max_amount, "ESCALATE", f"Amount {req.amount:g} exceeds autonomous mandate limit {req.mandate_max_amount:g}", req.mandate_id),
        _check("currency_permitted", req.currency.upper() == req.mandate_currency.upper(), "REFUSE", f"Currency '{req.currency}' is outside mandate currency '{req.mandate_currency}'", req.mandate_id),
        _check("source_account_permitted", req.source_account in req.permitted_source_accounts, "REFUSE", f"Source account '{req.source_account}' is outside the delegated mandate", req.mandate_id),
        _check("counterparty_approved", req.counterparty_status.upper() == "APPROVED", "REFUSE", f"Counterparty status is '{req.counterparty_status}'", "counterparty-status"),
        _check("account_active", req.account_status.upper() == "ACTIVE", "REFUSE", f"Account status is '{req.account_status}'", "account-status"),
        _check("risk_state_permits_execution", req.risk_state.upper() == "NORMAL", "ESCALATE", f"Risk state is '{req.risk_state}'", "risk-state"),
        _check("screening_clear", req.screening_status.upper() == "CLEAR", "REFUSE", f"Screening status is '{req.screening_status}'", req.screening_source),
        _check("screening_fresh", screening_age <= req.screening_max_age_seconds, "ESCALATE", f"Screening evidence age {int(screening_age)}s exceeds maximum age {req.screening_max_age_seconds}s", req.screening_source),
    ]

    failed = [c for c in checks if not c.passed]
    if any(c.outcome_on_failure == "REFUSE" for c in failed):
        decision = "REFUSE"
        reason_code = "AUTHORITY_NOT_ESTABLISHED"
        required_action = None
    elif failed:
        decision = "ESCALATE"
        reason_code = "ADDITIONAL_AUTHORITY_OR_EVIDENCE_REQUIRED"
        required_action = "Route for authorised intervention or refresh required evidence"
    else:
        decision = "ALLOW"
        reason_code = "AUTHORITY_ESTABLISHED"
        required_action = None

    rid = str(uuid.uuid4())
    valid_until = now + timedelta(seconds=60) if decision == "ALLOW" else None
    snapshot = asdict(req)
    for k, v in list(snapshot.items()):
        if isinstance(v, datetime):
            snapshot[k] = _aware(v).isoformat()

    receipt = AuthorityReceipt(
        id=rid,
        scenario_id=req.scenario_id,
        decision=decision,
        reason_code=reason_code,
        sealed_at=now,
        valid_until=valid_until,
        action_binding_hash=_binding(req),
        request_snapshot=snapshot,
        checks=checks,
        evidence_references=[{
            "type": "sanctions_screening",
            "source": req.screening_source,
            "status": req.screening_status,
            "captured_at": screening_time.isoformat(),
            "age_seconds": int(screening_age),
            "max_age_seconds": req.screening_max_age_seconds,
        }],
    )
    response = ExecutionResponse(
        decision=decision,
        reason_code=reason_code,
        authority_receipt_id=rid,
        valid_until=valid_until,
        required_action=required_action,
    )
    return response, receipt
