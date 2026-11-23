"""IE-W16: witness outage and concurrent high-water recovery characterisation.
Same-admin reference, no independent identity or external rail.
"""
import tempfile,threading
from pathlib import Path
from ie_w11_witness_contract_reference import Witness
from ie_w13_highwater_freshness_reference import HighWater
from ie_w15_partial_advance_reconciliation_reference import event,reconcile

def main():
    with tempfile.TemporaryDirectory() as d:
        w=Witness(Path(d)/"ledger.sqlite")
        h=HighWater(Path(d)/"highwater.sqlite")
        a=w.advance("witness-writer",event(0))
        assert a["decision"]=="ACCEPTED_REFERENCE"
        assert h.advance("payment",0,1,a["checkpoint_hash"])=="ADVANCED_REFERENCE"
        b=w.advance("witness-writer",event(1))
        assert b["decision"]=="ACCEPTED_REFERENCE"
        # The absence of a trusted witness confirmation is not permission to commit.
        assert reconcile(w,h,event(1),authorized=False)=="UNRESOLVED_REVIEW_REQUIRED"
        print("IE-W16 OUTAGE GREEN: no reviewer confirmation means no checkpoint finalisation")
        barrier=threading.Barrier(2);results=[]
        def worker():
            barrier.wait(timeout=10)
            results.append(reconcile(w,h,event(1),authorized=True))
        threads=[threading.Thread(target=worker) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(10)
        assert all(not t.is_alive() for t in threads)
        assert results.count("RECONCILED_REFERENCE_CHECKPOINT")==1,results
        assert all(x in ("RECONCILED_REFERENCE_CHECKPOINT","CURRENT_REFERENCE_CHECKPOINT","UNRESOLVED_CONCURRENT_ADVANCE") for x in results),results
        assert h.current("payment")["sequence"]==2
        print("IE-W16 CONCURRENT GREEN: one high-water advance; other caller reconciled or observed current state")
        # This is NOT real outage simulation: trusted reviewer is only a boolean.
        assert reconcile(w,h,event(1),authorized=True)=="CURRENT_REFERENCE_CHECKPOINT"
        print("IE-W16 PRESERVED RED: caller-controlled reviewer flag can impersonate approval; no independent custody or authenticated recovery")
        print("NOT QUALIFIED: real outage transport, identity, externally signed receipt, provider reconciliation")
if __name__=="__main__":main()
