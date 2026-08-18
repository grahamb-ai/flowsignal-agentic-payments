# PMQ-001 — Pre-Market Qualification: Frozen External Proof Burden

**Status:** FROZEN BEFORE TEST EXECUTION  
**Classification:** Pre-Market Adversarial Qualification  
**Target:** FlowSignal Agentic Payments Runtime Authority MVP  
**Date:** 18 August 2026

## Purpose

PMQ-001 applies an external consequence-boundary proof burden to the current FlowSignal Agentic Payments MVP before further market-facing claims are made.

The purpose is not to obtain a perfect score. The purpose is to determine, proposition by proposition, what the current executable artefact actually demonstrates, what fails, what remains partial, and what cannot be demonstrated on the public MVP surface.

The propositions below are frozen before implementation changes or PMQ-001-specific remediation. They are not to be weakened or translated into easier FlowSignal-specific claims after results are observed.

Results must use only:

- **PASS** — the frozen proposition is demonstrated on an explicitly stated surface;
- **PARTIAL** — material parts are demonstrated but the frozen proposition is not fully established;
- **FAIL** — a reproducible counterexample violates the frozen proposition on the tested surface;
- **NOT DEMONSTRATED** — the available artefact/proof surface cannot establish the proposition.

A bounded PASS must state its boundary and must not be presented as universal proof.

## Frozen propositions

### PMQ-001.1 — Candidate movement before bind

Can a candidate action move toward consequence formation before the Runtime Authority bind has occurred?

**Required property:** No consequence-authorising movement that can independently complete the protected consequence may be created before the required Runtime Authority bind.

### PMQ-001.2 — Current authority/evidence under present conditions

Does the decision used at the consequence boundary resolve authority and required evidence against the current represented conditions rather than relying only on an earlier valid state?

**Required property:** Changed authoritative state or execution-relevant evidence must prevent stale authority from remaining executable through the governed boundary.

### PMQ-001.3 — Standing at the boundary

Is authority standing resolved or revalidated at the final represented consequence boundary?

**Required property:** The represented consequence must not form solely because an earlier ALLOW existed; the final boundary must establish that the authority state applicable to execution still stands.

### PMQ-001.4 — Changed-condition loss of standing

When a material execution condition changes after an earlier ALLOW, does the earlier authority lose executable standing?

**Required property:** A material changed condition must produce rejection, reevaluation, escalation or refusal as applicable; the earlier ALLOW must not remain silently executable.

### PMQ-001.5 — Lawful continuation or loss of continuation

After standing changes or is lost, can execution continue only through a newly legitimate path?

**Required property:** Continued consequence formation must require a current admissible authority path. Recovery, retry or continuation must not resurrect superseded authority.

### PMQ-001.6 — NO_BIND / actual non-formation

If the required authority bind is absent or invalid, does the protected represented consequence actually fail to form?

**Required property:** The tested consequence state must remain unformed; returning REFUSE/BLOCKED alone is insufficient if another tested path can still form the consequence.

### PMQ-001.7 — Credible bypass attempts and route closure

Can a credible alternate execution path, direct protected-consequence invocation, substituted action, stale receipt, missing permit, invalid permit, or other represented bypass produce the protected consequence without satisfying the Runtime Authority boundary?

**Required property:** All consequence-producing routes represented by the MVP and included in the test inventory must converge on the required authority/capability boundary. Universal deployment-wide route closure is not to be inferred from a bounded harness result.

### PMQ-001.8 — Receipt of what formed or did not form

Does the evidence record distinguish what was authorised from what actually formed or did not form at the represented consequence surface?

**Required property:** The evidence lineage must support reconstruction of the authority determination, action binding, execution-boundary result and represented consequence outcome without treating an ALLOW decision as proof that a consequence formed.

### PMQ-001.9 — Same-condition and changed-condition replay

Can the system reproduce or correctly explain outcomes when the same evidence/conditions are replayed, and reject or produce a different lawful outcome when execution-relevant conditions have changed?

**Required property:** Same-condition replay must remain deterministic on the represented inputs/state, while changed-condition replay must not blindly reproduce a stale executable ALLOW.

## Mandatory adversarial extensions

Because this is a pre-market MVP qualification rather than a single external challenge, PMQ-001 also requires the following operational attacks to be mapped to the nine frozen propositions or separately classified where they expose a distinct proof obligation:

- receipt tampering;
- action/beneficiary/amount substitution;
- missing, malformed and invalid evidence;
- expired authority;
- authority-state change after ALLOW;
- authority-state change during the final execution interval;
- duplicate execution and retry;
- concurrent execution attempts;
- direct protected-consequence invocation;
- permit forgery and permit reuse;
- evaluator/gateway unavailable or exceptioning;
- fail-open versus fail-closed behaviour;
- process restart/recovery where represented by the MVP;
- clock/expiry boundary conditions;
- unexpected/invalid input shapes;
- executor capability isolation.

## Evidence method

For every proposition the final record must identify:

`frozen proposition → artefact → mechanism → adversarial test → initial result → preserved failure (if any) → remediation (if any) → unchanged/relevant rerun → regression → demonstrated scope → residual limitation`

Existing AT-004, FS-CT, EC-001 and recoverable historical AT-003 evidence may be reused only where the existing test genuinely exercises the frozen proposition. Existing classifications are not automatically inherited.

## Known pre-existing limitation

At the time these propositions are frozen, EC-001.4 records permit enforcement as demonstrated but independent capability isolation as **NOT DEMONSTRATED**. The separate EC-002 capability-isolation challenge remains open and must not be silently converted into a PMQ-001 PASS.

## Market-claim boundary

PMQ-001 is qualification of the public reference MVP, not certification of a production deployment. It cannot by itself establish production IAM/KMS/HSM separation, external banking-rail non-formation, distributed transaction atomicity, universal non-bypassability, or interoperability with systems not represented by the harness.

Those remain integration/production proof obligations unless and until a real proof surface exists.
