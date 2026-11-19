"""Test-only institutional issuer. Private key stays in test process, not provider."""
import json
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.provider_instruction_verifier import canonical_instruction

def issuer():
    return Ed25519PrivateKey.generate()

def signed_payment(private_key, payload):
    result = dict(payload)
    result.setdefault("payment_intent_id", result["transaction_id"])
    result.setdefault("action", "payment.release")
    result.setdefault("target", result["source_account"])
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    instruction = canonical_instruction(result)
    if instruction is None:
        raise ValueError("test issuer requires complete valid payment")
    message = json.dumps({"instruction": instruction, "expires_at": expires},
                         sort_keys=True, separators=(",", ":")).encode()
    result["institutional_authorization"] = {
        "expires_at": expires, "signature": private_key.sign(message).hex()}
    return result

def write_public_key(private_key, path):
    path.write_bytes(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    return path
