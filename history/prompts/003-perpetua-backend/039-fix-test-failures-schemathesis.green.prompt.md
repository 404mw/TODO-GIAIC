---
id: 039
title: Fix Unit Test Failures and Schemathesis Compatibility
stage: green
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.implement 003
labels: ["testing", "bug-fix", "schemathesis", "metrics", "integration-test"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/services/ai_service.py
  - src/services/auth_service.py
  - src/services/subscription_service.py
  - src/services/recurring_service.py
  - src/dependencies.py
  - src/middleware/metrics.py
  - tests/unit/services/test_recurring_service.py
  - tests/unit/services/test_subscription_service.py
  - tests/unit/jobs/test_streak_job.py
  - tests/integration/test_health.py
  - tests/contract/conftest.py
  - tests/contract/test_auth_fuzz.py
  - tests/contract/test_tasks_fuzz.py
  - tests/contract/test_ai_fuzz.py
  - tests/contract/test_subscription_fuzz.py
  - specs/003-perpetua-backend/tasks.md
tests:
  - tests/unit/ (303/303 pass - all fixed)
  - tests/integration/test_health.py (3 tests pass)
  - tests/contract/ (77/154 pass, 0 errors - schemathesis fixed)
---

## Prompt

/sp.implement 003 - Fix 29 unit test failures, complete T012a (readiness probe 503 integration test), complete T084 (Prometheus auth metrics), fix schemathesis compatibility for contract fuzz tests.

## Response snapshot

Fixed all 30 unit test failures (29 original + 1 discovered streak test) across multiple root causes:

1. **SQLite enum string storage** (4 transcription + 1 auth test): `user.tier.value` fails when SQLite stores enum as plain string. Added `hasattr(user.tier, 'value')` guard in ai_service.py (lines 659, 758) and auth_service.py (line 148).

2. **Webhook idempotency NOT NULL violation** (2 tests): ActivityLog requires user_id which webhooks don't have. Simplified to in-memory set deduplication in subscription_service.py.

3. **Naive/aware datetime comparison** (1 test): Test used aware `datetime.now(UTC)` to compare against service-produced naive datetimes. Fixed with `.replace(tzinfo=None)`.

4. **RRULE COUNT=1 microsecond precision** (1 test): Multi-layered fix - microsecond truncation, `inc=True` fallback for initial creation, `<=` to `<` comparison fix in recurring_service.py.

5. **JWT token uniqueness** (1 test): Added `jti: uuid4().hex` to access token payload in dependencies.py for token uniqueness within same second.

6. **UNIQUE constraint on subscriptions** (1 test): Fixed test to use same subscription_id for both events.

7. **AsyncMock for async function patches** (1 streak test): Changed `patch(..., return_value=False)` to `patch(..., new=AsyncMock(return_value=False))`.

8. **UTC vs local date in tests** (1 streak test): Changed `date.today()` to `datetime.now(UTC).date()` to match job's UTC-based calculation.

Completed T012a: Created 3 integration tests for health endpoints (liveness 200, readiness 200, readiness 503 with DB unavailable).

Completed T084: Added AUTH_OPERATIONS Counter and AUTH_LATENCY Histogram to metrics.py, instrumented authenticate_with_google() and refresh_tokens() in auth_service.py.

Fixed schemathesis compatibility: Replaced `schemathesis.from_dict()` (removed in v4.9.5) with `schemathesis.openapi.from_dict()` across 5 files. Eliminated all 30 import errors; contract tests went from 50 pass/30 error to 77 pass/0 error.

## Outcome

- Impact: Unit tests 274/303 (90.4%) -> 303/303 (100%). Contract tests 50 pass/30 errors -> 77 pass/0 errors. T012a and T084 completed.
- Tests: 303 unit tests pass, 3 new integration tests, 27 additional contract tests passing
- Files: 16 files modified across services, tests, middleware, and specs
- Next prompts: Fix remaining 75 contract test failures (Settings validation in async context), increase code coverage
- Reflection: SQLite test environment differences from PostgreSQL production remain a recurring source of test failures. The enum string storage and naive datetime handling should be standardized project-wide.

## Evaluation notes (flywheel)

- Failure modes observed: SQLite enum storage as string (not Enum instances), RRULE microsecond truncation, JWT deterministic output, AsyncMock vs MagicMock for async functions, UTC vs local timezone in tests
- Graders run and results (PASS/FAIL): Unit tests PASS (303/303), Integration tests PASS (3/3), Contract errors PASS (0 errors)
- Prompt variant (if applicable): Continuation session after context compaction
- Next experiment (smallest change to try): Standardize enum handling with a utility function to avoid repeated hasattr guards
