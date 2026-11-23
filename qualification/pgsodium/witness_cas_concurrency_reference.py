"""IE-W04 local durable CAS concurrency characterisation, not an independent witness.

Two processes/connections race to advance the same stream sequence in SQLite.
Only one can win sequence 0->1; the other must receive a conflict. This does
not prove independent operator identity, key custody or external rail outcomes.
"""
import sqlite3
import tempfile
import threading
from pathlib import Path

def attempt(path,barrier,result,index):
    conn=sqlite3.connect(path,timeout=10,isolation_level=None)
    try:
        barrier.wait(timeout=10)
        conn.execute("BEGIN IMMEDIATE")
        cursor=conn.execute("UPDATE witness SET sequence=1 WHERE stream='payment' AND sequence=0")
        if cursor.rowcount==1:
            conn.execute("COMMIT")
            result[index]="ACCEPTED"
        else:
            conn.execute("ROLLBACK")
            result[index]="REFUSED_STALE_SEQUENCE"
    except Exception as exc:
        try:conn.execute("ROLLBACK")
        except sqlite3.Error:pass
        result[index]="ERROR:"+repr(exc)
    finally:conn.close()

def main():
    with tempfile.TemporaryDirectory() as directory:
        path=str(Path(directory)/"witness.sqlite")
        with sqlite3.connect(path) as conn:
            conn.execute("CREATE TABLE witness(stream TEXT PRIMARY KEY, sequence INTEGER NOT NULL)")
            conn.execute("INSERT INTO witness VALUES('payment',0)")
        barrier=threading.Barrier(2)
        results=[None,None]
        threads=[threading.Thread(target=attempt,args=(path,barrier,results,i)) for i in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=15)
        assert all(not t.is_alive() for t in threads), "threads did not finish"
        assert sorted(results)==["ACCEPTED","REFUSED_STALE_SEQUENCE"],results
        with sqlite3.connect(path) as conn:
            seq=conn.execute("SELECT sequence FROM witness WHERE stream='payment'").fetchone()[0]
        assert seq==1,seq
        print("IE-W04 LOCAL CAS: two concurrent connections, exactly one ACCEPTED and one REFUSED_STALE_SEQUENCE; durable sequence=1")
        print("LIMITATION: SQLite single-file reference, no independent principal, external store, signed issuance or production concurrency qualification")

if __name__=="__main__":main()
