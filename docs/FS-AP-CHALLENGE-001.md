# FS-AP-CHALLENGE-001
## External Challenge and Adversarial Test Register

**Project:** FlowSignal Agentic Payments Harness  
**Context:** UK Financial Services AI Adoption Plan — Recommendation 10  
**Status:** Working Engineering Register  
**Baseline:** v0.9-baseline  
**Next Test Revision:** v0.10  

---

## 1. Purpose

Following publication of FS-AN-004 and the accompanying FlowSignal Agentic Payments Harness, external practitioners raised a number of substantive technical challenges concerning the implementation and the evidential claims that can reasonably be made from it.

This register records those challenges and translates them into explicit adversarial test obligations for the next revision of the reference implementation.

The objective is not to demonstrate that the implementation always succeeds.

The objective is to expose the proposition to conditions capable of falsifying, limiting or refining the claims made for Runtime Authority in the agentic-payments context.

A failed adversarial test is therefore a valid and potentially valuable result where it identifies a boundary, bypass, unsupported assumption or incomplete control.

---

## 2. Provenance and Attribution

The challenges recorded here arose from public technical discussion following publication of the FlowSignal Agentic Payments work.

Contributors to that discussion include:

- Richard Lynes
- Roman Murtazin
- Ishaan Ghosh
- Luis Fernando Martinez Chavez
- Mahreen U.
- Dextra Labs
- other participants in the public discussion

Attribution records the provenance of technical challenge inputs only.

Inclusion in this register does not imply that any contributor has formally reviewed, verified or endorsed FlowSignal, FS-AN-004, the Runtime Authority model, the UK Financial Services AI Adoption Plan analysis, or the reference implementation.

FlowSignal remains solely responsible for the interpretation, implementation and conclusions arising from these challenges.

---

## 3. Baseline

The implementation state preceding this challenge cycle has been preserved as:

**v0.9-baseline**

The baseline must remain reproducible and must not be rewritten to incorporate subsequent test outcomes.

Adversarial testing will be developed separately against revision:

**adversarial-testing-v0.10**

This preserves a clear distinction between:

1. the implementation originally published;
2. challenges subsequently raised;
3. tests derived from those challenges;
4. resulting evidence;
5. any later architectural or implementation changes.

---

# 4. Challenge Register

## CH-001 — Independent Authority Predicate Evaluation

### Challenge

A valid identity or authentication result must not obscure a failure in the authority required for the specific financial action.

At execution, at least three questions should remain independently observable:

1. Does the delegated mandate remain valid now?
2. Does the mandate's attenuated scope cover this exact financial action?
3. Does the earlier approval remain applicable to the current request and context?

### Test Objective

Demonstrate that each authority predicate can independently alter the Runtime Authority determination.

For combined failure cases, preserve:

- which predicate or predicates failed;
- evidence used for each predicate;
- relevant evidence timestamps;
- resulting determination;
- whether the combination of failures materially altered the determination.

### Falsification Condition

The implementation fails this challenge if a predicate failure cannot be independently identified or if a valid identity/authentication state masks an authority failure.

---

## CH-002 — Escalation Timeout and Fail-Closed Behaviour

### Challenge

An unresolved ESCALATE state must not become implicit permission through timeout, system failure, unavailable escalation infrastructure or operational pressure.

Expiry of an escalation should also remain evidentially distinguishable from an escalation that was never raised.

### Test Objective

Test behaviour when:

- escalation remains unresolved;
- escalation expires;
- the escalation service becomes unavailable;
- a response arrives after expiry;
- execution is attempted while escalation remains pending.

### Expected Safety Property

Absence of a valid current authority determination must not become permission to execute.

### Falsification Condition

The implementation fails this challenge if an unresolved, expired or unavailable escalation path allows the protected financial consequence to proceed without a new valid authority determination.

---

## CH-003 — Executor Binding

### Challenge

An ALLOW, ESCALATE or REFUSE record is evidence of a Runtime Authority determination.

It does not, by itself, demonstrate that the determination was causally binding on the executor.

### Test Objective

Attempt execution:

- without a Runtime Authority determination;
- following REFUSE;
- while ESCALATE remains unresolved;
- using an expired determination;
- using a replayed previous ALLOW;
- using a determination relating to a materially different action.

### Expected Property

The protected executor should require a valid and current Runtime Authority determination appropriate to the exact action being executed.

### Falsification Condition

The implementation fails this challenge if the protected executor can create the financial consequence without consuming an appropriate current determination.

