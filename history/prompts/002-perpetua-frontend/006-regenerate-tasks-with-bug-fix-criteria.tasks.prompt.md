---
id: 006
title: Regenerate Tasks With Bug Fix Criteria
stage: tasks
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.plan
labels: ["tasks", "bug-fix", "api-contract", "spec-v1.1", "findings"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/tasks.md
tests:
  - "Manual verification: Phase 14 acceptance criteria per FINDINGS.md"
---

## Prompt

feature: 002
detailed findings: @FINDINGS.md

user prompt:
regenerate tasks.md with the updated requirements as acceptance criteria.

## Response snapshot

Regenerated `specs/002-perpetua-frontend/tasks.md` (v2) based on `spec.md` v1.1 and `FINDINGS.md`. Key changes:

1. **Phases 1–13**: Retained all 121 existing tasks with [X] marks. Updated task descriptions for affected tasks (T036, T038, T039, T050, T058, T063, T071, T072, T074, T087, T088, T090) to embed the correct API contracts and acceptance criteria from spec.md v1.1.

2. **Phase 14 (NEW — Bug Fix Sprint)**: Added 14 new tasks (T122–T135) ordered by FINDINGS.md severity:
   - **CRITICAL**: T122 (BUG-01A guard subtask fetch), T123 (BUG-06A force-complete endpoint), T124 (BUG-06B version field), T125 (BUG-07 notes task-scoped endpoints)
   - **HIGH**: T126 (BUG-06C wire reminder API), T127 (BUG-08 subscription endpoint)
   - **MEDIUM**: T128 (BUG-05 notifications page), T129 (mark-as-read endpoint), T130 (BUG-02 cache key), T131 (BUG-04 mobile modal)
   - **LOW**: T132 (BUG-01B listener guard), T133 (BUG-03 mobile bar)
   - **SECURITY**: T134 (S-01 HttpOnly cookies), T135 (S-03 console.log removal)

Each Phase 14 task includes: file reference, code-level fix instructions, and checkboxed acceptance criteria traceable to spec.md v1.1 FR/NFR references and FINDINGS.md bug IDs.

Total task count updated from 121 → 135 tasks across 14 phases.

## Outcome

- ✅ Impact: tasks.md now serves as the canonical implementation checklist for the Bug Fix Sprint; every FINDINGS.md issue is captured as a testable, traceable task with explicit acceptance criteria
- 🧪 Tests: Each Phase 14 task has inline acceptance criteria checkboxes ([ ]) derived from spec.md v1.1 requirements
- 📁 Files: specs/002-perpetua-frontend/tasks.md (overwritten)
- 🔁 Next prompts: `/sp.implement` to execute Phase 14 bug fixes; or `/sp.adr` for HttpOnly cookie migration (architectural decision)
- 🧠 Reflection: Existing tasks (Phases 1–13) descriptions were updated in place to embed the correct contracts — this preserves the done/not-done status while making the specification the single source of truth for what "done" means

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): sp.plan invoked for task regeneration (tasks stage)
- Next experiment: run `/sp.implement` targeting Phase 14 tasks in priority order
