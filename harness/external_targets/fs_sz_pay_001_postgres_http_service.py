"""HTTP service for the bounded FS-SZ-PAY-001 PostgreSQL provider candidate.

The service has only a payment endpoint; no authority mutation, reset or state
endpoint. DB credentials are supplied by its own process environment.
"""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import psycopg
from cryptography.hazmat.primitives import serialization

from app.engines.fs_sz_pay_001_postgres_provider import PostgreSQLProtectedLedger


class Handler(BaseHTTPRequestHandler):
    ledger = None

    def do_POST(self):
        if self.path != "/payments":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 65536:
                self.send_error(413)
                return
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("object expected")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400)
            return
        status, response = self.ledger.transfer(payload)
        body = json.dumps(response, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--mandate-id", required=True)
    parser.add_argument("--issuer-public-key-file", required=True)
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "::1"):
        parser.error("qualification provider refuses non-loopback bind without deployment security qualification")
    if os.environ.get("FS_QUAL_WRITER_DSN"):
        parser.error("provider process must not receive institutional authority-writer credentials")
    dsn = os.environ["FS_QUAL_EXECUTOR_DSN"]
    with Path(args.issuer_public_key_file).open("rb") as handle:
        key = serialization.load_pem_public_key(handle.read())
    Handler.ledger = PostgreSQLProtectedLedger(
        connect=lambda: psycopg.connect(dsn),
        verification_key=key, mandate_id=args.mandate_id)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
