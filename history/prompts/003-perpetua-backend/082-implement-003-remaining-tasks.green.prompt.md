---
id: 082
title: Implement 003 Remaining Tasks
stage: green
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.implement 003 remaining tasks
labels: ["implementation","unit-tests","focus-mode","ai-credits","notifications","recovery"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/models/ai_session_counter.py (new)
  - alembic/versions/009_ai_session_counters.py (new)
  - src/models/__init__.py (modified)
  - src/models/focus.py (modified)
  - src/config.py (modified)
  - src/schemas/focus.py (modified)
  - src/services/focus_service.py (modified)
  - src/api/focus.py (modified)
  - src/services/ai_service.py (modified)
  - src/services/credit_service.py (modified)
  - src/jobs/tasks/subscription_job.py (modified)
  - src/jobs/tasks/credit_job.py (modified)
  - src/services/recovery_service.py (modified)
  - src/middleware/error_handler.py (modified)
  - tests/unit/api/test_notes_standalone.py (new)
  - tests/unit/services/test_subscription_renewal.py (new)
  - tests/unit/services/test_note_tombstone.py (new)
  - tests/unit/services/test_ai_service_unit.py (modified)
  - tests/unit/middleware/test_error_handler.py (modified)
  - specs/003-perpetua-backend/tasks.md (modified)
tests:
  - tests/unit/api/test_notes_standalone.py (8 new tests)
  - tests/unit/services/test_subscription_renewal.py (3 new tests)
  - tests/unit/services/test_note_tombstone.py (4 new tests)
---

## Prompt

003 remaining tasks

## Response snapshot

Implemented all remaining incomplete tasks from `specs/003-perpetua-backend/tasks.md`:

**Task 4.3 [L1]**: Added TODO comment near former `_task_request_counters` dict in `ai_service.py` noting DB-backed replacement.

**Task 4.3a**: Created `AISessionCounter` SQLModel (`src/models/ai_session_counter.py`) with `session_id`, `task_id`, `count`, `expires_at` fields and composite unique index. Created Alembic migration 009. Replaced in-memory counter dict in `AIService` with DB-backed `_get_session_counter()` / `_increment_session_counter()` methods. Also fixed SQLite timezone comparison bug (`expires_at.tzinfo is None → replace(tzinfo=UTC)`).

**Task 5.5**: Added `focus_session_timeout_minutes: int = Field(default=90)` to `Settings`. Added `goal_duration_minutes` field to `FocusSession` model and `FocusSessionResponse` schema. Added `focus_duration` to `FocusStartRequest`. Added `FocusDurationInvalidError` + validation in `FocusService.start_session()`. Added lazy auto-stop in `_get_active_session()` for sessions exceeding timeout.

**Task 4.2a**: Implemented `CreditService.renew_subscription_credits(user_id)` with carryover logic: `carryover = min(current_sub_balance, max_carryover)`. Added `_process_subscription_renewals()` step in `subscription_job.py`.

**Task 6.2**: Added `_prune_old_notifications()` (deletes notifications >30 days) and `_cleanup_ai_session_counters()` (deletes expired AI counters) to `credit_job.py` as Steps 4-5 in `handle_credit_expire()`.

**Task 7.1**: Wrote 15 new unit tests across 3 new files:
- `test_notes_standalone.py` (8 tests): standalone note creation, archived filter, convert no-archive, 402 LIMIT_EXCEEDED, 410 ENDPOINT_GONE
- `test_subscription_renewal.py` (3 tests): carryover 30→80, carryover 60→100 capped, Free user unaffected
- `test_note_tombstone.py` (4 tests): legacy task_id silently ignored, modern format recovery, tombstone deletion, cross-user access denied

**Bug fix**: `LimitExceededError` was inheriting `status_code=409` from `ConflictError` but FR-012 v1.2 requires HTTP 402. Fixed by overriding `AppError.__init__` directly with `status_code=402`.

**RecoveryService extension**: Added `recover_tombstone()` generic method and `_recover_note_from_tombstone()` helper for FR-013 migration tolerance (legacy `task_id` field in NOTE tombstone entity_data is silently ignored).

All 15 new tests pass. 676 unit tests pass (34 pre-existing SQLite enum failures unchanged).

## Outcome

- ✅ Impact: Closes all 7 remaining open Task 7.1 items + Tasks 4.3/4.3a/5.5/4.2a/6.2 subtasks
- 🧪 Tests: 15 new passing tests; 676 total passing unit tests
- 📁 Files: 20 files modified/created
- 🔁 Next prompts: Contract tests update (Task 3.7c/7.3), scalability test (Task 7.4), deploy prep
- 🧠 Reflection: SQLite datetime timezone handling requires `.replace(tzinfo=UTC)` guard on any `expires_at` comparison. `LimitExceededError` status_code was 409 despite spec requiring 402 — fixed as part of test coverage.

## Evaluation notes (flywheel)

- Failure modes observed: SQLite naive datetime comparison TypeError in ai_service.py; `LimitExceededError` inheriting wrong status_code; `TestClearSessionCounters` testing removed in-memory dict
- Graders run and results (PASS/FAIL): All 15 new tests PASS; all previously-passing tests continue to pass
- Prompt variant (if applicable): sp.implement skill
- Next experiment: Add contract test updates for new note schema (no task_id, 402 instead of 409)
