# FlowSignal™ Runtime Authority
## Verification Report — September 2026

**Status:** Verified reference implementation candidate  
**Verification result:** 124/124 selected cross-family tests GREEN  
**Purpose:** External technical and commercial evidence summary

---

## 1. Executive summary

FlowSignal is developing Runtime Authority Infrastructure for autonomous enterprise systems.

Its purpose is to determine whether a proposed action remains authorised and admissible immediately before operational consequence is allowed to form.

The reference implementation has now completed a deliberate failure-first verification programme across the authority lifecycle and protected execution boundary.

The work did not begin from an assumption that the implementation was correct. Verification cases were designed to challenge whether apparently valid execution material could still produce a protected consequence when required authority relationships were missing, reused, substituted or incorrectly composed.

Several cases exposed genuine weaknesses. Those failures were preserved as evidence, their causes were traced, and narrowly scoped remediations were applied without deleting or weakening the relevant negative-path cases.

The final selected cross-family regression completed:

```
124 passed in 0.68s
```

This report describes what that result demonstrates — and what it does not.

---

## 2. The question being tested

Enterprise systems commonly establish approval before execution.

For autonomous systems, that is not enough.

The runtime question is:

> Does the authority relied upon by this exact execution still correspond to the actor, action, target, mandate, current state and execution material at the point consequence is about to form?

FlowSignal treats this as an execution-boundary problem.

The reference implementation therefore tests not merely whether an approval or permit exists, but whether the authority chain presented at protected execution remains causally and structurally connected to the decision that was actually validated.

---

## 3. Verification scope

The final selected regression spans:

- **R1 — Exact money:** rejection of unsafe or ambiguous monetary representations.
- **R2 — Authority and authoritative state:** authority domain, authoritative evidence, resolution, determination and final-bind revalidation.
- **R3 — Approval:** correspondence between approval state and executable authority.
- **R4 — Authority usage:** reservation, consumption and bounded authority usage.
- **R5 — Lineage:** preservation of required authority lineage.
- **R6 — Final-bind provenance and causal correspondence:** proof that execution material derives from the successful final-bind path rather than merely resembling it.
- **Integrated payment path:** end-to-end reference execution.
- **Protected execution boundary:** enforcement immediately before consequence formation.

The final verification workflow also deliberately includes the R1 exact-money and R2 authoritative-state regressions that had previously been omitted from the branch workflow.

---

## 4. What the failure-first work found

### 4.1 Genuine provenance could be reused with a different signed permit

A valid final-bind provenance record was originally bound to the authority lineage and usage reservation, but not to the exact permit signature produced by that mint event.

A separately signed permit carrying the same legitimate lineage was therefore able, in the first-failure state, to reach:

```
CONSEQUENCE_FORMED
```

**Remediation:** final-bind provenance was bound to the exact permit signature at establishment and verification.

**Result:** the demonstrated cross-permit reuse route no longer forms a protected consequence.

### 4.2 Possession of low-level reference capabilities could substitute for causal final-bind

The reference implementation originally used module-level capability objects to gate low-level operations.

A caller able to reach all relevant low-level reference capabilities could construct mutually consistent permit, usage, provenance and registry material without traversing the successful integrated final-bind path.

The first-failure result was:

```
CONSEQUENCE_FORMED
```

**Remediation:** successful final-bind now emits a one-shot causal grant. Final-bind provenance establishment requires and consumes that grant.

**Result:** possession of the tested low-level reference capabilities alone is insufficient to manufacture equivalent executable state.

### 4.3 A genuine causal grant was not initially bound to the exact decision artifacts

The first causal-grant design proved successful final-bind for the operation/exercise/attempt relationship, but did not bind the grant to the exact determination and constraint validated by that final-bind.

Substituted decision identifiers could therefore be carried consistently through downstream material.

The first-failure result was:

```
CONSEQUENCE_FORMED
```

**Remediation:** the one-shot causal grant was extended to bind the exact determination ID and constraint ID in addition to the protected operation, authority exercise and execution attempt.

