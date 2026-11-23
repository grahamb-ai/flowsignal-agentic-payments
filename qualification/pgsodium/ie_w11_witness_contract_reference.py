"""IE-W11 local witness API contract reference. Same-admin SQLite, NOT independent custody."""
import hashlib
import json
import sqlite3
import tempfile
import threading
from pathlib import Path

def digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class Witness:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS checkpoints(stream TEXT PRIMARY KEY, seq INTEGER NOT NULL, hash TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY, stream TEXT NOT NULL, seq INTEGER NOT NULL, hash TEXT NOT NULL, body TEXT NOT NULL)")
    def advance(self,identity,payload):
        if identity!="witness-writer":
            return {"decision":"REFUSED_UNAUTHENTICATED"}
        required=("event_id","stream","expected_sequence","authority_epoch","intent_id","target","outcome","evidence_hash")
        if not isinstance(payload,dict) or any(k not in payload for k in required):
            return {"decision":"REFUSED_INVALID_BINDING"}
        if any(not isinstance(payload[k],str) or not payload[k] for k in ("event_id","stream","intent_id","target","outcome","evidence_hash")):
            return {"decision":"REFUSED_INVALID_BINDING"}
        if type(payload["expected_sequence"]) is not int or payload["expected_sequence"]<0 or type(payload["authority_epoch"]) is not int or payload["authority_epoch"]<=0:
            return {"decision":"REFUSED_INVALID_BINDING"}
        with sqlite3.connect(self.path,timeout=10,isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM events WHERE event_id=?",(payload["event_id"],)).fetchone():
                db.execute("ROLLBACK")
                return {"decision":"REFUSED_REPLAY"}
            row=db.execute("SELECT seq,hash FROM checkpoints WHERE stream=?",(payload["stream"],)).fetchone()
            seq,previous=(row if row else (0,"GENESIS"))
            if payload["expected_sequence"]!=seq:
                db.execute("ROLLBACK")
                return {"decision":"REFUSED_STALE_SEQUENCE"}
            event_hash=digest({"previous":previous,"event":payload})
            db.execute("INSERT INTO events VALUES(?,?,?,?,?)",(payload["event_id"],payload["stream"],seq+1,event_hash,json.dumps(payload,sort_keys=True)))
            db.execute("INSERT INTO checkpoints VALUES(?,?,?) ON CONFLICT(stream) DO UPDATE SET seq=excluded.seq,hash=excluded.hash",(payload["stream"],seq+1,event_hash))
            db.execute("COMMIT")
            return {"decision":"ACCEPTED_REFERENCE","sequence":seq+1,"checkpoint_hash":event_hash}
    def read(self,stream):
        with sqlite3.connect(self.path) as db:
            row=db.execute("SELECT seq,hash FROM checkpoints WHERE stream=?",(stream,)).fetchone()
        return {"sequence":row[0],"checkpoint_hash":row[1]} if row else {"sequence":0,"checkpoint_hash":"GENESIS"}
    def unsupported(self,identity,operation):
        return {"decision":"REFUSED_UNSUPPORTED_OPERATION"}

def test():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"witness.sqlite"
        w=Witness(p)
        event={"event_id":"E1","stream":"payment","expected_sequence":0,"authority_epoch":4,"intent_id":"I1","target":"sandbox-provider","outcome":"REFUSED_AUTHORITY","evidence_hash":"reference-only"}
        assert w.advance("executor",event)["decision"]=="REFUSED_UNAUTHENTICATED"
        assert w.unsupported("witness-writer","reset")["decision"]=="REFUSED_UNSUPPORTED_OPERATION"
        assert w.advance("witness-writer",{**event,"authority_epoch":0})["decision"]=="REFUSED_INVALID_BINDING"
        results=[]
        gate=threading.Barrier(2)
        def worker():
            gate.wait()
            results.append(w.advance("witness-writer",event)["decision"])
        ts=[threading.Thread(target=worker) for _ in range(2)]
        for t in ts:t.start()
        for t in ts:t.join(10)
        assert sorted(results)==["ACCEPTED_REFERENCE","REFUSED_REPLAY"],results
        assert w.advance("witness-writer",{**event,"event_id":"E2"})["decision"]=="REFUSED_STALE_SEQUENCE"
        assert Witness(p).read("payment")["sequence"]==1
        print("IE-W11 LOCAL GREEN: unauthorized writer refused, reset refused, invalid epoch refused, concurrent duplicate once, stale sequence refused, restart retained")
        p.unlink()
        assert Witness(p).read("payment")["sequence"]==0
        print("IE-W11 PRESERVED RED: same administrator deleting SQLite witness resets high-water state")
        print("NOT QUALIFIED: real IAM, independent admin, authenticated rail, signed receipts, issuer key lifecycle, crash semantics")
if __name__=="__main__":test()
