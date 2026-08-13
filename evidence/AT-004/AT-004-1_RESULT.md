# AT-004.1 - Authority Source Separation



**Test Series:** AT-004 - Independence Challenge

**Test:** AT-004.1 - Authority Source Separation

**Date:** 13 August 2026

**Status:** PASS



## Objective



Determine whether separating authoritative mandate state from the execution environment materially changes the Runtime Authority determination when the execution environment presents a different authority value.



## Baseline



Existing scenario AP-002 established:



* Proposed payment: GBP 1,400,000

* Authoritative mandate limit: GBP 1,000,000

* Expected determination: ESCALATE



Existing non-database regression baseline:



* 55 tests passed



## Variant A - Presented Authority Consumed



The test scenario presented:



* Proposed payment: GBP 1,400,000

* Presented mandate limit: GBP 2,000,000



The existing Runtime Authority implementation consumed the presented mandate value.



**Observed determination: ALLOW**



The `amount\_within\_limit` check passed because GBP 1,400,000 was evaluated against the presented GBP 2,000,000 limit.



## Variant B - Independent Authority Consumed



A separate Runtime Authority mandate store was introduced containing:



* Mandate: MANDATE-TREASURY-001

* Authoritative mandate limit: GBP 1,000,000



The test scenario remained unchanged and continued to present a mandate limit of GBP 2,000,000.



Runtime Authority evaluated the same GBP 1,400,000 proposed payment against its independently held GBP 1,000,000 authoritative limit.



**Observed determination: ESCALATE**



The Authority Receipt explicitly recorded:



* Presented mandate limit: GBP 2,000,000

* Authoritative mandate limit: GBP 1,000,000

* `amount\_within\_limit`: false

* Determination: ESCALATE



## Observed Differential



**Presented authority consumed**



GBP 1.4m request â†’ GBP 2m presented limit â†’ **ALLOW**



**Independent authority consumed**



GBP 1.4m request â†’ GBP 2m presented limit â†’ GBP 1m authoritative limit â†’ **ESCALATE**



## Finding



AT-004.1 demonstrates that separating authoritative mandate state from the execution environment can prevent a different locally presented authority value from changing the Runtime Authority outcome.



The test does not establish that architectural independence is universally necessary or sufficient.



It establishes a narrower, falsifiable result:



> Where the execution environment presents authority state that differs from independently held authoritative state, consuming the independent state can preserve the intended authority constraint.



## Regression



Following introduction of the independent authority source:



**55 tests passed.**



No regression was observed in the existing non-database test suite.



## Evidence



* Scenario: `harness/scenarios/AT-004-1\_independence\_test.json`

* Independent receipt: `harness/receipts/AT-004-1\_independent\_receipt.json`

* Authority source: `app/engines/authority\_store.py`

* Runtime evaluator: `app/engines/financial\_runtime.py`



## Limitation / Next Question



AT-004.1 tests authority-source separation only.



It does not yet establish whether the execution environment can alter, replace, disable or otherwise influence the independent evaluator itself.



That question is reserved for subsequent AT-004 tests.