**Result:** substituted decision artifacts are rejected before protected consequence formation.

### 4.4 Incorrect correspondence could consume a genuine grant

A mismatched presentation was correctly rejected, but the reference grant consumer removed the genuine grant before checking correspondence. A later valid presentation therefore failed as well.

This was **not** an unauthorised-consequence finding. It was a bounded availability weakness.

**Remediation:** comparison and consumption now occur atomically under the existing lock. Incorrect correspondence does not remove the grant; exact correspondence consumes it once.

**Result:** the valid grant survives an incorrect presentation while retaining single-use semantics.

---

## 5. Verification progression

The preserved evidence shows the verification progressing through increasingly stronger checkpoints:

| Checkpoint | Result |
|---|---:|
| Preserved baseline before next-order R6 verification | 111 GREEN |
| Exact-permit provenance remediation checkpoint | 113 GREEN |
| Causal final-bind remediation checkpoint | 114 GREEN |
| One-shot causal grant verification | 115 GREEN |
| Exact decision-correspondence remediation | 116 GREEN |
| Grant mismatch-preservation remediation | 117 GREEN |
| Expanded cross-family regression | 124 GREEN |
| Final confirmation | **124 GREEN in 0.68s** |

The importance of this progression is not the test count by itself. It is that meaningful first failures were retained and the regression suite grew without removing the conditions that exposed them.

---

## 6. What is demonstrated

Within the tested reference-harness boundary, the evidence demonstrates that:

- final-bind provenance must correspond to the exact execution permit;
- provenance from one tested execution chain cannot simply be transplanted into another tested chain to form a protected consequence;
- the tested collection of low-level reference capabilities cannot substitute for successful causal final-bind;
- the one-shot causal grant corresponds to the exact tested decision artifacts and execution lineage;
- incorrect grant correspondence is rejected without destroying a still-valid grant;
- successful grant consumption remains single-use; and
- the selected R1–R6 and integrated execution families remain regression-compatible at the final checkpoint.

These are concrete tested properties, not a claim that every possible runtime-authority failure mode has been eliminated.

---

## 7. What is not claimed

This verification does **not** establish:

- production certification;
- production-grade persistence;
- multi-process or distributed coordination;
- distributed atomicity;
- crash or power-loss durability;
- production IAM, HSM or KMS isolation;
- external payment-system idempotency;
- resistance to arbitrary mutation of private process-local reference state;
- complete rollback resistance across every possible state store; or
- global closure of every possible runtime-authority route.

Those concerns require separate production architecture, infrastructure and independent verification.

---

## 8. Why this matters commercially

The exercise demonstrates the difference between asserting that an autonomous action is authorised and producing evidence that the execution boundary actually enforces that authority relationship.

For an enterprise deployment, the same verification method can be applied to a selected consequential workflow:

1. identify the protected execution point;
2. define the authority and admissibility invariants;
3. exercise failure, substitution, replay and stale-state conditions;
4. preserve first failures;
5. remediate demonstrated weaknesses without weakening the verification boundary;
6. rerun the integrated regression; and
7. produce an evidence pack showing what was tested, what failed, what changed and what subsequently passed.

That is the basis of FlowSignal's Authority Validation approach.

---

## 9. Evidence position

The underlying repository retains the detailed failure-first records, remediation lineage and regression evidence supporting this summary.

The verified engineering/checkpoint head is:

```
257d28cd6171475afd6b6b37b2db2a954399939b
```

A subsequent evidence-only annotation records the final 124/124 confirmation.

---

## 10. Conclusion

The FlowSignal reference implementation has reached a bounded verified candidate checkpoint.

The significant result is not simply that the final suite is GREEN.

It is that the implementation was allowed to fail under deliberately difficult verification conditions, those failures were preserved, the demonstrated weaknesses were corrected narrowly, and the complete selected cross-family suite remained GREEN afterwards.

**Before AI acts, know it's authorised.**

**FlowSignal™ — EXECUTE WITH AUTHORITY. DEFEND WITH EVIDENCE.**
