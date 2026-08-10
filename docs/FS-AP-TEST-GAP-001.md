# FS-AP-TEST-GAP-001
## v0.9 Baseline Test Coverage and Adversarial Test Gap

**Project:** FlowSignal Agentic Payments Harness  
**Context:** UK Financial Services AI Adoption Plan — Recommendation 10  
**Baseline:** v0.9-baseline  
**Adversarial Revision:** v0.10  

---

## 1. Purpose

This note records the distinction between the test coverage already present in the preserved v0.9 Agentic Payments Harness and the additional proof obligations identified through external technical challenge following publication.

The purpose is to avoid representing existing baseline behaviour as newly demonstrated adversarial evidence.

---

## 2. v0.9 Baseline

The preserved v0.9 harness contains six executable tests.

Those tests primarily exercise Runtime Authority determination behaviour and evidence preservation under a set of predefined agentic-payment scenarios.

Existing coverage includes conditions relating to:

- permitted payment execution conditions;
- required provenance and evidence references;
- authenticated and delegated agent state;
- changes in runtime conditions;
- counterparty or action-context changes;
- preservation of determination evidence.

The v0.9 tests therefore provide evidence about the behaviour of the Runtime Authority determination logic.

They do not by themselves establish that every determination is causally enforced across the financial consequence surface.

---

## 3. Newly Identified Proof Obligations

External technical challenge raised additional questions that are not established merely by the existing six tests.

### GAP-001 — Independent Predicate Failure Visibility

Determine whether mandate validity, action scope and continuing approval applicability can be independently evaluated and evidenced.

### GAP-002 — ESCALATE Timeout Behaviour

Determine whether an unresolved or expired ESCALATE state fails closed rather than becoming implicit permission.

### GAP-003 — Executor Binding

Determine whether the protected executor can operate without consuming a valid current Runtime Authority determination.

### GAP-004 — Stale or Replayed ALLOW

Determine whether an earlier ALLOW determination can be reused after expiry, context change or for a materially different action.

### GAP-005 — Alternate Execution Route

Determine whether REFUSE on the nominal route can be bypassed through another represented executor, credential, API or execution path.

### GAP-006 — Protected-State Verification

Determine whether the financial consequence actually occurred after each attempted execution, rather than relying solely on the Runtime Authority decision record.

### GAP-007 — Enforcement Evidence

Determine whether evidence can distinguish:

1. the authority determination;
2. the executor response; and
3. the resulting protected financial state.

---

## 4. Test Boundary

The v0.10 adversarial suite will not replace or rewrite the original six v0.9 tests.

The original tests remain part of the preserved baseline.

The new tests will address only the additional proof obligations defined above.

---

## 5. Engineering Principle

A Runtime Authority determination and enforcement of that determination are separate evidential questions.

The v0.9 baseline primarily demonstrates determination behaviour.

The v0.10 adversarial phase will test the stronger proposition:

> Did the Runtime Authority determination actually constrain the protected financial consequence within the declared execution surface?
