#!/usr/bin/env bash
set -euo pipefail
# PostgreSQL concurrent revocation vs payment commitment, deterministic lock order.
# A separate writer transaction revokes and holds the mandate row lock.
# The executor must wait and then observe the committed revocation.
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-RACE',1,false);
RESET ROLE;
SQL
writer_log=$(mktemp)
executor_log=$(mktemp)
psql -v ON_ERROR_STOP=1 >"$writer_log" 2>&1 <<'SQL' &
SET ROLE fs_authority_writer;
BEGIN;
UPDATE fs_provider.mandates SET revoked=true,epoch=2 WHERE id='MANDATE-RACE' AND epoch=1;
SELECT pg_sleep(3);
COMMIT;
RESET ROLE;
SQL
writer_pid=$!
sleep 1
psql -v ON_ERROR_STOP=1 >"$executor_log" 2>&1 <<'SQL' &
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('RACE-INTENT','MANDATE-RACE',1,100,'BENEFICIARY')='REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS concurrent_post_revocation_refused;
RESET ROLE;
SQL
executor_pid=$!
wait "$writer_pid" || { cat "$writer_log"; exit 1; }
wait "$executor_pid" || { cat "$executor_log"; exit 1; }
cat "$writer_log" "$executor_log"
psql -v ON_ERROR_STOP=1 <<'SQL'
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE intent_id='RACE-INTENT'
) THEN 1 ELSE 0 END AS no_concurrent_commit;
SQL
rm -f "$writer_log" "$executor_log"
