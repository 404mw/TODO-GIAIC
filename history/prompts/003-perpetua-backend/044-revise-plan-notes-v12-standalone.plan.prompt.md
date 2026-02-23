---
id: 044
title: Revise Plan Notes v1.2 Standalone
stage: plan
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.plan
labels: ["plan", "notes", "standalone", "api-revamp", "data-model", "limits"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/data-model.md
tests:
  - N/A (plan artifact — no tests run)
---

## Prompt

003

revise plan as per updated spec and update Note model, remove task_id FK, update database schema per Section B of @ANALYSIS_REVAMP_003.md

## Response snapshot

Ran `/sp.plan 003` with instruction to revise plan per spec v1.2 (Notes standalone
redesign) and Section B of ANALYSIS_REVAMP_003.md.

**Codebase analysis findings:**

- `backend/src/models/note.py`: Note model already standalone (no task_id FK, has user_id,
  archived, voice fields). Model matches spec v1.2 — no code change needed here.
- `backend/src/models/user.py`: Already has `notes: list["Note"] = Relationship(back_populates="user")`.
- `backend/src/models/task.py`: No notes relationship (already clean).
- **Gap 1**: `lib/limits.py` has `FREE_TIER_NOTE_LIMIT=10, PRO_TIER_NOTE_LIMIT=25` — spec v1.2 requires 20/50.
- **Gap 2**: `schemas/note.py` NoteUpdate missing `archived: bool | None` field — spec says PATCH supports archived.
- **Gap 3**: `note_service.py` update_note() doesn't handle archived field.
- **Gap 4**: No 410 Gone routes for deprecated `POST/GET /tasks/{task_id}/notes`.
- **Gap 5**: NoteLimitExceededError should map to 402 (verify existing handler).

**Artifacts produced:**

1. `specs/003-perpetua-backend/plan.md` — Comprehensive plan with all 9 architecture layers,
   v1.1→v1.2 delta section with 5 explicit code changes, constitution check, risk analysis.
2. `specs/003-perpetua-backend/data-model.md` — Entity definitions for Note v1.2, migration
   checklist, state transitions, tombstone backward compatibility notes.

**Key decisions documented:**
- No DB migration needed (task_id was never in deployed baseline)
- Note limits updated to 20/50 (code change in limits.py)
- NoteUpdate extended with `archived` field; guard: block content update on already-archived note
- Convert endpoint remains "suggestion" flow (user confirms before task creation) per Constitution IV.2
- 410 Gone routes for deprecated task-scoped endpoints

## Outcome

- ✅ Impact: plan.md updated with spec v1.2 Note model; 5 code changes identified and documented
- 🧪 Tests: No tests run (plan artifact)
- 📁 Files: specs/003-perpetua-backend/plan.md, specs/003-perpetua-backend/data-model.md
- 🔁 Next prompts: `/sp.tasks 003` to update tasks.md replacing Task 3.7 with 3.7a/b/c; then `/sp.implement 003`
- 🧠 Reflection: Note model was already fully migrated in code — analysis confirmed spec and code aligned on data model. Only limits.py constants and schema/service/API gaps remain.

## Evaluation notes (flywheel)

- Failure modes observed: None — codebase already partially aligned with spec v1.2
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Update limits.py constants and run existing note tests to see failures
