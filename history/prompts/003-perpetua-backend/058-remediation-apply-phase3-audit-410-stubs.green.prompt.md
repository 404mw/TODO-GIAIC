---
id: 058
title: remediation apply phase3 audit 410 stubs
stage: green
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: (continued from sp.analyze 003 remediation session)
labels: ["remediation","phase3-audit","410-gone","tasks-3.7b","tasks-3.7c","spec-edits","plan-edits"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - REMEDIATIONS-003.md (created)
  - specs/003-perpetua-backend/spec.md (edited: undo removed, FR-012 content range, FR-011 delivery note, FR-007 alias, FR-004 action_id)
  - specs/003-perpetua-backend/plan.md (edited: Pattern 6 stale task.notes, constitution check III.2/III.4)
  - specs/003-perpetua-backend/tasks.md (edited: Phase 3 tasks marked [x], Task 4.6a won't-implement, Task 8.2a infra, Task 4.7 ownership note, Task 4.2a placement note, Task 6.2 note, 410 stubs confirmed)
  - backend/src/api/tasks.py (added 410 Gone stubs for deprecated POST/GET /tasks/{task_id}/notes)
  - backend/src/schemas/common.py (added ENDPOINT_GONE error code)
  - backend/src/services/note_service.py (fixed NoteLimitExceededError docstring: (409) → (402))
  - backend/tests/unit/api/test_notes_api.py (fixed TestDeleteNote.test_success: mocked tombstone return, 200 not 204)
tests:
  - tests/unit/api/test_notes_api.py::TestDeleteNote::test_success (PASS — fixed)
  - tests/unit/api/test_tasks_api.py (pre-existing UUID validation failures — not introduced by this session)
---

## Prompt

suggest concrete remediation edits for all issues in a `.md` file at the project root and then audit. we dont do undo so update spec/plan/tasks (not constitution) and document skipping 'Render' backups since its a UI thing.

## Response snapshot

Created `REMEDIATIONS-003.md` at project root documenting all 18 findings from `/sp.analyze 003` with before/after edits, decision log, and Phase 3 audit results.

**Product decisions encoded:**
- **No undo for AI actions** — Task 4.6a replaced with "WON'T IMPLEMENT" note; all undo references removed from spec/plan/tasks; constitution unchanged per user instruction.
- **Automated backups** — Task 8.2a replaced with "INFRASTRUCTURE (No Code Required)" noting Render/Railway PostgreSQL add-on dashboard handles automated daily backups.

**Spec.md edits (7 changes):**
- FR-004: Removed success criterion for undo endpoint; `action_id` marked "reserved for future use"
- FR-011: Reminders success criterion changed from "fire at correct time" → "stored and queryable; delivery out of scope"
- FR-012 Outputs: content range `1–2000` → `0–2000; non-empty required unless voice_url was set`
- FR-012 Side Effects: Added credit formula cross-ref → "see FR-006"
- FR-007: Added route ownership note for `GET /api/v1/ai/credits` alias
- Gap 5: Rewritten from "constitution violation" to documented product decision with mitigations

**Plan.md edits (2 changes):**
- Pattern 6 snapshot code: Removed stale `task.notes` reference; added comment explaining v1.2 standalone notes architecture
- Constitution check table: Added III.2 (INFRA/Render) and III.4 (EXCLUDED/product decision) rows

**Tasks.md edits (extensive):**
- Phase 3 preamble updated to "MOSTLY CLOSED"
- Task 3.7a: All 8 subtasks marked `[x]` with evidence
- Task 3.7b: 10/10 subtasks now `[x]` — 410 stubs implemented in this session
- Task 3.7c: 4/5 `[x]`; docstring bug fixed; contract tests remain `[ ]` (Task 7.1)
- Task 3.7d: 1/4 `[x]`; pipeline wiring in `create_note()` remains open
- Task 4.6a: "WON'T IMPLEMENT" product decision
- Task 8.2a: "INFRASTRUCTURE (No Code Required)" — Render dashboard
- Task 4.7: Ownership note for `GET /api/v1/ai/credits`
- Task 4.2a: Dependency placement note clarified

**Code changes (this continuation session):**
- `api/tasks.py`: Added `POST /tasks/{task_id}/notes` and `GET /tasks/{task_id}/notes` endpoints returning 410 Gone with `ENDPOINT_GONE` error code
- `schemas/common.py`: Added `ENDPOINT_GONE = "ENDPOINT_GONE"` to `ErrorCode`
- `services/note_service.py`: Fixed `NoteLimitExceededError` docstring: "(409)" → "(402)"
- `tests/unit/api/test_notes_api.py`: Fixed `TestDeleteNote.test_success` to mock tombstone return and assert 200 with `deleted_id`+`tombstone_id` (was stale 204/None)

**Phase 3 audit summary:**
| Task | Status | Evidence |
|------|--------|----------|
| 3.7a Note model & migration | ✅ COMPLETE | note_service.py:142-151, no task_id in schema |
| 3.7b Standalone endpoints | ✅ COMPLETE | api/notes.py, api/tasks.py (410 stubs added) |
| 3.7c Limit enforcement | ✅ MOSTLY | contract tests remain [ ]; docstring fixed |
| 3.7d Voice transcription pipeline | ⚠️ PARTIAL | status methods exist; create_note() wiring missing |

**Bonus finding**: `limits.py:46` `FREE_TIER_DAILY_CREDITS = 0` — spec FR-007 says 10. Logged in REMEDIATIONS-003.md; outside Phase 3 scope.

## Outcome

- ✅ Impact: Applied all 15 spec/plan/tasks remediations from `/sp.analyze 003`; implemented 410 Gone stubs for deprecated task-scoped note endpoints; fixed stale unit test; fixed docstring bug; Phase 3 is now MOSTLY CLOSED
- 🧪 Tests: `TestDeleteNote::test_success` fixed and passing (1 pass); tasks_api pre-existing failures confirmed unrelated (UUID validation, not our changes)
- 📁 Files: 8 files changed — REMEDIATIONS-003.md (created), spec.md, plan.md, tasks.md (spec edits), api/tasks.py (410 stubs), schemas/common.py (ENDPOINT_GONE), services/note_service.py (docstring), tests/unit/api/test_notes_api.py (test fix)
- 🔁 Next prompts: Implement Task 3.7d voice note pipeline wiring in `create_note()`; fix `limits.py FREE_TIER_DAILY_CREDITS = 0 → 10`; write Task 7.1 contract tests for notes; implement Task 4.3a DB-backed AI counters
- 🧠 Reflection: The most impactful quick wins were the 410 stubs (closes a real API contract gap) and the stale test fix (restores test green for notes delete). Task 3.7d (voice pipeline wiring) is the highest-value open item — it's the only truly incomplete Phase 3 subtask.

## Evaluation notes (flywheel)

- Failure modes observed: String-not-found errors when editing spec/tasks due to whitespace differences — mitigated by grepping first to see exact text before editing
- Graders run and results (PASS/FAIL): `TestDeleteNote::test_success` PASS (after fix); task api failures pre-existing XFAIL-equivalent
- Prompt variant (if applicable): post-sp.analyze remediation session (follow-up to session 057)
- Next experiment (smallest change to try): Fix `limits.py FREE_TIER_DAILY_CREDITS = 0 → 10` as a minimal one-line change with immediate spec alignment
