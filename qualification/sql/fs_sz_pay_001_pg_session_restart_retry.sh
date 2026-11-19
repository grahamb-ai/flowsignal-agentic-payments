#!/usr/bin/env bash
set -euo pipefail
# Durable commit, lost acknowledgement and retry across a fresh PostgreSQL connection.
# This tests session restart, not a database-server crash.
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-RESTART',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('RESTART-INTENT','MANDATE-RESTART',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END AS first_commit;
RESET ROLE;
SQL
# Deliberately discard the first session's successful response as if the caller lost its acknowledgement.
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('RESTART-INTENT','MANDATE-RESTART',1,100,'BENEFICIARY')='REFUSED_DUPLICATE_INTENT' THEN 1 ELSE 0 END AS duplicate_after_session_restart;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE intent_id='RESTART-INTENT')=1 THEN 1 ELSE 0 END AS durable_single_commit;
RESET ROLE;
SQL
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
UPDATE fs_provider.mandates SET revoked=true,epoch=2 WHERE id='MANDATE-RESTART' AND epoch=1;
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('RESTART-NEW','MANDATE-RESTART',1,100,'BENEFICIARY')='REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS after_revocation_refused;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE mandate_id='MANDATE-RESTART')=1 THEN 1 ELSE 0 END AS no_second_commit;
RESET ROLE;
SQL
