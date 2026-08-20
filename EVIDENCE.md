# FlowSignal Agentic Payments — Executable Evidence Index

**Status:** Public engineering evidence index  
**Updated:** 20 August 2026  
**Scope:** FlowSignal Agentic Payments reference-MVP  
**Production certification:** No

> **This file is an index to executable evidence. It is not itself the evidence.** Follow each entry to the implementation, executable test, preserved qualification record and CI execution evidence.

## Evidence standard

FlowSignal uses the following evidence chain:

**Claim / proposition → implementation artifact → executable test → observed result or preserved failure → remediation where required → semantic rerun → demonstrated scope → residual limitation**

A PASS is not a claim of universal or production correctness. Where evidence is incomplete, the qualification remains PARTIAL or NOT DEMONSTRATED.

## Current qualified public baseline

The maintained reference-MVP has a qualified regression of **53 passed / 0 failed**. This is a regression count, **not 53 independent proofs**.

The qualified candidate was executed on a clean GitHub-hosted Ubuntu runner using Python 3.11, installing dependencies from this repository and running `pytest -q`. GitHub Actions run `32175169365` recorded `53 passed in 3.01s` before the qualified candidate was merged into the maintained baseline.

This is **clean hosted CI reproduction**, not independent third-party validation.

## Primary executable evidence map

| Proposition | Primary executable evidence | What the evidence demonstrates | Current bounded result |
|---|---|---|---|
| Standing still valid at consequence boundary | [`harness/tests/test_pmq002_3_concurrent_authority_revocation.py`](harness/tests/test_pmq002_3_concurrent_authority_revocation.py), [`harness/tests/test_pmq002_4_expiry_at_boundary.py`](harness/tests/test_pmq002_4_expiry_at_boundary.py) | Current authority/temporal standing is exercised at the represented final consequence boundary, including concurrent revocation and expiry while waiting for that boundary. | PASS — represented reference-MVP |
| Previously valid authority cannot remain sufficient after relevant state change | [`harness/tests/test_pmq002_3_concurrent_authority_revocation.py`](harness/tests/test_pmq002_3_concurrent_authority_revocation.py), [`harness/tests/test_pmq002_5_authority_state_rollback.py`](harness/tests/test_pmq002_5_authority_state_rollback.py) | Stale/superseded authority and reachable rollback/resurrection conditions are exercised before represented consequence formation. | PASS — tested state paths |
| Changed condition can cause refusal/non-formation | [`harness/tests/test_pmq002_3_concurrent_authority_revocation.py`](harness/tests/test_pmq002_3_concurrent_authority_revocation.py), [`harness/tests/test_pmq002_4_expiry_at_boundary.py`](harness/tests/test_pmq002_4_expiry_at_boundary.py) | Earlier-valid conditions can change before the final boundary and prevent represented consequence formation. | PASS — tested changes |
| Required evidence unavailable must fail closed | [`harness/tests/test_pmq001_fail_closed_evidence.py`](harness/tests/test_pmq001_fail_closed_evidence.py) | Unavailable required evidence is exercised as a failure condition rather than converted into permission. | PASS — tested evidence condition |
| Direct no-bind / pre-bind capability bypass | [`harness/tests/test_pmq001_prebind_capability_bypass.py`](harness/tests/test_pmq001_prebind_capability_bypass.py) | A direct bypass was executed. It initially succeeded in obtaining consequence-forming capability without the required authority evidence; the failure was preserved, remediated and rerun. | PASS for tested bypass; universal route closure remains PARTIAL |
| Permit cannot remain valid after final-boundary expiry | [`harness/tests/test_pmq001_delayed_permit_expiry.py`](harness/tests/test_pmq001_delayed_permit_expiry.py), [`harness/tests/test_pmq002_4_expiry_at_boundary.py`](harness/tests/test_pmq002_4_expiry_at_boundary.py) | Temporal standing at the protected boundary was adversarially exercised. A real expiry-boundary weakness was found and remediated. | PASS — tested temporal boundary |
| Exact permit cannot form repeated represented consequences | [`harness/tests/test_pmq001_duplicate_permit_replay.py`](harness/tests/test_pmq001_duplicate_permit_replay.py), [`harness/tests/test_pmq002_1_restart_replay.py`](harness/tests/test_pmq002_1_restart_replay.py), [`harness/tests/test_pmq002_2_multi_instance_replay.py`](harness/tests/test_pmq002_2_multi_instance_replay.py) | Sequential/concurrent replay, restart replay and tested shared-store multi-instance replay are exercised. Historical replay failures are preserved. | PASS — tested replay surfaces |
| Authority cannot resurrect through tested rollback | [`harness/tests/test_pmq002_5_authority_state_rollback.py`](harness/tests/test_pmq002_5_authority_state_rollback.py) | A reachable authority-state rollback/resurrection weakness was deliberately exercised, failed, remediated and rerun. | PASS — tested reachable mutation path |
| Consequence outcome evidence is separate from authority decision | [`harness/tests/test_pmq001_consequence_outcome_receipt.py`](harness/tests/test_pmq001_consequence_outcome_receipt.py), [`harness/tests/test_pmq002_6_consequence_evidence_crash.py`](harness/tests/test_pmq002_6_consequence_evidence_crash.py) | A decision receipt is not treated as proof of consequence state. Consequence formation plus subsequent evidence failure was deliberately exercised and remediated. | PASS — represented consequence evidence |
| Consumed-before-formation failure remains recoverable | [`harness/tests/test_pmq002_7_consumed_before_formation_crash.py`](harness/tests/test_pmq002_7_consumed_before_formation_crash.py) | Catchable executor failure after permit consumption records recoverable non-formation rather than silently losing consequence state. | PASS — tested failure window |
| Hard process termination does not invent a known outcome | [`harness/tests/test_pmq002_8_hard_crash_recovery.py`](harness/tests/test_pmq002_8_hard_crash_recovery.py) | The represented hard-kill window preserves an UNRESOLVED state rather than falsely claiming formation/non-formation; replay remains controlled. | PASS — tested crash window |
| Permit consumption and initial outcome creation are atomic for tested store design | [`harness/tests/test_pmq002_9_two_store_atomicity.py`](harness/tests/test_pmq002_9_two_store_atomicity.py) | The crash window between consumption and initial outcome creation was exercised and remediated using the represented SQLite transaction boundary. | PASS — tested store design |
| Durable state rollback must not resurrect consumed permit | [`harness/tests/test_pmq002_10_storage_rollback.py`](harness/tests/test_pmq002_10_storage_rollback.py) | Restoring tested permit/outcome stores to pre-execution snapshots initially re-enabled the exact permit and formed a second represented consequence. Failure preserved; surviving reference anchor added; unchanged semantic challenge rerun. | PASS only when separate reference anchor survives |

