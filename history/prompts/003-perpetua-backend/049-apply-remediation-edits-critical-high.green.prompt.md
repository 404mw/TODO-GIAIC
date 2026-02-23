---
id: "049"
title: Apply Remediation Edits — CRITICAL + HIGH Findings
stage: green
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: apply remediation edits
labels: ["remediation","notes","auth","ai-limits","tombstone","config","kickstart-credits","spec-sync"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/config.py
  - backend/src/services/ai_service.py
  - backend/src/services/auth_service.py
  - backend/src/services/note_service.py
  - backend/src/api/notes.py
  - backend/src/lib/limits.py
  - backend/src/schemas/note.py
  - specs/003-perpetua-backend/spec.md
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/tasks.md
  - specs/003-perpetua-backend/data-model.md
tests:
  - tests/unit/services/test_note_service.py (run, 9 pre-existing failures unrelated to changes)
  - tests/unit/services/test_ai_service.py (run, all pass)
  - tests/unit/services/test_auth_service.py (run, 1 pre-existing failure; regression fixed)
---

## Prompt

apply remediation edits

(Context: All 10 CRITICAL + HIGH findings from PHR #048 cross-artifact analysis of spec v1.2 post-revamp. User confirmed scope "All 10 (CRITICAL + HIGH)".)

## Response snapshot

Applied all CRITICAL and HIGH remediation edits across 8 code files and 4 spec artifacts.

**D1 — Constitution IX.4: AI thresholds moved to config**
- `config.py`: Added `ai_task_warning_threshold: int = Field(default=5)` and `ai_task_block_threshold: int = Field(default=10)` as Pydantic Settings fields
- `ai_service.py`: Removed hardcoded class attributes `AI_TASK_WARNING_THRESHOLD = 5` and `AI_TASK_BLOCK_THRESHOLD = 10`; updated `chat()` references to `self.settings.*`

**E1 — Kickstart credits (FR-007) wired into auth flow**
- `auth_service.py`: `create_or_update_user` returns `User` (public API preserved); `authenticate_with_google` pre-checks user existence then calls `credit_service.grant_kickstart_credits(user.id)` for new users

**C1+C2 — Note DELETE tombstone + FIFO limit enforcement (FR-013)**
- `note_service.py`: `delete_note()` now creates `DeletionTombstone(entity_type=NOTE)` and calls `_enforce_tombstone_limit()` before deletion; new `_enforce_tombstone_limit()` uses FIFO strategy (delete oldest when count >= MAX_TOMBSTONES_PER_USER)
- `schemas/note.py`: `NoteUpdate` gains `archived: bool | None` field
- `note_service.py`: `update_note()` blocks only content edits on archived notes (not unarchive toggle)
- `api/notes.py`: DELETE endpoint returns HTTP 200 `{"deleted_id": ..., "tombstone_id": ...}` instead of 204
- `limits.py`: `FREE_TIER_NOTE_LIMIT = 20`, `PRO_TIER_NOTE_LIMIT = 50` (v1.2 values)

**Artifact fixes (F1, F2, F4, F5, B2, D2, D3)**
- `plan.md`: Layer 8 trigger corrected to convert-call-time; hedging language removed from Change 4
- `tasks.md`: Phase discipline notice added; Task 7.1 test description corrected; H2/H3/C1/M2 marked complete
- `spec.md`: Gap 5 (Constitution III.4 AI undo violation) documented; B2 unarchive criterion and tombstone_id added
- `data-model.md`: Content limit history corrected; migration checklist items marked complete

**Regression fix**: Initial implementation of `create_or_update_user` returning `Tuple[User, bool]` broke 2 existing tests. Fixed by preserving the `User`-only return type and using a pre-existence query in `authenticate_with_google` instead.

## Outcome

- ✅ Impact: All 10 CRITICAL/HIGH findings from analysis #048 addressed; 0 new regressions introduced
- 🧪 Tests: 56 pass, 10 fail (all 10 pre-existing — SQLite returns enum fields as plain strings; `user.tier.value` fails on `str` object)
- 📁 Files: 8 backend source files + 4 spec artifacts modified
- 🔁 Next prompts: E2 (monthly credit renewal Task 4.2a), E3 (voice transcription pipeline Task 3.7d), note recovery endpoint (Task 6.3), fix pre-existing SQLite enum test failures
- 🧠 Reflection: Changing a method's return type from scalar to tuple breaks callers — always check all call sites including tests before changing public API signatures

## Evaluation notes (flywheel)

- Failure modes observed: Tuple return type change broke unit tests that call the public method directly; caught by running tests immediately after implementing
- Graders run and results (PASS/FAIL): unit tests — 56 PASS, 10 FAIL (pre-existing)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Fix pre-existing SQLite enum failures by normalizing `user.tier` to `UserTier` enum in conftest test_user fixture or by using `.value` defensively in service layer
