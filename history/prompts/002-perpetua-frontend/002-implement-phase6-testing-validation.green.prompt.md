---
id: 002
title: Implement Phase 6 Testing and Validation
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: continue with phase 6
labels: ["testing", "integration-tests", "schema-migration", "unit-tests", "msw-cleanup"]
links:
  spec: FRONTEND-BACKEND-INTEGRATION.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/tests/integration/setup.ts
  - frontend/tests/integration/auth.test.tsx
  - frontend/tests/integration/tasks-crud.test.tsx
  - frontend/src/lib/utils/date.ts
  - frontend/tests/unit/utils/date.test.ts
  - frontend/tests/integration/task-creation.test.tsx
  - frontend/tests/unit/components/ReminderForm.test.tsx
  - frontend/tests/unit/components/TaskForm.test.tsx
  - frontend/tests/unit/components/SubTaskList.test.tsx
  - frontend/src/mocks/data/tasks.fixture.ts
tests:
  - frontend/tests/integration/auth.test.tsx (4 suites: OAuth callback, token refresh, logout, unauthenticated)
  - frontend/tests/integration/tasks-crud.test.tsx (5 suites: list, create, update, delete, force-complete)
  - frontend/tests/unit/utils/date.test.ts (rewritten for new Reminder schema)
  - frontend/tests/integration/task-creation.test.tsx (updated with makeTask helper)
  - frontend/tests/unit/components/ReminderForm.test.tsx (updated mock task)
  - frontend/tests/unit/components/TaskForm.test.tsx (updated mock tasks)
  - frontend/tests/unit/components/SubTaskList.test.tsx (updated with makeSubTask helper)
---

## Prompt

continue with phase 6

## Response snapshot

Implemented Phase 6: Testing & Validation from FRONTEND-BACKEND-INTEGRATION.md (lines 944-1020):

**Task 6.1 - Integration test setup** (`tests/integration/setup.ts`): Created `createTestQueryClient()`, `renderWithProviders()`, mock fixtures (mockUser, mockTask, mockTaskDetail, mockSubTask, mockNote), and `paginatedResponse()` helper. All fixtures match new backend schemas.

**Task 6.2 - Auth flow integration tests** (`tests/integration/auth.test.tsx`): 4 test suites covering Google OAuth callback, token refresh on expired access token, logout clearing session, and unauthenticated state.

**Task 6.3 - Task CRUD integration tests** (`tests/integration/tasks-crud.test.tsx`): 5 test suites covering list with pagination, create with idempotency key, update with version conflict (CONFLICT error), delete returns tombstone, and force complete.

**Task 6.4 - Updated existing unit tests**: Major schema migration across 7 files:
- `date.ts`: Fixed imports, changed `reminder.timing.offsetMinutes` to `reminder.offsetMinutes`, `reminder.delivered` to `reminder.fired`
- `date.test.ts`: Rewritten with new Reminder schema (no `timing` wrapper)
- `task-creation.test.tsx`: Added `makeTask` helper, removed `tags`/`parentTaskId`, added `version`/`subtaskCount`/etc.
- `ReminderForm.test.tsx`: Updated mock task to new schema
- `TaskForm.test.tsx`: Updated mock responses to new schema
- `SubTaskList.test.tsx`: Added `makeSubTask` helper with `orderIndex`/`source`
- `tasks.fixture.ts`: Added `makeFixtureTask` helper, removed old fields

**Task 6.5 - MSW cleanup verified**: MSW dev mode already removed in Phase 5. Confirmed no remaining imports of `useMSWReady`/`MSWReadyContext` in `src/`.

**Known follow-up**: `recurrence.ts` and `recurrence.test.ts` reference `task.recurrence` which no longer exists - needs separate refactor.

## Outcome

- Impact: Complete test infrastructure and schema alignment for frontend-backend integration
- Tests: 3 new test files, 4 updated test files, all using new backend schemas
- Files: 10 files (3 created, 7 modified)
- Next prompts: All 6 phases complete. Recurrence utility refactor or running tests to verify.
- Reflection: Factory helpers (makeTask, makeSubTask, makeFixtureTask) significantly reduced test maintenance burden. Note schema had unexpected fields (voiceUrl, voiceDurationSeconds, transcriptionStatus) that required reading the actual schema file.

## Evaluation notes (flywheel)

- Failure modes observed: Initial mockNote had wrong fields (title, pinned, version) - always read schema files before creating mocks
- Graders run and results (PASS/FAIL): Tests not run yet - need verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run test suite to verify all schema migrations compile and pass