---

## CH-004 — Alternate-Route Challenge

### Challenge

Blocking one execution interface does not demonstrate control of the protected financial consequence if the same or materially equivalent consequence can be created through another route.

Potential routes may include:

- another API;
- another executor;
- another credential;
- a service account;
- another delegated agent;
- an orchestration path;
- another materially equivalent execution mechanism represented within the declared test environment.

### Test Objective

Following REFUSE or invalidation of authority, attempt to recreate the protected consequence through each declared alternative execution route.

### Expected Property

The protected consequence should not be reproducible through an alternative route that falls within the declared execution surface.

### Falsification Condition

The challenge is failed if an alternative route successfully produces the protected consequence despite the Runtime Authority determination.

Such a failure must be preserved as evidence rather than hidden or reclassified.

---

## CH-005 — Consequence-Surface Verification

### Challenge

An Authority Receipt witnesses a determination.

It does not, by itself, prove enforcement.

The resulting protected state must therefore be independently observed after an execution attempt.

### Test Objective

Following each adversarial execution attempt:

1. inspect the Runtime Authority determination;
2. inspect the executor response;
3. inspect the resulting protected state;
4. determine whether the intended financial consequence actually occurred;
5. preserve the evidence linking those observations.

### Expected Property

A REFUSE or invalidated authority state should prevent the protected consequence across the declared execution surface.

### Falsification Condition

The challenge is failed if the evidence records REFUSE while the protected financial consequence nevertheless occurs within the declared test surface.

---

## CH-006 — Policy Explicitness and Tacit Organisational Authority

### Challenge

Runtime admissibility rules can only deterministically evaluate authority conditions that have been made sufficiently explicit.

Institutional authority may partly exist in undocumented practice, human judgement or organisational convention rather than formal machine-evaluable policy.

### Test Objective

Ensure that the implementation distinguishes between:

- an explicit rule evaluated successfully;
- insufficient evidence;
- unavailable policy;
- ambiguous policy;
- authority conditions outside the declared rule set.

### Expected Property

The implementation must not manufacture deterministic authority from organisational knowledge that has not been represented as trusted evidence or policy.

### Falsification Condition

The implementation fails this challenge if missing or ambiguous institutional authority is silently interpreted as permission.

---

## CH-007 — Architecture, Implementation and Evidence Separation

### Challenge

Architecture describes the intended control proposition.

Implementation demonstrates one operationalisation of that proposition.

Evidence records what a particular implementation actually did.

These must remain distinct.

### Test Objective

Ensure implementation evidence is tied to:

- a specific source revision;
- a specific test configuration;
- specific inputs;
- specific outputs;
- relevant timestamps;
- the resulting protected-state observation.

### Expected Property

Implementation evidence must not be represented as formal proof of every architectural claim.

### Falsification Condition

The evidential claim is invalid if evidence cannot be associated with the implementation revision and test conditions that produced it.

---

# 5. Adversarial Test Progression

The next test phase will use the following progression:

**Determination Integrity**  
↓  
**Executor Binding**  
↓  
**Alternate-Route Challenge**  
↓  
**Protected-State Observation**  
↓  
**Preserved Evidence**

This progression deliberately moves beyond asking whether Runtime Authority produced the expected decision.

The stronger question is:

> Did that determination actually govern the protected financial consequence across the declared execution surface?

---

## 6. Evidence Principle

The adversarial test suite must preserve both successful and failed tests.

A failed test may demonstrate:

- an implementation defect;
- an incomplete execution boundary;
- an alternate route around Runtime Authority;
- an unsupported architectural assumption;
- an evidential limitation;
- a need to narrow the claim being made.

Such outcomes are part of the engineering evidence.

They must not be removed merely to produce a fully passing test suite.

---

## 7. Scope Limitation

The adversarial tests demonstrate properties only within the execution surface explicitly represented by the reference implementation.

Passing the alternate-route tests does not establish universal consequence-surface closure across arbitrary external financial infrastructure.

Any claim of enforcement or consequence-surface closure must therefore identify the execution surface over which that claim was tested.

---

## 8. Next Step

The challenge register will now be translated into executable adversarial tests.

The initial test families will cover:

1. authority predicate isolation and combined failures;
2. ESCALATE timeout and fail-closed behaviour;
3. executor binding;
4. stale and replayed determinations;
5. alternate execution routes;
6. protected-state verification;
7. evidence preservation.

Results will be compared against the preserved **v0.9-baseline** before any resulting implementation changes are incorporated.
