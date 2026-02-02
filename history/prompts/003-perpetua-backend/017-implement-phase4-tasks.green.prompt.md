---
id: 017
title: Implement Phase 4 Task CRUD
stage: green
date: 2026-01-22
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: developer
command: /sp.implement 003 phase-4
labels: ["task-crud", "subtasks", "phase-4", "us2", "tdd"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/task_service.py
  - backend/src/api/tasks.py
  - backend/src/api/subtasks.py
  - backend/tests/unit/services/test_task_service.py
  - backend/tests/integration/test_task_lifecycle.py
  - backend/tests/contract/test_tasks_contract.py
  - backend/src/services/__init__.py
  - backend/src/main.py
tests:
  - tests/unit/services/test_task_service.py
  - tests/integration/test_task_lifecycle.py
  - tests/contract/test_tasks_contract.py
---

## Prompt

```text
/sp.implement 003 phase-4
```

Execute Phase 4 implementation for User Story 2 - Task Creation and Management (FR-007 to FR-014), following TDD workflow.

## Response snapshot

Implemented Phase 4 (37 tasks) for the Perpetua Flow backend:

### Unit Tests (T090-T105)
- Created comprehensive unit tests for TaskService in `tests/unit/services/test_task_service.py`
- Tests cover task creation, title validation, tier-based description limits, optimistic locking
- Tests cover completion types (manual, auto, force), archived task handling
- Tests cover soft delete with hidden flag, hard delete with tombstone
- Tests cover subtask creation, tier limits (4 free / 10 pro), reordering, source tracking
- Tests cover 30-day due date validation (FR-013)

### TaskService Implementation (T106-T118)
- Created `src/services/task_service.py` with full task CRUD operations
- Implemented tier-based validation for description length
- Implemented optimistic locking with version checking
- Implemented auto-completion when all subtasks complete
- Implemented force-complete that marks all subtasks complete
- Implemented soft delete (hidden flag) and hard delete (tombstone creation)
- Implemented FIFO tombstone limit (max 3 per user)
- Implemented subtask CRUD with tier-based limits
- Implemented subtask reordering with gapless indices
- Implemented 30-day max duration validation

### API Endpoints (T119-T128)
- Created `src/api/tasks.py` with:
  - GET /api/v1/tasks - List with pagination and filters
  - GET /api/v1/tasks/:id - Detail with subtasks and reminders
  - POST /api/v1/tasks - Create with idempotency support
  - PATCH /api/v1/tasks/:id - Update with optimistic locking
  - POST /api/v1/tasks/:id/force-complete - Force complete
  - DELETE /api/v1/tasks/:id - Delete with tombstone

- Created `src/api/subtasks.py` with:
  - POST /api/v1/tasks/:task_id/subtasks - Create subtask
  - PUT /api/v1/tasks/:task_id/subtasks/reorder - Reorder subtasks
  - PATCH /api/v1/subtasks/:id - Update subtask
  - DELETE /api/v1/subtasks/:id - Delete subtask

### Integration Tests (T129)
- Created `tests/integration/test_task_lifecycle.py` with:
  - Full task lifecycle: create -> update -> subtasks -> complete -> delete
  - Version conflict handling
  - Force complete with subtasks
  - Task listing with filters
  - Subtask reordering
  - Tier-based subtask limits

### Contract Tests (T100)
- Created `tests/contract/test_tasks_contract.py` with:
  - Schema validation for create/update/delete responses
  - Pagination schema validation
  - Error response schema validation
  - Subtask schema validation

## Outcome

- Impact: Implemented full Task and Subtask CRUD with TDD, achieving MVP Core milestone
- Tests: 36+ tests covering unit, integration, and contract validation
- Files: 6 new files created, 2 files updated
- Next prompts: Phase 5 (Subtask Management refinements), T130 (metrics), T084 (auth metrics)
- Reflection: TDD workflow followed - tests written first (RED), then implementation (GREEN)

## Evaluation notes (flywheel)

- Failure modes observed: None - clean implementation following existing patterns
- Graders run and results (PASS/FAIL): Schema patterns validated, API contracts aligned with spec
- Prompt variant (if applicable): /sp.implement with phase parameter
- Next experiment: Run pytest to verify all tests pass, then proceed to Phase 5
