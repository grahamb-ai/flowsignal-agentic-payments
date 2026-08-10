from __future__ import annotations
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import ExecutionAttempt, validate_execution

ROOT = Path(__file__).resolve().parents[1]


def _dt(v: str) -> datetime:
    return datetime.fromisoformat(v.replace("Z", "+00:00"))


def main() -> int:
    base = load_scenario(ROOT / "harness" / "scenarios" / "AP-001_allow.json")
    response, receipt = evaluate_financial(base)

    scenario = json.loads(
        (ROOT / "harness" / "scenarios" / "AP-006_action_substitution.json")
        .read_text(encoding="utf-8")
    )
    x = scenario["execution_attempt"]

    attempt = ExecutionAttempt(
        actor_id=x["actor_id"],
        principal_id=x["principal_id"],
        action=x["action"],
        target=x["target"],
        amount=float(x["amount"]),
        currency=x["currency"],
        source_account=x["source_account"],
        beneficiary=x["beneficiary"],
        purpose=x["purpose"],
        mandate_id=x["mandate_id"],
        attempted_at=_dt(x["attempted_at"]),
    )

    gateway = validate_execution(receipt, attempt)

    output = {
        "runtime_authority": {
            "decision": response.decision,
            "authority_receipt_id": response.authority_receipt_id,
            "authorised_beneficiary": base.beneficiary,
            "action_binding_hash": receipt.action_binding_hash,
        },
        "execution_attempt": {
            "beneficiary": attempt.beneficiary,
            "amount": attempt.amount,
            "source_account": attempt.source_account,
        },
        "execution_gateway": asdict(gateway),
        "financial_consequence": "NO EXECUTION" if gateway.status == "BLOCKED" else "EXECUTION PERMITTED",
    }

    out = ROOT / "harness" / "receipts" / "AP-006_gateway_evidence.json"
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
