"""IE-04 signed-checkpoint rollback RED characterisation and monotonic witness candidate.

A valid *old* signed checkpoint is cryptographically authentic. Without a
separately retained monotonic witness, it may pass after later events vanish.
This test is local only; it does not establish independent storage or custody.
"""
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def wire(v):
    return json.dumps(v,sort_keys=True,separators=(",",":")).encode()

def anchor(events):
    head=bytes(32)
    for event in events:
        head=hashlib.sha256(head+wire(event)).digest()
    return {"stream":"fs-sz-pay-001","sequence":len(events),"head_sha256":head.hex()}

def signature_ok(payload,sig,key):
    try:
        key.verify(sig,payload)
        return True
    except Exception:
        return False

def main():
    key=Ed25519PrivateKey.generate()
    trusted=key.public_key()
    history=[{"id":1,"intent":"A"},{"id":2,"intent":"B"}]
    old=wire(anchor(history[:1]))
    current=wire(anchor(history))
    old_sig=key.sign(old)
    current_sig=key.sign(current)
    assert signature_ok(old,old_sig,trusted)
    assert anchor(history[:1])==json.loads(old)
    print("IE-04 ROLLBACK PRESERVED RED: authentic old signed anchor and truncated ledger pass signature/hash-only checks")
    assert signature_ok(current,current_sig,trusted)
    assert json.loads(old)["sequence"] < json.loads(current)["sequence"]
    # Witness sequence is held outside the attacker-controlled ledger/anchor.
    witness_sequence=json.loads(current)["sequence"]
    assert json.loads(old)["sequence"] < witness_sequence
    print("IE-04 MONOTONIC WITNESS CANDIDATE: old authentic signed anchor refused by separately retained high-water sequence")
    assert json.loads(current)["sequence"]==witness_sequence
    print("IE-04 CURRENT: latest signed anchor accepted against retained witness sequence")
    print("LIMITATION: witness is local in-memory simulation; no independent durable anti-rollback service or crash/recovery")

if __name__=="__main__":
    main()
