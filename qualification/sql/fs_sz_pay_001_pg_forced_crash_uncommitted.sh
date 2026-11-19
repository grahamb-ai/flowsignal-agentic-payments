#!/usr/bin/env bash
set -euo pipefail
# Crash point: after a guarded INSERT inside an open transaction, before COMMIT.
# Force-kill PostgreSQL and restart its existing ephemeral CI container.
# Expected: uncommitted transfer rolls back; intent may be committed exactly once
# after recovery if mandate is still valid. This is NOT a live-rail result.
: "${PGDATABASE:?}" "${PGUSER:?}" "${PGPASSWORD:?}"
container_id=$(docker ps --filter ancestor=postgres:16 --format '{{.ID}}' | head -n 1)
[[ -n "$container_id" ]] || { echo "PostgreSQL container not found"; exit 1; }
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-CRASH-UNCOMMITTED',1,false);
RESET ROLE;
SQL
# A single long-lived client holds a transaction open with the guarded
# commitment already inserted but not committed.
client_log=$(mktemp)
PGAPPNAME=fs_crash_uncommitted_client psql -v ON_ERROR_STOP=1 >"$client_log" 2>&1 <<'SQL' &
SET ROLE fs_payment_executor;
BEGIN;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('CRASH-UNCOMMITTED-INTENT','MANDATE-CRASH-UNCOMMITTED',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END;
SELECT pg_sleep(20);
COMMIT;
SQL
client_pid=$!
# Confirm that the transaction reached pg_sleep (therefore prior INSERT ran)
# using pg_stat_activity, not merely a timing assumption.
observed=0
for i in $(seq 1 40); do
 if psql -Atqc "SELECT count(*) FROM pg_stat_activity WHERE application_name='fs_crash_uncommitted_client' AND query LIKE 'SELECT pg_sleep(20)%' AND state='active'" | grep -qx '[1-9][0-9]*'; then observed=1; break; fi
 sleep 0.25
done
[[ "$observed" == 1 ]] || { cat "$client_log"; echo "Crash point not reached"; kill "$client_pid" || true; exit 1; }
docker kill "$container_id" >/dev/null
wait "$client_pid" || true
docker start "$container_id" >/dev/null
ready=0
for i in $(seq 1 60); do
 if pg_isready -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" >/dev/null 2>&1; then ready=1; break; fi
 sleep 1
done
[[ "$ready" == 1 ]] || { cat "$client_log"; echo "Postgres failed to recover"; exit 1; }
psql -v ON_ERROR_STOP=1 <<'SQL'
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE intent_id='CRASH-UNCOMMITTED-INTENT'
) THEN 1 ELSE 0 END AS uncommitted_crash_rolled_back;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('CRASH-UNCOMMITTED-INTENT','MANDATE-CRASH-UNCOMMITTED',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END AS retry_commits_once;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('CRASH-UNCOMMITTED-INTENT','MANDATE-CRASH-UNCOMMITTED',1,100,'BENEFICIARY')='REFUSED_DUPLICATE_INTENT' THEN 1 ELSE 0 END AS subsequent_retry_refused;
RESET ROLE;
SQL
rm -f "$client_log"
