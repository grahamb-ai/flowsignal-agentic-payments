# Runtime Authority for Agentic Payments

**An open engineering reference project examining how institutional authority can be independently determined and enforced immediately before an autonomous financial action becomes a represented financial consequence.**

## Why This Project Exists

The UK Financial Services AI Adoption Plan identifies agentic payments as an emerging area for industry development.

Recommendation 10 proposes an industry-led trust framework for agentic payments, including work around legal/liability frameworks, Know Your Agent protocols, authentication and governance.

This project examines a narrower implementation question:

> **Once an autonomous agent is known, authenticated and operating under delegated authority, what determines whether that authority remains sufficient for the specific financial action immediately before execution?**

The project explores **Runtime Authority** as one architectural answer.

## Runtime Authority

Within this reference project, Runtime Authority evaluates whether sufficient represented institutional authority exists for a proposed autonomous action immediately before the protected consequence boundary.

**Actor + Mandate + Proposed Action + Current Context + Applicable Constraints + Trusted Evidence**

→ **Runtime Authority**

→ **ALLOW | ESCALATE | REFUSE**

→ **Execution Gateway**

→ **Represented Financial Consequence**

The autonomous system may remain probabilistic. The represented authority boundary can be deterministic.

## Executable Evidence

The primary public evidence index is [`EVIDENCE.md`](EVIDENCE.md).

> **EVIDENCE.md is an index to executable evidence; it is not itself the evidence.**

It links the engineering propositions directly to implementation/test artifacts, preserved failures, remediation records, reruns and explicit residual limitations.

The current qualified reference-MVP candidate was reproduced on a clean GitHub-hosted Ubuntu runner using Python 3.11 and the repository dependency manifest. The qualified run recorded:

**53 passed / 0 failed**

This is a regression count, **not 53 independent proofs**, and clean hosted CI reproduction is **not independent third-party validation**.

The evidence estate deliberately preserves material failures discovered during adversarial qualification, including consequence-producing bypass/replay/rollback failures before remediation. See [`evidence/PMQ-001/`](evidence/PMQ-001/), [`evidence/PMQ-002/`](evidence/PMQ-002/) and [`evidence/CAT-001/`](evidence/CAT-001/).

## Current Qualification Boundary

The maintained reference-MVP has been exercised against standing-at-effect, stale authority, changed conditions, temporal expiry, direct bypass, consequence non-formation, replay, restart, concurrency, evidence failure, crash recovery and durable rollback propositions.

The architecture-neutral CAT-001 record currently classifies the FlowSignal reference-MVP as **14 PASS · 1 PARTIAL · 0 FAIL · 0 NOT DEMONSTRATED** under its frozen fifteen-proposition burden.

The single PARTIAL is governed route closure: tested governed consequence-producing bypasses have been exercised and remediated, but **universal external route closure is not demonstrated**.

CAT-001 is a qualification/evidence-mapping record. The executable tests and execution records linked from [`EVIDENCE.md`](EVIDENCE.md) are the primary engineering evidence.

## What This Project Does Not Claim

The public reference-MVP does **not** establish:

- production certification;
- universal route closure or universal non-bypassability;
- prevention across real bank/payment rails;
- external physical consequence non-formation;
- production process/IAM/KMS/HSM isolation;
- distributed consensus, serializability or multi-region correctness;
- resistance to privileged host/storage compromise;
- rollback resistance where every store and surviving reference anchor is coherently restored or compromised;
- immutable/write-once external audit infrastructure;
- real external evidence-provider outage/transport/malformed-payload behaviour unless explicitly tested; or
- independent third-party reproduction, validation or commercial endorsement.

Those are separate proof obligations and must not be inferred from the reference-MVP evidence.

## What Runtime Authority Is Not

Runtime Authority is not intended to replace identity/authentication, Know Your Agent infrastructure, fraud detection, sanctions/AML controls, risk systems, institutional policy, human approval, legal/regulatory judgement or payment infrastructure.

Those functions remain authoritative in their domains. Runtime Authority may consume trusted evidence/assertions from them where relevant to the execution-authority determination.

## Architectural Analysis

The architectural foundation for this project is:

### [FS-AN-004 — The Runtime Authority Requirement in Agentic Payments](docs/FS-AN-004%20v1.0%20Released.pdf)

FS-AN-004 treats Runtime Authority as an architectural proposition for investigation and testing, **not** as a requirement stated by HM Treasury.

## Reproduce

```bash
git clone https://github.com/grahamb-ai/flowsignal-agentic-payments.git
cd flowsignal-agentic-payments
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```

Future repository changes may change the collected test count. Read any count with its relevant commit/workflow evidence rather than as a permanent product metric.

## Research Approach

**Define → Implement → Test → Challenge → Preserve Failure → Remediate → Rerun → Bound Claim**

The objective is not to assume Runtime Authority is correct. It is to make the proposition sufficiently explicit that it can be implemented, tested, challenged and falsified.

## Independence and Attribution

This is an independent FlowSignal engineering research project.

It is informed by implementation questions arising from the UK Financial Services AI Adoption Plan but is **not affiliated with, endorsed by, or produced on behalf of HM Treasury, the FCA or any other UK government or regulatory body**.

Runtime Authority, the associated architecture and the interpretations presented here are FlowSignal's independent technical analysis.

---

**FlowSignal™ — Execute with Authority. Defend with Evidence.**

© 2026 FlowSignal. All rights reserved.
