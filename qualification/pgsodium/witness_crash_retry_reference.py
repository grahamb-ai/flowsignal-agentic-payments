"""IE-W05: durable issuance / lost acknowledgement / crash-point reference.

SQLite transaction commits event + receipt atomically. A process termination
before COMMIT rolls both back. After COMMIT, retry returns same receipt.
This is not an independent witness service or external payment evidence.
"""
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":")).encode()

def initialize(db):
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE stream(id TEXT PRIMARY KEY, seq INTEGER NOT NULL)")
        conn.execute("CREATE TABLE receipts(intent TEXT PRIMARY KEY, stream TEXT NOT NULL, seq INTEGER NOT NULL, receipt BLOB NOT NULL, UNIQUE(stream,seq))")
        conn.execute("INSERT INTO stream VALUES('payments',0)")

def issue(db,intent,crash_before_commit=False):
    conn=sqlite3.connect(db,isolation_level=None,timeout=10)
    try:
        conn.execute("BEGIN IMMEDIATE")
        prior=conn.execute("SELECT seq,receipt FROM receipts WHERE intent=?",(intent,)).fetchone()
        if prior:
            conn.execute("COMMIT")
            return ("REPLAY_SAME_RECEIPT",prior[0],prior[1])
        seq=conn.execute("SELECT seq FROM stream WHERE id='payments'").fetchone()[0]+1
        payload=canonical({"stream":"payments","intent":intent,"sequence":seq,"outcome":"REFERENCE_ACCEPTED"})
        conn.execute("INSERT INTO receipts VALUES(?,?,?,?)",(intent,"payments",seq,payload))
        conn.execute("UPDATE stream SET seq=? WHERE id='payments'",(seq,))
        if crash_before_commit:
            # Equivalent transactional state to a backend killed before COMMIT.
            conn.close()
            return ("CRASH_BEFORE_COMMIT",seq,None)
        conn.execute("COMMIT")
        return ("ISSUED",seq,payload)
    finally:
        try:conn.close()
        except Exception:pass

def count(db):
    with sqlite3.connect(db) as conn:
        return conn.execute("SELECT count(*) FROM receipts").fetchone()[0],conn.execute("SELECT seq FROM stream WHERE id='payments'").fetchone()[0]

def main():
    with tempfile.TemporaryDirectory() as directory:
        db=str(Path(directory)/"witness.sqlite")
        initialize(db)
        first=issue(db,"IE-W05-01",crash_before_commit=True)
        assert first[0]=="CRASH_BEFORE_COMMIT" and count(db)==(0,0)
        print("IE-W05 PRE-COMMIT INTERRUPTION: no durable receipt and no sequence advance")
        accepted=issue(db,"IE-W05-01")
        assert accepted[0]=="ISSUED" and count(db)==(1,1)
        print("IE-W05 RETRY AFTER ROLLBACK: one durable receipt and sequence 1")
        retry=issue(db,"IE-W05-01")
        assert retry[0]=="REPLAY_SAME_RECEIPT" and retry[2]==accepted[2] and count(db)==(1,1)
        print("IE-W05 LOST ACK: same receipt returned, no duplicate sequence or receipt")
        second=issue(db,"IE-W05-02")
        assert second[0]=="ISSUED" and second[1]==2 and count(db)==(2,2)
        print("IE-W05 NEW INTENT: next sequence 2, exactly two durable receipts")
        print("LIMITATION: simulated connection termination only; no OS SIGKILL, independent signer, append-only external store or rail settlement")

if __name__=="__main__":main()
