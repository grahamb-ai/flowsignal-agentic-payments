"""Generate real-login hostile challenges against signed final SQL boundary.

Must be run after the candidate schema and pgsodium extension are installed.
The login's access to the signed function is intentional; unsigned legacy
function access must be denied. No test signing private key is used here.
"""
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
v=json.loads(subprocess.check_output(
    [sys.executable,str(root/"harness/tests/fs_sz_pay_001_final_boundary_interop_vectors.py")],text=True))
c=v["canonical_instruction"]
def q(x):return "'"+str(x).replace("'","''")+"'"
args=[
 q("TEST-ISSUER"),"NULL::bytea","NULL::bytea",
 q("UNSIGNED-SERVICE-LOGIN"),q(c["mandate_id"]),str(c["authority_epoch"]),
 q(c["source_account"]),q("ATTACKER"),str(c["amount_minor"]),
 q(c["currency"]),q(c["action"]),q(c["target"])
]
print("\\set ON_ERROR_STOP on")
print("SELECT current_user AS authenticated_login;")
print("SELECT fs_provider.commit_signed_if_current("+",".join(args)+") AS unsigned_signed_function_outcome;")
print("SELECT count(*) AS unsigned_durable_commit_count FROM fs_provider.commits WHERE intent_id='UNSIGNED-SERVICE-LOGIN';")
print("SELECT has_function_privilege(current_user,'fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE') AS old_unsigned_function_executable;")
