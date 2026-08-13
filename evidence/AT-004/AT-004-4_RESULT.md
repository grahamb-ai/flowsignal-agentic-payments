# AT-004.4 - Authority Receipt Integrity



Date: 13 August 2026

Status: PASS AFTER REMEDIATION



## Objective



Determine whether an Authority Receipt exposes a receipt-level integrity

mechanism that the Execution Gateway verifies before relying upon the

receipt for consequential execution.



## Architectural Invariant



A consequential execution control should not rely solely upon the

contents of an Authority Receipt without an independently verifiable

means of establishing that the protected receipt contents remain

consistent with the determination produced by Runtime Authority.



## Initial Architecture



AuthorityReceipt contained:



\- id

\- scenario\_id

\- decision

\- reason\_code

\- sealed\_at

\- valid\_until

\- action\_binding\_hash

\- request\_snapshot

\- checks

\- evidence\_references



The existing action\_binding\_hash bound the proposed execution action to

the authority determination.



However, the receipt itself exposed no receipt-level keyed integrity

proof that the Execution Gateway verified before trusting the receipt.



## Initial Test



Test:



test\_at004\_4\_authority\_receipt\_exposes\_verifiable\_integrity



Initial result:



FAIL



Assertion:



AuthorityReceipt exposes no receipt-level integrity proof that an

Execution Gateway can independently verify.



This failure was preserved in:



AT-004-4\_FAILURE.md



## Finding



The original implementation demonstrated action binding but did not

demonstrate receipt-level keyed integrity verification at the

Execution Gateway.



Action binding and receipt integrity are separate properties.



A valid action\_binding\_hash does not, by itself, establish the

integrity of the Authority Receipt as a whole.



## Remediation



A harness-level HMAC-SHA256 receipt-integrity mechanism was introduced.



Runtime Authority now generates receipt\_hmac from protected receipt

fields including:



\- receipt id

\- scenario id

\- decision

\- reason code

\- sealed time

\- validity time

\- action binding hash



The HMAC key is not carried inside AuthorityReceipt.



The Execution Gateway recomputes and verifies the receipt HMAC before

it considers:



\- ALLOW status

\- receipt expiry

\- action binding



If receipt integrity verification fails, the gateway returns:



BLOCKED



Reason:



AUTHORITY\_RECEIPT\_INTEGRITY\_INVALID



## Behavioural Verification



The original structural test was replaced by behavioural tests.



Test 1:



test\_at004\_4\_gateway\_rejects\_receipt\_with\_invalid\_integrity\_proof



Result:



PASS



A receipt carrying an invalid integrity proof was rejected by the

Execution Gateway with:



AUTHORITY\_RECEIPT\_INTEGRITY\_INVALID



Test 2:



test\_at004\_4\_valid\_receipt\_still\_reaches\_gateway



Result:



PASS



A legitimately generated AP-001 Authority Receipt continued through the

Execution Gateway and produced:



ALLOW

PERMITTED

BOUND\_ALLOW\_VALID

EXECUTION PERMITTED



## Regression Result



Full non-database regression suite:



58 passed in 0.49s



No regression was observed across the exercised non-database harness.



## Final Finding



Within the exercised implementation, the Execution Gateway now verifies

a keyed integrity proof on protected Authority Receipt fields before it

relies upon the Runtime Authority determination.



The initial absence of receipt-level integrity verification was

falsifiable, was demonstrated by test, was preserved, and was then

remediated.



The same class of assurance requirement was retested after remediation

and passed.



## Scope



This result demonstrates keyed receipt-integrity verification within the

current proof-of-concept harness.



It does not demonstrate:



\- production key management

\- hardware-backed key protection

\- public-key signature infrastructure

\- organisational separation of signing and verification keys

\- external third-party verification

\- integrity coverage of every field contained within request\_snapshot,

&#x20; checks, or evidence\_references

\- security of every possible real-world execution path



The HMAC key used in the harness is deliberately a proof-of-concept

implementation detail and must not be represented as production-grade

key management.



## Relationship to AT-004 Series



AT-004.1 demonstrated authority-source separation.



AT-004.2 demonstrated that authority-source separation alone is

insufficient where the governed environment controls which evaluator

and authority state are consumed.



AT-004.3 demonstrated the requirement for execution non-bypassability

across the exercised consequence path.



AT-004.4 demonstrates that the Execution Gateway must also establish

receipt integrity before relying upon the Runtime Authority

determination.



Together, the exercised chain is now:



Authoritative State

&#x20;   ->

Runtime Authority Determination

&#x20;   ->

Integrity-Protected Bound Authority Receipt

&#x20;   ->

Mandatory Execution Gateway

&#x20;   ->

Consequence



