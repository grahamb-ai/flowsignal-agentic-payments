from __future__ import annotations

import argparse
import json
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock


class CapabilityLedger:
    """External target state plus one-time consequence capabilities.

    Capability release is conditional on FlowSignal having already established
    durable permit consumption and an unresolved consequence outcome for the
    same exact action binding. The target therefore does not accept a FlowSignal
    permit as a payment credential by itself.

    This is a bounded reference integration. Reading the named FlowSignal
    execution-state stores is the explicit trust/integration seam under test; it
    is not a claim of production IAM, database isolation, HSM/KMS custody, or
    universal route closure.
    """

    def __init__(self, permit_store: Path, outcome_store: Path) -> None:
        self._lock = Lock()
        self.permit_store = permit_store
        self.outcome_store = outcome_store
        self.reset()

    def reset(self) -> None:
        with getattr(self, "_lock", Lock()):
            self.source_balance = 5_000_000.0
            self.beneficiary_balances: dict[str, float] = {}
            self.transfers: list[dict] = []
            self.capabilities: dict[str, dict] = {}

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "source_balance": self.source_balance,
                "beneficiary_balances": dict(self.beneficiary_balances),
                "transfer_count": len(self.transfers),
                "transfers": list(self.transfers),
                "issued_capability_count": len(self.capabilities),
                "used_capability_count": sum(1 for c in self.capabilities.values() if c["used"]),
            }

    def _flow_state_allows_release(self, permit_signature: str, action_binding_hash: str) -> bool:
        if not self.permit_store.exists() or not self.outcome_store.exists():
            return False

        try:
            with sqlite3.connect(self.permit_store) as connection:
                consumed = connection.execute(
                    "SELECT 1 FROM consumed_execution_permits WHERE signature = ?",
                    (permit_signature,),
                ).fetchone()
            if consumed is None:
                return False

            with sqlite3.connect(self.outcome_store) as connection:
                outcome = connection.execute(
                    """
                    SELECT action_binding_hash, outcome
                    FROM consequence_outcomes
                    WHERE permit_signature = ?
                    """,
                    (permit_signature,),
                ).fetchone()
            if outcome is None:
                return False
            stored_binding, stored_outcome = outcome
            return (
                stored_binding == action_binding_hash
                and stored_outcome == "CONSEQUENCE_OUTCOME_UNRESOLVED"
            )
        except sqlite3.Error:
            return False

    def release_capability(self, payload: dict) -> tuple[int, dict]:
        required = {
            "permit_signature",
            "action_binding_hash",
            "source_account",
            "beneficiary",
            "amount",
            "currency",
            "purpose",
        }
        missing = sorted(required - payload.keys())
        if missing:
            return 400, {"error": "MISSING_FIELDS", "fields": missing}

        permit_signature = str(payload["permit_signature"])
        action_binding_hash = str(payload["action_binding_hash"])
        if not self._flow_state_allows_release(permit_signature, action_binding_hash):
            return 403, {"error": "CAPABILITY_RELEASE_NOT_AUTHORISED"}

        with self._lock:
            for token, capability in self.capabilities.items():
                if capability["permit_signature"] == permit_signature:
                    return 200, {"status": "CAPABILITY_ALREADY_ISSUED", "capability": token}

            token = secrets.token_urlsafe(32)
            self.capabilities[token] = {
                "permit_signature": permit_signature,
                "action_binding_hash": action_binding_hash,
                "source_account": str(payload["source_account"]),
                "beneficiary": str(payload["beneficiary"]),
                "amount": float(payload["amount"]),
                "currency": str(payload["currency"]),
                "purpose": str(payload["purpose"]),
                "used": False,
            }
            return 201, {"status": "CAPABILITY_ISSUED", "capability": token}

    def transfer(self, payload: dict, capability_token: str | None) -> tuple[int, dict]:
        if not capability_token:
            return 401, {"error": "CAPABILITY_REQUIRED"}

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

        with self._lock:
            capability = self.capabilities.get(capability_token)
            if capability is None:
                return 403, {"error": "CAPABILITY_INVALID"}
            if capability["used"]:
                return 409, {"error": "CAPABILITY_ALREADY_USED"}

            expected = {
                "source_account": str(payload["source_account"]),
                "beneficiary": str(payload["beneficiary"]),
                "amount": float(payload["amount"]),
                "currency": str(payload["currency"]),
                "purpose": str(payload["purpose"]),
            }
            for field, actual in expected.items():
                if capability[field] != actual:
                    return 403, {"error": "CAPABILITY_SCOPE_MISMATCH", "field": field}

            amount = expected["amount"]
            if amount <= 0:
                return 400, {"error": "INVALID_AMOUNT"}
            if expected["currency"] != "GBP":
                return 400, {"error": "UNSUPPORTED_CURRENCY"}
            if amount > self.source_balance:
                return 409, {"error": "INSUFFICIENT_FUNDS"}
            if any(t["transaction_id"] == payload["transaction_id"] for t in self.transfers):
                return 409, {"error": "DUPLICATE_TRANSACTION"}

            capability["used"] = True
            self.source_balance -= amount
            beneficiary = expected["beneficiary"]
            self.beneficiary_balances[beneficiary] = (
                self.beneficiary_balances.get(beneficiary, 0.0) + amount
            )
            transfer = {
                "transaction_id": str(payload["transaction_id"]),
                **expected,
            }
            self.transfers.append(transfer)
            return 201, {"status": "TRANSFER_RECORDED", "transfer": transfer}


LEDGER: CapabilityLedger | None = None


class Handler(BaseHTTPRequestHandler):
    server_version = "CBP003CapabilityTarget/1.0"

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
        assert LEDGER is not None
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
            return
        if self.path == "/state":
            self._respond(200, LEDGER.snapshot())
            return
        self._respond(404, {"error": "NOT_FOUND"})

    def do_POST(self) -> None:  # noqa: N802
        assert LEDGER is not None
        try:
            payload = self._json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._respond(400, {"error": "INVALID_JSON"})
            return

        if self.path == "/capabilities/release":
            status, result = LEDGER.release_capability(payload)
            self._respond(status, result)
            return

        if self.path == "/payments":
            auth = self.headers.get("Authorization", "")
            token = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else None
            status, result = LEDGER.transfer(payload, token)
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
    global LEDGER
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--permit-store", required=True)
    parser.add_argument("--outcome-store", required=True)
    args = parser.parse_args()

    LEDGER = CapabilityLedger(Path(args.permit_store), Path(args.outcome_store))
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
