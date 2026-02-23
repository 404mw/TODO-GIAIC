---
id: 068
title: Update 003 Plan v1.2 Remediations
stage: plan
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.plan update 003 plan as per updated 003 spec and attached file
labels: ["plan","notes-standalone","v1.2","remediation","data-model"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/data-model.md
tests:
  - null
---

## Prompt

update 003 plan as per updated 003 spec and attached file

## Response snapshot

Updated `specs/003-perpetua-backend/plan.md` (v1.0 → v1.2) and `specs/003-perpetua-backend/data-model.md`
to align with spec.md v1.2 (Notes standalone redesign) and all applicable REMEDIATIONS-003-v3.md items.

**plan.md changes:**
1. Header: version 1.0 → 1.2, date 2026-02-17 → 2026-02-23; source updated to spec v1.2 + remediations
2. API Layer Notes router: "Task notes" → "Standalone user notes (v1.2); deprecated endpoints → 410 Gone"
3. TaskInstance model code: removed `notes: list["Note"]` relationship; added v1.2 comment
4. Database tables: `notes: Task notes` → `notes: Standalone user notes (v1.2 — no task_id FK)`
5. Recovery snapshot code: removed `"notes"` from task snapshot; added v1.2 explanation comment
6. Service Layer Key Services: added full NoteService description (limits, voice, archived, convert)
7. AIService key functions: added convert endpoint + TODO comment about in-memory counter (Task 4.3a)
8. Module Breakdown: added NoteService section with key functions, schema notes, dependencies
9. Conclusion test count (C2): `843 unit, 201 integration, 150 contract` → `843 unit + 201 integration; ~150 schemathesis contract tests are a subset`
10. Performance targets (L1): added "single-instance" qualifier; multi-instance pending Task 4.3a + Task 7.4
11. Background jobs (M5): expanded with mandatory notification pruning (MUST, not MAY) + monthly subscription renewal (Task 4.2a) + AI session counter cleanup (Task 4.3a)

**data-model.md changes (H4 + H5 + M4):**
- H4: marked 410 Gone stub as `[x]` confirmed in `src/api/tasks.py`; remaining 3 `[ ]` items pointed to Task 7.1
- H5: `content` field constraint: `1–2000 chars` → `0–2000 chars; min 1 unless voice_url set`; constraints table updated
- M4: added scope disclaimer noting document covers v1.2 migration changes only

## Outcome

- ✅ Impact: plan.md v1.2 is now consistent with spec.md v1.2 and REMEDIATIONS-003-v3.md (trivial-effort items H4, H5, M4, C2, L1, M5 applied; background jobs section expanded for Task 4.2a)
- 🧪 Tests: no tests run (documentation-only change)
- 📁 Files: specs/003-perpetua-backend/plan.md, specs/003-perpetua-backend/data-model.md
- 🔁 Next prompts: `/sp.tasks` to update tasks.md; apply remaining high-effort remediations (C1 API.md, H1 Task 4.2a, H2 Task 4.3a, M1 unit tests)
- 🧠 Reflection: setup-plan.ps1 overwrote plan.md with template on invocation — always restore from git first before editing

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 overwrites plan.md with template; must restore from git before editing
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): run sp.tasks to propagate v1.2 task changes
