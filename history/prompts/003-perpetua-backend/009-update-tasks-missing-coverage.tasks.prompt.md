---
id: 009
title: Update Tasks Missing Coverage
stage: tasks
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: developer
command: /sp.tasks
labels: ["tasks", "task-update", "fr-013", "fr-069", "bug-fix", "consistency"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - null
---

## Prompt

003-perpetua-backend

## HIGH Priority

### Missing Task Coverage: FR-013
- **Location:** tasks.md (missing)
- **Issue:** FR-013 "maximum task duration of 30 days from creation" has no validation task
- **Recommendation:** Add to Phase 4:
  ```
  - [ ] T130a [US2] Test: Task creation fails if due_date > created_at + 30 days in tests/unit/services/test_task_service.py (FR-013)
  - [ ] T130b [US2] Implement 30-day max duration validation in src/services/task_service.py (FR-013)
  ```

### Missing Task Coverage: FR-069
- **Location:** tasks.md (missing)
- **Issue:** FR-069 "backward compatibility within major version" has no deprecation strategy task
- **Recommendation:** Add to Phase 24:
  ```
  - [ ] T416a [Polish] Document API versioning and deprecation policy in docs/api-versioning.md (FR-069)
  ```

## MEDIUM Priority

### I3: Task Count Inconsistency
- **Location:** tasks.md Summary vs Phase counts
- **Issue:** Summary says "Total Tasks: 416" but Phase 1 numbering (T001-T029) suggests 29 tasks while text says "28 tasks"
- **Recommendation:** Reconcile:
  - Phase 1 header says "28 tasks" but has T001-T029 (29 task IDs)
  - Verify each phase and update summary

### I5: User Story 5 Split Across Phases
- **Location:** tasks.md Phases 7, 12, 13
- **Issue:** US5 "Notes with Voice Recording" spans 3 non-consecutive phases (7, 12, 13) which may cause confusion
- **Recommendation:** Add phase notes explaining split

### G1: Missing Concurrent Update Stress Test
- **Location:** tasks.md Phase 23
- **Issue:** spec.md Edge Cases mention concurrent updates but no dedicated stress test
- **Recommendation:** Add to Phase 23:
  ```
  - [ ] T402a [Validation] Create concurrent update stress test (optimistic locking) in tests/integration/test_concurrent_updates.py
  ```

### G2: Missing Readiness Probe Test
- **Location:** tasks.md
- **Issue:** T012 creates health endpoints but no integration test for readiness probe
- **Recommendation:** Add to Phase 1:
  ```
  - [ ] T012a [Infra] Integration test: Readiness probe returns 503 when DB unavailable in tests/integration/test_health.py
  ```

## LOW Priority

### T1: Terminology Standardization
- **Location:** tasks.md throughout
- **Issue:** "Task Instance" vs "task" used interchangeably
- **Recommendation:** Standardize during implementation

### Unmapped Documentation Tasks
- **Location:** tasks.md T138, T252, T262, T348, T366, T384
- **Issue:** 6 documentation tasks have no FR reference
- **Recommendation:** These are quality assurance tasks - acceptable

## Response snapshot

Updated tasks.md with the following changes:

**HIGH Priority - Implemented:**
- Added T130a and T130b for FR-013 (30-day max task duration validation) in Phase 4
- Added T416a for FR-069 (API versioning documentation) in Phase 24

**MEDIUM Priority - Implemented:**
- Fixed Phase 1 header: corrected from "28 tasks" to "30 tasks" (was 29, now 30 with T012a)
- Added T012a for readiness probe integration test (FR-067)
- Added T402a for concurrent update stress test (FR-014)
- Added US5 Split Notes to Phases 7, 12, and 13 explaining the dependency structure

**LOW Priority - Implemented:**
- Added terminology standardization note in the Notes section

**Summary Updates:**
- Total tasks: 416 -> 421 (+5 new tasks)
- Phase 1: 28 -> 30 tasks
- Phase 4: 35 -> 37 tasks
- Phase 23: 20 -> 21 tasks
- Phase 24: 14 -> 15 tasks
- MVP tasks: ~94 -> ~99 tasks

## Outcome

- Impact: 5 new tasks added to ensure complete FR coverage, phase headers corrected for accuracy
- Tests: No new tests executed; task definitions added for future test implementation
- Files: specs/003-perpetua-backend/tasks.md modified
- Next prompts: Begin Phase 1 implementation, validate task counts match actual tasks
- Reflection: The original task generation missed FR-013 validation tasks and FR-069 documentation task. The a/b suffix approach for insertion preserves existing task ID references.

## Evaluation notes (flywheel)

- Failure modes observed: Task count header mismatch (28 vs 29), missing FR coverage (FR-013, FR-069)
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): Standard /sp.tasks with user-provided gap analysis
- Next experiment (smallest change to try): Add automated task count validation in task generation workflow
