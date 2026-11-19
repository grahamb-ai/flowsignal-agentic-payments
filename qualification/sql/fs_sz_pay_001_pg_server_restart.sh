#!/usr/bin/env bash
set -euo pipefail
# Server restart recovery qualification. Runs inside GitHub Actions runner against
# a Docker PostgreSQL service. No live rail and no claims about ambiguous remote effects.
: "${PGDATABASE:?}" "${PGUSER:?}" "${PGPASSWORD:?}"
container_id=$(docker ps --filter ancestor=postgres:16 --format '{{.ID}}' | head -n 1)
if [[ -z "$container_id" ]]; then echo "PostgreSQL service container not found"; exit 1; fi
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-SERVER-RESTART',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('SERVER-RESTART-INTENT','MANDATE-SERVER-RESTART',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END AS committed_before_server_restart;
RESET ROLE;
SQL
echo "Restarting ephemeral PostgreSQL service container $container_id"
docker restart "$container_id" >/dev/null
ready=0
for attempt in $(seq 1 40); do
 if pg_isready -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" >/dev/null 2>&1; then ready=1; break; fi
 sleep 1
done
[[ "$ready" == 1 ]] || { echo "PostgreSQL unavailable after restart"; exit 1; }
psql -v ON_ERROR_STOP=1 <<'SQL'
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('SERVER-RESTART-INTENT','MANDATE-SERVER-RESTART',1,100,'BENEFICIARY')='REFUSED_DUPLICATE_INTENT' THEN 1 ELSE 0 END AS restart_retry_refused;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits WHERE intent_id='SERVER-RESTART-INTENT')=1 THEN 1 ELSE 0 END AS durable_record_survived;
RESET ROLE;
SET ROLE fs_authority_writer;
UPDATE fs_provider.mandates SET revoked=true,epoch=2 WHERE id='MANDATE-SERVER-RESTART' AND epoch=1;
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('SERVER-RESTART-NEW','MANDATE-SERVER-RESTART',1,100,'BENEFICIARY')='REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS post_restart_revocation_refused;
RESET ROLE;
SQL
