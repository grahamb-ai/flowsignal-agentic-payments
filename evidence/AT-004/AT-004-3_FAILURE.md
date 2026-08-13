# AT-004.3 - Determination Non-Bypassability



Date: 13 August 2026

Status: FAIL - preserved prior to remediation



## Objective



Determine whether every path capable of reaching the represented

consequential execution state must consume a valid Execution Gateway

determination.



## Baseline



Existing non-database regression suite:



55 passed



The existing Execution Gateway correctly validates:



\- Runtime Authority decision

\- determination validity / expiry

\- action binding



Existing AP-006 tests demonstrate that the gateway blocks an altered

execution attempt and permits an exact action bound to a valid ALLOW.



## Adversarial Invariant



No governed consequence may be reported as EXECUTION PERMITTED unless

that consequence has consumed a PERMITTED Execution Gateway determination.



## Test



Scenario: AP-001



Runtime Authority determination:



ALLOW



Represented financial consequence:



EXECUTION PERMITTED



Execution Gateway result:



None



## Result



FAIL



Assertion:



Execution was reported as PERMITTED without consuming the Execution

Gateway determination.



## Finding



Within the v0.9 demonstration surface, AP-001 can reach the represented

EXECUTION PERMITTED state without consuming an Execution Gateway

determination.



The Execution Gateway itself is not shown to be defective.



Rather, the test demonstrates that correct gateway logic does not by

itself establish universal non-bypassability. The architecture must also

ensure that every consequence-producing path is structurally downstream

of the gateway.



## Scope



This test does not demonstrate that an unauthorised real-world bank

transfer occurred.



The tested consequence is the harness representation

"EXECUTION PERMITTED".



The result therefore establishes a failure of the non-bypassability

invariant within the exercised v0.9 demonstration surface.



## Regression



Original non-database suite after introduction of AT-004.3:



55 passed



The new AT-004.3 challenge fails independently of the existing baseline.



## Remediation Status



Not remediated.



Failure intentionally preserved before architectural strengthening.



