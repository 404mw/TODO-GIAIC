---
id: 056
title: Update 003 Tasks — Apply Remediation Edits
stage: tasks
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.tasks update 003 tasks as per updated 003 plan and @remediation-tasks.md
labels: ["tasks","remediation","notes-standalone","production-blocker","phase-discipline"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - none
---

## Prompt

update 003 tasks as per updated 003 plan and @remediation-tasks.md

## Response snapshot

Applied all 16 remediations from `remediation-tasks.md` to `specs/003-perpetua-backend/tasks.md`:

- **CON1**: Added Resolution Protocol block to Phase Discipline Notice (audit → mark → implement)
- **C1**: Task 4.6a — added 🚨 PRODUCTION BLOCKER notice + Spec.md Gap 5 reference
- **C2**: Task 8.2a — added 🚨 PRODUCTION BLOCKER notice + updated retention note (≥7 days)
- **E1**: Added AUDIT REQUIRED blockquote above Task 3.7a covering all modified source files
- **F1a**: Task 3.7b NoteCreate — updated `content` to `0–2000 chars` with conditional min_length via `model_validator`
- **F1b**: Task 3.7b AC — added 2 voice-content test cases (empty+no voice_url → 400; empty+voice_url → 201)
- **F4**: Task 3.7c — marked 402 LIMIT_EXCEEDED subtask as `[x]` with plan.md + data-model.md evidence
- **F5b**: Task 6.2 AC — changed premature `✅` on prune criterion to `[ ]` with pending note
- **C5**: Task 4.3 — added `[X] Implement chat_stream()` subtask with full SSE spec
- **C5b**: Task 4.3 AC — added 2 streaming AC lines
- **C6**: Task 4.3a — added ⚠️ SCALABILITY BLOCKER notice referencing Task 7.4 and NFR-004
- **E2**: Regeneration Checklist — fixed FR count from 15 to 16 (FR-001–FR-016)
- **E3**: Task 6.1 AC — added Constitution V.2 AI logging AC (actor, task_id, timestamp, credits_used, action_type)
- **E4**: Task 7.1 — added 2 subscription credit carryover test subtasks
- **D1**: Task 4.7 — added Acceptance Criteria for shared `CreditService.get_balance()` across both credit endpoints
- **F2a**: Removed Task 4.2a block from Phase 4 (replaced with placeholder note)
- **F2b**: Inserted Task 4.2a (Monthly Subscription Credit Renewal) into Phase 5 after Task 5.6, with 🚨 PRODUCTION BLOCKER notice

## Outcome

- ✅ Impact: tasks.md now accurately reflects plan v1.2 and remediation-tasks.md findings; all 16 issues addressed
- 🧪 Tests: no tests run (doc-only change)
- 📁 Files: specs/003-perpetua-backend/tasks.md
- 🔁 Next prompts: audit Tasks 3.7a–d against source files; implement Task 4.6a (undo mechanism); implement Task 4.2a (monthly renewal)
- 🧠 Reflection: All CRITICAL and HIGH priority remediations applied cleanly. F2a/F2b (phase migration) required careful anchor matching to avoid replacing wrong block.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): audit Tasks 3.7a–d against modified source files and close open [ ] items
