# FS-CLAIM-001 — FlowSignal Claims & Evidence Register

**Version:** v0.1  
**Status:** Maintained claim-control register  
**Scope:** FlowSignal Agentic Payments public reference-MVP and associated public positioning  
**Purpose:** Ensure material FlowSignal claims remain tied to identifiable evidence, explicit qualification and permitted wording.

> **Control rule:** A document, diagram or marketing statement is not implementation evidence merely because it states a proposition. Implementation claims require an implementation artefact plus executable/observable evidence appropriate to the claim.

> **Public-scope exclusion:** Internal pricing, buyer economics, willingness-to-pay assumptions, ROI/TCO models, build-vs-buy analysis, commercial thresholds and customer-specific economic frameworks are outside the scope of this public register and must not be published here.

## Status vocabulary

- **SUPPORTED — BOUNDED:** evidence supports the proposition within an explicitly identified tested/represented surface.
- **PARTIAL:** evidence supports a material subset, but not the full proposition.
- **NOT DEMONSTRATED:** the available evidence does not establish the proposition.
- **EXTERNAL VALIDATION PENDING:** internal/bounded evidence exists but the stated external proof obligation has not yet been completed.
- **PROHIBITED OVERSTATEMENT:** wording exceeds the current evidence boundary and should not be used as an established fact.

## Canonical evidence authority

The current qualified public engineering baseline is defined by the root `README.md` and `EVIDENCE.md`. Historical evidence files preserve the result and qualification valid at the time they were created and must not be treated as the current regression count or current universal claim boundary.

## Claims register

| ID | Material claim | Evidence anchor | Status | Permitted public wording | Do not state as established fact |
|---|---|---|---|---|---|
| CL-001 | FlowSignal makes a Runtime Authority determination for a specific proposed action before the represented protected execution/consequence point. | `README.md`; `EVIDENCE.md`; maintained harness tests | SUPPORTED — BOUNDED | “FlowSignal evaluates current authority immediately before a protected execution point.” | “FlowSignal controls every consequence in every environment.” |
| CL-002 | Canonical Runtime Authority outcomes are ALLOW / ESCALATE / REFUSE. | Runtime Authority implementation and scenario tests | SUPPORTED — BOUNDED | “FlowSignal produces deterministic ALLOW / ESCALATE / REFUSE authority outcomes for defined inputs/rules.” | “The outcome proves the action is legally, morally, clinically or regulatorily correct.” |
| CL-003 | Previously valid authority can become insufficient after relevant authoritative state changes. | `EVIDENCE.md`; PMQ-001/PMQ-002 changed-state, revocation, expiry and rollback tests | SUPPORTED — BOUNDED | “Previously valid authority is not treated as sufficient after tested relevant state changes.” | “All possible real-world changes are automatically discovered.” |
| CL-004 | An ALLOW/permit is bound to the action evaluated and tested substitutions are rejected. | AP-006; action-binding tests; CBP-001 | SUPPORTED — BOUNDED | “Within the tested surface, authority for Action A cannot be reused for a materially different Action B.” | “No substitution is possible through any external route.” |
| CL-005 | Required evidence unavailability can fail closed. | `test_pmq001_fail_closed_evidence.py`; evidence index | SUPPORTED — BOUNDED | “Tested required-evidence unavailability fails closed.” | “All external evidence-provider failures are covered.” |
| CL-006 | Tested stale/expired/replayed permits do not form repeated represented consequences after remediation. | PMQ-001/PMQ-002 replay, expiry, restart and multi-instance tests | SUPPORTED — BOUNDED | “The maintained reference-MVP rejects the tested stale/expired/replayed permit conditions.” | “Universal replay prevention across all production deployments.” |
| CL-007 | A changed condition can prevent represented consequence formation. | CBP-001; PMQ-002 revocation/expiry tests | SUPPORTED — BOUNDED | “In the tested protected-consequence surface, changed authority conditions prevented the represented consequence from forming.” | Unqualified “the payment never executes” or “FlowSignal prevents physical consequence formation everywhere.” |
| CL-008 | FlowSignal has tested direct bypass/no-bind weaknesses, preserved failures, remediated them and rerun the challenges. | `EVIDENCE.md`; PMQ-001; CAT-001 qualification | SUPPORTED — BOUNDED | “Direct bypass conditions were adversarially tested; discovered failures were preserved, remediated and rerun.” | “FlowSignal is universally non-bypassable.” |
| CL-009 | Universal route closure / universal non-bypassability is established. | Current evidence explicitly disclaims this | NOT DEMONSTRATED | “Universal route closure remains a separate proof obligation.” | “FlowSignal cannot be bypassed.” |
| CL-010 | FlowSignal prevents settlement/execution across real external bank/payment rails. | Current public reference-MVP explicitly disclaims this | NOT DEMONSTRATED | “External payment-rail validation remains environment-specific and pending.” | “FlowSignal prevents bank settlement” based on the public harness alone. |
| CL-011 | FlowSignal provides evidence/receipts supporting reconstruction of tested determinations and consequence outcomes. | Authority Receipt tests; consequence-outcome evidence tests; `EVIDENCE.md` | SUPPORTED — BOUNDED | “The tested implementation records evidence supporting reconstruction of the exercised determination/outcome.” | “The receipt alone proves legal compliance or every physical consequence state.” |
| CL-012 | FlowSignal is architecturally independent of the proposing/executing system. | Architecture plus tested authority-source/evaluator separation; deployment independence remains environment-dependent | PARTIAL | “FlowSignal is designed as an independent Runtime Authority layer; the reference work tests important separation properties.” | “Every deployment is independently isolated by definition.” |
| CL-013 | FlowSignal determines whether delegated authority remains legitimately exercisable. | Implementation evaluates defined institutional authority conditions; substantive legal legitimacy is outside public MVP claim boundary | SUPPORTED — BOUNDED / QUALIFIED | “FlowSignal determines whether defined current authority conditions remain sufficient for the specific attempted action.” | “FlowSignal determines legal/regulatory legitimacy.” |
| CL-014 | FlowSignal reduces operational/regulatory risk or prevents losses. | No customer outcome evidence in public reference-MVP | EXTERNAL VALIDATION PENDING | “FlowSignal is designed to reduce exposure to execution under stale or insufficient authority.” | “FlowSignal has proven it reduces losses, fines or regulatory risk.” |
| CL-015 | FlowSignal enables additional safe automation or reduces manual controls. | No customer outcome evidence in public reference-MVP | EXTERNAL VALIDATION PENDING | “Additional automation or control reduction is a potential customer outcome that must be established separately.” | “FlowSignal has proven automation savings” without customer evidence. |
| CL-016 | FlowSignal is production-certified / regulator-approved / independently third-party validated. | Public evidence explicitly says no | NOT DEMONSTRATED | “Public reference implementation; external validation is a separate proof obligation.” | “Certified”, “approved”, “endorsed”, or “independently validated” unless a named completed process supports it. |
| CL-017 | No other system performs an equivalent function / the category did not previously exist. | No exhaustive market evidence | PROHIBITED OVERSTATEMENT | “FlowSignal addresses a distinct Runtime Authority problem at the execution boundary.” | “No system does this”, “this layer does not exist”, “first/only” absent separately verified evidence. |
| CL-018 | Runtime Authority is universally required before consequence formation. | Architectural proposition, not universally established by the harness | PROHIBITED OVERSTATEMENT as empirical fact | “FlowSignal provides independent Runtime Authority infrastructure for protected execution points.” | “Every consequential AI system requires FlowSignal/Runtime Authority.” |

