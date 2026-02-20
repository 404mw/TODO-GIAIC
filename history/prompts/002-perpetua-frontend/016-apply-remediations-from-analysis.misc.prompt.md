---
id: "016"
title: Apply Remediations from sp.analyze
stage: misc
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: apply remediations from sp.analyze 002
labels: ["remediation", "tdd", "nfr-004", "constitution", "consistency"]
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
  - none (artifact edits only)
---

## Prompt

dont just suggest but apply remediations. and for FINDINGS.md, that file wasnt supposed to stay so keep everything but remove the reference.

## Response snapshot

Applied all critical, high, and medium remediations across spec.md, plan.md, and tasks.md:

**tasks.md changes:**
- H1: Updated prerequisites header from `spec v1.1` → `spec v1.2.0`
- C1 (TDD): Inserted RED test tasks (T161–T166) immediately before their paired GREEN implementation tasks in Phase 14 — Red→Green pairs now in correct Constitution §VIII order
- C2/H4: Added T167–T170 (NFR-004 autosave + form-persist gap): T167/T168 (debounced 5s autosave in TaskDetailView), T169/T170 (TaskForm draft localStorage persistence)
- U5: Added T135/T138 coordination note + expanded T135 scope to include auth.service.ts
- Replaced "Phase 14 Bug-Fix Tests" subsection in Phase 16 with a pointer note (tests now co-located in Phase 14)
- Updated total count: 166 → 170 tasks
- Updated Phase 14 execution order table to show RED/GREEN pairs

**plan.md changes:**
- C3: Corrected §IX Constitution §V from "N/A" to ✅ with FR-009 + T160 evidence
- H2: Added §IX entries for NFR-003 (a11y), offline-first scope (DEFERRED), updated §III for NFR-004 gap tasks
- I1: Completed focus-mode.store.ts definition in §3B (added pausedAt, elapsedSeconds, pause(), resume(), localStorage persistence note)
- L1: Removed "(FINDINGS.md v2026-02-18)" from §XI header — kept all content
- Updated §VIII Testing Doctrine to reflect Phase 14 TDD restructuring
- Updated plan version: 1.2.0 → 1.3.0

**spec.md changes:**
- H3/I2: Added [DEFERRED] marker to NFR-005 "Network reconnect syncs queued actions" success criterion
- H3/I2: Added [DEFERRED] marker to §VI system-wide CRUD offline functional criterion
- Updated spec version: 1.2.0 → 1.3.0

## Outcome

- ✅ Impact: All 3 CRITICAL issues resolved; all 4 HIGH issues addressed; I1, U5, L1 MEDIUM/LOW issues applied
- 🧪 Tests: No tests run (artifact edits); T167–T170 add 4 new test+impl tasks for NFR-004
- 📁 Files: spec.md v1.3.0, plan.md v1.3.0, tasks.md updated (170 tasks)
- 🔁 Next prompts: Run /sp.implement — all critical blockers resolved; no CRITICAL issues remain
- 🧠 Reflection: The TDD restructuring (C1) required inserting 6 RED tasks into Phase 14 before their GREEN counterparts and replacing the Phase 16 "Phase 14 Bug-Fix Tests" section with a pointer. The FINDINGS.md reference was cleanly removed from the §XI header while preserving all defect content.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): direct remediation follow-up to PHR 015
- Next experiment: Verify Phase 14 TDD pairs by running sp.analyze again after implementation begins
