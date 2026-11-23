"""IE-W12 signed witness receipt reference; local key and store, NOT independent custody."""
import base64, hashlib, json, tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from ie_w11_witness_contract_reference import Witness

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()

def sign_receipt(key,decision,stream,event,checkpoint):
    body={"decision":decision,"stream":stream,"event_id":event,"sequence":checkpoint["sequence"],"checkpoint_hash":checkpoint["checkpoint_hash"],"schema":"IE-W12-REFERENCE-1"}
    return {"body":body,"signature":base64.b64encode(key.sign(canonical(body))).decode()}

def verify_receipt(public,receipt,expected):
    try:
        body=receipt["body"]
        if body != expected: return False
        public.verify(base64.b64decode(receipt["signature"],validate=True),canonical(body))
        return True
    except (KeyError,TypeError,ValueError,InvalidSignature):
        return False

def main():
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"witness.sqlite"
        w=Witness(path)
        key=Ed25519PrivateKey.generate()
        public=key.public_key()
        event={"event_id":"IE-W12-E1","stream":"payment","expected_sequence":0,"authority_epoch":4,"intent_id":"I1","target":"sandbox","outcome":"REFUSED_AUTHORITY","evidence_hash":hashlib.sha256(b"synthetic").hexdigest()}
        outcome=w.advance("witness-writer",event)
        assert outcome["decision"]=="ACCEPTED_REFERENCE"
        receipt=sign_receipt(key,outcome["decision"],event["stream"],event["event_id"],w.read("payment"))
        assert verify_receipt(public,receipt,receipt["body"])
        changed=json.loads(json.dumps(receipt));changed["body"]["sequence"]=999
        assert not verify_receipt(public,changed,changed["body"])
        assert not verify_receipt(public,receipt,{**receipt["body"],"event_id":"other"})
        assert not verify_receipt(Ed25519PrivateKey.generate().public_key(),receipt,receipt["body"])
        assert Witness(path).read("payment")["checkpoint_hash"]==receipt["body"]["checkpoint_hash"]
        print("IE-W12 LOCAL GREEN: signed receipt verified, mutation/identity/key substitution refused, restart checkpoint retained")
        path.unlink()
        assert Witness(path).read("payment")["sequence"]==0
        # A signed receipt proves only a past claim under the locally trusted key.
        # It cannot independently prove the latest state after store deletion.
        assert verify_receipt(public,receipt,receipt["body"])
        print("IE-W12 PRESERVED RED: old authentic receipt still verifies after locally administered ledger deletion; independent monotonic freshness absent")
        print("NOT QUALIFIED: independent key custody, real issuer, signed rail, admin rollback resistance")
if __name__=="__main__":main()
