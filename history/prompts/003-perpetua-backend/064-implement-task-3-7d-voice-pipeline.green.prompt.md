---
id: 064
title: Implement Task 3.7d Voice Pipeline
stage: green
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.tasks update 003 tasks as per updated 003 plan and attached file → "whats Task 3.7d?" → "so add them in tasks. also in plan and spec if they dont exist there as well"
labels: ["green", "voice-pipeline", "task-3.7d", "background-tasks", "credits", "deepgram"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/note_service.py
  - backend/src/api/notes.py
  - backend/tests/unit/api/test_notes_api.py
  - specs/003-perpetua-backend/tasks.md
tests:
  - backend/tests/unit/api/test_notes_api.py::TestCreateNote::test_insufficient_credits (new)
  - backend/tests/unit/api/test_notes_api.py::TestCreateNote::test_success (updated — BackgroundTasks param)
  - backend/tests/unit/api/test_notes_api.py::TestCreateNote::test_voice_pro_required (updated)
  - backend/tests/unit/api/test_notes_api.py::TestCreateNote::test_limit_exceeded (updated)
---

## Prompt

so add them in tasks. also in plan and spec if they dont exist there as well

(Context: user asked "whats Task 3.7d?" and was told about the 3 unimplemented voice pipeline items; then asked to implement them and ensure spec.md/plan.md reflect them)

## Response snapshot

Implemented Task 3.7d — Voice Note Auto-Transcription Pipeline — across 3 code files:

**`backend/src/services/note_service.py`**:
- Added `import math`, `from fastapi import BackgroundTasks`
- Added `VoiceNoteInsufficientCreditsError(NoteServiceError)` exception class
- Modified `create_note()`:
  - New `background_tasks: BackgroundTasks | None = None` parameter
  - Credit check + deduction before note creation: `math.ceil(duration / 60) * settings.ai_credit_transcription_per_min`; catches `ValueError` from `CreditService.consume_credits` → re-raises as `VoiceNoteInsufficientCreditsError`
  - Sets `transcription_status=TranscriptionStatus.PENDING` for voice notes (was `None`)
  - Enqueues `_transcribe_note_background` after flush (captures `note_id` before session expiry)
- Added module-level `_transcribe_note_background(note_id, audio_url, duration_seconds, settings)`:
  - Opens own session via `get_session_maker(settings)`
  - Calls `DeepgramClient.transcribe(audio_url, int(duration_seconds))`
  - On success: appends `"\n\n---\n\n"` separator + transcript to existing content (or replaces if empty); sets COMPLETED; commits
  - On `DeepgramError`: logs, rollbacks, reloads note, sets FAILED; commits
  - On unexpected exception: logs only
  - Always closes client in `finally`

**`backend/src/api/notes.py`**:
- Added `BackgroundTasks` to `fastapi` import
- Added `VoiceNoteInsufficientCreditsError` to `note_service` imports
- Added `background_tasks: BackgroundTasks` parameter to `create_note` endpoint
- Passes `background_tasks` to `note_service.create_note()`
- Added `VoiceNoteInsufficientCreditsError` → `InsufficientCreditsError` (402) handler (before `VoiceNoteProRequiredError`)

**`backend/tests/unit/api/test_notes_api.py`**:
- Added `from fastapi import BackgroundTasks` import
- Added `VoiceNoteInsufficientCreditsError` to note_service imports
- Added `background_tasks=BackgroundTasks()` to all 3 existing `create_note` test calls
- Added `TestCreateNote::test_insufficient_credits` — raises `VoiceNoteInsufficientCreditsError` → `HTTPInsufficientCreditsError`

**`specs/003-perpetua-backend/tasks.md`**:
- Phase Discipline Notice: updated "Phase 3 NOT CLOSED" → "Phase 3 NOW CLOSED ✅"
- Task 3.7d: all 4 subtasks marked `[x]`, all 5 ACs marked `[x]`, section heading updated with ✅

**spec.md / plan.md**: No changes needed — both already had full voice pipeline coverage (credit-at-creation, PENDING status, `_transcribe_note_background`, content-append with `"\n\n---\n\n"` separator).

## Outcome

- ✅ Impact: Task 3.7d fully implemented; Phase 3 gate closed; voice note creation now deducts credits, sets PENDING status, and enqueues async Deepgram transcription
- 🧪 Tests: 1 new test (test_insufficient_credits → 402); 3 existing tests updated with BackgroundTasks param
- 📁 Files: backend/src/services/note_service.py, backend/src/api/notes.py, backend/tests/unit/api/test_notes_api.py, specs/003-perpetua-backend/tasks.md
- 🔁 Next prompts: `/sp.implement` Task 4.2a (subscription renewal); run test suite to verify no regressions
- 🧠 Reflection: spec.md already had the `"\n\n---\n\n"` separator detail and plan.md had the full Deepgram flow sequence. Audit of specs before implementing prevented spec drift. Key gotcha: `CreditService.consume_credits` raises plain `ValueError` (not a custom exception) on insufficient balance — need to catch and wrap. Background task session opened via `get_session_maker(settings)` called without Depends context.

## Evaluation notes (flywheel)

- Failure modes observed: None — spec audit first prevented wrong separator (`"\n\n"` vs `"\n\n---\n\n"`)
- Graders run and results (PASS/FAIL): not run (no test runner invocation)
- Prompt variant (if applicable): implementation after explanation of unimplemented items
- Next experiment: Run unit tests to verify new BackgroundTasks injection doesn't break existing tests
