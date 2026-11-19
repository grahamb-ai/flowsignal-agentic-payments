"""Durable signed-commit reconciliation after ambiguous acknowledgement.

The commit has already happened in signed_commit_lost_ack_retry.py. This is a
separate process that reads durable state after the first process exits.
Read-only reconciliation is deliberately independent of the caller's result.
"""
import psycopg2
ADMIN=dict(host="127.0.0.1",port=55432,dbname="postgres",user="postgres",password="qualification-only")
intent="RETRY-LOST-ACK-001"
with psycopg2.connect(**ADMIN) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT intent_id,mandate_id,epoch,amount_minor,beneficiary FROM fs_provider.commits WHERE intent_id=%s",(intent,))
        rows=cur.fetchall()
assert len(rows)==1,("unresolved or duplicate durable record",rows)
assert rows[0]==(intent,"RETRY-MANDATE-001",7,75000000,"BENEFICIARY-001"),rows
print("RECONCILIATION: COMMITTED; matching durable signed-intent fields; count=1; PASS")
print("READ-ONLY DB RECONCILIATION ONLY: no actual server crash, external rail settlement or durable signed receipt")
