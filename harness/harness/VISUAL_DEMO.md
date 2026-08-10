# FlowSignal Agentic Payments Visual Harness — v0.9

This release adds a dedicated live dashboard over the six FS-AN-004 canonical scenarios.

## Run the visual harness

Install the project requirements, then from the repository root:

```bash
uvicorn agentic_demo:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The visual dashboard is deliberately backed by the real financial-services Runtime Authority
engine rather than a JavaScript simulation.

## Demonstrated scenarios

| Scenario | Runtime / Gateway outcome |
|---|---|
| AP-001 — Within autonomous authority | ALLOW |
| AP-002 — Autonomous limit exceeded | ESCALATE |
| AP-003 — Counterparty changes after approval | REFUSE |
| AP-004 — CLEAR evidence becomes stale | ESCALATE |
| AP-005 — Delegated mandate expires | REFUSE |
| AP-006 — Authorised action is substituted before execution | BLOCKED |

## Screen layout

The dashboard is organised around three institutional questions:

1. **Proposed Payment** — what consequence is the autonomous actor requesting?
2. **Runtime Authority** — which bind-time authority conditions are satisfied?
3. **Governance Decision** — what outcome is enforced, and what Authority Receipt exists?

AP-006 additionally shows the Execution Gateway comparing the authorised action-binding hash
with the attempted execution hash.

The full Authority Receipt and canonical source scenario remain inspectable beneath the main
demonstration view.
