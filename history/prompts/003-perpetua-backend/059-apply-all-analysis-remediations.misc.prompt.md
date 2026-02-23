---
id: 059
title: Apply All Analysis Remediations
stage: misc
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: manual
labels: ["remediation","spec","plan","tasks","analysis","cross-artifact"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/tasks.md
tests:
  - n/a (doc-only changes)
---

## Prompt

i wold like you to apply remediation edits for all issues in thier respective files (spec.md, plan.md, tasks.md)

## Response snapshot

Applied all 17 findings from the `/sp.analyze 003` report as targeted edits across the three artifact files. No source code was modified — all changes are documentation and specification only.

**spec.md changes (5 edits)**:
- H4: Added `Force-Complete Response` subsection to FR-002 Outputs documenting `TaskCompletionResponse` with `unlocked_achievements: list[AchievementSummary]`
- H5 + M2: Rewrote FR-004 confirm-action Outputs to clarify `action_id` is transient (not persisted); removed orphaned `confirmed_ai_actions` table reference from Side Effects; updated Side Effects to reference Gap 5 explicitly
- M1: Changed FR-012 voice_duration_seconds output from hardcoded "1–300" to "1–MAX_AUDIO_DURATION_SECONDS (default: 300)" to align with FR-006 configurability
- M5: Changed convert endpoint HTTP code from 201 to 200; updated explanatory note

**plan.md changes (1 edit)**:
- M4: Added parenthetical "(tasks.md models the 12-week nominal estimate)" to Option 1 timeline to resolve 8-12 vs 12 week inconsistency

**tasks.md changes (11 edits)**:
- M8: Changed TDD declaration from "where applicable" to "per Constitution VIII.1"
- C1: Rewrote Phase Discipline Notice to state Phase 3 is "NOT CLOSED" with specific detail on what 3.7d is missing
- C2: Added [CRITICAL — C2] label to FREE_TIER_DAILY_CREDITS subtask and acceptance criterion in Task 3.7c
- H2: Added [H2] subtask and acceptance criterion for `GET /api/v1/notes/{note_id}` to Task 3.7b
- M5: Updated convert subtask and acceptance criterion to say HTTP 200 (not 201)
- M3: Corrected Task 5.1 seeded achievement count from "20+" to "11 achievements as defined in spec FR-008" with explicit list
- M6: Added API.md update acceptance criteria to Tasks 3.7b and 4.6
- M7: Added [M7] labels and clearer wording to notification pruning subtasks and acceptance criteria in Task 6.2
- L1: Strengthened Task 4.3 comment item with exact comment text required in ai_service.py

## Outcome

- ✅ Impact: All 17 analysis findings addressed in their respective artifact files; no unresolved placeholders remain
- 🧪 Tests: n/a (documentation-only changes)
- 📁 Files: specs/003-perpetua-backend/spec.md, plan.md, tasks.md
- 🔁 Next prompts: Run `/sp.implement` targeting C2 (limits.py fix); implement Task 3.7d (voice note pipeline); implement Task 4.2a (monthly credit renewal)
- 🧠 Reflection: All edits were minimal and targeted — no unrelated refactoring. CRITICAL findings (C1, C2) received prominence markers. Document-only remediation keeps code changes separate for explicit implementation.

## Evaluation notes (flywheel)

- Failure modes observed: One Edit failed due to exact-string mismatch (backtick rendering difference); resolved by re-reading the file section first
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.analyze again after implementing C2 to verify finding count drops
