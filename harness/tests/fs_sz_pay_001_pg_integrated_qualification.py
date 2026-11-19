"""Integration qualification: real PostgreSQL executor login, signed instruction and guarded commit.

Ephemeral CI-only credentials. Does not qualify production IAM or a live rail.
"""
import os
import psycopg
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.engines.fs_sz_pay_001_postgres_provider import PostgreSQLProtectedLedger
from tests.provider_signed_fixture import signed_payment

def main():
    key = Ed25519PrivateKey.generate()
    dsn = os.environ["FS_QUAL_EXECUTOR_DSN"]
    def connect():
        return psycopg.connect(dsn)
    ledger = PostgreSQLProtectedLedger(
        connect=connect, verification_key=key.public_key(), mandate_id="MANDATE-INTEGRATED")
    payload = {
        "transaction_id": "INTEGRATED-INTENT-1", "payment_intent_id": "INTEGRATED-INTENT-1",
        "mandate_id": "MANDATE-INTEGRATED", "authority_epoch": 1,
        "source_account": "TREASURY-001", "beneficiary": "SUPPLIER-A",
        "amount": "1250.00", "currency": "GBP", "purpose": "qualification",
        "action": "payment.release", "target": "external-payment-provider",
    }
    signed = signed_payment(key, payload)
    forged = dict(signed, beneficiary="ATTACKER")
    assert ledger.transfer(forged)[0] == 403, "tampered beneficiary accepted"
    assert ledger.transfer(payload)[0] == 403, "unsigned instruction accepted"
    assert ledger.transfer(signed) == (201, {"status": "TRANSFER_RECORDED"})
    assert ledger.transfer(signed)[0] == 409, "duplicate intent accepted"
    with connect() as db:
        with db.cursor() as cur:
            assert cur.execute("SELECT current_user").fetchone()[0] == "fs_payment_executor"
            try:
                cur.execute("UPDATE fs_provider.mandates SET revoked=true WHERE id='MANDATE-INTEGRATED'")
                raise AssertionError("executor mutated institutional authority")
            except psycopg.errors.InsufficientPrivilege:
                db.rollback()
    # Institutionally controlled writer performs revocation via a separate DB login.
    with psycopg.connect(os.environ["FS_QUAL_WRITER_DSN"]) as db:
        with db.cursor() as cur:
            assert cur.execute("SELECT current_user").fetchone()[0] == "fs_authority_writer"
            cur.execute("UPDATE fs_provider.mandates SET revoked=true, epoch=2 WHERE id='MANDATE-INTEGRATED' AND epoch=1")
            assert cur.rowcount == 1
    later = signed_payment(key, {**payload, "transaction_id": "INTEGRATED-INTENT-2", "payment_intent_id": "INTEGRATED-INTENT-2"})
    assert ledger.transfer(later)[0] == 403, "payment committed after revocation"
    with connect() as db:
        with db.cursor() as cur:
            assert cur.execute("SELECT count(*) FROM fs_provider.commits WHERE mandate_id='MANDATE-INTEGRATED'").fetchone()[0] == 1
    print("INTEGRATED SIGNED PROVIDER PASS: issuer, executor login, writer login, revocation, duplicate, tampering")

if __name__ == "__main__":
    main()