## Website wording control

Prefer wording that states the protected boundary and defined authority conditions explicitly.

**Preferred:**

> FlowSignal independently evaluates whether defined current authority conditions still permit a specific consequential action to proceed at a protected execution point.

Avoid universal or substantive-correctness wording such as:

- “Every important decision passes through...” unless explicitly describing a configured FlowSignal deployment;
- “make sure it is still right to proceed” where “right” could imply legal/moral/clinical correctness;
- “objective execution decision” where the intended claim is deterministic evaluation against defined authority conditions;
- “universal problem” as an established empirical/category fact.

## LinkedIn wording control

### GREEN — may use within the normal bounded context

- ALLOW / ESCALATE / REFUSE
- current authority before protected execution
- action-specific authority
- Authority Receipts / evidence
- preserved failures and remediation
- working/public reference implementation
- explicit claim boundaries

### AMBER — qualify every time

- “prevents unauthorised execution” → specify protected/tested execution path
- “consequence does not form” → specify represented/tested consequence surface
- “independent” → distinguish architecture/design from deployment isolation
- “defensible” → describe the evidence/reconstruction property; do not imply legal immunity
- “reduces risk” → state design objective or measured customer result only
- “before real-world impact” → only where the actual integration boundary supports that statement

### RED — do not use as established facts under the current evidence estate

- “Only admissible decisions can become real”
- “No system does this”
- “This layer doesn’t exist”
- “This is what regulators actually care about”
- unqualified “the payment never executes” based on a represented harness
- universal non-bypassability
- external physical non-formation
- regulator/Google/hyperscaler/third-party endorsement without explicit evidence
- proven customer outcome claims without supporting customer evidence

## External-party wording control

External engineering activity must be described according to its actual status. Integration work, technical discussions, evaluation routes, sandbox testing and commercial adoption are different states.

Use terms such as **integration engineering**, **evaluation**, **working toward live end-to-end validation**, or **exploring an independent testing route** where accurate. Do not convert those states into endorsement, certification, production adoption or customer validation.

## Pre-publication check

Before a material public claim is published, ask:

1. What exact proposition is being asserted?
2. Is it architectural intent, implemented behaviour, tested behaviour, external validation or customer outcome?
3. What evidence anchor supports that level of claim?
4. What qualification would a technically competent hostile reviewer reasonably require?
5. Does the wording imply legal/regulatory correctness, universal scope, production scope or third-party endorsement that the evidence does not establish?

If the answer to question 3 is unclear, downgrade the wording or do not publish the claim.

---

**Evidence first. Claim second. Scope explicit. Failures preserved. No extrapolation.**