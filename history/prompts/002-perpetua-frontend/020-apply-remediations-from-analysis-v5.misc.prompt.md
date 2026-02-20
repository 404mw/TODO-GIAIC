---
id: 020
title: Apply Remediations From Analysis v5
stage: misc
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.analyze (remediation application)
labels: ["remediation","spec","plan","tasks","sp.analyze","v5"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
  - specs/002-perpetua-frontend/plan.md
  - specs/002-perpetua-frontend/tasks.md
tests:
  - none (documentation updates only)
---

## Prompt

I would you like me to apply remediations for these findings. ask me for further clarifications

(User confirmed: apply all findings H+M+L; infer template paths from codebase; add T177 as new task; add spec note for M6 — no constitution amendment)

## Response snapshot

Applied all 13 sp.analyze v5 findings across spec.md, plan.md, and tasks.md.

### spec.md → v1.5.0
- H1: Added template endpoints (GET/POST /templates, POST /templates/{id}/instantiate, PATCH/DELETE /templates/{id}) to Appendix A; noted PATCH/DELETE are inferred from FR-007 pending API.md confirmation
- M3: Added env-absent startup-block requirement to FR-009 AI credit limits section
- M6: Added Constitution §V alignment note clarifying entity_id = task_id|note_id
- L3: Added cross-reference note in §VIII pointing to plan.md §VII as authoritative regeneration guide
- L5: Added edge case to FR-007 for backend failing to generate next recurring instance

### plan.md → v1.5.0
- L1: Fixed stale "Next version: 1.3.0" → "1.6.0 (after T134 + Phase 14 closed)"
- L4: Added notification.schema.ts to Layer 4 schema organization list

### tasks.md (177 tasks)
- H1 (also): T099 path corrected from `/api/v1/task-templates` → `/api/v1/templates` per API.md
- H2: T112 inserted at priority 0 in Phase 14 execution order table; T171 added at priority 2
- M1: T171 removed from Phase 9, inserted into Phase 14 Medium section before T174/T128
- M2: T175/T176 removed from Phase 13 "structurally complete" section; moved to Phase 15 with NFR-001 header
- M4: T177 (route transition measurement via router.events + performance.measure) added to Phase 15
- M5: T138 dependency note added to Phase 15 preamble ("depends T135 — do NOT begin T138 until T135 verified done")
- L2: T057 wording fixed ("Create" → "Update ... (created in T038)")
- Version notes, total count (176→177), reclassification notes updated throughout

## Outcome

- ✅ Impact: All 13 findings remediated; spec v1.5.0, plan v1.5.0, tasks v1.5.0; T112 now has explicit Phase 14 execution slot; T171 co-located with its consumers; T175/T176 phase-disciplined into Phase 15; T177 new measurement task; T099 path corrected
- 🧪 Tests: No tests run (documentation/planning updates only)
- 📁 Files: spec.md (7 edits), plan.md (4 edits), tasks.md (9 edits)
- 🔁 Next prompts: /sp.implement — all blockers resolved; Phase 14 execution order is now unambiguous
- 🧠 Reflection: Key catch this pass was T099 using `/task-templates` vs confirmed `/templates` in API.md — a subtle but breaking API contract bug that would have caused 404s on the templates tab. Also caught that T138 was marked [P] alongside T136/T137 despite having an ordering dependency on T135.

## Evaluation notes (flywheel)

- Failure modes observed: Cross-file path drift (T099 vs API.md); phase discipline violations from retroactive task additions
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): sp.analyze v5 remediation
- Next experiment: Run sp.analyze v6 after Phase 14 implementation to verify bug-fix tasks close their spec acceptance criteria
