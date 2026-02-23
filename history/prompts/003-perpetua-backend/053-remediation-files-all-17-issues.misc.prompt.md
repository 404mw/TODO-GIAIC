---
id: "053"
title: Remediation Files All 17 Issues
stage: misc
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: suggest concrete remediation edits for all issues in separate files (specs, plan and tasks) at the project root
labels: ["remediation", "cross-artifact", "spec", "plan", "tasks", "quality"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - remediation-spec.md
  - remediation-plan.md
  - remediation-tasks.md
tests:
  - none (documentation-only output)
---

## Prompt

suggest concrete remediation edits for all issues in separate files (specs, plan and tasks) at the project root

## Response snapshot

Created three remediation suggestion files at the project root (read-only suggestions, not applied):

**remediation-spec.md** — 3 findings (F1, B3, F6):
- F1: NoteCreate inputs block — clarify conditional min_length=0/1 rule; add 2 ACs for voice+empty content
- B3: Fix "1044 tests (843 unit, 201 integration, 150 contract)" → clarify 150 contract are subset of 201 integration; update in 2 places
- F6: Move error code split rationale from FR-007 into FR-012 Error Codes; leave cross-reference in FR-007

**remediation-plan.md** — 4 findings (F1, F3, B3, cosmetic):
- F1: Update NoteCreate schema in Layer 6 to use model_validator for conditional min_length; update error code table
- F3: Update Constitution Check IX.4 from "⚠️ PARTIAL — REQUIRES FIX" to "✅ PASS" (conditional on code verification)
- B3: Fix test count description in Technical Context block
- Cosmetic: Rename Change 5a → 5, Change 5 → 6 for logical ordering

**remediation-tasks.md** — 14 findings (CON1, C1, C2, F1, F2, C3, E1, F4, F5, C5, C6, E2, E3, E4, D1):
- CON1: Expand Phase Discipline Notice with a 3-step resolution protocol and current phase status
- C1 (4.6a): Add "🚨 PRODUCTION BLOCKER" header to Task 4.6a
- C2 (8.2a): Add "🚨 PRODUCTION BLOCKER" header to Task 8.2a
- F1 (3.7b): Update NoteCreate subtask to mention conditional min_length; add 2 voice+empty-content ACs
- F2 (4.2a): Remove Task 4.2a from Phase 4 (leave placeholder); re-insert after Task 5.6 in Phase 5 with updated subtasks and urgency note
- E1 (3.7a-d): Add audit instruction block above Task 3.7a to guide [ ] reconciliation against git-modified code
- F4 (3.7c): Mark 402 status subtask as [x] with confirmation note (aligning with plan.md Change 4 and data-model.md)
- F5 (6.2): Change prune AC from ✅ to [ ] to match incomplete subtasks
- C5 (4.3): Add streaming service subtask + 2 streaming ACs to Task 4.3
- C6 (4.3a): Add "⚠️ SCALABILITY BLOCKER" header to Task 4.3a
- E2: Fix Regeneration Checklist count "15" → "16 functional requirements (FR-001 through FR-016)"
- E3 (6.1): Add Constitution V.2 AI logging fields AC to Task 6.1
- E4 (7.1): Add 3 subscription credit carryover test subtasks to Task 7.1
- D1 (4.7): Add shared-service-method AC to Task 4.7

## Outcome

- ✅ Impact: 3 files created at project root; all 17 analysis findings have concrete FIND/REPLACE edits
- 🧪 Tests: None (suggestion files, not code)
- 📁 Files: remediation-spec.md, remediation-plan.md, remediation-tasks.md (all at project root)
- 🔁 Next prompts: User reviews and approves individual edits; apply manually or run `/sp.implement` for tasks changes
- 🧠 Reflection: F2 (Task 4.2a relocation) is the most structurally complex edit — requires a two-part change (remove from Phase 4, insert after Task 5.6 in Phase 5). CON1 and C1/C2 production blockers have the highest urgency. F3 (plan.md IX.4) is conditional — needs code verification first.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Follow-up to PHR 052 (sp.analyze)
- Next experiment (smallest change to try): Apply F4 (tasks.md 3.7c [x] marking) first as it's the lowest-risk reconciliation
