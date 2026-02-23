---
id: 045
title: Revise Tasks — Notes Standalone v1.2
stage: tasks
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.tasks
labels: ["tasks", "notes", "revamp", "standalone", "migration"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - "Task 3.7a acceptance: notes table has user_id/archived/voice fields, task_id removed"
  - "Task 3.7b acceptance: POST /api/v1/notes returns 201, GET /api/v1/notes returns PaginatedResponse"
  - "Task 3.7b acceptance: deprecated endpoints return 410 ENDPOINT_GONE"
  - "Task 3.7c acceptance: 402 LIMIT_EXCEEDED on note cap, 2000-char uniform content limit"
  - "Task 7.1 regression: standalone note creation, archived filter, convert, 402 vs 409, 410"
---

## Prompt

003
revise tasks as per updated specs and plan and replace Task 3.7 with Tasks 3.7a (migration), 3.7b (endpoints), 3.7c (limit enforcement) per Section C of @ANALYSIS_REVAMP_003.md

## Response snapshot

Replaced Task 3.7 (task-scoped notes, now obsolete) in `specs/003-perpetua-backend/tasks.md` with three new tasks aligned to FR-012 v1.2 (standalone notes redesign):

- **Task 3.7a** — Note Model & Migration (Standalone): Remove `task_id`/`order_index`, add `archived`/`voice_url`/`voice_duration_seconds`/`transcription_status`, update User/TaskInstance relationships, create Alembic migration.
- **Task 3.7b** — Standalone Note Endpoints: `POST/GET /api/v1/notes`, `PATCH/DELETE /api/v1/notes/{id}`, `POST /api/v1/notes/{id}/convert`, stub 410 for deprecated task-scoped routes, update schemas.
- **Task 3.7c** — Note Limit Enforcement Update: Enforce `402 LIMIT_EXCEEDED` (not `409`), user-scoped count, uniform 2000-char limit, update contract tests.

Also added 5 note regression test subtasks to **Task 7.1** for standalone creation, archived filter, convert archiving, 402-vs-409, and 410 deprecated endpoint behavior.

## Outcome

- ✅ Impact: tasks.md now fully aligned with spec.md FR-012 v1.2 and plan.md — all 8 coverage gaps from ANALYSIS_REVAMP_003.md addressed (standalone-note-create-endpoint, standalone-note-list-endpoint, note-archived-field, note-voice-fields, note-database-migration, note-task-id-removal, note-410-gone-routes, note limit error code)
- 🧪 Tests: 5 new regression test items added to Task 7.1; each task has explicit acceptance criteria
- 📁 Files: specs/003-perpetua-backend/tasks.md
- 🔁 Next prompts: `/sp.implement 003` — begin execution of Task 3.7a (model migration), then 3.7b (endpoints), then 3.7c (limit enforcement)
- 🧠 Reflection: Analysis document (ANALYSIS_REVAMP_003.md) provided exact Section C content used verbatim; tasks are directly executable without additional context. All 4 CRITICAL issues from analysis are now covered in tasks (C1 via spec update already done, C2/H4 via 3.7a, C3/C4 via 3.7c).

## Evaluation notes (flywheel)

- Failure modes observed: None — clean replacement using analysis document as authoritative source
- Graders run and results (PASS/FAIL): N/A (tasks document, not code)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run sp.implement with Task 3.7a to validate migration tasks are specific enough for autonomous execution
