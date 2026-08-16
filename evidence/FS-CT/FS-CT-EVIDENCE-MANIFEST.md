\# FS-CT Evidence Manifest



Date: 16 August 2026



\## Purpose



This manifest records the evidence artifacts and SHA-256 hashes associated

with the FlowSignal Consequence-Boundary Category Test exercise.



The manifest is intended to make the published proof surface identifiable

and independently integrity-checkable.



\## Test Status



Category Test suite:



3 passed

0 failed



Complete discovered regression suite:



72 passed

0 failed

0 errors

1 warning



The warning is an existing FastAPI/Starlette TestClient deprecation warning

and is unrelated to the Runtime Authority control surface.



\## Evidence Artifacts



\### Overall Category Test Result



File:



FS-CT-001\_RESULT.md



SHA-256:



6c80e16c9c11e9337cfc7bad1b808a3413d3fe5ffd5b677acff98178dbf217ac





\### Preserved Replay Failure



File:



FS-CT-003\_FAILURE.md



SHA-256:



bc00aa660a213854337b92c12c795d0534a6526be1123699931ac0cb2bfbd108





\### Replay Remediation Result



File:



FS-CT-003\_RESULT.md



SHA-256:



2956c85dac359fe11383dc69f9ff25007989fc2fa7d51db0407d65fd26ed47c0





\### Changed-Authority Challenge



File:



tests/test\_fs\_ct\_001\_category\_test.py



SHA-256:



558031350eeb35677e3d7fb708f16e164ad27196536a8446d098092517ab1458





\### Governed Route-Closure Challenge



File:



tests/test\_fs\_ct\_002\_route\_closure.py



SHA-256:



160ace104eef2ffccb90350d78bd48766abd26fc695ce33d648c59e64c66c4fe





\### Historical Replay Challenge



File:



tests/test\_fs\_ct\_003\_replay.py



SHA-256:



4c91f6acf7dbfa3a538b37897093070eb9701153c93c4ff68f1106c591bdadee





\### Replay Implementation



File:



app/engines/replay.py



SHA-256:



b9737d85cc87b4b080085bac4564a127e113550573552f4cba6f1cf872f453c1





\## Evidence Lineage



The Category Test evidence records the following engineering sequence:



claim

\-> adversarial challenge

\-> observed result

\-> preserved failure where applicable

\-> remediation

\-> unchanged retest

\-> complete regression

\-> bounded conclusion



FS-CT-003 is particularly significant because the original replay challenge

failed before remediation.



That failure remains preserved in:



FS-CT-003\_FAILURE.md



A dedicated replay capability was subsequently introduced and the original

challenge rerun without weakening its invariant.



The challenge then passed.





\## Demonstrated Scope



Within the execution surface exercised by the public FlowSignal Agentic

Payments Harness, the evidence demonstrates:



\- invalidation of prior ALLOW following authority-state change;

\- rejection of stale Authority Receipts at the Execution Gateway;

\- bounded governed-route closure;

\- requirement for fresh determination following changed authority state;

\- preservation of historical receipt state;

\- integrity verification of historical Authority Receipts; and

\- bounded historical Authority Receipt replay/reconstruction.





\## Explicit Limitations



The evidence does not demonstrate:



\- physical non-formation across external real-world payment rails;

\- universal non-bypassability across execution paths outside the harness; or

\- full deterministic re-execution from a complete frozen historical policy,

&#x20; rule, evidence and environmental estate.



No broader claim is made.





\## Verification



The hashes in this manifest were generated using SHA-256 immediately after

the final Category Test and complete regression runs.



Any subsequent modification to a listed artifact will change its hash and

should result in a new manifest or manifest revision.

