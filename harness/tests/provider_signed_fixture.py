"""Reference-only institutional signing fixture. Never use in production."""
import json
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.provider_instruction_verifier import canonical_instruction

def issuer():
    return Ed25519PrivateKey.generate()

def signed_payment(key, payload):
    payload = dict(payload)
    payload.setdefault("payment_intent_id", payload["transaction_id"])
    payload.setdefault("action", "payment.release")
    payload.setdefault("target", "external-payment-provider")
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    canonical = canonical_instruction(payload)
    assert canonical is not None, "fixture must supply complete payment identity"
    message = json.dumps({"instruction": canonical, "expires_at": expiry},
                         sort_keys=True, separators=(",", ":")).encode()
    payload["institutional_authorization"] = {
        "expires_at": expiry, "signature": key.sign(message).hex()}
    return payload

def write_public_key(key, path):
    path.write_bytes(key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    return path
