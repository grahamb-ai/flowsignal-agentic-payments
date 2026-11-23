"""FS-SZ-PAY-001: isolated-process receipt reference, NOT an independent deployment.

Tests IE-02, IE-03, IE-05 and IE-07 at cryptographic data-boundary level.
The key is generated locally for this test, outside the simulated DB records.
This is NOT proof of external rail execution, append-only storage or key isolation.
"""
import base64
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

def verify(receipt, signature, public_key, expected):
    if receipt is None or signature is None:
        return "UNVERIFIED_MISSING_RECEIPT"
    try:
        public_key.verify(signature, receipt)
    except InvalidSignature:
        return "UNVERIFIED_SIGNATURE"
    if receipt != canonical(expected):
        return "UNVERIFIED_BINDING_MISMATCH"
    return "VERIFIED_REFERENCE_RECEIPT"

def main():
    key = Ed25519PrivateKey.generate()
    public = key.public_key()
    event = {
        "event_id": 1, "payment_intent_id": "IE-001",
        "instruction_sha256": "a" * 64, "issuer": "institution-001",
        "authority_epoch": 8, "execution_target": "protected-provider",
        "executor": "payment-executor-001", "outcome": "COMMITTED_REFERENCE"
    }
    signed = canonical(event)
    signature = key.sign(signed)
    assert verify(signed, signature, public, event) == "VERIFIED_REFERENCE_RECEIPT"
    print("IE-REFERENCE: valid signed receipt verified (NOT external payment evidence)")

    assert verify(None, None, public, event) == "UNVERIFIED_MISSING_RECEIPT"
    print("IE-02: forged database row without receipt -> UNVERIFIED_MISSING_RECEIPT")

    modified = dict(event, payment_intent_id="IE-001", beneficiary="attacker")
    assert verify(signed, signature, public, modified) == "UNVERIFIED_BINDING_MISMATCH"
    print("IE-03: modified record -> UNVERIFIED_BINDING_MISMATCH")

    replay = dict(event, payment_intent_id="IE-002", executor="other-executor")
    assert verify(signed, signature, public, replay) == "UNVERIFIED_BINDING_MISMATCH"
    print("IE-05: receipt replay to other intent/executor -> UNVERIFIED_BINDING_MISMATCH")

    attacker = Ed25519PrivateKey.generate()
    assert verify(signed, attacker.sign(signed), public, event) == "UNVERIFIED_SIGNATURE"
    print("IE-07: administrator-controlled alternative key -> UNVERIFIED_SIGNATURE")
    print("SCOPE: local crypto characterisation only; no external key custody, independent store, actual rail or crash-safe receipt issuance")

if __name__ == "__main__":
    main()
