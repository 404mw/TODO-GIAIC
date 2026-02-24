---
id: "075"
title: Apply REMEDIATIONS-003-v5 spec edits
stage: misc
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: architext
command: apply REMEDIATIONS-003-v5.md section 1 (spec.md) and reflect into plan.md and tasks.md
labels: ["spec", "remediation", "documentation", "focus-mode", "performance", "nfr"]
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
  - none
---

## Prompt

@REMEDIATIONS-003-v5.md 
work on 1 (spec.md). no 2 (tasks.md) and 3 (API.md) yet. and all spec updates must be reflected in plan.md and tasks.md if they arent there already.

## Response snapshot

Applied all 4 spec.md edits from REMEDIATIONS-003-v5.md Section 1, then reflected each spec change into plan.md and tasks.md where not already present.

**spec.md changes (4 edits):**
- [H1] Changed test-count success criterion from ✅ to `[ ] PENDING` — the 1044-test count is aspirational, not yet met
- [M1] Added `FOCUS_SESSION_TIMEOUT_MINUTES` Configuration block to FR-009 Inputs; fixed Success Criteria to reference the env var instead of a hardcoded value
- [M4] Added `gamification/audit p95 < 300ms` target to NFR-001 performance table
- [M5] Clarified in FR-014 activity log that `task_id` is nullable (permitted null for transcription events not tied to a specific task)

**plan.md changes (reflecting M1 and M4):**
- [M1] Added FocusService section documenting `FOCUS_SESSION_TIMEOUT_MINUTES` env var with default, validation, and usage notes
- [M4] Updated Quality Gates performance targets line to include `gamification/audit p95 < 300ms`

**tasks.md changes (reflecting M1 and M4):**
- [M1] Added `[ ]` subtask under Task 5.5 to assert `FOCUS_SESSION_TIMEOUT_MINUTES` is read from env and defaults to 25
- [M4] Added `gamification/audit p95 < 300ms` to Task 7.4 acceptance criteria and Phase 8 quality standards section

## Outcome

- Impact: 4 spec remediations from REMEDIATIONS-003-v5.md Section 1 applied; changes propagated into plan.md and tasks.md for full cross-artifact consistency
- Tests: none run — documentation-only edits with no code changes
- Files: specs/003-perpetua-backend/spec.md, specs/003-perpetua-backend/plan.md, specs/003-perpetua-backend/tasks.md
- Next prompts: work on Section 2 (tasks.md) and Section 3 (API.md) from REMEDIATIONS-003-v5.md
- Reflection: Spec-to-plan-to-tasks propagation worked cleanly; M5 (nullable task_id) was already implicit in the data model and required only a clarifying sentence in spec.md, no plan/tasks change needed

## Evaluation notes (flywheel)

- Failure modes observed: none — all 4 edits were precise and localized with no unintended side effects
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): run cross-artifact analysis after Section 2 and 3 remediations to verify no new gaps introduced
