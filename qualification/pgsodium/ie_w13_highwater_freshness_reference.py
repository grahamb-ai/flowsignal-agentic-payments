"""IE-W13 dual-store high-water reference; same administrator, NOT independent custody."""
import tempfile
from pathlib import Path
import sqlite3
from ie_w11_witness_contract_reference import Witness

class HighWater:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS highwater(stream TEXT PRIMARY KEY, seq INTEGER NOT NULL, hash TEXT NOT NULL)")
    def advance(self,stream,expected_seq,new_seq,checkpoint_hash):
        with sqlite3.connect(self.path,timeout=10,isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT seq FROM highwater WHERE stream=?",(stream,)).fetchone()
            current=row[0] if row else 0
            if expected_seq!=current or new_seq!=current+1:
                db.execute("ROLLBACK")
                return "REFUSED_STALE_SEQUENCE"
            db.execute("INSERT INTO highwater VALUES(?,?,?) ON CONFLICT(stream) DO UPDATE SET seq=excluded.seq,hash=excluded.hash",(stream,new_seq,checkpoint_hash))
            db.execute("COMMIT")
            return "ADVANCED_REFERENCE"
    def current(self,stream):
        with sqlite3.connect(self.path) as db:
            row=db.execute("SELECT seq,hash FROM highwater WHERE stream=?",(stream,)).fetchone()
        return {"sequence":row[0],"checkpoint_hash":row[1]} if row else {"sequence":0,"checkpoint_hash":"GENESIS"}

def verify_latest(receipt_body,highwater):
    if highwater is None: return "UNRESOLVED_WITNESS_UNAVAILABLE"
    if receipt_body.get("sequence")!=highwater["sequence"] or receipt_body.get("checkpoint_hash")!=highwater["checkpoint_hash"]:
        return "REFUSED_OLD_OR_CONFLICTING_CHECKPOINT"
    return "CURRENT_REFERENCE_CHECKPOINT"

def main():
    with tempfile.TemporaryDirectory() as d:
        ledger=Path(d)/"ledger.sqlite"
        anchor=Path(d)/"highwater.sqlite"
        witness=Witness(ledger)
        hw=HighWater(anchor)
        for seq in (0,1):
            payload={"event_id":f"E{seq}","stream":"payment","expected_sequence":seq,"authority_epoch":4,"intent_id":f"I{seq}","target":"sandbox","outcome":"REFUSED_AUTHORITY","evidence_hash":f"synthetic-{seq}"}
            result=witness.advance("witness-writer",payload)
            assert result["decision"]=="ACCEPTED_REFERENCE"
            assert hw.advance("payment",seq,result["sequence"],result["checkpoint_hash"])=="ADVANCED_REFERENCE"
            if seq==0: old={"sequence":result["sequence"],"checkpoint_hash":result["checkpoint_hash"]}
        latest=witness.read("payment")
        assert verify_latest(latest,hw.current("payment"))=="CURRENT_REFERENCE_CHECKPOINT"
        assert verify_latest(old,hw.current("payment"))=="REFUSED_OLD_OR_CONFLICTING_CHECKPOINT"
        assert hw.advance("payment",0,1,"rollback")=="REFUSED_STALE_SEQUENCE"
        assert verify_latest(latest,None)=="UNRESOLVED_WITNESS_UNAVAILABLE"
        ledger.unlink()
        assert verify_latest(Witness(ledger).read("payment"),hw.current("payment"))=="REFUSED_OLD_OR_CONFLICTING_CHECKPOINT"
        assert HighWater(anchor).current("payment")["sequence"]==2
        print("IE-W13 LOCAL GREEN: old authentic checkpoint refused; local ledger deletion detected; high-water survives ledger reset; outage unresolved")
        anchor.unlink()
        assert HighWater(anchor).current("payment")["sequence"]==0
        print("IE-W13 PRESERVED RED: same administrator deleting high-water store defeats freshness custody")
        print("NOT QUALIFIED: separate administrator, signed checkpoint authentication, atomic cross-store commit, real rail")
if __name__=="__main__":main()
