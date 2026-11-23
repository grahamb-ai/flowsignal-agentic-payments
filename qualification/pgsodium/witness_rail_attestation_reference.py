"""IE-W07/W08: reject forged rail source evidence before outcome classification.

Reference only: an independent Ed25519 rail-status key is generated in this
test. This is NOT a real rail integration or externally controlled key.
"""
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from witness_outage_rail_contradiction_reference import classify

def wire(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def verify_and_classify(local_commit, witness_available, payload, signature, trusted_key, expected_intent):
    if not witness_available:
        return "REFUSED_WITNESS_UNAVAILABLE"
    if payload is None or signature is None:
        return "UNRESOLVED_MISSING_RAIL_ATTESTATION"
    try:
        trusted_key.verify(signature,payload)
    except (InvalidSignature,ValueError,TypeError):
        return "UNRESOLVED_UNTRUSTED_RAIL_ATTESTATION"
    try:
        statement=json.loads(payload)
    except (ValueError,UnicodeDecodeError):
        return "UNRESOLVED_INVALID_RAIL_ATTESTATION"
    if not isinstance(statement,dict) or wire(statement)!=payload or set(statement)!={"intent","rail_status","rail_event_id"} or statement["intent"]!=expected_intent:
        return "UNRESOLVED_RAIL_BINDING"
    if not isinstance(statement["rail_event_id"],str) or not statement["rail_event_id"]:
        return "UNRESOLVED_RAIL_BINDING"
    return classify(local_commit,True,statement["rail_status"])

def main():
    signer=Ed25519PrivateKey.generate()
    attacker=Ed25519PrivateKey.generate()
    trusted=signer.public_key()
    claim={"intent":"PAY-001","rail_status":"REJECTED","rail_event_id":"RAIL-001"}
    payload=wire(claim)
    signature=signer.sign(payload)
    assert verify_and_classify(True,True,payload,signature,trusted,"PAY-001")=="CONTRADICTORY_LOCAL_COMMIT_RAIL_REJECTED"
    print("IE-W08 AUTHENTIC REJECTION: verified rail REJECTED contradicts local COMMITTED")
    forged=wire(dict(claim,rail_status="SETTLED"))
    assert verify_and_classify(True,True,forged,attacker.sign(forged),trusted,"PAY-001")=="UNRESOLVED_UNTRUSTED_RAIL_ATTESTATION"
    print("IE-W08 FORGED RAIL: attacker-signed SETTLED refused")
    assert verify_and_classify(True,True,payload,signature,trusted,"PAY-002")=="UNRESOLVED_RAIL_BINDING"
    print("IE-W08 WRONG INTENT: genuine attestation cannot transfer to another payment")
    assert verify_and_classify(True,True,None,None,trusted,"PAY-001")=="UNRESOLVED_MISSING_RAIL_ATTESTATION"
    print("IE-W07 MISSING RAIL: absent attestation remains unresolved")
    assert verify_and_classify(True,False,payload,signature,trusted,"PAY-001")=="REFUSED_WITNESS_UNAVAILABLE"
    print("IE-W07 WITNESS OUTAGE: no successful classification despite valid rail signature")
    print("LIMITATION: simulated rail signer and policy only; no real rail, freshness, revocation, settlement finality or independent custody")

if __name__=="__main__":main()
