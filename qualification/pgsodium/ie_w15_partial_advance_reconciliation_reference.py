"""IE-W15 local idempotent recovery of ledger/high-water partial advance.
Not a cross-store transaction or independent administrator.
"""
import tempfile
from pathlib import Path
from ie_w11_witness_contract_reference import Witness
from ie_w13_highwater_freshness_reference import HighWater, verify_latest

def event(seq):
    return {"event_id":f"E{seq}","stream":"payment","expected_sequence":seq,"authority_epoch":4,
            "intent_id":f"I{seq}","target":"sandbox","outcome":"REFUSED_AUTHORITY",
            "evidence_hash":f"synthetic-{seq}"}

def reconcile(witness,highwater,expected_event,authorized=False):
    """A trusted reviewer flag simulates a separate attestation; NOT authentication."""
    if not authorized: return "UNRESOLVED_REVIEW_REQUIRED"
    stream=expected_event["stream"]
    ledger=witness.read(stream)
    mark=highwater.current(stream)
    if ledger["sequence"]==mark["sequence"] and ledger["checkpoint_hash"]==mark["checkpoint_hash"]:
        return "CURRENT_REFERENCE_CHECKPOINT"
    if ledger["sequence"]!=mark["sequence"]+1:
        return "UNRESOLVED_SEQUENCE_GAP"
    if expected_event["expected_sequence"]!=mark["sequence"]:
        return "UNRESOLVED_UNMATCHED_EVENT"
    # Inspect persisted event rather than trusting a caller's proposed hash.
    import json,sqlite3
    with sqlite3.connect(witness.path) as db:
        row=db.execute("SELECT seq,hash,body FROM events WHERE event_id=?",
                       (expected_event["event_id"],)).fetchone()
    if row is None or row[0]!=ledger["sequence"] or row[1]!=ledger["checkpoint_hash"] or json.loads(row[2])!=expected_event:
        return "UNRESOLVED_EVENT_MISMATCH"
    if highwater.advance(stream,mark["sequence"],ledger["sequence"],ledger["checkpoint_hash"])!="ADVANCED_REFERENCE":
        return "UNRESOLVED_CONCURRENT_ADVANCE"
    return "RECONCILED_REFERENCE_CHECKPOINT"

def main():
    with tempfile.TemporaryDirectory() as d:
        w=Witness(Path(d)/"ledger.sqlite");h=HighWater(Path(d)/"highwater.sqlite")
        first=w.advance("witness-writer",event(0))
        assert h.advance("payment",0,1,first["checkpoint_hash"])=="ADVANCED_REFERENCE"
        second=w.advance("witness-writer",event(1))
        assert second["decision"]=="ACCEPTED_REFERENCE"
        assert verify_latest(w.read("payment"),h.current("payment"))=="REFUSED_OLD_OR_CONFLICTING_CHECKPOINT"
        assert reconcile(w,h,event(1))=="UNRESOLVED_REVIEW_REQUIRED"
        assert reconcile(w,h,{**event(1),"evidence_hash":"substituted"},True)=="UNRESOLVED_EVENT_MISMATCH"
        assert reconcile(w,h,event(1),True)=="RECONCILED_REFERENCE_CHECKPOINT"
        assert reconcile(w,h,event(1),True)=="CURRENT_REFERENCE_CHECKPOINT"
        assert h.current("payment")["sequence"]==2
        print("IE-W15 LOCAL GREEN: partial advance blocked pending review; mismatch refused; exact persisted event reconciled once; retry idempotent")
        h.path and Path(h.path).unlink()
        assert HighWater(h.path).current("payment")["sequence"]==0
        print("IE-W15 PRESERVED RED: shared administrator can delete high-water; reviewer flag is not independent authenticated authority")
        print("NOT QUALIFIED: independent custody, cross-store atomicity, externally signed receipt, actual provider outcome")
if __name__=="__main__":main()
