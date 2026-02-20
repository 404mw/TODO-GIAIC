---
id: 014
title: Apply Remediation Edits from sp.analyze
stage: misc
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: (follow-up to /sp.analyze 002 — PHR 013)
labels: ["remediation", "spec-update", "tasks-update", "accessibility", "constitution", "ai-logging"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
  - specs/002-perpetua-frontend/tasks.md
tests:
  - (none — spec/task document edits only)
---

## Prompt

yep please

(User approved all proposed remediation edits from PHR 013's sp.analyze findings. Applied all 6 issue fixes: C1, C2, C3, H1, H2, H3.)

## Response snapshot

Applied 11 concrete edits across spec.md and tasks.md to resolve the top 6 findings from PHR 013:

**tasks.md changes:**
- T065 updated: added `localStorage` tick-write for focus crash recovery (H2 fix)
- Phase 13: added T157–T159 (NFR-003 accessibility — jest-axe, ARIA audit, keyboard nav test) (C1 fix)
- Phase 15: added T160 (Constitution §V AI interaction event logging) (C2 fix)
- Phase 16: added T161–T166 (Phase 14 bug-fix test tasks for T123, T124, T122+T130, T126, T127, T129) (C3 fix)
- Notes section: fixed MSW/jest.fn() contradiction (H3 fix); updated total task count 156 → 166

**spec.md changes:**
- Version bumped: 1.1.0 → 1.2.0 with updated changelog
- FR-004 success criterion fixed: "browser crash" → "browser reload from localStorage" (H2 fix)
- FR-009: added AI Logging Requirement block + success criteria (C2 fix)
- §V Non-Goals: added item 7 (offline-first mutation queue deferred) (H1 fix)
- §VII Gap 2: marked as RESOLVED (T111) (M2 fix from analysis — bonus)
- §X footer: version + date updated

**Result:** 0 critical constitutional violations remain in spec/tasks. 10 new tasks added (T157–T166). NFR-003 now has 3 dedicated tasks. Phase 14 all 14 bug-fixes now have corresponding test tasks.

## Outcome

- ✅ Impact: Resolved all 3 CRITICAL constitutional violations; addressed 3 HIGH issues; fixed 1 MEDIUM bonus; total task count 156 → 166
- 🧪 Tests: T157–T159 (axe-core/a11y), T161–T166 (Phase 14 regression tests) added as open tasks
- 📁 Files: specs/002-perpetua-frontend/spec.md (v1.2.0), specs/002-perpetua-frontend/tasks.md (166 tasks)
- 🔁 Next prompts: /sp.implement (Phase 14 is now unblocked — all acceptance criteria have test tasks); /sp.specify to add FR-014 (Onboarding Tour) if desired
- 🧠 Reflection: The Phase 14 test gap (C3) is a common failure mode for bug-fix sprints — acceptance criteria get written but test tasks are not added to Phase 16. Future sp.tasks runs should auto-generate a test stub for every bug-fix task.

## Evaluation notes (flywheel)

- Failure modes observed: Constitution §V AI Logging was missing from both spec and tasks — a silent omission rather than an override. Suggests sp.analyze should check for constitution §V compliance as a default pass.
- Graders run and results (PASS/FAIL): N/A (document edits)
- Prompt variant (if applicable): follow-up to PHR 013
- Next experiment (smallest change to try): Run /sp.implement for Phase 14 — T122 (subtask guard) and T123 (force-complete fix) are highest priority
