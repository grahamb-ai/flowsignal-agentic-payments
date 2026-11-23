#!/usr/bin/env bash
# IE-W10 read-only GCP inventory. Run locally with an authorised, read-only gcloud identity.
# NO deployments, IAM writes, resource creation, or public artifact uploads.
set -euo pipefail
: "${FS_GCP_PROJECT:?Set FS_GCP_PROJECT to an authorised non-production project ID}"
: "${FS_GCP_REGION:=europe-west2}"
command -v gcloud >/dev/null || { echo "gcloud CLI required" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 required" >&2; exit 2; }
OUT="${FS_IE_W10_OUT:-./ie-w10-private-evidence}"
mkdir -p "$OUT"
chmod 700 "$OUT"
umask 077
printf '%s\n' 'IE-W10 READ-ONLY INVENTORY / NOT A QUALIFICATION' > "$OUT/disposition.txt"
gcloud config get-value account > "$OUT/inventory-principal.txt" 2>&1
gcloud projects describe "$FS_GCP_PROJECT" --format=json > "$OUT/project.json"
gcloud projects get-iam-policy "$FS_GCP_PROJECT" --format=json > "$OUT/project-iam.json"
gcloud iam service-accounts list --project="$FS_GCP_PROJECT" --format=json > "$OUT/service-accounts.json"
gcloud run services list --project="$FS_GCP_PROJECT" --region="$FS_GCP_REGION" --format=json > "$OUT/cloud-run-services.json"
gcloud firestore databases list --project="$FS_GCP_PROJECT" --format=json > "$OUT/firestore-databases.json"
python3 - "$OUT" <<'PY'
import json, pathlib, sys
p=pathlib.Path(sys.argv[1])
for name in ("project","project-iam","service-accounts","cloud-run-services","firestore-databases"):
    value=json.loads((p/(name+".json")).read_text())
    print(name, "items:",len(value) if isinstance(value,list) else "object")
print("PRELIMINARY ONLY: service-level IAM, impersonation, inherited grants, data permissions, and independent witness custody NOT VERIFIED")
PY
echo "Evidence stored locally in $OUT. Treat as sensitive IAM metadata; do NOT commit or upload to public CI."
