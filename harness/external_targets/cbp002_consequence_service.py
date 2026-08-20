from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock


class ExternalLedger:
    """State owned by the external test service, not FlowSignal."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with getattr(self, "_lock", Lock()):
            self.source_balance = 5_000_000.0
            self.beneficiary_balances: dict[str, float] = {}
            self.transfers: list[dict] = []

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "source_balance": self.source_balance,
                "beneficiary_balances": dict(self.beneficiary_balances),
                "transfer_count": len(self.transfers),
                "transfers": list(self.transfers),
            }

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


LEDGER = ExternalLedger()


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
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
