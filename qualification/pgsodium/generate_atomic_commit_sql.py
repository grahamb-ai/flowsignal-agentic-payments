"""Generate isolated SQL qualification for signed atomic final commit."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
v=json.loads(subprocess.check_output([sys.executable,str(root/"harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],text=True))
c=v["canonical_instruction"]
def lit(x):return "'"+str(x).replace("'","''")+"'"
def call(intent,beneficiary,signature=True):
    return ("fs_provider.commit_signed_if_current("
        +",".join([lit("TEST-ISSUER"),"decode("+lit(v["signed_bytes_utf8_hex"])+",'hex')",
          "decode("+lit(v["signature_hex"] if signature else "00"*64)+",'hex')",
          lit(intent),lit(c["mandate_id"]),str(c["authority_epoch"]),lit(c["source_account"]),
          lit(beneficiary),str(c["amount_minor"]),lit(c["currency"]),lit(c["action"]),lit(c["target"])])
        +")")
print("\\set ON_ERROR_STOP on")
print(f"""INSERT INTO fs_provider.institutional_issuer_keys
(issuer_id,public_key,enabled,valid_from)
VALUES ('TEST-ISSUER',decode('{v["public_key_hex"]}','hex'),true,now()-interval '1 hour');
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked)
VALUES ('MANDATE-VECTOR',7,false);
RESET ROLE;
SET ROLE fs_commit_service;
SELECT 1 / CASE WHEN {call(c["payment_intent_id"],c["beneficiary"])}='COMMITTED'
 THEN 1 ELSE 0 END AS signed_commit;
SELECT 1 / CASE WHEN {call(c["payment_intent_id"],c["beneficiary"])}='REFUSED_DUPLICATE_INTENT'
 THEN 1 ELSE 0 END AS duplicate_refused;
SELECT 1 / CASE WHEN {call("UNSIGNED-ATTACK",c["beneficiary"],False)}='REFUSED_UNAUTHENTICATED_INSTRUCTION'
 THEN 1 ELSE 0 END AS forged_signature_refused;
SELECT 1 / CASE WHEN {call("OTHER-INTENT",c["beneficiary"])}='REFUSED_INVALID_BINDING'
 THEN 1 ELSE 0 END AS changed_intent_refused;
SELECT 1 / CASE WHEN {call(c["payment_intent_id"],"ATTACKER")}='REFUSED_INVALID_BINDING'
 THEN 1 ELSE 0 END AS changed_beneficiary_refused;
RESET ROLE;
SELECT 1 / CASE WHEN (SELECT count(*) FROM fs_provider.commits)=1
 THEN 1 ELSE 0 END AS one_durable_commit;
""")
