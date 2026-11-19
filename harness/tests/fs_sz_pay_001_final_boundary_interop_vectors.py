"""Deterministic Ed25519 final-boundary interoperability vectors.

These are NOT a final database verifier. They pin exact canonical bytes and
signature representation for evaluating a reviewed PostgreSQL implementation.
No institutional private key or production secret is used.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from app.engines.provider_instruction_verifier import canonical_instruction, verify_instruction

SEED = bytes(range(32))  # PUBLIC TEST VECTOR ONLY, NEVER USE AS A REAL ISSUER KEY
EXPIRY = "2099-01-01T00:00:00+00:00"
BASE = {
    "payment_intent_id": "VECTOR-001",
    "transaction_id": "VECTOR-001",
    "mandate_id": "MANDATE-VECTOR",
    "authority_epoch": 7,
    "source_account": "SOURCE-001",
    "beneficiary": "BENEFICIARY-001",
    "amount": "750000.00",
    "currency": "GBP",
    "action": "transfer",
    "target": "protected-provider",
}
private = Ed25519PrivateKey.from_private_bytes(SEED)
public = private.public_key()
canonical = canonical_instruction(BASE)
assert canonical is not None
signed_bytes = json.dumps(
    {"instruction": canonical, "expires_at": EXPIRY},
    sort_keys=True, separators=(",", ":")).encode("utf-8")
signature = private.sign(signed_bytes)
payload = {**BASE, "institutional_authorization": {
    "expires_at": EXPIRY, "signature": signature.hex()}}
assert verify_instruction(payload, public)
cases = []
for name, mutation in (
    ("changed_beneficiary", {"beneficiary": "ATTACKER"}),
    ("changed_amount", {"amount": "750000.01"}),
    ("changed_epoch", {"authority_epoch": 8}),
    ("changed_target", {"target": "alternate-provider"}),
    ("changed_intent", {"payment_intent_id": "VECTOR-002", "transaction_id": "VECTOR-002"}),
):
    candidate = {**payload, **mutation}
    assert not verify_instruction(candidate, public), name
    cases.append({"name": name, "accepted": False})
unsigned = {k: v for k, v in BASE.items()}
assert not verify_instruction(unsigned, public)
cases.append({"name": "unsigned", "accepted": False})
result = {
    "purpose": "REFERENCE INTEROPERABILITY ONLY — NOT FINAL COMMIT QUALIFICATION",
    "public_key_hex": public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw).hex(),
    "signed_bytes_utf8_hex": signed_bytes.hex(),
    "signature_hex": signature.hex(),
    "canonical_instruction": canonical,
    "positive": {"name": "valid_signed_instruction", "accepted": True},
    "negative": cases,
}
print(json.dumps(result, sort_keys=True, indent=2))
