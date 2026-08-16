\# FS-CT-001 - Consequence-Boundary Category Test



Date: 16 August 2026



Final Status: PARTIALLY DEMONSTRATED



Supporting Tests:



\- FS-CT-001 - Changed Authority After ALLOW

\- FS-CT-002 - Governed Route Closure

\- FS-CT-003 - Historical Determination Replay





\## Purpose



Apply an external public consequence-boundary challenge standard to the

FlowSignal Agentic Payments Harness and determine which properties can be

demonstrated by the existing public implementation.



The exercise was conducted as an adversarial engineering challenge rather

than as a conformance exercise.



Production/runtime logic was not modified before the initial challenges in

order to manufacture passing results.



Where a challenge exposed a limitation, that limitation was preserved before

remediation.





\## Claim Under Test



The principal bounded question was:



Can a previously valid authority determination continue to produce the

represented consequence after authoritative runtime state changes?



Supporting questions examined:



\- whether stale authority remains usable after changed conditions;

\- whether the governed consequence route remains closed to stale authority;

\- whether historical determination evidence remains preserved;

\- whether the historical determination can be independently reconstructed;

\- whether prohibited consequence non-formation can be demonstrated beyond

&#x20; the represented harness execution surface.





\## Baseline



Before introduction of the FS-CT Category Test series, the existing FlowSignal

test suite completed successfully.



Observed baseline:



59 passed

0 failed

0 errors

1 warning



A test-environment correction was required so the documented in-memory SQLite

fixture did not invoke the production PostgreSQL startup path.



That correction did not modify:



\- Runtime Authority logic;

\- Execution Gateway logic;

\- receipt logic;

\- authority evaluation;

\- decision logic; or

\- represented consequence handling.





\## Historical Non-Bypassability Evidence



The FS-CT exercise should be read alongside AT-004.3 - Determination

Non-Bypassability.



AT-004.3 previously exposed a weakness in the v0.9 demonstration surface.



The Runtime Authority and Execution Gateway were individually functioning,

but AP-001 through AP-005 could report:



EXECUTION PERMITTED



without consuming an Execution Gateway determination.



AT-004.3 therefore initially failed.



That failure was preserved before remediation.



The demonstration architecture was subsequently strengthened so that the

represented consequential execution state became downstream of Execution

Gateway validation.



The original AT-004.3 adversarial invariant was rerun and passed.



The AT-004.3 evidence explicitly limits this result to the represented

execution surface exercised by the harness.





\## Category Test Sequence



The FS-CT challenge exercised the following conceptual sequence.



T0:



\- candidate payment movement presented;

\- authority valid;

\- Runtime Authority returns ALLOW;

\- Authority Receipt issued;

\- action bound to receipt;

\- Execution Gateway can return PERMITTED.



T1:



\- authoritative runtime state changes;

\- the earlier Authority Receipt is presented again;

\- the previously authorised movement is attempted;

\- stale authority must not cross the changed-state boundary;

\- any continued execution must earn a determination against current state;

\- historical evidence must remain preserved.





\## FS-CT-001 - Changed Authority After ALLOW



Test:



tests/test\_fs\_ct\_001\_category\_test.py



Result:



PASS



A valid AP-001 movement was evaluated at T0.



Runtime Authority returned:



ALLOW



The resulting Authority Receipt was preserved.



The authoritative state version was then advanced.



The same movement was attempted using the earlier Authority Receipt.



Observed Execution Gateway result:



BLOCKED



Reason:



AUTHORITY\_STATE\_STALE\_REEVALUATION\_REQUIRED



The historical receipt retained its original:



\- receipt ID;

\- action-binding hash; and

\- authority-state version.





\### FS-CT-001 Finding



A prior ALLOW cannot cross an authority-state boundary through the governed

execution path using the stale Authority Receipt.



The historical receipt remains preserved rather than being rewritten to

represent the changed condition.





\## FS-CT-002 - Governed Route Closure



Test:



tests/test\_fs\_ct\_002\_route\_closure.py



Result:



PASS



The challenge first established that the T0 Authority Receipt could genuinely

produce:



PERMITTED



through the Execution Gateway.



The authoritative state version was then changed.



Direct reuse of the earlier receipt produced:



BLOCKED



with reason:



AUTHORITY\_STATE\_STALE\_REEVALUATION\_REQUIRED



The normal represented consequence-producing route was then exercised after

the state change.



The stale T0 receipt could not be carried forward through that governed route.



Where the same movement remained admissible following fresh evaluation,

continued execution required a new determination and Authority Receipt under

the current authority-state version.





\### FS-CT-002 Finding



Within the execution surface represented by the public harness, stale

authority cannot be reused through the tested governed route to produce:



EXECUTION PERMITTED



A changed authority-state boundary therefore requires a new runtime

determination before represented consequential execution can continue.





\## FS-CT-003 - Historical Determination Replay



Initial Status:



FAIL



Final Status:



PASS AFTER REMEDIATION





\### Initial Assessment



Initial inspection identified preserved historical evidence within the

Authority Receipt, including:



\- request snapshot;

