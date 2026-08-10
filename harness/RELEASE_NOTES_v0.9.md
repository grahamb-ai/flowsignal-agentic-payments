# v0.9 — Presentation & Architectural Clarity

This release freezes the six-scenario decision logic and refines the live demonstration layer.

## Changes
- Human-readable governance reasons are shown in the main UI while exact machine reason codes remain visible.
- AP-003 now highlights earlier APPROVED state versus current RESTRICTED state.
- AP-004 now exposes evidence age (8,100s) against the permitted maximum (3,600s).
- AP-005 now exposes mandate expiry against evaluation time.
- AP-006 now preserves the architectural distinction between Runtime Authority and enforcement:
  - Runtime Authority: ALLOW for Action A.
  - Execution Gateway: BLOCKED when Action B is presented.
- AP-006 retains both action-binding hashes as evidence of the mismatch.
- Added a six-step demo narrative for live FCA / financial-services walkthroughs.
- No changes to the underlying six-scenario decision logic.
