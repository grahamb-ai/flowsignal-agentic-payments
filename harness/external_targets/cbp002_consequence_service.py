from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock


class ExternalLedger:
    """State owned by the external test service, not FlowSignal."""

    def __init__(self, *, fence=None, mandate_id=None, authority_epoch=None, legacy_test_mode=False, authorization_public_key=None) -> None:
        # Fenced mode uses the provider's single authoritative commit store.
        # Legacy sandbox mode remains explicitly unqualified for route closure.
        if fence is None and not legacy_test_mode:
            raise RuntimeError('REFUSED_UNQUALIFIED_PROVIDER_ROUTE: authoritative fence required')
        self._authorization_public_key = authorization_public_key
        self._fence = fence
        self._mandate_id = mandate_id
        self._authority_epoch = authority_epoch
        if fence is not None and (not mandate_id or authority_epoch is None):
            raise ValueError('fenced ledger requires mandate and authority epoch')
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with getattr(self, "_lock", Lock()):
            self.source_balance = 5_000_000.0
            self.beneficiary_balances: dict[str, float] = {}
            self.transfers: list[dict] = []

    def snapshot(self) -> dict:
        if self._fence is not None:
            return {'transfer_count': self._fence.transfer_count(), 'mode': 'FENCED_REFERENCE'}
        with self._lock:
            return {
                "source_balance": self.source_balance,
                "beneficiary_balances": dict(self.beneficiary_balances),
                "transfer_count": len(self.transfers),
                "transfers": list(self.transfers),
            }

    def reconcile(self, payload: dict) -> tuple[int, dict]:
        """Authenticated, read-only status check for a specific signed instruction."""
        if self._fence is None:
            return 403, {"status": "REFUSED_UNQUALIFIED_PROVIDER_ROUTE"}
        from app.engines.provider_instruction_verifier import verify_instruction
        if not verify_instruction(payload, self._authorization_public_key):
            return 403, {"status": "REFUSED_UNAUTHENTICATED_INSTRUCTION"}
        if (payload.get("transaction_id") != payload.get("payment_intent_id")
                or payload.get("mandate_id") != self._mandate_id):
            return 403, {"status": "REFUSED_BINDING"}
        result = self._fence.reconcile_transfer(payload["payment_intent_id"], payload)
        return (200 if result["status"] in ("TRANSFER_RECORDED", "NOT_FOUND_IN_REFERENCE_LEDGER")
                else 403), result

    def transfer(self, payload: dict) -> tuple[int, dict]:
        required = {
            "transaction_id",
            "source_account",
            "beneficiary",
            "amount",
            "currency",
            "purpose",
        }
        missing = sorted(required - payload.keys())
        if missing:
            return 400, {"error": "MISSING_FIELDS", "fields": missing}

        if payload["currency"] != "GBP":
            return 400, {"error": "UNSUPPORTED_CURRENCY"}

        try:
            amount = float(payload["amount"])
        except (TypeError, ValueError):
            return 400, {"error": "INVALID_AMOUNT"}

        if amount <= 0:
            return 400, {"error": "INVALID_AMOUNT"}

        if self._fence is not None:
            from app.engines.provider_instruction_verifier import verify_instruction
            if not verify_instruction(payload, self._authorization_public_key):
                return 403, {"status": "REFUSED_UNAUTHENTICATED_INSTRUCTION"}
            # Do not allow caller-supplied mandate/epoch to be silently
            # evaluated under a different configured authority.
            if (payload.get("mandate_id") != self._mandate_id
                    or payload.get("authority_epoch") != self._authority_epoch):
                return 403, {"status": "REFUSED_AUTHORITY"}
            result = self._fence.commit_transfer(
                self._mandate_id, self._authority_epoch,
                str(payload["transaction_id"]), payload,
            )
            if result == "COMMITTED":
                return 201, {"status": "TRANSFER_RECORDED"}
            return 403 if result == "REFUSED_AUTHORITY" else 409, {"status": result}

        with self._lock:
            if any(t["transaction_id"] == payload["transaction_id"] for t in self.transfers):
                return 409, {"error": "DUPLICATE_TRANSACTION"}
            if amount > self.source_balance:
                return 409, {"error": "INSUFFICIENT_FUNDS"}

            self.source_balance -= amount
            beneficiary = str(payload["beneficiary"])
            self.beneficiary_balances[beneficiary] = (
                self.beneficiary_balances.get(beneficiary, 0.0) + amount
            )
            transfer = {
                "transaction_id": str(payload["transaction_id"]),
                "source_account": str(payload["source_account"]),
                "beneficiary": beneficiary,
                "amount": amount,
                "currency": str(payload["currency"]),
                "purpose": str(payload["purpose"]),
            }
            self.transfers.append(transfer)
            return 201, {"status": "TRANSFER_RECORDED", "transfer": transfer}


LEDGER = None  # Set explicitly by main(); never silently enable an unfenced route.


class Handler(BaseHTTPRequestHandler):
    server_version = "CBP002ExternalConsequence/1.0"

    def _json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _respond(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
            return
        if self.path == "/state":
            self._respond(200, LEDGER.snapshot())
            return
        self._respond(404, {"error": "NOT_FOUND"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._respond(400, {"error": "INVALID_JSON"})
            return

        if self.path == "/payments/reconcile":
            status, result = LEDGER.reconcile(payload)
            self._respond(status, result)
            return

        if self.path == "/payments":
            status, result = LEDGER.transfer(payload)
            self._respond(status, result)
            return

        if self.path == "/admin/reset":
            LEDGER.reset()
            self._respond(200, LEDGER.snapshot())
            return

        self._respond(404, {"error": "NOT_FOUND"})

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--legacy-test-mode", action="store_true", help="UNQUALIFIED historical sandbox only")
    parser.add_argument("--fence-db", default=None)
    parser.add_argument("--authorization-public-key-file", default=None)
    parser.add_argument("--mandate-id", default=None)
    parser.add_argument("--authority-epoch", type=int, default=None)
    args = parser.parse_args()
    global LEDGER
    if args.legacy_test_mode and args.fence_db:
        parser.error('legacy test mode and fenced provider mode are mutually exclusive')
    if args.fence_db:
        # Standalone script execution puts external_targets/ on sys.path, not harness/.
        # Resolve the repository's harness package root explicitly for this test service.
        import sys
        from pathlib import Path
        harness_root = str(Path(__file__).resolve().parents[1])
        if harness_root not in sys.path:
            sys.path.insert(0, harness_root)
        from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence
        fence = ProviderCommitFence(args.fence_db)
        if not args.authorization_public_key_file:
            parser.error('fenced provider requires issuer public verification key')
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        with open(args.authorization_public_key_file, 'rb') as key_file:
            verifier_key = serialization.load_pem_public_key(key_file.read())
        if not isinstance(verifier_key, Ed25519PublicKey):
            parser.error('fenced provider requires Ed25519 public key')
        LEDGER = ExternalLedger(fence=fence, mandate_id=args.mandate_id, authority_epoch=args.authority_epoch, authorization_public_key=verifier_key)
    else:
        LEDGER = ExternalLedger(legacy_test_mode=args.legacy_test_mode)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