\- decision;

\- reason code;

\- action-binding hash;

\- authority-state version;

\- checks;

\- evidence references; and

\- receipt integrity proof.



However, no dedicated historical replay mechanism existed.



Replay was therefore initially recorded as:



NOT DEMONSTRABLE FROM THE CURRENT PUBLIC IMPLEMENTATION





\### Adversarial Challenge



Test:



tests/test\_fs\_ct\_003\_replay.py



The challenge required the historical determination to remain independently

reconstructable after current authority state changed.



Fresh Runtime Authority evaluation was explicitly excluded as a substitute

for replay.





\### Initial Result



FAIL



Observed exception:



ModuleNotFoundError: No module named 'app.engines.replay'



The failure established that the existing implementation could perform fresh

evaluation but could not independently reconstruct the preserved historical

determination through a dedicated replay mechanism.



The failure was preserved before remediation in:



FS-CT-003\_FAILURE.md





\### Remediation



A dedicated historical Authority Receipt replay mechanism was introduced:



app/engines/replay.py



The mechanism:



\- consumes the preserved Authority Receipt;

\- verifies receipt integrity;

\- reconstructs the recorded historical determination;

\- preserves the historical authority-state version;

\- preserves the historical action-binding hash;

\- does not consult current authority state;

\- does not perform fresh Runtime Authority evaluation; and

\- does not rewrite the historical Authority Receipt.





\### Retest



The original FS-CT-003 adversarial test was rerun without weakening the

invariant.



Observed result:



PASS





\### FS-CT-003 Finding



Within the bounded public harness, a sealed historical Authority Receipt can

now be independently integrity-verified and its recorded historical

determination reconstructed after current authority state has changed.



This is bounded historical Authority Receipt replay/reconstruction.



It is not claimed as full deterministic re-execution of the complete

historical Runtime Authority evaluation from a frozen policy, rule, evidence

and environmental estate.





\## External Consequence Non-Formation



Status:



NOT DEMONSTRABLE FROM THE CURRENT PUBLIC HARNESS



The public Agentic Payments Harness represents financial consequence using

states including:



EXECUTION PERMITTED



EXECUTION WITHHELD



NO EXECUTION



The inspected public implementation does not contain an independently

consequence-producing banking or payment executor.



The Category Test therefore cannot establish from this harness that every

possible external banking, integration, administrative, operational or

payment path is physically unable to produce a prohibited consequence.



No such broader claim is made.





\## Final Regression



Following remediation of FS-CT-003, the complete discovered test suite was

executed.



Command:



python -m pytest -q



Observed result:



72 passed

0 failed

0 errors

1 warning



The warning is an existing FastAPI/Starlette TestClient deprecation warning

and is unrelated to Runtime Authority, Execution Gateway, receipt integrity,

authority-state handling or replay.



No regression was observed across the complete discovered test surface.





\## Final Findings



The FS-CT Category Test demonstrates within the exercised public harness:



\- invalidation of a prior ALLOW following authority-state change;

\- rejection of stale Authority Receipts before represented consequence;

\- preservation of historical receipt state;

\- bounded governed-route closure;

\- requirement for fresh determination following changed authority state;

\- integrity verification of preserved historical Authority Receipts; and

\- bounded historical determination replay/reconstruction.



The exercise does not demonstrate:



\- physical non-formation across external real-world payment rails; or

\- full deterministic re-execution from a complete frozen historical policy,

&#x20; rule, evidence and environmental estate.





\## Result Summary



FS-CT-001

Changed Authority After ALLOW

PASS



FS-CT-002

Governed Route Closure

PASS



FS-CT-003

Historical Determination Replay

INITIAL FAIL

PASS AFTER REMEDIATION



External Consequence Non-Formation

NOT DEMONSTRABLE FROM CURRENT PUBLIC HARNESS



Complete Regression

72 PASSED





\## Final Status



PARTIALLY DEMONSTRATED



The Category Test produced both positive and negative findings.



A genuine replay limitation was identified rather than inferred away.



The failure was preserved.



A dedicated replay capability was implemented.



The unchanged adversarial challenge subsequently passed.



Other tested properties passed without requiring their invariants to be

weakened.



External real-world consequence non-formation remains outside the demonstrated

scope of the public harness.





\## Claim Boundary



This result applies only to the public FlowSignal Agentic Payments Harness and

the execution surfaces exercised by the tests described above.



The result does not establish universal consequence custody,

non-bypassability or non-formation across systems and execution paths not

represented by the harness.



The evidence supports only the bounded claims actually exercised.





\## Engineering Conclusion



The Category Test was useful because it did not simply confirm the existing

architecture.



It exposed a capability that the implementation did not possess.



That absence was recorded as a failure before remediation.



The architecture was then strengthened and the original challenge rerun.



The resulting evidence therefore preserves both the limitation and the

subsequent engineering response.



The final proof surface is not represented by the number of passing tests

alone.



It is represented by the complete lineage:



claim -> challenge -> observed result -> preserved failure -> remediation ->

unchanged retest -> regression -> bounded conclusion.

