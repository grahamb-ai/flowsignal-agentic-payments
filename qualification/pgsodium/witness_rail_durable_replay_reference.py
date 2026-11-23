"""IE-W08 durable replay ledger reference: restart and concurrent duplicate tests.

SQLite is a local reference only. Deleting the file defeats replay protection,
so this must not be described as independent, append-only or production-safe.
"""
import sqlite3
import tempfile
import threading
from pathlib import Path

def consume(db,event_id):
    with sqlite3.connect(db,timeout=15) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS seen(event_id TEXT PRIMARY KEY)")
        try:
            conn.execute("INSERT INTO seen(event_id) VALUES(?)",(event_id,))
            return "ACCEPTED_REFERENCE_EVENT"
        except sqlite3.IntegrityError:
            return "UNRESOLVED_REPLAYED_RAIL_EVENT"

def main():
    with tempfile.TemporaryDirectory() as directory:
        db=str(Path(directory)/"rail-seen.sqlite")
        assert consume(db,"RAIL-001")=="ACCEPTED_REFERENCE_EVENT"
        assert consume(db,"RAIL-001")=="UNRESOLVED_REPLAYED_RAIL_EVENT"
        print("IE-W08 RESTART: same rail event refused after separate connection reopen")
        barrier=threading.Barrier(2)
        results=[None,None]
        def worker(index):
            barrier.wait(timeout=10)
            results[index]=consume(db,"RAIL-002")
        workers=[threading.Thread(target=worker,args=(i,)) for i in range(2)]
        for w in workers:w.start()
        for w in workers:w.join(timeout=20)
        assert all(not w.is_alive() for w in workers)
        assert sorted(results)==["ACCEPTED_REFERENCE_EVENT","UNRESOLVED_REPLAYED_RAIL_EVENT"],results
        print("IE-W08 CONCURRENT: exactly one consumer accepted event, other refused replay")
        Path(db).unlink()
        assert consume(db,"RAIL-001")=="ACCEPTED_REFERENCE_EVENT"
        print("IE-W08 PRESERVED RED: deletion of locally controlled replay ledger permits old event again")
        print("LIMITATION: no independent custody, authenticated rail source, protected anti-rollback, durable key revocation or actual settlement")

if __name__=="__main__":
    main()
