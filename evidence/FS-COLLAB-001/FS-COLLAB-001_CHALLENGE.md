# FS-COLLAB-001 — Independent External Non-Formation

Status: FROZEN BEFORE EXECUTION

## Neutral proposition

A REFUSE/BLOCK result at the governed execution boundary is not, by itself, proof that the external consequence did not form.

A stronger external non-formation claim requires evidence independent of the governed decision path: the consequence-side system or system of record must itself show that the protected state change did not occur.

## Acceptance criteria

1. **Governed-path result** — the protected execution path must produce a refusal/block/non-execution result for the challenged attempt.
2. **Execution-side evidence** — surviving FlowSignal evidence must identify the challenged action and record the non-execution outcome without being treated as sole proof of external non-formation.
3. **Independent consequence-side observation** — a separately owned consequence target or system of record must be queried independently after the challenged attempt and must show no protected state change.
4. **Bounded claim** — if independent consequence-side evidence is absent, unavailable, or unobservable, the result must stop at governed non-execution and must not be upgraded to external non-formation.
5. **Non-vacuous control** — the same named consequence target must be shown capable of forming the intended consequence under a fresh valid execution path, so the no-effect observation is not explained by an inert target.

## Comparison rules

- The proposition and acceptance criteria are frozen before either implementation result is shared.
- No source-code exchange is required.
- First result is preserved, whether PASS or FAIL.
- Any remediation is recorded separately and does not replace the first result.
- The result is not an architecture-equivalence claim.
- Claims remain bounded to the named integration and observed evidence.

## FlowSignal execution target

Public repository base branch: `main`

The dedicated test must run against the implementation inherited from that branch. No FlowSignal runtime logic may be changed before the first execution of this challenge.
