# AT-004.6 - Runtime Authority Context Freshness



Date: 13 August 2026

Status: PASS AFTER REMEDIATION



## Objective



Determine whether a still-valid and integrity-protected ALLOW receipt

remains sufficient for execution where relevant authoritative state

changes after the original Runtime Authority determination but before

consequence formation.



## Architectural Invariant



Temporal validity of an Authority Receipt must not, by itself, imply

continued execution eligibility where the authoritative state against

which the determination was made has subsequently changed.



Receipt freshness and authority-state freshness are separate

properties.



## Initial Architecture



Following AT-004.3, AT-004.4 and AT-004.5, the exercised execution path

provided:



\- mandatory Execution Gateway consumption

\- action binding

\- receipt expiry

\- keyed receipt-integrity verification

\- integrity protection of evidential receipt content



The Execution Gateway verified:



\- receipt integrity

\- ALLOW status

\- valid\_until

\- action binding



However, it did not establish whether the authoritative state used by

Runtime Authority remained current at the point of represented

execution.



## Initial Adversarial Result



FAIL



An ALLOW Authority Receipt remained:



\- authentic

\- integrity-valid

\- action-bound

\- temporally valid



while runtime authority context was changed before the execution

attempt.



The Execution Gateway still returned:



PERMITTED



The preserved initial failure is recorded in:



AT-004-6\_FAILURE.md



## Remediation



The authoritative state source was extended with a monotonically

changing authority-state version.



Runtime Authority now:



1\. reads the current authoritative state version at determination time;

2\. binds that version into the Authority Receipt; and

3\. includes the version inside the receipt HMAC integrity boundary.



The Execution Gateway now compares:



receipt.authority\_state\_version



with:



get\_authority\_state\_version()



immediately before accepting the Authority Receipt for execution.



If the versions differ, the Gateway returns:



BLOCKED



with reason:



AUTHORITY\_STATE\_STALE\_REEVALUATION\_REQUIRED



The Execution Gateway does not independently reinterpret the changed

policy or contextual state.



Instead, it refuses reliance upon the stale Authority Receipt and

requires a new Runtime Authority determination.



## Remediated Assurance Test



Test:



test\_at004\_6\_still\_valid\_receipt\_is\_blocked\_after\_authority\_state\_changes



Sequence:



1\. AP-001 is evaluated by Runtime Authority.

2\. An ALLOW Authority Receipt is produced.

3\. The authoritative state version is advanced.

4\. The original, otherwise-valid Authority Receipt is presented to the

&#x20;  Execution Gateway.

5\. The Gateway compares the receipt-bound state version with the current

&#x20;  authoritative state version.



Expected:



BLOCKED



Reason:



AUTHORITY\_STATE\_STALE\_REEVALUATION\_REQUIRED



Observed:



PASS



Pytest result:



1 passed



## Regression Result



Full non-database regression suite:



60 passed



No regressions were identified across the exercised AT-004 assurance

surface.



## Finding



Within the exercised implementation, an Authority Receipt can no longer

be relied upon solely because it remains cryptographically valid,

action-bound and within its valid\_until period.



The receipt is also bound to the generation of authoritative state

against which Runtime Authority made its determination.



A subsequent authoritative-state change invalidates reliance upon the

earlier determination at the Execution Gateway and requires Runtime

Authority re-evaluation.



This preserves the separation between:



Runtime Authority - determines admissibility



and:



Execution Gateway - enforces a current Runtime Authority determination



## Architectural Significance



AT-004.6 demonstrates that:



receipt freshness != authority-state freshness



A valid\_until window answers:



"Has this determination expired?"



The authority-state version answers:



"Was this determination made against the authoritative state that is

still current?"



Where the authoritative state generation has changed, the previous

determination is treated as stale even if its time-based validity window

has not expired.



## Scope



This is a proof-of-concept state-generation mechanism.



It does not demonstrate:



\- production distributed state synchronisation

\- consensus across multiple authority stores

\- durable state-version persistence

\- hardware-backed state integrity

\- production key management

\- atomic cross-system commit

\- every possible mutable context condition

\- every possible consequence-producing execution path



The test establishes the narrower property that, across the exercised

harness surface, a change in authoritative state generation causes an

earlier Authority Receipt to be rejected at the Execution Gateway and

sent back for Runtime Authority re-evaluation.



## Status



PASS AFTER REMEDIATION



Initial failure preserved.



Remediation verified.



Full non-database regression suite:



60 passed



