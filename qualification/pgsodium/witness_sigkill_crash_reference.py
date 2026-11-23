"""IE-W05 actual subprocess SIGKILL before and after SQLite commit.

Isolated local process crash test. No independent trust domain or external rail.
"""
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from witness_crash_retry_reference import initialize,issue,count

WORKER = r'''
import os,signal,sqlite3,sys
db,phase=sys.argv[1:]
conn=sqlite3.connect(db,isolation_level=None,timeout=10)
conn.execute("BEGIN IMMEDIATE")
seq=conn.execute("SELECT seq FROM stream WHERE id='payments'").fetchone()[0]+1
intent="IE-W05-SIGKILL-"+phase
payload=bytes("reference-receipt:"+intent,"utf-8")
conn.execute("INSERT INTO receipts VALUES(?,?,?,?)",(intent,"payments",seq,payload))
conn.execute("UPDATE stream SET seq=? WHERE id='payments'",(seq,))
if phase=="post":
    conn.execute("COMMIT")
print("READY_TO_KILL",flush=True)
os.kill(os.getpid(),signal.SIGKILL)
'''

def killed_worker(db,phase):
    result=subprocess.run([sys.executable,"-c",WORKER,db,phase],capture_output=True,text=True,timeout=15)
    assert result.returncode==-signal.SIGKILL,(result.returncode,result.stdout,result.stderr)
    assert "READY_TO_KILL" in result.stdout,result.stdout

def main():
    with tempfile.TemporaryDirectory() as directory:
        db=str(Path(directory)/"witness.sqlite")
        initialize(db)
        killed_worker(db,"pre")
        assert count(db)==(0,0),count(db)
        print("IE-W05 SIGKILL PRE-COMMIT: zero durable receipts; sequence zero")
        recovered=issue(db,"IE-W05-SIGKILL-pre")
        assert recovered[0]=="ISSUED" and count(db)==(1,1)
        print("IE-W05 SIGKILL PRE-COMMIT RETRY: one receipt, sequence one")
        killed_worker(db,"post")
        assert count(db)==(2,2),count(db)
        print("IE-W05 SIGKILL POST-COMMIT: receipt and sequence persisted despite lost acknowledgement")
        again=issue(db,"IE-W05-SIGKILL-post")
        assert again[0]=="REPLAY_SAME_RECEIPT" and count(db)==(2,2)
        print("IE-W05 SIGKILL POST-COMMIT RETRY: original receipt returned, zero duplicates")
        print("LIMITATION: local SQLite process kill only; no machine power loss, independent signer, storage isolation or external payment outcome")

if __name__=="__main__":main()
