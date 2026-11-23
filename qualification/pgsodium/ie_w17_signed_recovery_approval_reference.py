"""IE-W17 signed recovery approval reference; local key custody, not independent."""
import base64,json,tempfile,time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from ie_w11_witness_contract_reference import Witness
from ie_w13_highwater_freshness_reference import HighWater
from ie_w15_partial_advance_reconciliation_reference import event,reconcile

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def verify(public,proof,expected,now):
    try:
        body=proof["body"]
        if body!=expected or body["expires_at"]<=now or body["expires_at"]>now+300:
            return False
        public.verify(base64.b64decode(proof["signature"],validate=True),canonical(body))
        return True
    except (KeyError,TypeError,ValueError,InvalidSignature):
        return False

def recover(w,h,proof,expected,public,now):
    if not verify(public,proof,expected,now):
        return "REFUSED_UNAUTHENTICATED_RECOVERY"
    # The proof binds exact ledger event and expected high-water state.
    if h.current(expected["stream"])!=expected["prior_checkpoint"]:
        return "UNRESOLVED_STALE_RECOVERY_APPROVAL"
    if expected["event"]["stream"]!=expected["stream"] or w.read(expected["stream"])!=expected["proposed_checkpoint"]:
        return "UNRESOLVED_PROPOSED_CHECKPOINT_MISMATCH"
    return reconcile(w,h,expected["event"],authorized=True)

def main():
    with tempfile.TemporaryDirectory() as d:
        w=Witness(Path(d)/"ledger.sqlite");h=HighWater(Path(d)/"highwater.sqlite")
        first=w.advance("witness-writer",event(0))
        assert h.advance("payment",0,1,first["checkpoint_hash"])=="ADVANCED_REFERENCE"
        prior=h.current("payment")
        second=w.advance("witness-writer",event(1))
        assert second["decision"]=="ACCEPTED_REFERENCE"
        now=int(time.time())
        body={"schema":"IE-W17-RECOVERY-1","stream":"payment","event":event(1),
              "prior_checkpoint":prior,"proposed_checkpoint":w.read("payment"),
              "expires_at":now+120,"approval_id":"RECOVERY-001"}
        key=Ed25519PrivateKey.generate();pub=key.public_key()
        proof={"body":body,"signature":base64.b64encode(key.sign(canonical(body))).decode()}
        assert recover(w,h,{"body":body,"signature":"AA=="},body,pub,now)=="REFUSED_UNAUTHENTICATED_RECOVERY"
        assert recover(w,h,proof,{**body,"approval_id":"OTHER"},pub,now)=="REFUSED_UNAUTHENTICATED_RECOVERY"
        assert recover(w,h,proof,body,pub,now+121)=="REFUSED_UNAUTHENTICATED_RECOVERY"
        assert recover(w,h,proof,body,Ed25519PrivateKey.generate().public_key(),now)=="REFUSED_UNAUTHENTICATED_RECOVERY"
        assert recover(w,h,proof,body,pub,now)=="RECONCILED_REFERENCE_CHECKPOINT"
        assert recover(w,h,proof,body,pub,now)=="UNRESOLVED_STALE_RECOVERY_APPROVAL"
        assert h.current("payment")["sequence"]==2
        print("IE-W17 LOCAL GREEN: forged, substituted, expired and wrong-key approvals refused; signed recovery once; replay stale")
        print("IE-W17 PRESERVED RED: signing key and witness stores remain under same local administrator; approval provenance not independent")
        print("NOT QUALIFIED: institutional custody, real external outcome, independent verifier, privileged rollback")
if __name__=="__main__":main()
