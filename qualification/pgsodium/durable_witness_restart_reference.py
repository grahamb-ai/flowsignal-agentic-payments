"""IE-04 durable high-water witness: isolated SQLite reference.

Separate SQLite file and process-level restart simulate distinct storage, but
do NOT provide independently administered, append-only or tamperproof custody.
An operator with access to both stores can still roll back both.
"""
import json
import sqlite3
import tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from signed_checkpoint_rollback_reference import anchor,wire,signature_ok

def observe(db,stream,sequence):
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS highwater(stream TEXT PRIMARY KEY, sequence INTEGER NOT NULL CHECK(sequence>=0))")
        row=conn.execute("SELECT sequence FROM highwater WHERE stream=?",(stream,)).fetchone()
        if row and sequence<row[0]:
            return "REFUSED_STALE_SIGNED_ANCHOR"
        conn.execute("INSERT INTO highwater(stream,sequence) VALUES (?,?) ON CONFLICT(stream) DO UPDATE SET sequence=MAX(sequence,excluded.sequence)",(stream,sequence))
        return "ACCEPTED_REFERENCE_ANCHOR"

def main():
    signer=Ed25519PrivateKey.generate()
    trusted=signer.public_key()
    events=[{"id":1,"intent":"A"},{"id":2,"intent":"B"}]
    older=wire(anchor(events[:1]))
    latest=wire(anchor(events))
    older_sig=signer.sign(older)
    latest_sig=signer.sign(latest)
    with tempfile.TemporaryDirectory() as directory:
        db=str(Path(directory)/"independent-witness.sqlite")
        assert signature_ok(latest,latest_sig,trusted)
        assert observe(db,"fs-sz-pay-001",2)=="ACCEPTED_REFERENCE_ANCHOR"
        print("IE-04 DURABLE WITNESS: sequence 2 recorded to separate SQLite file")
        # Reopen the witness in a separate connection after simulated restart.
        assert signature_ok(older,older_sig,trusted)
        assert observe(db,"fs-sz-pay-001",1)=="REFUSED_STALE_SIGNED_ANCHOR"
        print("IE-04 RESTART: authentic older signed anchor refused after reopening durable witness")
        assert observe(db,"fs-sz-pay-001",2)=="ACCEPTED_REFERENCE_ANCHOR"
        print("IE-04 CURRENT: current signed anchor accepted after restart")
        # Preserve known weakness: an attacker who can rewrite witness store
        # can erase its monotonic state; this is not independently controlled.
        Path(db).unlink()
        assert observe(db,"fs-sz-pay-001",1)=="ACCEPTED_REFERENCE_ANCHOR"
        print("IE-04 WITNESS-STORE COMPROMISE RED: deleted high-water store permits authentic old anchor")
    print("LIMITATION: separate file only, no independent identity, immutable external anchor, multi-writer CAS or actual payment outcome")

if __name__=="__main__":
    main()
