# CAT-001 — Symmetric Cross-Architecture Comparative Result

**Date:** 20 August 2026  
**Status:** FROZEN COMPARATIVE QUALIFICATION RECORD  
**Classification vocabulary:** PASS · PARTIAL · FAIL · NOT DEMONSTRATED (ND)

## Frozen targets

### External public demonstrator

Repository: `Kamanaka5502/bind-time-authority-proof`  
Frozen commit: `d71d743e23098fb58454d8d412cb4a988681d2c1`  
Declared boundary: bounded public demonstrator; not production authority fabric

### FlowSignal

Repository: `grahamb-ai/flowsignal-agentic-payments`  
Frozen maintained MVP commit: `4c5092c8df704a58327c4a5e5c6ae9fc81755ef2`  
Declared boundary: represented Agentic Payments reference-MVP; not production certification

The external result was frozen before FlowSignal was classified. The same fifteen propositions and classification vocabulary were then applied to FlowSignal without weakening the burden.

## Comparative matrix

| Proposition | External target | FlowSignal |
|---|---|---|
| 1. Standing at effect | PARTIAL | PASS |
| 2. No stale authority | PARTIAL | PASS |
| 3. Changed-condition refusal | PARTIAL | PASS |
| 4. No resurrection without legitimate reissue | PARTIAL | PASS |
| 5. Governed route closure | PARTIAL | PARTIAL |
| 6. Independent execution capability | ND | PASS — bounded component/module |
| 7. Refusal means represented non-formation | PARTIAL | PASS — represented consequence |
| 8. Deterministic replay | PARTIAL | PASS — bounded |
| 9. Receipt / evidence integrity | PARTIAL | PASS — bounded consequence evidence |
| 10. Restart / persistence | PARTIAL | PASS — tested represented restart |
| 11. Concurrency / authority-change race | ND | PASS — in-process represented ordering |
| 12. Durable state rollback | PARTIAL | PASS — exact tested rollback with surviving anchor |
| 13. Fail closed | PARTIAL | PASS — bounded tested conditions |
| 14. Credible bypass attempt | ND | PASS — executed adversarial attempts |
| 15. Independent reproduction | PARTIAL | PASS — clean public CI reproduction |

## Descriptive counts

**External target:** 0 PASS · 12 PARTIAL · 3 ND · 0 FAIL  
**FlowSignal:** 14 PASS · 1 PARTIAL · 0 ND · 0 FAIL

These counts are descriptive only. The propositions are not additive proof units and this record is not a numerical product score.

## Interpretation

The external target is a meaningful bounded demonstrator of bind-time authority concepts. CAT-001 found no proposition on which the frozen public target demonstrated an actual violation resulting in an invalid represented protected consequence; accordingly it records no FAIL. Its principal limitation under CAT-001 is composition of the public evidence: authority-state/standing demonstrations and the consequence-like `/commit` route do not provide complete end-to-end proof across the frozen burden, and several adversarial/persistence/concurrency propositions are not publicly demonstrated.

FlowSignal's stronger CAT result is supported by a materially different evidence estate rather than terminology. The maintained reference-MVP contains consequence-forming tests that deliberately exercised stale standing, no-bind capability, duplicate/restart replay, temporal expiry, authority rollback, receipt failure, crash ambiguity, concurrency and durable-state rollback. Multiple propositions initially failed, including failures that actually formed a represented consequence. Those failures were preserved, mechanisms were strengthened, unchanged-semantic challenges were rerun, and the final integrated qualified candidate reproduced 53 passed / 0 failed on a clean GitHub-hosted runner.

FlowSignal does not receive a full PASS for governed route closure because universal external route closure remains NOT DEMONSTRATED. Other PASS results remain explicitly bounded to their tested reference-MVP surfaces and do not imply production IAM/KMS/HSM isolation, distributed consensus/serializability, universal route closure, real payment-rail prevention, immutable external audit evidence or physical non-formation.

## Strongest safe comparative conclusion

> Under a fifteen-proposition proof burden frozen before detailed inspection of the external target, the external public demonstrator earns 12 PARTIAL and 3 NOT DEMONSTRATED classifications, with no FAIL. Applying the same unchanged burden to the frozen FlowSignal reference-MVP earns 14 PASS and 1 PARTIAL, with no FAIL or ND. The difference is attributable to the executable evidence available within the two declared public/reference boundaries, particularly FlowSignal's composed protected-consequence tests, preserved failure lineage, adversarial reruns, persistence/concurrency qualification and clean CI reproduction. It is not evidence of production equivalence, universal superiority or a finding about either system's undisclosed production architecture.

## Non-claims

CAT-001 does not establish:

- production certification of FlowSignal;
- production inadequacy of the external target;
- architectural derivation, equivalence or non-equivalence beyond the tested propositions;
- universal non-bypassability of either architecture;
- distributed-system correctness beyond the explicitly tested surfaces;
- external physical payment non-formation; or
- independent commercial endorsement.

Evidence first. Scope explicit. Failures preserved. No extrapolation.
