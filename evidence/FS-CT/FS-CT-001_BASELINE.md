# FS-CT-001 Baseline

Date: 16 August 2026

Existing FlowSignal test suite before Category Test:

59 passed
0 failed
0 errors
1 warning - FastAPI/Starlette deprecation warning

Test-environment note:
tests/test_api.py was corrected so its documented in-memory SQLite fixture does not invoke the production PostgreSQL startup path.
No Runtime Authority, execution gateway, receipt, evaluation, or decision logic was modified.
