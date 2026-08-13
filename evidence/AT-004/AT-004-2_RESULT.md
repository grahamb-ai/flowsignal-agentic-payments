# AT-004.2 - Evaluator Independence



**Test Series:** AT-004 - Independence Challenge  

**Test:** AT-004.2 - Evaluator Independence  

**Date:** 13 August 2026  

**Status:** PASS



## Objective



Determine whether separation of authoritative mandate state is sufficient when the governed execution environment can control the evaluator that consumes that state.



AT-004.1 established that an independently held authoritative mandate value could prevent a different locally presented mandate value from controlling the Runtime Authority determination.



AT-004.2 tests the next boundary:



Can an evaluator under local execution-environment control ignore independently held authoritative state and produce a different determination?



## Baseline



The test used the same runtime scenario and authority state established in AT-004.1:



\- Proposed payment: GBP 1,400,000

\- Presented mandate limit: GBP 2,000,000

\- Authoritative mandate limit: GBP 1,000,000

\- Mandate: MANDATE-TREASURY-001



Initial regression baseline:



**55 tests passed.**



## Variant A - Independent Evaluator



The standard Runtime Authority evaluator consumed the independently held authoritative mandate limit.



Observed state:



\- Presented mandate limit: GBP 2,000,000

\- Authoritative mandate limit: GBP 1,000,000

\- Proposed payment: GBP 1,400,000

\- `amount\_within\_limit`: false



**Observed determination: ESCALATE**



The proposed payment exceeded the authoritative GBP 1,000,000 mandate limit.



## Variant B - Embedded / Locally Controlled Evaluator



A separate evaluator variant was created to represent an evaluator under the control of the governed execution environment.



The runtime inputs and authoritative state were unchanged.



The evaluator was altered to consume the locally presented mandate value rather than the independently held authoritative mandate value.



Observed state:



\- Presented mandate limit: GBP 2,000,000

\- Authoritative mandate limit: GBP 1,000,000

\- Proposed payment: GBP 1,400,000

\- `amount\_within\_limit`: true



**Observed determination: ALLOW**



The embedded evaluator therefore permitted the same proposed payment that the independent evaluator escalated.



## Observed Differential



**Independent evaluator**



GBP 1.4m payment  

â†’ GBP 1m authoritative limit consumed  

â†’ `amount\_within\_limit = false`  

â†’ **ESCALATE**



**Embedded / locally controlled evaluator**



GBP 1.4m payment  

â†’ GBP 2m presented limit consumed  

â†’ `amount\_within\_limit = true`  

â†’ **ALLOW**



The runtime request and independently held authoritative state were otherwise unchanged.



## Finding



AT-004.2 demonstrates that separation of authoritative state alone is not sufficient to preserve the intended authority constraint if the governed execution environment can control which authority state the evaluator consumes.



In this test, the authoritative GBP 1,000,000 mandate remained available and was explicitly recorded, but the locally controlled evaluator ignored it and consumed the presented GBP 2,000,000 value instead.



This changed the runtime determination from ESCALATE to ALLOW.



The test therefore provides evidence for a narrower architectural property:



> Authority-source independence can be undermined when the governed execution environment retains control over the evaluator responsible for consuming that authority.



## Relationship to AT-004.1



AT-004.1 demonstrated the value of separating authoritative state from locally presented authority state.



AT-004.2 demonstrates that this separation can be defeated if the evaluator itself remains under local control.



Taken together, the two tests distinguish:



1\. **Authority-state independence** - where authoritative mandate state resides.



2\. **Evaluator independence** - who controls the mechanism that determines which state governs the execution decision.



## Scope and Limitation



AT-004.2 does not establish that architectural independence alone guarantees non-bypassability, integrity or correct execution.



It demonstrates only that, under the tested conditions, evaluator control was sufficient to change the Runtime Authority determination despite unchanged authoritative state.



Further tests are required to determine whether a correct independent determination can itself be bypassed on the path to consequence formation.



## Evidence



\- Scenario: `harness/scenarios/AT-004-1\_independence\_test.json`

\- Independent evaluator: `app/engines/financial\_runtime.py`

\- Embedded evaluator variant: `app/engines/financial\_runtime\_embedded.py`

\- Independent runner: `harness/runner.py`

\- Embedded runner: `harness/runner\_embedded.py`

\- Authority source: `app/engines/authority\_store.py`



## Next Question



AT-004.1 tested authority-state independence.



AT-004.2 tested evaluator independence.



The next architectural question is:



> Even where authoritative state and the evaluator are independent, can a consequence-producing execution path bypass the resulting Runtime Authority determination?



That question should be tested separately rather than inferred from AT-004.1 or AT-004.2.



