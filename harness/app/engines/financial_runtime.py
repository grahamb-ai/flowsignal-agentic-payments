from __future__ import annotations

import hashlib, json, math, unicodedata, uuid
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from app.engines.authority_store import (
    get_authoritative_mandate_limit,
    get_authority_state_version,
)
from app.engines.financial_types import AuthorityReceipt, ExecutionResponse, FinancialAuthorityRequest, FinancialCheck
from app.engines.receipt_integrity import compute_receipt_hmac


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


def _meaningful_text(value: object) -> bool:
    """Require visible text and reject embedded Unicode control/format characters."""
    if not isinstance(value, str) or not value:
        return False
    if any(unicodedata.category(ch) in {"Cc", "Cf"} for ch in value):
        return False
    return any(ch.isprintable() and not ch.isspace() for ch in value)


def _valid_datetime(value: object) -> bool:
    return isinstance(value, datetime)


def _valid_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _valid_nonnegative_number(value: object) -> bool:
    return _valid_number(value) and value >= 0


def _valid_string_list(value: object) -> bool:
    return isinstance(value, list) and all(_meaningful_text(item) for item in value)


def _request_shape_valid(req: FinancialAuthorityRequest) -> bool:
    """Validate authority-bearing request shape before any semantic evaluation.

    Dataclass annotations are not runtime validation. A malformed request must therefore
    fail closed here rather than reach operations such as .upper(), datetime arithmetic,
    membership tests, or numeric comparisons that can raise or coerce unexpectedly.
    """
    required_text = (
        req.actor_id,
        req.principal_id,
        req.mandate_id,
        req.action,
        req.target,
        req.source_account,
        req.beneficiary,
        req.currency,
        req.purpose,
        req.kya_status,
        req.mandate_status,
        req.mandate_currency,
        req.counterparty_status,
        req.account_status,
        req.risk_state,
        req.screening_status,
    )
    return (
        all(_meaningful_text(value) for value in required_text)
        and isinstance(req.actor_authenticated, bool)
        and isinstance(req.approval_required, bool)
        and _valid_number(req.amount)
        and _valid_number(req.mandate_max_amount)
        and _valid_nonnegative_number(req.screening_max_age_seconds)
        and _valid_datetime(req.mandate_valid_until)
        and _valid_datetime(req.screening_captured_at)
        and _valid_datetime(req.requested_execution_time)
        and _valid_string_list(req.permitted_source_accounts)
    )


def _malformed_response(req: FinancialAuthorityRequest, *, sealed_at: datetime | None = None):
    """Return a deterministic REFUSE without constructing evidence from malformed values."""
    now = sealed_at if _valid_datetime(sealed_at) else (
        req.requested_execution_time if _valid_datetime(req.requested_execution_time) else datetime.now(timezone.utc)
    )
    now = _aware(now)
    rid = str(uuid.uuid4())
    response = ExecutionResponse(
        decision="REFUSE",
        reason_code="MALFORMED_AUTHORITY_REQUEST",
        authority_receipt_id=rid,
        valid_until=None,
        required_action=None,
    )
    return response, None


