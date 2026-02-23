---
id: 069
title: Update tasks v1.2 REMEDIATIONS-003-v3
stage: tasks
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.tasks update 003 tasks as per updated 003 plan and attached file
labels: ["tasks", "remediations", "v3", "phase-7", "api-docs", "blockers"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - null
---

## Prompt

update 003 tasks as per updated 003 plan and attached file

## Response snapshot

Updated `specs/003-perpetua-backend/tasks.md` v1.2 applying REMEDIATIONS-003-v3.md changes:

**C3 (CRITICAL)** — Regeneration Checklist and Phase 7 corrections:
- Version header: `REMEDIATIONS-003-v2.md` → `REMEDIATIONS-003-v3.md`
- Phase Discipline Notice: updated current phase status block to reflect v3 analysis; expanded blockers section with C1 CRITICAL detail (API.md stale for both notes and AI endpoints)
- Phase 7 header: added `⚠️ INCOMPLETE — see open [ ] items below`
- Regeneration Checklist: `[X] 1044 tests passing` → `[ ] 1044 tests passing — PENDING` with explanation of 7 unit tests (Task 7.1) and 2 scalability tests (Task 7.4) still `[ ]`

**H3 observation** — TODO comment not yet in `ai_service.py` near `_task_request_counters`; item remains `[ ]` in Task 4.3 (no change needed — already tracked).

**No-change items** (already applied or in other files):
- H4/H5/M4 (data-model.md) — already updated in prior session
- M2/M3/L1-L4 (spec.md) — already updated in prior session (PHR-067)
- H1/H2 (implementation tasks 4.2a, 4.3a) — code work, not spec text

## Outcome

- ✅ Impact: tasks.md now accurately reflects v3 analysis; Phase 7 correctly marked INCOMPLETE; blockers expanded with C1 context; Regeneration Checklist test item demoted to [ ] per Constitution II.1
- 🧪 Tests: no tests run (documentation-only change)
- 📁 Files: specs/003-perpetua-backend/tasks.md
- 🔁 Next prompts: implement H3 (add TODO comment to ai_service.py); implement C1 (update backend/docs/API.md for notes and AI endpoints); implement H1 (Task 4.2a monthly subscription renewal); implement H2 (Task 4.3a AI session counter DB)
- 🧠 Reflection: data-model.md and spec.md were already updated by PHR-067, so v3 changes to tasks.md were minimal (header, phase status, Phase 7 marker, checklist). The key insight is that C3 prevents Phase 7 from being checked off while Tasks 7.1 and 7.4 have open items.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): implement H3 (1-line TODO comment in ai_service.py) to unblock Task 4.3a
