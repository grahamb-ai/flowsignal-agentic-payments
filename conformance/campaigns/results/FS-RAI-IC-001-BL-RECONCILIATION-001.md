# FS-RAI-IC-001 — Frozen Baseline Reconciliation 001

**Status:** WORKING RECONCILIATION — EXECUTED CLOSURE MUST REMAIN BOUNDED  
**Baseline:** grahamb-ai/flowsignal-agentic-payments@471d8af596044d61f86f774f70cd8c6ff2efc31c  
**Current remediation branch:** fs-rai-v1-remediation  
**Latest full regression observed:** 88/88 GREEN

This record reconciles the eight independent failures preserved in FS-RAI-IC-001-BL-001 against implementation work and executable evidence accumulated on the remediation branch. It does not declare overall implementation conformance.

| Baseline class | Current classification | Basis / remaining gate |
|---|---|---|
| IC-FAIL-001 Exact amount semantics | IMPLEMENTED + EXECUTED; campaign closure record still required | Exact Decimal handling and JSON Decimal parsing are present in the remediation lineage and exercised by the green suite. Formal closure still requires binding the executed evidence to the campaign mapping/test-plan identity. |
| IC-FAIL-002 Approval requirement ignored | IMPLEMENTED + EXECUTED; bounded | Approval is now resolved from governing approval semantics, rule identity, eligible subjects, quorum/composition and operation binding rather than a request boolean. Existing tests exercise the approval path. NORM-PAY-001 canonical baseline has no required approval, so applicable approval vectors must remain explicit rather than inferred. |
| IC-FAIL-003 Request can self-supply mandate authority | IMPLEMENTED + EXECUTED; PARTIAL wider proposition review remains | Unknown mandate no longer falls back to request-presented mandate maximum. Resolution requires institutional mandate snapshot plus actor and operational standing evidence. However target/beneficiary/purpose scope construction and the complete proposition-source boundary still require hostile review before this class is called route-wide closed. |
| IC-FAIL-004 No coherent authority snapshot | PARTIAL / NOT CLOSED | Mandate state now has a coherent snapshot identity, epoch/fence and source provenance; actor and operational evidence have their own source versions and the context binds a version-vector identity. This is stronger than baseline, but the current implementation does not yet demonstrate that all authority-material multi-source evidence belongs to one authoritative compatible cut. |
| IC-FAIL-005 Aggregate authority/reservation absent | CLOSED — TESTED R1 REFERENCE PATH | Aggregate reservation/consumption/quarantine semantics, shared mandate capacity, epoch non-replenishment, caller-window closure and authoritative usage-window rollover have executed failure/remediation evidence. See CL-005, CL-005A, CL-005B and CL-005C. This is not route-wide/durable production closure. |
| IC-FAIL-006 Exercise/attempt identities absent | IMPLEMENTED + EXECUTED; PARTIAL lineage hardening remains | Explicit authority exercise and execution attempt identities exist and are bound into determination/constraint/execution provenance. Remaining concerns include stable institutional-operation lineage and protected-operation-class verification across retry/attempt semantics. |
| IC-FAIL-007 Semantic definition/source provenance unbound | IMPLEMENTED + EXECUTED; PARTIAL campaign proof remains | Semantics version, definition and source are represented in authoritative snapshot/resolution and propagated into the execution permit. Evidence propositions carry semantic definition, authoritative source, competence and source version. Full campaign mapping/evidence closure remains required. |
| IC-FAIL-008 Epoch/fence scope absent | IMPLEMENTED + EXECUTED; PARTIAL transition/provenance hardening remains | Authority epoch, fence scope, fence and snapshot are represented and final-bind/gateway lineage uses them. Usage-window work has also demonstrated that epoch movement is not economic replenishment. Production-grade competent epoch-transition provenance and cross-domain scope closure remain unresolved. |

## Reconciliation result

The original eight failures are no longer an undifferentiated RED surface.

- **IC-FAIL-005** has a preserved bounded closure for the tested R1 reference path.
- **IC-FAIL-001, 002, 003, 006, 007 and 008** have material implementation remediation and executable green evidence, but must not yet be promoted to unconditional campaign PASS.
- **IC-FAIL-004** remains the clearest unresolved original baseline property: coherent multi-source authority-state compatibility at one authority-relevant cut has not yet been demonstrated.

## Next target

Attack IC-FAIL-004 directly.

The decisive question is not whether each source has a version. It is:

> Can individually competent and current-looking authority propositions from mutually incompatible source generations be assembled into one apparently sufficient AuthorityResolutionContext?

A RED reproduction would show that a version vector is descriptive but not itself proof of cross-source compatibility. A GREEN result must establish an independently grounded compatibility rule/cut rather than merely hashing the presented versions.

No released fixture change is authorised by this reconciliation.
