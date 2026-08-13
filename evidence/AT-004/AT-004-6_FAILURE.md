# AT-004.6 - Runtime Authority Context Freshness



Date: 13 August 2026

Status: FAIL - preserved prior to remediation



## Objective



Determine whether a still-valid and integrity-protected ALLOW receipt

remains sufficient for execution where relevant runtime authority

context changes after the original determination but before consequence

formation.



## Architectural Invariant



Temporal validity of an Authority Receipt should not, by itself, imply

continued admissibility where material authority context can change

during the receipt validity window.



Receipt freshness and authority-state freshness are separate properties.



## Starting Architecture



Following AT-004.3, AT-004.4 and AT-004.5, the exercised execution path

provides:



\- mandatory Execution Gateway consumption

\- action binding

\- receipt expiry

\- keyed receipt-integrity verification

\- integrity protection of evidential receipt content



The Execution Gateway verifies:



\- receipt integrity

\- ALLOW status

\- valid\_until

\- action binding



Counterparty status and risk state are evaluated when Runtime Authority

creates the Authority Receipt.



Repository inspection identified no corresponding revalidation of those

mutable conditions at the Execution Gateway.



## Adversarial Assurance Test



Test:



test\_at004\_6\_still\_valid\_receipt\_does\_not\_revalidate\_changed\_context



AP-001 was evaluated under an admissible context and produced:



ALLOW



Before the represented execution attempt, the runtime context was then

changed so that:



counterparty\_status = BLOCKED



and:



risk\_state = ELEVATED



The original Authority Receipt remained within its valid\_until window.



The unchanged, integrity-valid Authority Receipt was then presented to

the Execution Gateway for the originally bound execution action.



## Initial Result



FAIL



The Execution Gateway returned:



PERMITTED



The test expected:



BLOCKED



Assertion:



Gateway permitted execution using a still-valid ALLOW receipt without

revalidating changed authority context



Pytest result:



1 failed



## Finding



Within the exercised implementation, temporal validity of an authentic

ALLOW receipt is currently treated as sufficient for continued

execution eligibility where the action binding remains unchanged.



The Execution Gateway does not currently demonstrate revalidation of

the changed counterparty and risk-state conditions exercised by this

test.



Therefore an Authority Receipt can remain:



\- authentic

\- integrity-valid

\- action-bound

\- temporally valid



while the runtime context upon which the original authority

determination depended has changed.



## Architectural Significance



This demonstrates a distinction between:



1\. receipt validity; and

2\. continued runtime admissibility.



A receipt validity window answers:



"Has this authority determination expired?"



It does not necessarily answer:



"Do the conditions that made this execution admissible still hold?"



For mutable conditions capable of changing before consequence

formation, a time-valid receipt alone does not establish current

authority-state freshness.



## Scope



This test exercises two mutable contextual conditions:



\- counterparty\_status

\- risk\_state



It does not establish that every runtime condition must always be

revalidated at the Execution Gateway.



It does not demonstrate:



\- cryptographic failure

\- receipt alteration

\- action substitution

\- execution-gateway bypass

\- production-system exploitation

\- every possible context-change condition



The finding is narrower:



the current harness does not revalidate the tested mutable authority

context before relying upon a still-valid ALLOW receipt.



## Remediation Status



Not remediated.



Failure intentionally preserved before architectural strengthening.





