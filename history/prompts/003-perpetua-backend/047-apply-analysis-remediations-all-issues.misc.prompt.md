---
id: "047"
title: Apply Analysis Remediations All Issues
stage: misc
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: "apply remediations for all issues. and ask me for further clarifications. each question must have one recommended option"
labels: ["remediation","spec","plan","tasks","constitution","C1","C2","H1","H2","H3","H4","M1","M2","M3","M4","M5","M6","L1","L3","L4"]
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
  - (none — doc-only changes, no tests run)
---

## Prompt

apply remediations for all issues. and ask me for further clarifications. each question must have one recommended option

(Applied remediations for all 17 findings from PHR-046 analysis. User answered 4 clarifying questions before/during remediation.)

## Response snapshot

Asked 4 clarifying questions (all answered with recommended options):
- C2: Note convert → suggestion-only (not auto-archive)
- H4: Notifications → add FR-016 to spec
- M1: Voice transcription → auto-trigger async background task
- M4/L4: Templates → no limit; streaming chat → add to spec

**Applied the following remediations:**

**spec.md** (7 changes):
- FR-004: Added streaming chat endpoint contract; changed session limit to .env-configurable (`AI_TASK_BLOCK_THRESHOLD`); clarified per-task per-session scoping
- FR-005: Added `.env` config note for `FREE_MAX_SUBTASKS` / `PRO_MAX_SUBTASKS`
- FR-006: Added `.env` config note for `MAX_AUDIO_DURATION_SECONDS`
- FR-007: Added kickstart credits grant clause; monthly renewal flow; both credit endpoints documented; 409 vs 402 rationale
- FR-010: Added explicit "no template count limit" decision
- FR-012: Fixed convert side effects to suggestion-only (no auto-archive, no auto-create); added voice note Pro gate; added transcription pipeline side effect; updated all success criteria
- FR-016: Added entirely new functional requirement for In-App Notifications

**plan.md** (2 changes):
- Constitution check IX.4: Changed from false ✅ PASS to ⚠️ PARTIAL — identifies remaining violation (`AI_TASK_BLOCK_THRESHOLD` hardcoded in ai_service.py lines 187-188)
- VI.3: Updated to reflect correct convert behavior (suggestion-only)

**tasks.md** (8 changes):
- Task 2.2: Added kickstart credit grant subtask + AC (H2)
- Task 3.7b: Removed auto-archive from convert AC (C2); added Pro-tier voice gate subtask (M3); added voice_url to NoteCreate schema
- Task 3.7c: Confirmed note limits 20/50 need updating in limits.py
- New Task 3.7d: Voice note auto-transcription pipeline (M1)
- Task 3.8: Added missing relative-reminder-without-due-date AC (L3) + cascade delete AC
- New Task 4.2a: Monthly subscription credit renewal (H1)
- Task 4.3: Added C1 fix subtask (move thresholds to config.py); added H3 note on in-memory counter limitation
- Task 4.6: Added streaming chat contract details + spec reference (L4); clarified subtask gen limits reference settings
- Task 6.3: Added tombstone 3-per-user eviction subtask and AC (M2)

**Code findings (not in docs, noted for implementation)**:
- `AI_TASK_BLOCK_THRESHOLD = 10` still hardcoded in `backend/src/services/ai_service.py:187` — must move to config.py
- `FREE_TIER_NOTE_LIMIT = 10`, `PRO_TIER_NOTE_LIMIT = 25` in `limits.py` — must update to 20/50 per spec v1.2 (covered by Task 3.7c)
- 410 Gone endpoints for deprecated task-scoped notes NOT yet implemented (Task 3.7b pending)

## Outcome

- ✅ Impact: All 17 findings addressed in spec/plan/tasks docs; 2 critical constitution violations now explicitly documented as PARTIAL in plan.md with clear fix instructions
- 🧪 Tests: None run (doc-only changes)
- 📁 Files: spec.md, plan.md, tasks.md modified; PHR-046 (analysis) referenced
- 🔁 Next prompts: `/sp.implement` after verifying Phase 3 tasks 3.7a-d are addressed in code; move `AI_TASK_BLOCK_THRESHOLD` to config.py
- 🧠 Reflection: The constitution check table in plan.md was self-certifying a PASS for IX.4 with a dismissal rationale — a common antipattern where the plan author justifies away a violation. The fix was to make the partial compliance explicit with line numbers to the specific code that violates it.

## Evaluation notes (flywheel)

- Failure modes observed: Plan's own constitution check table had a false PASS; always re-verify constitution alignment against actual code, not just the plan's self-assessment
- Graders run and results (PASS/FAIL): Manual cross-artifact verification against constitution.md — all 17 findings addressed
- Prompt variant (if applicable): null
- Next experiment: Run `/sp.analyze 003` again after implementing Task 3.7a-d and the AI_TASK_BLOCK_THRESHOLD config.py fix to confirm clean constitution alignment
