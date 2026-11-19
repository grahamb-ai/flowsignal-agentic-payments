"""Reference provider-side Ed25519 payment instruction verification.

Only public verification material belongs at the provider. The issuer's private
key is supplied externally and is never loaded by this verifier.
"""
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical_instruction(payload):
    try:
        amount = Decimal(str(payload["amount"]))
        minor = amount * 100
        if not amount.is_finite() or amount <= 0 or minor != minor.to_integral_value():
            return None
        required = ("payment_intent_id", "mandate_id", "authority_epoch",
                    "source_account", "beneficiary", "currency", "action", "target")
        if any(not payload.get(k) for k in required):
            return None
        if type(payload["authority_epoch"]) is not int or payload["authority_epoch"] <= 0:
            return None
        return {"payment_intent_id": str(payload["payment_intent_id"]),
                "mandate_id": str(payload["mandate_id"]),
                "authority_epoch": payload["authority_epoch"],
                "source_account": str(payload["source_account"]),
                "beneficiary": str(payload["beneficiary"]),
                "amount_minor": int(minor),
                "currency": str(payload["currency"]),
                "action": str(payload["action"]), "target": str(payload["target"])}
    except (KeyError, ValueError, TypeError, InvalidOperation, OverflowError):
        return None

def verify_instruction(payload, public_key: Ed25519PublicKey):
    if not isinstance(public_key, Ed25519PublicKey):
        return False
    instruction = canonical_instruction(payload)
    proof = payload.get("institutional_authorization")
    if instruction is None or not isinstance(proof, dict):
        return False
    try:
        expires = datetime.fromisoformat(proof["expires_at"])
        if expires.tzinfo is None or expires.astimezone(timezone.utc) <= datetime.now(timezone.utc):
            return False
        signed = json.dumps({"instruction": instruction, "expires_at": proof["expires_at"]},
                            sort_keys=True, separators=(",", ":")).encode()
        public_key.verify(bytes.fromhex(proof["signature"]), signed)
        return True
    except (KeyError, ValueError, TypeError, OverflowError, Exception):
        return False
