# FlowSignal Agentic Payments Harness — v0.9 FROZEN

Status: Frozen reference demonstrator

This frozen release preserves the six validated canonical scenarios and the presentation refinements introduced in v0.9.

## Final panel structure

1. Proposed Payment
2. Runtime Authority
3. Execution Enforcement

This wording reflects the architectural separation between:
- the proposed consequence;
- the bind-time Runtime Authority determination; and
- downstream enforcement of that determination at the execution boundary.

## Canonical scenarios

- AP-001 — ALLOW
- AP-002 — ESCALATE
- AP-003 — REFUSE
- AP-004 — ESCALATE
- AP-005 — REFUSE
- AP-006 — Runtime Authority ALLOW + Execution Gateway BLOCKED

## Freeze rule

No further functional or presentation changes should be made to v0.9-frozen.
Any future changes should increment the harness version.
