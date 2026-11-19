#!/usr/bin/env bash
set -euo pipefail
# Forced server crash AFTER durable COMMIT, while caller session remains alive
# without receiving a final application-level acknowledgement.
: "${PGDATABASE:?}" "${PGUSER:?}" "${PGPASSWORD:?}"
container_id=$(docker ps --filter ancestor=postgres:16 --format '{{.ID}}' | head -n 1)
[[ -n "$container_id" ]] || { echo "PostgreSQL container missing"; exit 1; }
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-POSTCOMMIT-CRASH',1,false);
RESET ROLE;
SQL
client_log=$(mktemp)
PGAPPNAME=fs_postcommit_crash_client psql -v ON_ERROR_STOP=1 >"$client_log" 2>&1 <<'SQL' &
SET ROLE fs_payment_executor;
BEGIN;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('POSTCOMMIT-CRASH-INTENT','MANDATE-POSTCOMMIT-CRASH',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END;
COMMIT;
SELECT pg_sleep(20);
SQL
client_pid=$!
observed=0
for i in $(seq 1 80); do
 if psql -Atqc "SELECT count(*) FROM pg_stat_activity WHERE application_name='fs_postcommit_crash_client' AND query LIKE 'SELECT pg_sleep(20)%' AND state='active'" | grep -qx '[1-9][0-9]*'; then observed=1; break; fi
 sleep 0.25
done
[[ "$observed" == 1 ]] || { cat "$client_log"; kill "$client_pid" || true; echo "Post-commit crash point not reached"; exit 1; }
docker kill "$container_id" >/dev/null
wait "$client_pid" || true
docker start "$container_id" >/dev/null
ready=0
for i in $(seq 1 60); do
 if pg_isready -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" >/dev/null 2>&1; then ready=1; break; fi
 sleep 1
done
[[ "$ready" == 1 ]] || { echo "Database did not recover"; exit 1; }
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE intent_id='POSTCOMMIT-CRASH-INTENT')=1 THEN 1 ELSE 0 END AS postcommit_record_durable;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('POSTCOMMIT-CRASH-INTENT','MANDATE-POSTCOMMIT-CRASH',1,100,'BENEFICIARY')='REFUSED_DUPLICATE_INTENT' THEN 1 ELSE 0 END AS lost_ack_retry_refused;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE intent_id='POSTCOMMIT-CRASH-INTENT')=1 THEN 1 ELSE 0 END AS no_duplicate_commit;
RESET ROLE;
SQL
rm -f "$client_log"