def evaluate_financial(req: FinancialAuthorityRequest, *, sealed_at: datetime | None = None):
    if not _request_shape_valid(req):
        return _malformed_response(req, sealed_at=sealed_at)

    authoritative_limit = get_authoritative_mandate_limit(req.mandate_id)
    mandate_resolved = authoritative_limit is not None
    effective_limit = authoritative_limit if authoritative_limit is not None else 0.0

    now = _aware(sealed_at or req.requested_execution_time)
    expiry = _aware(req.mandate_valid_until)
    screening_time = _aware(req.screening_captured_at)
    raw_screening_age = (now - screening_time).total_seconds()
    screening_age = max(0.0, raw_screening_age)

    amount_valid = _valid_number(req.amount) and req.amount > 0
    required_text_valid = all(
        _meaningful_text(value)
        for value in (
            req.actor_id, req.principal_id, req.mandate_id, req.action, req.target,
            req.source_account, req.beneficiary, req.currency, req.purpose,
        )
    )

    checks = [
        _check("required_authority_text_valid", required_text_valid, "REFUSE", "Required authority/action text is empty or non-meaningful", "request"),
        _check("mandate_resolved", mandate_resolved, "REFUSE", f"Mandate '{req.mandate_id}' is not present in the authoritative mandate store", req.mandate_id),
        _check("actor_authenticated", req.actor_authenticated is True, "REFUSE", "Actor authentication is not established", "authentication"),
        _check("kya_verified", req.kya_status.upper() == "VERIFIED", "REFUSE", f"KYA status is '{req.kya_status}'", "kya"),
        _check("mandate_active", req.mandate_status.upper() == "ACTIVE", "REFUSE", f"Mandate status is '{req.mandate_status}'", req.mandate_id),
        _check("mandate_not_expired", now <= expiry, "REFUSE", "Delegated mandate has expired", req.mandate_id),
        _check("action_permitted", req.action == "payment.release", "REFUSE", f"Action '{req.action}' is not permitted", req.mandate_id),
        _check("target_permitted", req.target == "TREASURY_PAYMENT_GATEWAY", "REFUSE", f"Target '{req.target}' is not permitted", req.mandate_id),
        _check("amount_valid", amount_valid, "REFUSE", "Payment amount must be finite and greater than zero", req.mandate_id),
        _check("amount_within_limit", amount_valid and req.amount <= effective_limit, "ESCALATE", "Amount exceeds autonomous mandate limit", req.mandate_id),
        _check("currency_permitted", req.currency.upper() == req.mandate_currency.upper(), "REFUSE", f"Currency '{req.currency}' is outside mandate currency '{req.mandate_currency}'", req.mandate_id),
        _check("source_account_permitted", req.source_account in req.permitted_source_accounts, "REFUSE", f"Source account '{req.source_account}' is outside the delegated mandate", req.mandate_id),
        _check("counterparty_approved", req.counterparty_status.upper() == "APPROVED", "REFUSE", f"Counterparty status is '{req.counterparty_status}'", "counterparty-status"),
        _check("account_active", req.account_status.upper() == "ACTIVE", "REFUSE", f"Account status is '{req.account_status}'", "account-status"),
        _check("risk_state_permits_execution", req.risk_state.upper() == "NORMAL", "ESCALATE", f"Risk state is '{req.risk_state}'", "risk-state"),
        _check("approval_not_required", req.approval_required is False, "ESCALATE", "Explicit approval is required before execution", "approval"),
        _check("screening_clear", req.screening_status.upper() == "CLEAR", "REFUSE", f"Screening status is '{req.screening_status}'", req.screening_source),
        _check("screening_not_future_dated", raw_screening_age >= 0, "ESCALATE", "Screening evidence is future-dated relative to evaluation time", req.screening_source),
        _check("screening_policy_valid", req.screening_max_age_seconds >= 0, "ESCALATE", "Screening freshness policy cannot be negative", req.screening_source),
        _check("screening_fresh", raw_screening_age >= 0 and req.screening_max_age_seconds >= 0 and screening_age <= req.screening_max_age_seconds, "ESCALATE", f"Screening evidence age {int(screening_age)}s exceeds maximum age {req.screening_max_age_seconds}s", req.screening_source),
    ]

    failed = [c for c in checks if not c.passed]
    if any(c.outcome_on_failure == "REFUSE" for c in failed):
        decision, reason_code, required_action = "REFUSE", "AUTHORITY_NOT_ESTABLISHED", None
    elif failed:
        decision, reason_code = "ESCALATE", "ADDITIONAL_AUTHORITY_OR_EVIDENCE_REQUIRED"
        required_action = "Route for authorised intervention or refresh required evidence"
    else:
        decision, reason_code, required_action = "ALLOW", "AUTHORITY_ESTABLISHED", None

    rid = str(uuid.uuid4())
    valid_until = now + timedelta(seconds=60) if decision == "ALLOW" else None
    snapshot = asdict(req)
    snapshot["presented_mandate_max_amount"] = req.mandate_max_amount
    snapshot["authoritative_mandate_max_amount"] = authoritative_limit
    for k, v in list(snapshot.items()):
        if isinstance(v, datetime):
            snapshot[k] = _aware(v).isoformat()

    evidence_references = [{
        "type": "sanctions_screening", "source": req.screening_source,
        "status": req.screening_status, "captured_at": screening_time.isoformat(),
        "age_seconds": int(screening_age), "max_age_seconds": req.screening_max_age_seconds,
    }]
    authority_state_version = get_authority_state_version()
    receipt_hmac = compute_receipt_hmac(
        receipt_id=rid, scenario_id=req.scenario_id, decision=decision,
        reason_code=reason_code, sealed_at=now, valid_until=valid_until,
        action_binding_hash=_binding(req), authority_state_version=authority_state_version,
        request_snapshot=snapshot, checks=checks, evidence_references=evidence_references,
    )
    receipt = AuthorityReceipt(
        id=rid, scenario_id=req.scenario_id, decision=decision, reason_code=reason_code,
        sealed_at=now, valid_until=valid_until, action_binding_hash=_binding(req),
        authority_state_version=authority_state_version, receipt_hmac=receipt_hmac,
        request_snapshot=snapshot, checks=checks, evidence_references=evidence_references,
    )
    response = ExecutionResponse(
        decision=decision, reason_code=reason_code, authority_receipt_id=rid,
        valid_until=valid_until, required_action=required_action,
    )
    return response, receipt
