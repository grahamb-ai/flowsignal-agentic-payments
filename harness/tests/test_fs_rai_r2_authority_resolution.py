from datetime import timezone
from pathlib import Path

import pytest

from app.engines.authority_resolution import (
    AuthorityResolutionError,
    resolve_payment_authority,
)
from harness.runner import load_scenario


SCENARIO = Path(__file__).parents[1] / "harness" / "scenarios" / "AP-001_allow.json"


def _request():
    return load_scenario(SCENARIO, rebase_to_now=False)


def test_slice_c_builds_one_coherent_resolution_context():
    req = _request()
    semantics, evidence, graph, scope, context = resolve_payment_authority(
        req, resolved_at=req.requested_execution_time
    )
    assert semantics.protected_operation_class == "treasury.payment"
    assert context.semantics_set_id == semantics.semantics_set_id
    assert context.derivation_graph_id == graph.graph_id
    assert scope.derivation_graph_id == graph.graph_id
    assert set(context.evidence_member_ids) == {item.evidence_id for item in evidence}
    assert scope.authority_subject_id == req.actor_id
    assert scope.max_amount >= req.amount


def test_request_side_authentication_cannot_manufacture_unknown_actor():
    req = _request()
    req.actor_id = "attacker-controlled-agent"
    req.actor_authenticated = True
    req.kya_status = "VERIFIED"
    with pytest.raises(AuthorityResolutionError, match="unresolved"):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)


def test_presented_mandate_limit_cannot_expand_authoritative_limit():
    req = _request()
    req.mandate_max_amount = req.amount * 100
    req.amount = req.mandate_max_amount
    with pytest.raises(AuthorityResolutionError, match="amount outside"):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)


def test_unknown_beneficiary_cannot_self_supply_operational_standing():
    req = _request()
    req.beneficiary = "ATTACKER-SUPPLIER"
    req.counterparty_status = "APPROVED"
    req.account_status = "ACTIVE"
    req.risk_state = "NORMAL"
    with pytest.raises(AuthorityResolutionError, match="unresolved"):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)


def test_context_identity_changes_when_authority_cut_changes():
    req = _request()
    _, _, _, _, before = resolve_payment_authority(
        req, resolved_at=req.requested_execution_time
    )
    from app.engines.institutional_authority import advance_authority_fence
    advance_authority_fence()
    _, _, _, _, after = resolve_payment_authority(
        req, resolved_at=req.requested_execution_time
    )
    assert before.context_id != after.context_id
    assert before.authority_cut_id != after.authority_cut_id


def test_known_approved_beneficiary_still_requires_mandate_scope():
    from dataclasses import replace
    from app.engines.authority_evidence_adapters import register_operational_standing_for_test

    req = _request()
    alternate = "SUPPLIER-Y"
    register_operational_standing_for_test(
        alternate,
        counterparty_status="APPROVED",
        account_status="ACTIVE",
        risk_state="NORMAL",
        source_version="1",
    )
    req = replace(req, beneficiary=alternate)

    with pytest.raises(AuthorityResolutionError, match="beneficiary|mandate|scope|authoritative"):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)


def test_authorised_beneficiary_cannot_substitute_unapproved_account_reference():
    """MV-003 / NORM-PAY-001: beneficiary identity does not authorise any account."""
    from dataclasses import replace

    req = _request()
    assert req.beneficiary == "SUPPLIER-X"
    req = replace(
        req,
        beneficiary_account_reference="ACCT-SUPPLIER-X-ATTACKER",
    )

    with pytest.raises(
        AuthorityResolutionError,
        match="beneficiary account does not correspond to authorised beneficiary",
    ):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)


def test_compatibility_cut_must_correspond_to_current_mandate_generation():
    """IC-FAIL-004: an explicit actor/operational cut cannot bless a new mandate cut by itself."""
    from app.engines.institutional_authority import advance_mandate_source_generation_without_compatibility_for_test

    req = _request()
    _, _, _, _, before = resolve_payment_authority(
        req, resolved_at=req.requested_execution_time
    )

    # Advance only the authoritative mandate source generation. Actor and operational
    # source generations remain unchanged and retain only their old explicit cut.
    advance_mandate_source_generation_without_compatibility_for_test()

    with pytest.raises(
        AuthorityResolutionError,
        match="compatible multi-source authority cut not established",
    ):
        resolve_payment_authority(req, resolved_at=req.requested_execution_time)
