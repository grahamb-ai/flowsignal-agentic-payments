from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from harness.runner import load_scenario
from app.engines.financial_runtime import evaluate_financial
from app.engines.execution_gateway import ExecutionAttempt, validate_execution

ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = ROOT / "harness" / "scenarios"
UI_FILE = ROOT / "demo-ui" / "agentic-payments.html"

app = FastAPI(
    title="FlowSignal Agentic Payments Harness",
    description="FS-AN-004 executable Runtime Authority reference harness.",
    version="0.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCENARIO_FILES = {
    "AP-001": "AP-001_allow.json",
    "AP-002": "AP-002_limit_escalate.json",
    "AP-003": "AP-003_post_approval_counterparty_change.json",
    "AP-004": "AP-004_stale_screening_evidence.json",
    "AP-005": "AP-005_expired_mandate.json",
    "AP-006": "AP-006_action_substitution.json",
}

SCENARIO_SUMMARY = {
    "AP-001": {
        "short": "Within authority",
        "expected": "ALLOW",
        "principle": "All required authority conditions remain satisfied.",
    },
    "AP-002": {
        "short": "Limit exceeded",
        "expected": "ESCALATE",
        "principle": "The proposed consequence exceeds the autonomous mandate ceiling.",
    },
    "AP-003": {
        "short": "State changed",
        "expected": "REFUSE",
        "principle": "Earlier approval does not override current counterparty state.",
    },
    "AP-004": {
        "short": "Evidence stale",
        "expected": "ESCALATE",
        "principle": "Correct evidence can become insufficient when it is no longer current.",
    },
    "AP-005": {
        "short": "Mandate expired",
        "expected": "REFUSE",
        "principle": "Identity can remain valid after delegated authority has expired.",
    },
    "AP-006": {
        "short": "Action substituted",
        "expected": "BLOCKED",
        "principle": "ALLOW A cannot be reused to execute materially different Action B.",
    },
}


def _ser(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_ser(v) for v in value]
    if isinstance(value, dict):
        return {k: _ser(v) for k, v in value.items()}
    try:
        return _ser(asdict(value))
    except TypeError:
        return value


def _scenario_doc(scenario_id: str) -> dict[str, Any]:
    filename = SCENARIO_FILES.get(scenario_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Unknown scenario")
    return json.loads((SCENARIO_DIR / filename).read_text(encoding="utf-8"))


def evaluate_scenario(scenario_id: str) -> dict[str, Any]:
    if scenario_id == "AP-006":
        base = load_scenario(SCENARIO_DIR / SCENARIO_FILES["AP-001"])
        response, receipt = evaluate_financial(base)
        doc = _scenario_doc("AP-006")
        x = doc["execution_attempt"]
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
            attempted_at=datetime.fromisoformat(x["attempted_at"].replace("Z", "+00:00")),
        )
        gateway = validate_execution(receipt, attempt)
        return {
            "scenario_id": scenario_id,
            "title": doc["title"],
            "purpose": doc["purpose"],
            "source": doc,
            "execution_response": _ser(response),
            "authority_receipt": _ser(receipt),
            "execution_attempt": _ser(attempt),
            "execution_gateway": _ser(gateway),
            "financial_consequence": "NO EXECUTION" if gateway.status == "BLOCKED" else "EXECUTION PERMITTED",
        }

    doc = _scenario_doc(scenario_id)
    req = load_scenario(SCENARIO_DIR / SCENARIO_FILES[scenario_id])
    response, receipt = evaluate_financial(req)
    consequence = {
        "ALLOW": "EXECUTION PERMITTED",
        "ESCALATE": "EXECUTION WITHHELD",
        "REFUSE": "NO EXECUTION",
    }[response.decision]
    return {
        "scenario_id": scenario_id,
        "title": doc["title"],
        "purpose": doc["purpose"],
        "source": doc,
        "execution_response": _ser(response),
        "authority_receipt": _ser(receipt),
        "execution_gateway": None,
        "financial_consequence": consequence,
    }


@app.get("/")
def dashboard():
    return FileResponse(UI_FILE)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.9.0", "profile": "agentic-payments"}


@app.get("/api/scenarios")
def list_scenarios():
    return [
        {"id": sid, **SCENARIO_SUMMARY[sid]}
        for sid in SCENARIO_FILES
    ]


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    return _scenario_doc(scenario_id)


@app.post("/api/scenarios/{scenario_id}/evaluate")
def run_scenario(scenario_id: str):
    return evaluate_scenario(scenario_id)
