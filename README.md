# Runtime Authority for Agentic Payments

**An open engineering reference project examining how institutional authority can be independently determined and enforced immediately before an autonomous financial action becomes a financial consequence.**

## Why This Project Exists

The UK Financial Services AI Adoption Plan identifies agentic payments as an emerging area for industry development.

Recommendation 10 proposes an industry-led trust framework for agentic payments, including work around:

- Legal & Liability Frameworks
- Know Your Agent (KYA) protocols
- Authentication & Governance

These are important foundations for trusted agentic financial infrastructure.

This project examines a narrower implementation question that arises when an authenticated autonomous agent moves from proposing an action to causing a financial consequence:

> **Once an autonomous agent is known, authenticated and operating under delegated authority, what determines whether that authority remains sufficient for the specific financial action immediately before execution?**

The project explores **Runtime Authority** as one architectural answer to that question.

---

## The Execution-Authority Problem

Identity can establish **who or what the agent is**.

Authentication can establish **whether the interaction is genuine**.

A mandate can establish **what authority has previously been delegated**.

But financial execution introduces another question:

> **May this specific action legitimately execute under current institutional conditions?**

Those conditions may have changed since the agent was authenticated, the action was planned or an earlier approval was obtained.

Examples include:

- mandate expiry or revocation;
- transaction limits;
- beneficiary or counterparty changes;
- account status;
- policy changes;
- fraud or risk state;
- sanctions or screening evidence;
- evidence freshness;
- approval state; and
- escalation availability.

The project investigates how that final execution-authority determination can be made explicit, enforceable and evidentially reconstructable.

---

## Runtime Authority

Within this project, Runtime Authority is the function that evaluates whether sufficient institutional authority exists for a proposed autonomous action immediately before consequence formation.

Conceptually:

**Actor + Mandate + Proposed Action + Current Context + Applicable Constraints + Trusted Evidence**

→ **Runtime Authority**

→ **ALLOW | ESCALATE | REFUSE**

→ **Execution Gateway**

→ **Financial Consequence**

The autonomous system may remain probabilistic.

The institution's final authority boundary does not have to be.

---

## What Runtime Authority Is Not

Runtime Authority is not intended to replace:

- Know Your Agent infrastructure;
- identity or authentication;
- fraud detection;
- sanctions, AML or financial-crime controls;
- risk systems;
- institutional policy;
- human approval;
- legal or regulatory judgement; or
- payment infrastructure.

These functions remain authoritative within their respective domains.

Runtime Authority may consume trusted evidence or assertions produced by those functions where relevant to the execution-authority determination.

---

## Architectural Analysis

The architectural foundation for this project is:

### [FS-AN-004 — The Runtime Authority Requirement in Agentic Payments](docs/FS-AN-004%20v1.0%20Released.pdf)

**Architectural Analysis of Recommendation 10 of the UK Financial Services AI Adoption Plan**

FS-AN-004 examines the relationship between:

- agent identity;
- authentication;
- delegated authority;
- runtime context;
- execution binding;
- deterministic authority determination;
- escalation;
- evidence freshness;
- revalidation;
- Authority Receipts;
- execution enforcement;
- interoperability; and
- independent assurance.

The paper treats Runtime Authority as an architectural proposition for investigation and testing, not as a requirement stated by HM Treasury.

---

## Engineering Programme

This repository will progressively contain the engineering evidence used to test that proposition.

Planned work includes:

1. **Agentic Payments Reference Implementation**  
   A bounded autonomous financial workflow demonstrating ALLOW, ESCALATE and REFUSE outcomes.

2. **Execution-Bind Testing**  
   Demonstrating that authority is evaluated immediately before financial consequence formation.

3. **Revalidation & Evidence Freshness**  
   Testing state changes, expired evidence and post-approval revalidation.

4. **Authority Receipt & Replay**  
   Producing reconstructable evidence of execution-authority determinations.

5. **Adversarial & Stress Testing**  
   Testing attempted bypass, action substitution, dependency failure and high-volume execution.

6. **ORAI Interoperability**  
   Exploring implementation-independent authority interaction across heterogeneous agent and financial platforms.

---

## ORAI

This project is expected to use the **Open Runtime Authority Interface (ORAI)** as an implementation-independent interaction contract.

ORAI remains separate from this financial-services project.

The objective is not to create a proprietary financial-services version of Runtime Authority, but to test whether a common authority interaction can operate across different agents, platforms and institutional implementations.

The guiding principle is:

> **Standardise the authority interaction, not the institution's authority decision.**

---

## Current Status

**Phase: Architectural foundation / reference implementation preparation**

Current artefact:

- FS-AN-004 v1.0 — *The Runtime Authority Requirement in Agentic Payments*

Next phase:

- Agentic payments reference implementation
- Deterministic test scenarios
- Assurance evidence
- Multi-platform interoperability experiments

---

## Research Approach

The project follows an evidence-first progression:

**Define → Implement → Test → Challenge → Interoperate → Measure → Review**

The objective is not to assume that the Runtime Authority architecture is correct.

It is to make the proposition sufficiently explicit that it can be implemented, tested, challenged and potentially falsified.

---

## Independence and Attribution

This is an independent FlowSignal engineering research project.

It is informed by implementation questions arising from the UK Financial Services AI Adoption Plan but is **not affiliated with, endorsed by, or produced on behalf of HM Treasury, the FCA or any other UK government or regulatory body**.

References to Recommendation 10 describe the policy context from which the engineering question examined by this project arises.

Runtime Authority, the associated architecture and the interpretations presented here are FlowSignal's independent technical analysis.

---

## FlowSignal

FlowSignal develops independent Runtime Authority infrastructure for consequential autonomous systems.

The core architectural principle is:

> **An autonomous system may propose a consequence. It should not be the final authority that permits that consequence to occur.**

---

© 2026 FlowSignal. All rights reserved.
