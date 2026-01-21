---
id: 001
title: Apply Tasks Remediations from Analysis
stage: tasks
date: 2026-01-21
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: developer
command: /sp.tasks
labels: [remediation, tasks, spec-sync, plan-sync]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - n/a (task documentation only)
---

## Prompt

@003-analysis2.md

spec and plan remediations has been applied. mirror then in feature tasks in addition to applying suggested tasks remediations.

## Response snapshot

Applied all remediations from the `/sp.analyze 003` report to tasks.md:

**Spec Remediations Mirrored:**
- SPEC-R1: FR-035 session-scoped counter (already covered in T224, T225)
- SPEC-R2: FR-069a/b API deprecation headers → T402b, T402c
- SPEC-R3: US9 AS4 achievement notification → T305a, T305b

**Plan Remediations Mirrored:**
- PLAN-R1: Audio format requirements → T273a, T273b + checkpoint reference
- PLAN-R2: RefreshToken storage → T078 reference to plan.md AD-001

**Task Remediations Applied:**
- TASK-R1 (HIGH): T078a, T078b, T078c - User profile endpoint (FR-070)
- TASK-R2 (HIGH): T402b, T402c - API versioning validation
- TASK-R3 (HIGH): T305a, T305b - Achievement notification
- TASK-R4 (MEDIUM): T358a, T358b, T358c - Push token storage
- TASK-R5 (MEDIUM): T273a, T273b - WebSocket timeout validation
- TASK-R6 (LOW): Task count updated to 433
- TASK-R7 (LOW): WebSocket filename already aligned

**Summary:**
- Total new tasks added: 12
- Total tasks: 421 → 433
- FR coverage: 69 → 71 (FR-070, FR-069a, FR-069b)
- Checkpoints updated: 3, 13, 19

## Outcome

- ✅ Impact: All analysis remediations now reflected in tasks.md with full traceability
- 🧪 Tests: No code tests (documentation task), validation via grep confirmed all 12 tasks present
- 📁 Files: 1 file modified (specs/003-perpetua-backend/tasks.md)
- 🔁 Next prompts: /sp.implement or manual task execution
- 🧠 Reflection: Remediation changelog added to tasks.md provides audit trail for changes

## Evaluation notes (flywheel)

- Failure modes observed: None - all edits applied cleanly
- Graders run and results (PASS/FAIL): Manual grep validation PASS - all 12 new tasks found
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Consider automating remediation application via skill
