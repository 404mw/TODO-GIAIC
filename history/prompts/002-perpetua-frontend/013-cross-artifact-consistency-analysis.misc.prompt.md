---
id: 013
title: Cross-Artifact Consistency Analysis (sp.analyze 002)
stage: misc
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.analyze 002
labels: ["analysis", "consistency", "constitution", "coverage", "quality-gate"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
  - specs/002-perpetua-frontend/plan.md
  - specs/002-perpetua-frontend/tasks.md
  - .specify/memory/constitution.md
tests:
  - (none — read-only analysis run)
---

## Prompt

002

(Invoked via /sp.analyze skill with feature argument "002", targeting specs/002-perpetua-frontend/)

## Response snapshot

Ran full cross-artifact consistency analysis across spec.md (v1.1.0), plan.md (v1.2.0), tasks.md (156 tasks, Phases 1–16), and constitution.md (v1.0.0).

**15 findings total** (3 CRITICAL, 3 HIGH, 5 MEDIUM, 4 LOW):

**CRITICAL:**
- C1: NFR-003 Accessibility has ZERO task coverage — no axe-core CI, screen-reader, or a11y audit tasks exist despite clear spec success criteria.
- C2: Constitution §V AI Logging violated — no task implements mandatory AI interaction event logging (task_id, timestamp, actor) required by FR-009 and constitution.
- C3: Constitution §VIII TDD violated — Phase 14 bug-fix tasks T122–T135 all lack corresponding test tasks in Phase 16.

**HIGH:**
- H1: NFR-005 Reliability offline support (IndexedDB queue, circuit breaker, reconnect sync) has near-zero task coverage.
- H2: FR-004 "Focus time persisted even if browser crashes" is untestable — Zustand is in-memory only; no localStorage tick-write task exists.
- H3: tasks.md Phase 16 contains direct contradiction on MSW test strategy (jest.fn() vs MSW network-level).

**MEDIUM:** spec version drift (L1/M4), spec §VII gap tracker stale (M2), voice notes silently unimplemented (M3), onboarding tour lacks backing FR (M5), NFR-001 Lighthouse/CLS measurement gaps (M1).

**LOW:** Version header in spec (L1), CSRF note not in T134 AC (L2), T050/T124 ownership overlap (L3), AI credit mock values (L4).

**Coverage metrics:**
- FRs: 13/13 = 100% covered
- NFRs: 6/7 = 86% (NFR-003 = 0%)
- Overall: 19/20 = 95%
- Constitution alignment: 2 CRITICAL violations (§V AI Logging, §VIII TDD for Phase 14)

**Recommended next steps before /sp.implement:**
1. Add NFR-003 accessibility tasks via /sp.tasks
2. Add AI logging requirement to spec.md + Phase 15 task
3. Add Phase 14 test tasks to Phase 16

## Outcome

- ✅ Impact: Identified 3 blocking constitutional violations and 6 coverage/consistency gaps before implementation begins; prevents shipping without a11y coverage or Phase 14 test regressions
- 🧪 Tests: none (read-only analysis)
- 📁 Files: none modified (read-only analysis)
- 🔁 Next prompts: /sp.specify (add FR-014 onboarding, AI logging), /sp.tasks (Phase 14 tests, NFR-003), /sp.adr offline-first-architecture
- 🧠 Reflection: NFR-003 accessibility gap is consistently the most overlooked category in reverse-engineered frontends; should be a default checklist item in future sp.analyze runs.

## Evaluation notes (flywheel)

- Failure modes observed: Voice Notes (Pro) feature silently unimplemented in tasks despite schema presence; onboarding tour lacks FR backing
- Graders run and results (PASS/FAIL): N/A (analysis only)
- Prompt variant (if applicable): sp.analyze 002 (first formal run post v1.2 plan update)
- Next experiment (smallest change to try): Add NFR-003 tasks first — it's a constitution compliance gate
