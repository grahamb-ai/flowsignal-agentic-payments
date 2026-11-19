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

    def commit_transfer(self, mandate_id, authority_epoch, intent_id, payload):
        """Atomically check standing and record the actual represented transfer.

        The same SQLite transaction owns revocation ordering, uniqueness, and
        the transfer record. This is not a real payment provider or live rail.
        """
        from decimal import Decimal, InvalidOperation
        try:
            amount = Decimal(str(payload["amount"]))
            minor = amount * 100
            if amount <= 0 or minor != minor.to_integral_value():
                return "REFUSED_INVALID_AMOUNT"
            amount_minor = int(minor)
        except (KeyError, ValueError, InvalidOperation, TypeError):
            return "REFUSED_INVALID_AMOUNT"
        if not intent_id or not mandate_id:
            return "REFUSED_INVALID_BINDING"
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS transfer_records (
                intent_id TEXT PRIMARY KEY, mandate_id TEXT NOT NULL,
                epoch INTEGER NOT NULL, amount_minor INTEGER NOT NULL,
                beneficiary TEXT NOT NULL, source_account TEXT NOT NULL,
                currency TEXT NOT NULL
            )""")
            db.execute("BEGIN IMMEDIATE")
            state = db.execute(
                "SELECT epoch, revoked FROM mandates WHERE id=?", (mandate_id,)
            ).fetchone()
            if state is None or state[1] or state[0] != authority_epoch:
                return "REFUSED_AUTHORITY"
            if db.execute("SELECT 1 FROM commits WHERE intent_id=?", (intent_id,)).fetchone():
                return "REFUSED_DUPLICATE_INTENT"
            if payload.get("currency") != "GBP" or not payload.get("beneficiary") or not payload.get("source_account"):
                return "REFUSED_INVALID_BINDING"
            db.execute("INSERT INTO commits(intent_id,mandate_id,epoch) VALUES(?,?,?)",
                       (intent_id,mandate_id,authority_epoch))
            db.execute("""INSERT INTO transfer_records
                (intent_id,mandate_id,epoch,amount_minor,beneficiary,source_account,currency)
                VALUES(?,?,?,?,?,?,?)""",
                (intent_id,mandate_id,authority_epoch,amount_minor,
                 payload["beneficiary"],payload["source_account"],payload["currency"]))
            return "COMMITTED"

    def transfer_count(self):
        with self._connect() as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='transfer_records'").fetchone()
            return db.execute("SELECT COUNT(*) FROM transfer_records").fetchone()[0] if exists else 0

    def reconcile_transfer(self, intent_id, instruction):
        """Read durable provider commitment by stable intent without creating a transfer.

        A missing record is NOT proof that a payment never occurred on another
        route or rail. Caller authentication is enforced by the provider layer.
        """
        from decimal import Decimal, InvalidOperation
        with self._connect() as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='transfer_records'").fetchone()
            if not exists:
                return {"status": "NOT_FOUND_IN_REFERENCE_LEDGER"}
            row = db.execute(
                "SELECT mandate_id,epoch,amount_minor,beneficiary,source_account,currency "
                "FROM transfer_records WHERE intent_id=?", (intent_id,)
            ).fetchone()
            if row is None:
                return {"status": "NOT_FOUND_IN_REFERENCE_LEDGER"}
            try:
                amount_minor = int(Decimal(str(instruction["amount"])) * 100)
            except (KeyError, InvalidOperation, ValueError, TypeError):
                return {"status": "REFUSED_BINDING"}
            expected = (instruction.get("mandate_id"), instruction.get("authority_epoch"),
                        amount_minor, instruction.get("beneficiary"),
                        instruction.get("source_account"), instruction.get("currency"))
            if row != expected:
                return {"status": "REFUSED_BINDING"}
            return {"status": "TRANSFER_RECORDED", "payment_intent_id": intent_id}
