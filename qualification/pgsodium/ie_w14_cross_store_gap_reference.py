"""IE-W14 crash-gap characterisation between ledger and high-water stores.
Local same-admin reference. Preserve cross-store non-atomic RED.
"""
import tempfile
from pathlib import Path
from ie_w11_witness_contract_reference import Witness
from ie_w13_highwater_freshness_reference import HighWater,verify_latest

def event(seq):
    return {"event_id":f"E{seq}","stream":"payment","expected_sequence":seq,"authority_epoch":4,"intent_id":f"I{seq}","target":"sandbox","outcome":"REFUSED_AUTHORITY","evidence_hash":f"synthetic-{seq}"}

def main():
    with tempfile.TemporaryDirectory() as d:
        w=Witness(Path(d)/"ledger.sqlite")
        h=HighWater(Path(d)/"highwater.sqlite")
        first=w.advance("witness-writer",event(0))
        assert first["decision"]=="ACCEPTED_REFERENCE"
        assert h.advance("payment",0,1,first["checkpoint_hash"])=="ADVANCED_REFERENCE"
        # Simulated interruption between independent durable writes.
        second=w.advance("witness-writer",event(1))
        assert second["decision"]=="ACCEPTED_REFERENCE"
        assert w.read("payment")["sequence"]==2 and h.current("payment")["sequence"]==1
        assert verify_latest(w.read("payment"),h.current("payment"))=="REFUSED_OLD_OR_CONFLICTING_CHECKPOINT"
        print("IE-W14 GREEN: partial advance detected as unresolved mismatch, not current witness evidence")
        # Critical limitation: if a caller treated ledger acceptance as final, it would
        # have acknowledged E1 without a protected high-water advancement.
        print("IE-W14 PRESERVED RED: ledger accepted event before high-water confirmation; no atomic cross-store commit")
        # A new caller cannot naively replay the same event: duplicate in ledger.
        assert w.advance("witness-writer",event(1))["decision"]=="REFUSED_REPLAY"
        print("IE-W14 RECOVERY BLOCKER: duplicate prevents naive retry; reconciliation protocol required")
        print("NOT QUALIFIED: independent operator, authenticated receipts, provider outcome, crash-safe cross-store protocol")
if __name__=="__main__":main()
