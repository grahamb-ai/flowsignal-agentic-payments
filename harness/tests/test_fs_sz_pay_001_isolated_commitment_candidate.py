"""Safety regression for replacement boundary before any commit credential exists."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.fs_sz_pay_001_isolated_commitment_candidate import IsolatedCommitmentBoundaryCandidate


def test_replacement_never_commits_even_with_valid_signature():
    from datetime import datetime, timedelta, timezone
    import json
    from app.engines.provider_instruction_verifier import canonical_instruction

    key = Ed25519PrivateKey.generate()
    verifier = IsolatedCommitmentBoundaryCandidate(
        verification_key=key.public_key(), mandate_id="MANDATE-CANDIDATE")
    payload = {
        "payment_intent_id": "INTENT-CANDIDATE", "transaction_id": "INTENT-CANDIDATE",
        "mandate_id": "MANDATE-CANDIDATE", "authority_epoch": 1,
        "source_account": "SOURCE", "beneficiary": "BENEFICIARY",
        "amount": "750000.00", "currency": "GBP",
        "action": "transfer", "target": "protected-provider",
    }
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    signed = json.dumps(
        {"instruction": canonical_instruction(payload), "expires_at": expiry},
        sort_keys=True, separators=(",", ":")).encode()
    payload["institutional_authorization"] = {
        "expires_at": expiry, "signature": key.sign(signed).hex()}
    assert verifier.assess(payload)[0] == 202
    assert verifier.commit(payload) == (503, {"status": "REFUSED_FINAL_BOUNDARY_NOT_QUALIFIED"})
    altered = {**payload, "beneficiary": "ATTACKER"}
    assert verifier.assess(altered)[0] == 403
    assert verifier.commit(altered)[0] == 403
    assert verifier.commit({k: v for k, v in payload.items() if k != "institutional_authorization"})[0] == 403

def test_replacement_refuses_authentic_but_wrong_execution_scope():
    from datetime import datetime, timedelta, timezone
    import json
    from app.engines.provider_instruction_verifier import canonical_instruction

    key = Ed25519PrivateKey.generate()
    verifier = IsolatedCommitmentBoundaryCandidate(
        verification_key=key.public_key(),
        mandate_id="MANDATE-CANDIDATE",
        expected_source_account="SOURCE",
    )
    baseline = {
        "payment_intent_id": "SCOPE-001", "transaction_id": "SCOPE-001",
        "mandate_id": "MANDATE-CANDIDATE", "authority_epoch": 1,
        "source_account": "SOURCE", "beneficiary": "BENEFICIARY",
        "amount": "750000.00", "currency": "GBP",
        "action": "transfer", "target": "protected-provider",
    }

    def sign(payload):
        expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        signed = json.dumps(
            {"instruction": canonical_instruction(payload), "expires_at": expiry},
            sort_keys=True, separators=(",", ":")).encode()
        return {**payload, "institutional_authorization": {
            "expires_at": expiry, "signature": key.sign(signed).hex()}}

    assert verifier.assess(sign(baseline))[0] == 202
    for change in (
        {"action": "refund"},
        {"target": "alternate-executor"},
        {"source_account": "OTHER-SOURCE"},
        {"currency": "USD"},
        {"mandate_id": "OTHER-MANDATE"},
    ):
        status, _ = verifier.assess(sign({**baseline, **change}))
        assert status == 403, change
    assert verifier.commit(sign(baseline))[0] == 503
