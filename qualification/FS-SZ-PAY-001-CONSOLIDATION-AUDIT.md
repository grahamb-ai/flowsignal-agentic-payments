# FS-SZ-PAY-001 — Consolidation audit and candidate gate

Status: **INVENTORY BASELINE ONLY — NOT INTEGRATED OR QUALIFIED**.

## Repository inventory
GitHub REST branch listing returned 53 branches, including 21 named `qualification/fs-sz-pay-001-*`. Main at audit: `471d8af596...`.

## Selected starting point
`qualification/fs-sz-pay-001-mandate-required` (46 commits ahead of main, zero behind), copied without modification into `qualification/fs-sz-pay-001-consolidation-candidate`. This is a staging baseline, not an endorsement of the branch's behaviour.

## Branch families to reconcile
| Source | Contribution | Consolidation treatment |
|---|---|---|
| T17–T19 | External adapter, lost acknowledgement and capability route | Present in later lineage; verify both paths |
| T20 | Preserved duplicate business-payment retry counterexample | Keep RED as acceptance test |
| T21 | Durable payment-intent claim, separate-process uniqueness | Review and port where justified |
| T22 | Atomic permit/intent/unresolved state candidate | **Divergent**: 11 commits behind latest branch's ancestry; inspect before selective port |
| T23 | Unfenced provider commitment RED | Preserve historical failure, never silently remove |
| T24–T25 | Provider commitment fence and refusal classification | Present in latest lineage; revalidate |
| T26 | Empty/unsigned provider outcome handling | **Divergent**: 4 commits not in latest branch ancestry; inspect before port |
| T27 | Provider receipt authenticity challenge | Unqualified; do not represent as proven |
| Integrated/race | FlowSignal adapter + simulated provider and concurrency | Present in latest lineage; revalidate |
| Route closure/atomic/HTTP | Direct provider atomic ledger, fail-closed startup and HTTP tests | Present in latest lineage; revalidate |
| Mandate binding/required | Explicit authority context tests | Current branch head; not yet proven integrated end-to-end |
| CBP-003 and PMQ | Earlier route closure, crash/replay/rollback work | Compare contracts and test coverage; do not assume changes absent from main |

## Evidence already observed
- Integrated reference fence: 8/8 targeted tests GREEN.
- Integrated concurrency: 9/9 targeted tests GREEN (20 rounds in one test).
- Original direct provider route: RED, simulated payment committed after revocation.
- Configured atomic direct route: 3/3 targeted tests GREEN, but legacy mode explicitly bypassed.
- HTTP route: 7/7 targeted tests GREEN.
- Mandate substitution: original RED, correction 3/3 targeted GREEN.
- Historical T23 remains RED by design on full regression; do not relabel full suite GREEN.

## Hard acceptance gates for one candidate
1. Preserve frozen counterexamples and first-RED evidence separately from corrected acceptance tests.
2. Verify that payment identity is stable across newly issued permits and alternate routes, with durable single-commit enforcement.
3. Make provider mandate, epoch and payment details explicit and authentically bound; reject missing or substituted context.
4. Ensure **every in-scope** HTTP/direct/capability path invokes the same atomic authoritative commitment operation; exclude or remove legacy bypass from the declared protected boundary.
5. Test revocation before commitment, commit before revocation, concurrent ordering, retry after unknown outcome, and restart/crash windows through the *integrated* route.
6. Run complete regression with documented expected historical REDs; do not weaken tests to force a green total.
7. Publish precise evidence and limitations: simulated SQLite provider only; not live-rail certification, production trust isolation, or universal route closure.

## Next engineering action
Diff T21/T22 and T26 against this candidate at file and behaviour level. Selectively port the smallest proven mechanisms and tests, resolve overlapping changes in `protected_consequence.py` and `external_consequence_adapter.py`, and run a single integrated qualification workflow. **Do not merge into main until reviewed and qualified.**
