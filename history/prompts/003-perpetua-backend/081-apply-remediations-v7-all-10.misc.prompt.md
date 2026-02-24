---
id: 081
title: Apply REMEDIATIONS-003-v7 all 10 fixes
stage: misc
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: architext
command: /sp.specify apply those proposed remediations in @REMEDIATIONS-003-v7.md for specs in @specs/003-perpetua-backend/spec.md
labels: ["remediations","spec-update","api-docs","tasks","plan"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/docs/API.md
  - specs/003-perpetua-backend/spec.md
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/tasks.md
tests:
  - none (doc-only changes)
---

## Prompt

apply those proposed remediations in @REMEDIATIONS-003-v7.md for specs in @specs/003-perpetua-backend/spec.md

## Response snapshot

Applied all 10 remediations from REMEDIATIONS-003-v7.md (PHR-080 cross-artifact analysis) across 4 files:

**R1** (API.md): Added `DELETE /api/v1/notes/{note_id}` dedicated section with 200 response body (`deleted_id` + `tombstone_id`), tombstone pool note, and error codes (403, 404).

**R2** (API.md): Expanded the `POST /notes/{note_id}/convert` note — clarified `notes_converted` increments regardless of subsequent task creation; added error codes block (400, 402, 404, 503).

**R3** (tasks.md Task 3.7b): Closed `[ ]` BLOCKING NFR-006 item — marked `[x]` confirming API.md documents all 6 standalone note endpoints (with tombstone response + errors and convert error codes).

**R4** (tasks.md Task 4.6): Closed `[ ]` BLOCKING NFR-006 item — marked `[x]` confirming API.md documents all AI endpoints with streaming final event, confirm-action shape, and GET /ai/credits alias.

**R5** (tasks.md Task 8.4): Closed reopened `[ ]` docs item — marked `[x]` confirming Tasks 3.7b and 4.6 blocking items resolved (2026-02-24).

**R6** (plan.md Pattern 6 `recover_tombstone`): Added `version=1` to `TaskInstance` and `Subtask` constructor calls; added inline comments referencing spec FR-013.

**R7** (plan.md Pattern 6 `delete_task`): Added 3-tombstone-per-user FIFO eviction block before tombstone creation; uses `_get_user_tombstones()` + `min(…, key=lambda t: t.created_at)`.

**R8** (plan.md NoteService schema note): Replaced misleading "min_length=0 when voice_url present; min_length=1 otherwise" wording with authoritative phrasing: field-level always `min_length=0`; `model_validator` enforces the conditional.

**R9** (spec.md FR-012 Side Effects): Added **Stuck-pending behavior** paragraph after the voice-note transcription bullet — documents manual recovery, cites `BackgroundTasks` limitation, references Gap 2 / Phase 9 JobQueue.

**R10** (tasks.md Task 4.3): Reformatted `[ ]` TODO comment item as `PENDING CODE CHANGE` with fenced Python block showing the exact two-line comment to add; preserves `[ ]` status since the code change is still outstanding.

## Outcome

- ✅ Impact: 14 findings from PHR-080 → 10 actionable doc/spec remediations all applied; API.md now has full DELETE /notes and convert error-code coverage; tasks.md blocking items resolved; plan.md code examples corrected; spec.md stuck-pending edge case documented
- 🧪 Tests: none (doc-only changes; no code modified)
- 📁 Files: backend/docs/API.md, specs/003-perpetua-backend/spec.md, specs/003-perpetua-backend/plan.md, specs/003-perpetua-backend/tasks.md
- 🔁 Next prompts: /sp.implement Task 4.2a (subscription renewal), Task 6.2 M7 (notification pruning), Task 5.5 [ ] items (focus auto-stop), Task 7.1 [ ] items (7 unit tests), Task 4.3 TODO comment (code-level, 2 lines)
- 🧠 Reflection: All remediations were applied in dependency order (R1 → R2 → R3 → R4 → R5 for tasks that depend on prior API.md edits). No new NEEDS CLARIFICATION markers introduced. plan.md code examples now match spec + tasks evidence.

## Evaluation notes (flywheel)

- Failure modes observed: none — all 10 edits had clear, unambiguous old/new string targets
- Graders run and results (PASS/FAIL): n/a (doc changes)
- Prompt variant (if applicable): null
- Next experiment: run /sp.analyze again after implementing Task 4.2a + 6.2 M7 to confirm remaining open gaps
