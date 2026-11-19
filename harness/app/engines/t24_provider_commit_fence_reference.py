"""T24 bounded provider-side commit fence.

One SQLite authority database serialises revocation and commitment in a
single transaction. This is a cooperating simulated provider, not a live rail.
"""
import sqlite3
from pathlib import Path

class ProviderCommitFence:
    def __init__(self, path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS mandates (id TEXT PRIMARY KEY, epoch INTEGER NOT NULL, revoked INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS commits (intent_id TEXT PRIMARY KEY, mandate_id TEXT NOT NULL, epoch INTEGER NOT NULL)")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10.0)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    def establish(self,mandate_id,epoch=1):
        with self._connect() as db:
            db.execute("INSERT INTO mandates(id,epoch,revoked) VALUES(?,?,0)",(mandate_id,epoch))
    def revoke(self,mandate_id):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE mandates SET revoked=1,epoch=epoch+1 WHERE id=?",(mandate_id,))
    def commit(self,mandate_id,authority_epoch,intent_id):
        if not intent_id:
            raise ValueError("stable payment intent required")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state=db.execute("SELECT epoch,revoked FROM mandates WHERE id=?",(mandate_id,)).fetchone()
            if state is None or state[1] or state[0]!=authority_epoch:
                return "REFUSED_AUTHORITY"
            cur=db.execute("INSERT OR IGNORE INTO commits(intent_id,mandate_id,epoch) VALUES(?,?,?)",(intent_id,mandate_id,authority_epoch))
            return "COMMITTED" if cur.rowcount==1 else "REFUSED_DUPLICATE_INTENT"
    def count(self):
        with self._connect() as db:
            return db.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
