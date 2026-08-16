\# FS-CT-003 - Historical Determination Replay



Date: 16 August 2026



Status: FAIL - preserved prior to remediation



\## Objective



Determine whether a historical Runtime Authority determination can be

independently replayed from preserved evidence without consulting or

rewriting current authority state.



\## Invariant



A historical authority determination must remain reproducible from its

preserved evidence after authoritative runtime state changes.



A fresh re-evaluation is not replay.



Replay must preserve the historical result and must not rewrite prior truth.



\## Baseline



The existing public FlowSignal Agentic Payments Harness provides:



\- Authority Receipts;

\- request snapshots;

\- action-binding hashes;

\- authority-state versions;

\- receipt integrity evidence;

\- deterministic Runtime Authority evaluation.



No dedicated replay mechanism had previously been identified.



\## Test



Test:



tests/test\_fs\_ct\_003\_replay.py



Sequence:



1\. AP-001 was evaluated under valid authority state.

2\. Runtime Authority returned ALLOW.

3\. The Authority Receipt and its historical evidence were preserved.

4\. The authoritative runtime state version was advanced.

5\. The test attempted to invoke an independent replay mechanism using the

&#x20;  preserved Authority Receipt.



\## Result



FAIL



Observed exception:



ModuleNotFoundError: No module named 'app.engines.replay'



Assertion:



No independent replay mechanism exists. The current harness can re-evaluate

a request, but cannot reconstruct the historical determination from preserved

evidence.



\## Finding



The current public implementation can perform fresh deterministic evaluation,

but does not expose an independent historical replay mechanism.



Re-running evaluate\_financial() would evaluate the request against execution

logic again and would therefore constitute re-evaluation rather than replay

of the preserved historical determination.



The existence of request\_snapshot, receipt integrity and authority-state

versioning is not by itself sufficient to establish replay.



\## Scope



This failure applies to the replay capability of the public Agentic Payments

Harness.



It does not indicate a failure of:



\- Runtime Authority evaluation;

\- execution gateway validation;

\- action binding;

\- receipt integrity;

\- authority-state freshness;

\- changed-condition invalidation.



Those properties are tested separately.



\## Relationship to FS-CT Category Test



FS-CT-001 demonstrated that a prior ALLOW cannot cross an authority-state

boundary through the governed execution path.



FS-CT-002 demonstrated bounded route closure against reuse of stale authority.



FS-CT-003 demonstrates that the historical determination cannot yet be

independently replayed from preserved evidence.



Replay therefore remains unproven in the current implementation.



\## Remediation Status



Not remediated.



Failure intentionally preserved before implementation of any replay

capability.

