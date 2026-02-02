---
id: "031"
title: Implement Phase 18 Task Recovery
stage: green
date: 2026-01-27
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.implement 003 phase-18
labels: ["recovery", "tombstone", "FR-062", "FR-063", "FR-064", "US13"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/recovery_service.py
  - backend/src/api/recovery.py
  - backend/src/main.py
  - backend/src/middleware/metrics.py
  - backend/tests/unit/services/test_recovery_service.py
  - backend/tests/integration/test_recovery_lifecycle.py
  - specs/003-perpetua-backend/tasks.md
tests:
  - tests/unit/services/test_recovery_service.py
  - tests/integration/test_recovery_lifecycle.py
---

## Prompt

003 phase-18

## Response snapshot

Implemented Phase 18: User Story 13 - Task Deletion and Recovery (FR-062 to FR-064), completing all 14 tasks (T335-T348).

### Files Created
- `backend/src/services/recovery_service.py` - RecoveryService with tombstone listing, task recovery with original ID/timestamp restoration, FIFO enforcement, and skip flags for achievements/streaks (FR-064)
- `backend/src/api/recovery.py` - API endpoints: GET /api/v1/tombstones and POST /api/v1/tasks/recover/:tombstone_id with 7-day recovery window validation
- `backend/tests/unit/services/test_recovery_service.py` - 11 unit tests covering tombstone serialization, FIFO limits, ID restoration, timestamp preservation, subtask recovery, tombstone cleanup, ID collision handling, and achievement/streak skip flags
- `backend/tests/integration/test_recovery_lifecycle.py` - 4 integration tests covering full lifecycle (create->delete->list->recover), 404 handling, 409 collision, and FIFO eviction

### Files Modified
- `backend/src/main.py` - Registered recovery_router and recovery_tasks_router
- `backend/src/middleware/metrics.py` - Added RECOVERY_OPERATIONS counter and RECOVERY_LATENCY histogram with helper functions
- `specs/003-perpetua-backend/tasks.md` - Marked T335-T348 as [X] complete

### Key Design Decisions
- RecoveryService uses skip flags (skip_achievement_processing, skip_streak_processing) on the service instance to signal downstream handlers
- Recovery restores original UUID and created_at timestamp from tombstone entity_data
- 7-day recovery window enforced at API layer
- Tombstone is deleted after successful recovery

## Outcome

- Impact: Full task recovery system with tombstone-based undo for deleted tasks
- Tests: 11 unit tests + 4 integration tests covering FR-062, FR-063, FR-064
- Files: 4 created, 3 modified
- Next prompts: Phase 19 (Notifications) or run test suite
- Reflection: Leveraged existing tombstone model and hard_delete_task pattern from Phase 4

## Evaluation notes (flywheel)

- Failure modes observed: Pre-existing ActivityLog metadata shadow issue prevents full import chain test
- Graders run and results (PASS/FAIL): Syntax validation PASS for all 4 new files
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
