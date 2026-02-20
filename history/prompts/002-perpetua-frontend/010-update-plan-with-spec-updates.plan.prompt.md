---
id: "010"
title: Update plan.md with SPEC_UPDATES findings
stage: plan
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.plan update 002 plan as per updated spec and findings in @SPEC_UPDATES.md (plan only). ask me for further clarification each question must have one recommended option
labels: ["plan-update","notes-standalone","routes","tdd-deviation","api-contract"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/plan.md
tests:
  - none
---

## Prompt

update 002 plan as per updated spec and findings in @SPEC_UPDATES.md (plan only).

ask me for further clarification each question must have one recommended option

## Response snapshot

Updated `specs/002-perpetua-frontend/plan.md` from v1.1.0 → v1.2.0 applying 7 targeted changes derived from SPEC_UPDATES.md:

1. **Header/version** — bumped to 1.2.0, date 2026-02-19
2. **§II.Layer1 routes** (UPDATE-13) — added 6 missing protected routes: `/dashboard/tasks/new`, `/dashboard/tasks/completed`, `/dashboard/tasks/[id]/edit`, `/dashboard/notifications`, `/dashboard/settings/hidden-tasks`, `/dashboard/settings/archived-notes`
3. **§3A useNotes hook** (UPDATE-02) — rewrote from task-scoped to standalone architecture (`GET/POST /api/v1/notes`, added `useDeleteNote`, `useArchiveNote`, updated `useConvertNote`)
4. **§XI.1 violations table** (UPDATE-02) — removed C-03/C-04 (no longer violations; standalone notes is now correct design); added architecture note explaining the change; T125 scope reduced to PATCH-only fix (C-05)
5. **§VIII Tech Debt item 2** (UPDATE-05) — marked "Service Worker Token Management" as RESOLVED by T110; added pending note about T134 superseding it
6. **§IX.VIII Testing Doctrine** (UPDATE-03) — changed from ✅ Fully compliant to ⚠️ Partially compliant; documented V1 test existence/non-mapping as deviation per spec.md §X.5
7. **Footer version control** — updated to 1.2.0 with full version history

All 4 clarification questions answered by user with recommended options.

## Outcome

- ✅ Impact: plan.md now accurately reflects standalone notes architecture, 6 previously-undocumented routes, resolved SW token gap, and acknowledged TDD deviation
- 🧪 Tests: none (documentation-only change)
- 📁 Files: specs/002-perpetua-frontend/plan.md
- 🔁 Next prompts: Apply SPEC_UPDATES to spec.md (UPDATE-01 through UPDATE-14); run /sp.tasks to add T136-T138 for NFR-006 observability
- 🧠 Reflection: Clarifying questions before edits prevented incorrect removal of C-05 from violations table and ensured version alignment (1.2.0 vs 1.1.0)

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment: Apply same update workflow to spec.md using SPEC_UPDATES UPDATE-01 through UPDATE-14
