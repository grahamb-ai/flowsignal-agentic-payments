# AT-004.5 - Authority Receipt Evidence Integrity



Date: 13 August 2026

Status: PASS AFTER REMEDIATION



## Objective



Determine whether the receipt-level integrity mechanism protects the

evidential content carried by the Authority Receipt, in addition to the

fields directly consumed by the Execution Gateway.



## Architectural Invariant



Where an Authority Receipt is relied upon as evidence of why a runtime

authority determination was made, the evidential content represented by

that receipt should remain inside a verifiable integrity boundary.



Execution integrity and evidential integrity are related but distinct

properties.



## Initial Architecture



Following AT-004.4, AuthorityReceipt contained a keyed HMAC covering:



\- receipt id

\- scenario id

\- decision

\- reason code

\- sealed time

\- validity time

\- action binding hash



The Execution Gateway verified that HMAC before relying upon the receipt.



However, AuthorityReceipt also carried:



\- request\_snapshot

\- checks

\- evidence\_references



These evidential fields were outside the HMAC calculation.



## Initial Adversarial Assurance Test



Test:



test\_at004\_5\_receipt\_evidence\_is\_inside\_integrity\_boundary



A legitimately generated AP-001 Authority Receipt first passed integrity

verification.



A changed copy of the receipt was then created with a different

screening\_status inside request\_snapshot.



The receipt integrity verifier was run against that changed receipt.



## Initial Result



FAIL



Assertion:



Authority Receipt evidential content changed while receipt integrity

verification still succeeded



The failure was preserved in:



AT-004-5\_FAILURE.md



## Finding



The initial AT-004.4 implementation protected the enforcement-critical

subset of the receipt but did not protect all evidential content carried

by the receipt.



This demonstrated a distinction between:



1\. execution-control integrity; and

2\. evidential-record integrity.



The Authority Receipt could continue to pass integrity verification even

where request\_snapshot no longer represented the same evidential content

that existed when the receipt was created.



## Remediation



The receipt-integrity mechanism was strengthened to use one deterministic

canonical representation of the complete protected receipt content.



The HMAC now includes:



\- receipt id

\- scenario id

\- decision

\- reason code

\- sealed time

\- validity time

\- action binding hash

\- request\_snapshot

\- checks

\- evidence\_references



Dataclass values, dictionaries, lists and datetime values are normalised

into deterministic forms before HMAC calculation.



The same canonicalisation logic is used for both receipt generation and

receipt verification.



## Retest



The original AT-004.5 test was rerun unchanged.



Result:



PASS



Changing screening\_status inside request\_snapshot now causes receipt

integrity verification to fail.



This closes the exact failure originally demonstrated by AT-004.5.



## Regression Result



Full non-database regression suite:



59 passed in 0.45s



No regression was observed across the exercised non-database harness.



## Final Finding



Within the exercised implementation, the receipt-level keyed integrity

mechanism now protects both:



1\. the enforcement-critical authority determination fields; and

2\. the evidential content carried by the Authority Receipt.



A change to the tested evidential snapshot after receipt generation is

therefore detectable by the receipt-integrity verifier.



## Significance



The exercised chain now supports both sides of the architectural claim:



Execute with Authority



and



Defend with Evidence



The Runtime Authority determines whether execution is admissible.



The resulting Authority Receipt binds the execution action, carries the

evidential basis for the determination, and exposes a keyed integrity

proof covering that protected content.



The Execution Gateway verifies receipt integrity before relying upon the

authority determination.



## Scope



This result is limited to the current proof-of-concept harness.



It does not demonstrate:



\- production-grade key management

\- hardware-backed key protection

\- public-key signature infrastructure

\- external third-party verification

\- organisational separation of signing and verification infrastructure

\- immutable external evidence storage

\- protection against every possible runtime attack

\- coverage of every real-world consequence path



The HMAC key remains a harness-level proof-of-concept mechanism and must

not be represented as production-grade key management.



## Relationship to AT-004 Series



AT-004.1 demonstrated authority-source separation.



AT-004.2 demonstrated that authority-source separation alone is

insufficient where the governed environment controls which evaluator and

authority state are consumed.



AT-004.3 demonstrated execution non-bypassability across the exercised

consequence path.



AT-004.4 demonstrated receipt-integrity verification at the Execution

Gateway.



AT-004.5 demonstrated evidential integrity of the receipt content itself.



The exercised chain is now:



Authoritative State

&#x20;   ->

Runtime Authority Determination

&#x20;   ->

Bound Authority Receipt

&#x20;   ->

Integrity-Protected Decision and Evidence

&#x20;   ->

Mandatory Execution Gateway

&#x20;   ->

Consequence