## Preserved failure record

The public evidence estate intentionally contains failures. They are not removed from the engineering history when the implementation is strengthened.

Material failures discovered during qualification include:

- direct pre-bind/no-bind execution capability allowing a represented consequence without the required Runtime Authority evidence;
- sequential/concurrent exact-permit replay;
- replay after represented restart forming a second represented consequence;
- permit expiry while waiting for the protected boundary;
- reachable authority-state rollback/resurrection;
- represented consequence formation followed by consequence-evidence failure;
- consumed-before-formation execution failure ambiguity;
- hard process termination leaving execution state uncertain;
- crash between durable permit consumption and outcome creation;
- durable store rollback resurrecting a consumed permit and forming a second represented consequence.

The detailed failure → remediation → rerun lineage is retained under [`evidence/PMQ-001/`](evidence/PMQ-001/), [`evidence/PMQ-002/`](evidence/PMQ-002/) and the architecture-neutral [`evidence/CAT-001/`](evidence/CAT-001/) qualification record.

## Reproduce the current test corpus

A technically competent reviewer should not need private instructions from FlowSignal to execute the public test corpus.

```bash
git clone https://github.com/grahamb-ai/flowsignal-agentic-payments.git
cd flowsignal-agentic-payments
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```

The qualified candidate associated with the current evidence estate produced **53 passed / 0 failed** on GitHub-hosted CI. Future repository changes may legitimately change the collected test count; therefore the number should always be read with the relevant commit/workflow evidence rather than treated as a permanent product metric.

## What this evidence does NOT establish

The public reference-MVP does **not** claim to demonstrate:

- production certification;
- universal route closure or universal non-bypassability;
- prevention across real bank/payment rails;
- external physical consequence non-formation;
- production process/IAM/KMS/HSM isolation;
- distributed consensus, serializability or multi-region correctness;
- resistance to privileged host/storage compromise;
- rollback resistance where every store and surviving reference anchor is coherently restored or compromised;
- immutable/write-once external audit infrastructure;
- real external evidence-provider outage/transport/malformed-payload behaviour unless explicitly tested;
- independent third-party reproduction, validation or commercial endorsement.

Those are separate proof obligations. They must not be inferred from the reference-MVP evidence above.

## Architecture-neutral qualification

[`evidence/CAT-001/CAT-001_COMPARATIVE_RESULT.md`](evidence/CAT-001/CAT-001_COMPARATIVE_RESULT.md) is a qualification report and evidence mapping. **It is not the primary evidence.** The executable tests and observed execution records linked above are the primary engineering evidence.

CAT-001 deliberately froze its proposition set before comparative assessment and retains PASS / PARTIAL / FAIL / NOT DEMONSTRATED classifications with explicit residual limitations.

---

**Evidence first. Claim second. Scope explicit. Failures preserved. No extrapolation.**
