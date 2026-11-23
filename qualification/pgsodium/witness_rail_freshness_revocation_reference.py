"""IE-W08 signed rail evidence freshness, key epoch and replay reference.

This is a local policy characterisation. Trusted clock, key status and replay
registry are supplied by the test, not by an independent rail authority.
"""
import json
from datetime import datetime,timezone,timedelta
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def wire(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def check(payload,signature,keys,now,expected_intent,seen):
    try:
        obj=json.loads(payload)
        if wire(obj)!=payload or set(obj)!={"intent","status","event_id","key_id","issued_at","expires_at"}:
            return "UNRESOLVED_BINDING"
        if obj["intent"]!=expected_intent or obj["status"] not in ("SETTLED","REJECTED"):
            return "UNRESOLVED_BINDING"
        key=keys.get(obj["key_id"])
        if key is None or not key["enabled"]:
            return "UNRESOLVED_REVOKED_RAIL_KEY"
        key["public"].verify(signature,payload)
        issued=datetime.fromisoformat(obj["issued_at"])
        expires=datetime.fromisoformat(obj["expires_at"])
        if issued.tzinfo is None or expires.tzinfo is None or issued>now or expires<=now or expires-issued>timedelta(minutes=5):
            return "UNRESOLVED_STALE_RAIL_EVIDENCE"
        if obj["event_id"] in seen:
            return "UNRESOLVED_REPLAYED_RAIL_EVENT"
        seen.add(obj["event_id"])
        return "VERIFIED_RAIL_STATUS_REFERENCE"
    except (InvalidSignature,ValueError,KeyError,TypeError,AttributeError):
        return "UNRESOLVED_UNVERIFIED_RAIL"

def main():
    signer=Ed25519PrivateKey.generate()
    now=datetime(2026,11,23,10,0,tzinfo=timezone.utc)
    keys={"rail-v1":{"public":signer.public_key(),"enabled":True}}
    def statement(event,issued,expires):
        return wire({"intent":"PAY-001","status":"SETTLED","event_id":event,"key_id":"rail-v1","issued_at":issued.isoformat(),"expires_at":expires.isoformat()})
    current=statement("EVENT-001",now-timedelta(seconds=20),now+timedelta(minutes=2))
    assert check(current,signer.sign(current),keys,now,"PAY-001",set())=="VERIFIED_RAIL_STATUS_REFERENCE"
    print("IE-W08 FRESH: bounded signed rail statement accepted in reference")
    seen=set()
    assert check(current,signer.sign(current),keys,now,"PAY-001",seen)=="VERIFIED_RAIL_STATUS_REFERENCE"
    assert check(current,signer.sign(current),keys,now,"PAY-001",seen)=="UNRESOLVED_REPLAYED_RAIL_EVENT"
    print("IE-W08 REPLAY: same signed rail event refused by local seen-event registry")
    expired=statement("EVENT-002",now-timedelta(minutes=4),now-timedelta(minutes=1))
    assert check(expired,signer.sign(expired),keys,now,"PAY-001",set())=="UNRESOLVED_STALE_RAIL_EVIDENCE"
    print("IE-W08 EXPIRED: authentic stale rail evidence refused")
    future=statement("EVENT-003",now+timedelta(minutes=1),now+timedelta(minutes=3))
    assert check(future,signer.sign(future),keys,now,"PAY-001",set())=="UNRESOLVED_STALE_RAIL_EVIDENCE"
    print("IE-W08 FUTURE: future-dated evidence refused")
    keys["rail-v1"]["enabled"]=False
    assert check(current,signer.sign(current),keys,now,"PAY-001",set())=="UNRESOLVED_REVOKED_RAIL_KEY"
    print("IE-W08 REVOKED: formerly valid signature refused after key revocation")
    print("LIMITATION: local clock, mutable in-memory replay registry and key status; no external rail or independent trust domain")

if __name__=="__main__":main()
