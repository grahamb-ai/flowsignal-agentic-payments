# FlowSignal Agentic Payments Runtime Authority Harness

**Executable companion to FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

**Historical baseline:** v0.9 Frozen Reference Demonstrator  
**Current status:** Maintained reference-MVP  
**Current qualified public baseline:** see [`../EVIDENCE.md`](../EVIDENCE.md)

> **Status rule:** historical documents and evidence records may state the valid result at the time they were created. The root [`README.md`](../README.md) and [`EVIDENCE.md`](../EVIDENCE.md) define the current qualified public baseline. Test counts must always be read with their relevant commit/workflow evidence rather than as permanent product metrics.

## Purpose

This repository contains an executable reference harness for the Runtime Authority architecture described in:

**FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

It examines a specific question arising as autonomous agents move from proposing financial actions to causing represented financial consequences:

> Once an autonomous agent is known, authenticated and operating under delegated authority, what determines whether that authority remains sufficient for the specific financial action immediately before execution?

Within this reference implementation, Runtime Authority evaluates whether sufficient represented institutional authority exists for a specific proposed action immediately before the protected consequence boundary.

It does not determine whether an agent is intelligent, trustworthy or generally authorised.

The canonical outcomes are:

- **ALLOW**
- **ESCALATE**
- **REFUSE**

## Core principle

> **Same trusted agent. Different execution authority.**

Identity and authentication establish important facts about an autonomous agent. They do not, by themselves, establish whether a particular financial action remains authorised at the moment of execution.

The harness therefore evaluates the proposed action against the applicable mandate, represented institutional state, constraints and trusted evidence immediately before the represented protected consequence boundary.

## Architecture

The demonstrator separates three functions:

1. **Proposed action** — the autonomous system proposes a financial action.
2. **Runtime Authority** — the action is evaluated against current represented authority conditions.
3. **Execution enforcement** — the resulting authority determination is consumed at the represented protected-consequence boundary before the represented consequence is permitted to form.

An ALLOW applies only to the action that was evaluated. It cannot be reused as authority for a materially different action.

## Canonical scenarios

The frozen v0.9 harness contains six core scenarios:

- **AP-001 — Within Authority:** ALLOW.
- **AP-002 — Limit Exceeded:** ESCALATE.
- **AP-003 — State Changed:** REFUSE.
- **AP-004 — Evidence Stale:** ESCALATE.
- **AP-005 — Mandate Expired:** REFUSE.
- **AP-006 — Action Substituted:** Runtime Authority ALLOW for Action A; Execution Gateway BLOCKED for materially different Action B with `ACTION_BINDING_MISMATCH`.

AP-006 demonstrates, for the exercised reference implementation, that:

> **ALLOW A cannot be reused to execute materially different Action B.**

The result concerns the **represented financial consequence in the harness**. It is not evidence of control over an external bank or payment rail.

## Runtime Authority checks

The reference scenarios exercise action-specific runtime checks including:

- actor authentication;
- Know Your Agent status;
- mandate validity and expiry;
- permitted action;
- autonomous amount ceiling;
- permitted currency and source account;
- counterparty and account state;
- represented institutional risk state;
- screening status; and
- evidence freshness.

The purpose is not to prescribe a universal set of financial controls. The harness demonstrates how represented institution-specific authority conditions can be evaluated deterministically at the tested execution boundary.

## Authority receipts and action binding

Each Runtime Authority determination produces an evidential Authority Receipt. For permitted actions, the receipt provides the basis for binding the determination to the exact action that was evaluated.

AP-006 canonicalises and hashes the authorised action. Immediately before represented execution, the Execution Gateway independently derives the hash of the action presented. If the hashes differ, the gateway blocks the attempted represented execution.

This does not retrospectively change the original Runtime Authority determination: the original ALLOW remains valid for the action that was actually evaluated.

## Adversarial assurance history

Following the frozen v0.9 baseline, the harness was subjected to adversarial testing under AT-004. The work challenged authority-source separation, evaluator control, execution routing, receipt integrity, evidence integrity and authority-state freshness.

The important engineering record is not that every test passed first time. Several did not.

Material weaknesses were preserved before remediation, including:

- a represented consequential path that could bypass the Execution Gateway;
- insufficient receipt-integrity coverage;
- evidential content that could be changed outside the original integrity boundary; and
- a valid ALLOW receipt remaining executable after represented authoritative state advanced.

The relevant failure and remediation records remain under [`../evidence/AT-004/`](../evidence/AT-004/). Later PMQ and CBP evidence extends the qualification work substantially beyond the original AT-004 baseline.

## Current evidence

The canonical current evidence index is [`../EVIDENCE.md`](../EVIDENCE.md).

It maps propositions to implementation artifacts, executable tests, preserved failures, remediation records, reruns and residual limitations.

A technically competent reviewer should use the current evidence index rather than an historical test count in this file to determine the maintained qualification status.

## Reproduce

From the repository root:

```bash
git clone https://github.com/grahamb-ai/flowsignal-agentic-payments.git
cd flowsignal-agentic-payments
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```

## Scope and claim boundary

The harness provides evidence about the behaviour of the public reference implementation under the specific conditions exercised.

It does **not** establish:

- production certification;
- universal route closure or universal non-bypassability;
- prevention across real bank/payment rails;
- external physical consequence non-formation;
- production process/IAM/KMS/HSM isolation;
- distributed consensus, serializability or multi-region correctness;
- resistance to privileged host/storage compromise;
- immutable/write-once external audit infrastructure;
- independent third-party reproduction, validation or commercial endorsement; or
- legal or regulatory compliance.

Those are separate proof obligations and must not be inferred from this reference harness.

---

**Evidence first. Claim second. Scope explicit. Failures preserved. No extrapolation.**
