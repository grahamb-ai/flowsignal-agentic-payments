# AT-004.5 - Authority Receipt Evidence Integrity



Date: 13 August 2026

Status: FAIL - preserved prior to remediation



## Objective



Determine whether the Authority Receipt integrity mechanism protects

the evidential content carried by the receipt, not only the

enforcement-critical fields used by the Execution Gateway.



## Architectural Invariant



If the Authority Receipt is intended to serve as an evidential record,

material evidential content carried by that receipt should fall within

the receipt integrity boundary.



A receipt should not continue to verify successfully where its

evidential content has changed after sealing.



## Starting Architecture



Following AT-004.4, the Authority Receipt included keyed HMAC-SHA256

integrity protection.



The HMAC covered the enforcement-critical subset of the receipt,

including:



\- receipt identity

\- scenario identity

\- decision

\- reason code

\- sealed time

\- valid\_until

\- action binding



However, the receipt also carried richer evidential content:



\- request\_snapshot

\- checks

\- evidence\_references



Repository inspection showed that these evidential fields were not

included in the initial HMAC payload.



## Adversarial Assurance Test



Test:



test\_at004\_5\_receipt\_evidence\_is\_inside\_integrity\_boundary



Sequence:



1\. AP-001 was evaluated normally.

2\. An ALLOW Authority Receipt was created.

3\. Receipt HMAC verification succeeded.

4\. The carried request\_snapshot was changed after sealing.

5\. Receipt HMAC verification was performed again.



The test expected integrity verification to fail after the evidential

content had changed.



## Initial Result



FAIL



The modified receipt continued to pass HMAC verification.



The test therefore established that the initial AT-004.4 integrity

boundary did not cover all evidential content carried by the Authority

Receipt.



## Finding



Within the exercised implementation, the initial keyed integrity

mechanism protected an enforcement-critical subset of the Authority

Receipt but did not protect the complete evidential record.



This exposed a distinction between:



1\. execution-control integrity; and

2\. evidential-record integrity.



The finding did not demonstrate an Execution Gateway bypass.



The gateway did not consume the changed evidential fields when deciding

whether to permit the bound execution.



The weakness was narrower:



the receipt could continue to verify as integrity-valid even though

material evidential content carried by the receipt had changed.



## Architectural Significance



If an Authority Receipt is expected to support later reconstruction,

audit or defence of the Runtime Authority determination, evidential

content that forms part of that record should not sit outside the

integrity boundary.



Otherwise a receipt can remain valid for enforcement while no longer

being a trustworthy representation of the evidence originally sealed

with the determination.



## Scope



This test exercised a change to request\_snapshot.



It did not establish:



\- execution-gateway bypass

\- action substitution

\- cryptographic key compromise

\- production-system exploitation

\- external immutable storage

\- production key management

\- every possible evidential field

\- every possible receipt format



The finding is limited to the exercised proof-of-concept integrity

mechanism.



## Remediation Status



Not remediated at the time of this preserved failure.



The subsequent remediation expanded the HMAC integrity boundary to

include:



\- request\_snapshot

\- checks

\- evidence\_references



The remediated result is recorded separately in:



AT-004-5\_RESULT.md



## Evidence Note



This failure note was reconstructed on 13 August 2026 from the recorded

AT-004.5 test result after the local failure markdown file was found to

be empty.



The underlying failure result and remediation sequence were preserved

in the engineering test record.

