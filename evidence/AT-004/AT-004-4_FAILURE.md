# AT-004.4 - Authority Receipt Integrity



Date: 13 August 2026

Status: FAIL - preserved prior to remediation



## Objective



Determine whether an Authority Receipt exposes receipt-level integrity

information that an Execution Gateway can independently verify before

relying upon the receipt.



## Architectural Invariant



A consequential execution control should not rely solely upon the

contents of an Authority Receipt without an independently verifiable

means of establishing the integrity of that receipt.



## Source Inspection



AuthorityReceipt currently contains:



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



Repository inspection identified references to records being "sealed",

but did not identify receipt-level signature, MAC, HMAC, receipt hash,

integrity hash, or equivalent verification mechanism on AuthorityReceipt.



## Adversarial Assurance Test



Test:



test\_at004\_4\_authority\_receipt\_exposes\_verifiable\_integrity



The test inspected the AuthorityReceipt data model for a receipt-level

integrity proof exposed to the Execution Gateway.



Candidate integrity fields tested:



\- signature

\- integrity\_hash

\- receipt\_hash

\- mac

\- hmac



## Initial Result



FAIL



Assertion:



AuthorityReceipt exposes no receipt-level integrity proof that an

Execution Gateway can independently verify.



Pytest result:



1 failed



## Finding



Within the exercised implementation, AuthorityReceipt does not expose

a receipt-level integrity proof of the forms tested.



The existing action\_binding\_hash binds the proposed execution action

to the authority determination, but it does not by itself establish

the integrity or provenance of the Authority Receipt as a whole.



Therefore the current implementation does not demonstrate independent

receipt-integrity verification at the Execution Gateway.



## Scope



This test does not demonstrate successful alteration, fabrication or

substitution of an Authority Receipt.



It establishes a narrower structural finding:



the current AuthorityReceipt interface does not expose the tested

receipt-level integrity mechanism for independent gateway verification.



Further testing would be required before making claims about specific

receipt-alteration or substitution behaviours.



## Remediation Status



Not remediated.



Failure intentionally preserved before architectural strengthening.



