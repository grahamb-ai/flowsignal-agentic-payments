# CAT-001 — Cross-Architecture Runtime Authority Qualification

**Status:** FROZEN CHALLENGE

**Purpose:** Apply the same evidential burden to different public runtime-authority / consequence-boundary demonstrators without moving the goalposts after implementation details are examined.

**Classification vocabulary:** `PASS · PARTIAL · FAIL · NOT DEMONSTRATED (ND)`

---

## 1. Qualification principle

CAT-001 is architecture-neutral.

It does not assume FlowSignal, OATS, Millings, TA-14, Runtime Authority Control, or any other named architecture is correct, equivalent, derived from another system, or production-ready.

The qualification rule is:

> **Same proposition. Same proof burden. Same evidence standard.**

For every proposition, the evidence record must preserve:

> **Claim / proposition → artifact → mechanism → test → initial result or failure → remediation, if any → unchanged or semantically preserved rerun → demonstrated scope → residual limitation**

A failed proposition MUST NOT be silently replaced with an easier proposition after the result is known.

An unavailable or unpublished test surface is `NOT DEMONSTRATED`, not automatically `FAIL`.

A bounded demonstrator PASS MUST remain attached to its tested boundary and MUST NOT be extrapolated to production infrastructure, undisclosed components, external systems, physical consequences, distributed guarantees, or universal route closure unless those surfaces are actually demonstrated.

---

## 2. Frozen target boundary

CAT-001 may be applied only to a lawfully accessible public proof / demonstrator surface and its documented public interfaces.

It does not require or authorize:

- defeating access controls;
- accessing private or production systems;
- obtaining undisclosed source code;
- copying or republishing proprietary implementation material;
- reverse engineering beyond what is necessary to exercise documented public behavior;
- claiming conclusions about an undisclosed production architecture from a bounded public demonstrator.

Where a public repository explicitly states that it is a bounded demonstrator rather than the production implementation, CAT-001 conclusions MUST preserve that limitation.

---

## 3. Frozen propositions

### CAT-001.1 — Standing at effect

**Proposition**

Authority relied upon for consequence formation MUST be evaluated against the authority state that stands at the represented consequence boundary, rather than relying solely on historical request-time or approval-time state.

**Required evidence**

A test must distinguish an earlier-valid state from the state that exists when consequence formation is attempted.

**PASS condition**

The represented consequence forms only when the authority relied upon still has standing at the tested boundary.

**FAIL condition**

A represented consequence forms using authority that the tested system itself treats as no longer standing at that boundary.

---

### CAT-001.2 — No stale authority

**Proposition**

A previously valid authorization / standing object MUST NOT continue to authorize a represented consequence after a material authority-state change that makes it stale.

**Required evidence**

Freeze a valid authority object, introduce a material state change, then attempt the same represented consequence using the pre-change object.

**PASS condition**

Execution is refused, invalidated, or otherwise prevented from forming the represented consequence.

---

### CAT-001.3 — Changed-condition refusal

**Proposition**

The system MUST expose a changed-condition scenario in which a condition relevant to authority changes after initial acceptance and before consequence formation, and the represented execution path responds according to that changed state.

**Required evidence**

The before-state, changed condition, resulting determination, and consequence outcome must all be observable enough to reproduce.

**ND condition**

The public surface asserts changed-condition handling but exposes no executable or independently reproducible changed-condition test.

---

### CAT-001.4 — No resurrection without legitimate reissue

**Proposition**

Authority that has become stale, revoked, superseded, or otherwise invalid MUST NOT regain standing merely because earlier state reappears or a historical object is replayed, unless a legitimate reissue / reauthorization event occurs under the represented model.

**Required evidence**

Attempt to restore or replay prior authority after invalidation without a legitimate reissue.

---

### CAT-001.5 — Governed route closure

**Proposition**

Within the represented public demonstrator boundary, a credible consequence-producing path MUST NOT bypass the authority enforcement path being claimed.

**Required evidence**

Identify the public consequence-producing surface and attempt the most credible reachable bypass available through the published demonstrator.

**Scope rule**

A PASS may establish closure only for the tested governed/public routes. Universal external route closure is `ND` unless independently demonstrated.

---

### CAT-001.6 — Independent execution capability

**Proposition**

Within the represented boundary, code or components outside the authority decision / issuance mechanism MUST NOT be able to manufacture or independently obtain whatever execution capability is sufficient to form the protected consequence.

**Required evidence**

Attempt to create, forge, substitute, or directly invoke the execution-enabling capability using only the accessible public demonstrator surface.

**Scope rule**

Module-level or same-process separation MUST NOT be described as production IAM / KMS / HSM or process-isolation proof unless those boundaries are actually demonstrated.

---

### CAT-001.7 — Refusal means represented non-formation

**Proposition**

When the system returns or records a refusal for the protected action, the represented protected consequence MUST NOT form through the tested governed path.

**Required evidence**

Observe both the refusal determination and the actual represented consequence state.

**Scope rule**

A public demonstrator may prove represented non-formation. Physical external non-formation is `ND` unless the external consequence is actually integrated and observed.

---

### CAT-001.8 — Deterministic replay

**Proposition**

The demonstrator's replay claim MUST be reproducible for the state it says is deterministic.

**Required evidence**

At minimum test:

1. same relevant state + same relevant inputs;
2. changed relevant state + historical authority / prior input;
3. replay after refusal, revocation, expiry, or supersession where the demonstrator claims such behavior.

**PASS condition**

Observed replay behavior matches the declared deterministic / authority semantics for the tested cases.

---

