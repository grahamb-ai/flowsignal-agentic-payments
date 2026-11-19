"""Actual PostgreSQL integration for replacement reference; not credential-theft closure."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import psycopg
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.provider_instruction_verifier import canonical_instruction
from app.engines.fs_sz_pay_001_authenticated_commit_reference import AuthenticatedCommitmentReference

dsn = os.environ["FS_QUAL_COMMIT_SERVICE_DSN"]
admin = os.environ["FS_QUAL_ADMIN_DSN"]
key = Ed25519PrivateKey.generate()
service = AuthenticatedCommitmentReference(
    connect=lambda: psycopg.connect(dsn), verification_key=key.public_key(),
    mandate_id="MANDATE-REPLACEMENT-INT", expected_source_account="SOURCE",
)

def signed(intent, *, epoch=1, beneficiary="BENEFICIARY", amount="750000.00"):
    payload = {
        "payment_intent_id": intent, "transaction_id": intent,
        "mandate_id": "MANDATE-REPLACEMENT-INT", "authority_epoch": epoch,
        "source_account": "SOURCE", "beneficiary": beneficiary,
        "amount": amount, "currency": "GBP", "action": "transfer",
        "target": "protected-provider",
    }
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    body = json.dumps(
        {"instruction": canonical_instruction(payload), "expires_at": expiry},
        sort_keys=True, separators=(",", ":")).encode()
    payload["institutional_authorization"] = {
        "expires_at": expiry, "signature": key.sign(body).hex()}
    return payload

with psycopg.connect(admin, autocommit=True) as db:
    db.execute("SET ROLE fs_authority_writer")
    db.execute("INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES (%s,1,false)",
               ("MANDATE-REPLACEMENT-INT",))
    db.execute("RESET ROLE")

original = signed("REPLACEMENT-INTENT-001")
assert service.transfer(original)[0] == 201
assert service.transfer(original)[0] == 409
assert service.transfer({**original, "beneficiary": "ATTACKER"})[0] == 403
assert service.transfer({k:v for k,v in original.items() if k != "institutional_authorization"})[0] == 403

with psycopg.connect(admin, autocommit=True) as db:
    db.execute("SET ROLE fs_authority_writer")
    db.execute("UPDATE fs_provider.mandates SET revoked=true,epoch=2 WHERE id=%s",
               ("MANDATE-REPLACEMENT-INT",))
    db.execute("RESET ROLE")

assert service.transfer(signed("REPLACEMENT-INTENT-002"))[0] == 403
with psycopg.connect(admin) as db:
    count = db.execute(
        "SELECT count(*) FROM fs_provider.commits WHERE mandate_id=%s",
        ("MANDATE-REPLACEMENT-INT",)).fetchone()[0]
assert count == 1, count
print("AUTHENTICATED REPLACEMENT REFERENCE PASS: valid, replay, tamper, unsigned, revoked")
print("NOT BOUNDARY-02: service credential can still call unsigned SQL function directly")
