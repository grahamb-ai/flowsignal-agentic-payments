\# FS-CT-003 - Historical Determination Replay



Date: 16 August 2026



Final Status: PASS AFTER REMEDIATION



Historical Failure: PRESERVED





\## Objective



Determine whether a historical Runtime Authority determination can be

independently reconstructed from preserved evidence without consulting or

rewriting current authority state.





\## Invariant



A historical authority determination must remain reproducible from its

preserved evidence after authoritative runtime state changes.



A fresh re-evaluation is not replay.



Replay must preserve historical truth and must not rewrite the original

Authority Receipt.





\## Initial Condition



The existing public FlowSignal Agentic Payments Harness preserved substantial

historical evidence within the Authority Receipt, including:



\- request snapshot;

\- decision;

\- reason code;

\- action-binding hash;

\- authority-state version;

\- checks;

\- evidence references; and

\- receipt integrity proof.



However, inspection identified no dedicated mechanism capable of consuming

that preserved evidence and independently reconstructing the historical

determination.



Fresh deterministic evaluation was available, but fresh evaluation is not

historical replay.





\## Adversarial Test



Test:



tests/test\_fs\_ct\_003\_replay.py



The challenge performed the following sequence:



1\. AP-001 was evaluated under valid authority state.

2\. Runtime Authority returned ALLOW.

3\. The resulting Authority Receipt and historical evidence were preserved.

4\. The authoritative runtime state version was advanced.

5\. The test attempted to invoke an independent replay mechanism using the

&#x20;  preserved historical Authority Receipt.

6\. The replay mechanism was required to reconstruct the historical result

&#x20;  without consulting current authority state or performing a fresh Runtime

&#x20;  Authority evaluation.





\## Initial Result



FAIL



Observed exception:



ModuleNotFoundError: No module named 'app.engines.replay'



Observed assertion:



No independent replay mechanism exists. The current harness can re-evaluate

a request, but cannot reconstruct the historical determination from preserved

evidence.



The failure was preserved before remediation in:



FS-CT-003\_FAILURE.md





\## Initial Finding



The existing implementation preserved evidence sufficient to describe and

integrity-protect the historical determination, but did not expose an

independent mechanism for replaying or reconstructing that determination.



The existence of a request snapshot, receipt integrity proof and

authority-state version was not treated as sufficient evidence of replay.



The challenge therefore failed.





\## Remediation



A dedicated historical Authority Receipt replay mechanism was introduced:



app/engines/replay.py



The replay mechanism:



\- consumes the preserved Authority Receipt;

\- verifies receipt integrity;

\- reconstructs the recorded historical determination;

\- preserves the historical authority-state version;

\- preserves the historical action-binding hash;

\- does not consult current authority state;

\- does not invoke fresh Runtime Authority evaluation; and

\- does not rewrite the original Authority Receipt.



No weakening or alteration of the original FS-CT-003 adversarial invariant

was required.





\## Retest



The original FS-CT-003 adversarial test was rerun after implementation of the

replay mechanism.



The test itself was not weakened to obtain the result.



Observed result:



1 passed



The historical determination remained reconstructable after current authority

state changed.



The original Authority Receipt retained its historical:



\- receipt identity;

\- decision;

\- reason code;

\- action-binding hash;

\- authority-state version; and

\- request snapshot.





\## Final Result



PASS AFTER REMEDIATION



The same adversarial challenge that originally exposed the absence of an

independent replay mechanism subsequently passed following implementation of

the dedicated replay capability.



Within the bounded public harness, a sealed historical Authority Receipt can

now be independently integrity-verified and its recorded historical

determination reconstructed after current authority state has changed,

without consulting current authority state or performing a fresh Runtime

Authority evaluation.





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





\## Claim Boundary



FS-CT-003 demonstrates bounded historical Authority Receipt

replay/reconstruction.



It does not demonstrate full deterministic re-execution of the complete

historical Runtime Authority evaluation from a frozen historical policy,

rule, evidence and environmental estate.



Such a broader capability would require preservation and reconstruction of

the complete historical evaluation environment and should be challenged

separately.



FS-CT-003 also does not establish physical non-formation of consequences

across external banking, payment, integration, administrative or operational

execution surfaces.





\## Relationship to the FS-CT Category Test



FS-CT-001:



PASS



A prior ALLOW cannot cross a changed authority-state boundary through the

governed execution path using the stale Authority Receipt.



FS-CT-002:



PASS



Stale authority cannot reach the represented consequence through the tested

governed route. Continued execution following the authority-state change must

obtain a fresh determination under current state.



FS-CT-003:



Initial Result: FAIL



Final Result: PASS AFTER REMEDIATION



Historical Authority Receipt replay/reconstruction is now demonstrated within

the bounded public harness.



External real-world consequence non-formation remains outside the demonstrated

scope of the current public implementation.





\## Engineering Conclusion



FS-CT-003 produced a falsifiable result.



The original architecture preserved historical determination evidence but did

not provide an independent replay mechanism.



The adversarial challenge exposed that limitation.



The failure was preserved.



A dedicated replay mechanism was introduced.



The original challenge was rerun without weakening its invariant and passed.



The complete discovered regression suite subsequently passed.



The resulting claim remains deliberately bounded to the proof surface

actually exercised.

