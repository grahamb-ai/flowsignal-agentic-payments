#!/usr/bin/env bash
set -euo pipefail
# Reverse ordering: the payment's guarded commit acquires the mandate lock first.
# A later revocation cannot retroactively invalidate an already formed commitment.
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-REVERSE',1,false);
RESET ROLE;
SQL
executor_log=$(mktemp)
writer_log=$(mktemp)
psql -v ON_ERROR_STOP=1 >"$executor_log" 2>&1 <<'SQL' &
SET ROLE fs_payment_executor;
BEGIN;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('REVERSE-INTENT','MANDATE-REVERSE',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END AS commitment_before_revocation;
SELECT pg_sleep(3);
COMMIT;
RESET ROLE;
SQL
executor_pid=$!
sleep 1
psql -v ON_ERROR_STOP=1 >"$writer_log" 2>&1 <<'SQL' &
SET ROLE fs_authority_writer;
BEGIN;
UPDATE fs_provider.mandates SET revoked=true,epoch=2 WHERE id='MANDATE-REVERSE' AND epoch=1;
COMMIT;
RESET ROLE;
SQL
writer_pid=$!
wait "$executor_pid" || { cat "$executor_log"; exit 1; }
wait "$writer_pid" || { cat "$writer_log"; exit 1; }
cat "$executor_log" "$writer_log"
psql -v ON_ERROR_STOP=1 <<'SQL'
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE intent_id='REVERSE-INTENT')=1 THEN 1 ELSE 0 END AS committed_before_revocation_remains;
SELECT 1 / CASE WHEN (SELECT revoked AND epoch=2 FROM fs_provider.mandates WHERE id='MANDATE-REVERSE') THEN 1 ELSE 0 END AS revocation_applied;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('REVERSE-AFTER','MANDATE-REVERSE',1,100,'BENEFICIARY')='REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS subsequent_commit_refused;
RESET ROLE;
SQL
rm -f "$executor_log" "$writer_log"