### CAT-001.9 — Receipt / evidence integrity

**Proposition**

Published receipts, chain summaries, or evidence objects MUST support the claim being made about determination and represented consequence state.

**Required evidence**

Determine whether the evidence records only what the evaluator decided, or also provides evidence of what represented consequence formed or did not form. Test available tamper / substitution detection where claimed.

**Classification rule**

A decision receipt alone MUST NOT be treated as proof of consequence non-formation.

---

### CAT-001.10 — Restart / persistence

**Proposition**

Where the public claim depends on state surviving process lifetime, security-relevant state MUST survive the represented restart boundary or the limitation must be explicit.

**Required evidence**

Repeat a relevant replay / stale-authority / consumption scenario across a fresh process or documented restart boundary.

**ND condition**

The public demonstrator has no persistence claim or no restart-capable public surface.

---

### CAT-001.11 — Concurrency / authority-change race

**Proposition**

A represented consequence MUST NOT form from authority that loses standing during a tested concurrent authority-change / consequence-formation race, except where the system's explicit serialization semantics establish a lawful ordering in which consequence formation completes first.

**Required evidence**

Exercise at least one reproducible interleaving between authority-state change and consequence formation.

**Scope rule**

In-process locking is not distributed serializability or consensus proof.

---

### CAT-001.12 — Durable state rollback

**Proposition**

If the public demonstrator relies on durable authority / execution state, restoration of older durable state MUST NOT silently resurrect authority or execution capability that the demonstrator claims is no longer valid.

**Required evidence**

Where the public surface supports persistence, restore or simulate restoration of an earlier state and attempt the previously invalid / consumed / superseded action.

**ND condition**

The demonstrator exposes no durable-state surface on which the proposition can be tested.

---

### CAT-001.13 — Fail closed

**Proposition**

If evidence or authority standing required by the represented decision cannot be established, the system MUST NOT convert uncertainty or missing state into permission.

**Required evidence**

Where the public surface permits, test missing, malformed, unavailable, contradictory, or otherwise unverifiable authority/evidence state.

**PASS condition**

The protected action does not form under the tested unresolved state.

---

### CAT-001.14 — Credible bypass attempt

**Proposition**

At least one credible bypass attempt against the published consequence boundary MUST be executed rather than merely discussed.

**Required evidence**

Preserve the exact bypass proposition, method, initial result, and whether the attempt succeeded or failed.

**Classification rule**

A failed bypass attempt is useful PASS evidence only for that tested bypass. It MUST NOT be generalized into universal non-bypassability.

---

### CAT-001.15 — Independent reproduction

**Proposition**

The public proof claim SHOULD be reproducible by an independent party from the published object and its documented run instructions, without private intervention required to obtain the claimed public result.

**Required evidence**

Record:

- repository / object identifier;
- exact commit or immutable revision where available;
- environment assumptions;
- commands / public invocation path;
- observed result;
- deviations from documented instructions, if any.

**Classification rule**

If the public repository does not contain enough material to reproduce a claimed proposition, classify that proposition `ND`; do not infer failure of an undisclosed implementation.

---

## 4. Result-record requirements

Every CAT-001 proposition record MUST include:

1. frozen proposition;
2. target repository / object and exact revision if available;
3. public claim being tested;
4. public artifact / surface exercised;
5. test method;
6. initial result;
7. classification: `PASS · PARTIAL · FAIL · ND`;
8. failure evidence if applicable;
9. remediation if performed by the target owner or in a separately authorized test branch;
10. rerun of the same or semantically preserved proposition;
11. demonstrated scope;
12. residual limitations;
13. explicit statement of what the result does **not** prove.

Historical failures MUST remain preserved even where later remediation produces PASS.

---

## 5. Symmetry rule

CAT-001 results MUST be publishable even where they are inconvenient to the assessor.

Therefore:

- if FlowSignal fails a frozen CAT proposition, record `FAIL`;
- if another architecture passes where FlowSignal previously failed, record `PASS`;
- if a target exposes insufficient public evidence, record `ND`;
- if only part of a proposition is demonstrated, record `PARTIAL`;
- do not reinterpret a bounded PASS as production certification;
- do not reinterpret ND as evidence that a private implementation cannot satisfy the proposition.

No architecture receives a lower or higher evidential burden because of its author, brand, terminology, commercial position, or prior public criticism.

---

## 6. Initial application target

The first external public demonstrator proposed for CAT-001 application is:

**Repository:** `Kamanaka5502/bind-time-authority-proof`

At freeze time, its public README describes the repository as a **bounded demonstrator**, expressly not the production authority fabric, and publicly states demonstrator-level claims including bind-time authority posture, epoch change / reissue, stale-authority refusal, deterministic replay, bounded receipts / chain summaries, fail-closed behavior, no resurrection without reissue, and mutation detectability.

CAT-001 therefore assesses only what that public demonstrator and its published evidence actually expose.

It does **not** assess, infer, reproduce, or make claims about the repository owner's undisclosed production evaluator, signing infrastructure, key management, standing-token format, corridor implementation, production ledger, customer policy, or commercial deployment architecture.

---

## 7. Freeze rule

This document is frozen **before detailed implementation inspection or target-specific test construction**.

Subsequent target-specific tests may operationalize these propositions, but MUST NOT weaken them after the target implementation is examined.

If a proposition proves technically inapplicable to a target's published boundary, record the reason and classify `ND` or `PARTIAL` as appropriate rather than replacing the proposition.

Any future change to CAT-001 after target testing begins MUST be versioned separately and MUST NOT overwrite this frozen challenge record.
