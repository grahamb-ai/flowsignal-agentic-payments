"""IE-04 externally held signature anchor: local reference, not independent deployment.

The verifier trusts a separately generated Ed25519 public key, not a key
obtained from the administrator-controlled database. The private key remains
in this test process, so key custody and external durability are NOT proven.
"""
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def wire(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode("utf-8")

def checkpoint(events):
    previous=bytes(32)
    for event in events:
        previous=hashlib.sha256(previous+wire(event)).digest()
    return {"sequence":len(events),"head_sha256":previous.hex(),"stream":"fs-sz-pay-001"}

def verify(events, anchor_bytes, signature, trusted_public_key):
    try:
        trusted_public_key.verify(signature,anchor_bytes)
    except InvalidSignature:
        return "UNVERIFIED_ANCHOR_SIGNATURE"
    if anchor_bytes != wire(checkpoint(events)):
        return "UNVERIFIED_ANCHOR_MISMATCH"
    return "VERIFIED_REFERENCE_ANCHOR"

def main():
    authority=Ed25519PrivateKey.generate()
    public=authority.public_key()
    original=[
      {"event_id":1,"intent":"IE04-A","outcome":"COMMITTED_REFERENCE","amount_minor":100},
      {"event_id":2,"intent":"IE04-B","outcome":"REFUSED_REFERENCE","amount_minor":200},
    ]
    anchor=wire(checkpoint(original))
    signature=authority.sign(anchor)
    assert verify(original,anchor,signature,public)=="VERIFIED_REFERENCE_ANCHOR"
    print("IE-04 SIGNED ANCHOR BASELINE: trusted-key signature and ledger checkpoint verified")
    changed=[dict(original[0],amount_minor=900),original[1]]
    assert verify(changed,anchor,signature,public)=="UNVERIFIED_ANCHOR_MISMATCH"
    print("IE-04 ALTER: changed database ledger refused against retained signed anchor")
    assert verify(original[:1],anchor,signature,public)=="UNVERIFIED_ANCHOR_MISMATCH"
    print("IE-04 DELETE: truncated ledger refused against retained signed anchor")
    attacker=Ed25519PrivateKey.generate()
    forged_anchor=wire(checkpoint(changed))
    assert verify(changed,forged_anchor,attacker.sign(forged_anchor),public)=="UNVERIFIED_ANCHOR_SIGNATURE"
    print("IE-04 DUAL-REWRITE: attacker ledger and forged anchor refused by independently trusted public key")
    print("LIMITATION: trusted key is local test-only; no external operator, durable independent store, key rotation, rollback prevention or rail outcome")

if __name__=="__main__":main()
