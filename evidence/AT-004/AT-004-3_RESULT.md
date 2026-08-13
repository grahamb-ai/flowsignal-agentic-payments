# AT-004.3 - Determination Non-Bypassability



Date: 13 August 2026

Final Status: PASS AFTER REMEDIATION

Historical Failure: PRESERVED



## Objective



Determine whether every path capable of reaching the represented

consequential execution state must consume a valid Execution Gateway

determination.



The architectural invariant tested was:



No governed consequence may be reported as EXECUTION PERMITTED unless

that consequence has consumed a PERMITTED Execution Gateway determination.



## Baseline



Existing non-database regression suite:



55 passed



The existing Execution Gateway already validated:



\- Runtime Authority decision

\- determination validity / expiry

\- action binding



Existing AP-006 tests demonstrated that the gateway:



\- blocks an altered execution attempt; and

\- permits an exact action bound to a valid ALLOW.



The initial question was therefore not whether the Execution Gateway

worked correctly when invoked.



The question was whether every represented consequence-producing path

was required to invoke it.



## Initial Architecture



Inspection of the v0.9 demonstration surface identified two execution

patterns.



AP-006:



Runtime Authority

â†’ Execution Gateway

â†’ represented consequence



AP-001 through AP-005:



Runtime Authority

â†’ represented consequence



For AP-001 through AP-005, the demonstration derived the represented

financial consequence directly from the Runtime Authority decision.



An ALLOW determination could therefore produce:



EXECUTION PERMITTED



without a corresponding Execution Gateway result.



## Adversarial Test



A new test was introduced:



test\_at004\_3\_execution\_permitted\_requires\_gateway\_validation



The test used AP-001 and asserted:



1\. The scenario reached the represented state EXECUTION PERMITTED.

2\. An Execution Gateway result existed.

3\. The Execution Gateway result was PERMITTED.



No existing production logic was changed before the first execution

of this test.



## Initial Result



FAIL



Observed state:



Runtime Authority decision:

ALLOW



Represented financial consequence:

EXECUTION PERMITTED



Execution Gateway:

None



Assertion failure:



Execution was reported as PERMITTED without consuming the Execution

Gateway determination.



The original 55-test non-database regression suite remained:



55 passed



This established that AT-004.3 exposed an architectural invariant not

covered by the existing baseline tests.



The failure was preserved before remediation in:



AT-004-3\_FAILURE.md



## Finding



Within the exercised v0.9 demonstration surface, correct Execution

Gateway logic was not sufficient to establish universal

non-bypassability.



A represented consequence path could reach EXECUTION PERMITTED without

consuming an Execution Gateway determination.



The weakness was therefore not the validation logic inside the gateway.



The weakness was that use of the gateway was not structurally required

across all exercised scenario paths.



## Remediation



The normal AP-001 through AP-005 scenario path was strengthened.



Each evaluated request now constructs an ExecutionAttempt and submits

the Authority Receipt and ExecutionAttempt to:



validate\_execution()



The represented consequence is now downstream of the Execution Gateway.



EXECUTION PERMITTED is returned only when the gateway returns:



PERMITTED



ESCALATE continues to produce:



EXECUTION WITHHELD



Other non-permitted outcomes produce:



NO EXECUTION



AP-006 retains its existing altered-action gateway challenge.



## Retest



The original AT-004.3 adversarial test was rerun without weakening or

changing the invariant.



Result:



1 passed



The previously failing AP-001 path now produced a valid Execution

Gateway result before reaching EXECUTION PERMITTED.



## Final Regression



The complete non-database test suite was rerun after remediation.



Result:



56 passed



This consists of the original 55 passing tests plus the new AT-004.3

non-bypassability test.



No regression was observed across the exercised non-database test

surface.



## Final Result



PASS AFTER REMEDIATION



AT-004.3 demonstrated an initial failure of the determination

non-bypassability invariant within the exercised v0.9 demonstration

surface.



The architecture was strengthened so that represented consequential

execution is downstream of Execution Gateway validation.



The same adversarial invariant that originally failed subsequently

passed.



## Scope and Limitations



This test does not demonstrate that an unauthorised real-world bank

transfer occurred.



The tested consequence is the harness representation:



EXECUTION PERMITTED



The result therefore demonstrates non-bypassability across the

execution surface exercised by this harness and this test.



It does not establish that every possible external, operational,

integration, administrative, database, or real-world payment path is

non-bypassable.



Any broader claim would require those additional consequence-producing

surfaces to be identified and independently challenged.



## Relationship to AT-004 Series



AT-004.1 - Authority Source Separation



Demonstrated that separating authoritative mandate state from locally

presented authority can prevent a different locally presented mandate

value from changing the Runtime Authority determination.



Result: PASS



AT-004.2 - Evaluator Independence



Demonstrated that authoritative state separation alone is insufficient

when a locally controlled evaluator can choose to ignore that state and

consume locally presented authority instead.



Result: PASS



AT-004.3 - Determination Non-Bypassability



Demonstrated that correct Runtime Authority and Execution Gateway logic

alone are insufficient if a represented consequence-producing path is

not structurally required to consume the gateway determination.



Initial Result: FAIL



Final Result: PASS AFTER REMEDIATION



Together, the three tests distinguish:



\- independence of authoritative state;

\- independence/control of authority evaluation; and

\- non-bypassability of the resulting determination at consequential

&#x20; execution.



These are related but distinct architectural properties.



