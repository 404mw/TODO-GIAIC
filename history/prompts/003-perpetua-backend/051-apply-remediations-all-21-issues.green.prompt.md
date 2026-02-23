---
id: 051
title: Apply Remediations All 21 Issues
stage: green
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: apply remediation edits for all issues (follow-up to /sp.analyze 003)
labels: ["remediation","spec","plan","tasks","constitution","notes-v1.2","undo","ai-governance"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/tasks.md
tests:
  - none (documentation changes only)
---

## Prompt

suggest concrete remediation edits for all issues
[follow-up]: update the original files instead

## Response snapshot

Applied all 21 remediation edits across spec.md, plan.md, and tasks.md in-place.

**spec.md (13 edits)**:
- C3: Added `confirm-action` endpoint contract + success criteria to FR-004
- M4: Added voice note pending content state definition to FR-012 Inputs
- L3: Added 201 semantics note to convert endpoint in FR-012
- H2: Added voice note credit deduction rule to FR-012 Side Effects, Error Codes, Success Criteria
- H5: Added AI Interaction event type to FR-014 Logged Events (with Constitution V.2 fields)
- H3: Removed "inferred" from NFR-001 performance targets → "contractual"
- M7: Replaced vague "approach pro limits" with numeric effective limits (455 tasks, 20 daily AI credits)
- M6: Changed "confidence > 0.85 typical" → "p50 > 0.85" in FR-006
- M1: Renamed duplicate Gap 5 → Gap 6 (test coverage) and Gap 6 → Gap 7 (subscription payment)
- L4: Clarified ai/credits as alias with no duplicate logic in FR-007

**plan.md (2 edits)**:
- H1: Fixed DELETE /notes status 204 → 200 in Layer 6 endpoints table
- H1: Added Change 5a block with correct 200 + {deleted_id, tombstone_id} response implementation

**tasks.md (11 edits)**:
- L2: Updated header date to 2026-02-22
- H1: Fixed Task 3.7b DELETE acceptance criteria to include tombstone_id
- H1: Fixed Task 3.7b subtask DELETE response to include tombstone_id
- H6: Task 4.3 deferred item now references Task 4.3a (not open-ended)
- H6: Added new Task 4.3a (multi-process AI session counters via DB)
- C1+H4: Added new Task 4.6a (AI action undo — Constitution III.4 compliance)
- M5: Task 4.2a now has dependency note on Task 5.6; uses Subscription.current_period_end
- M2: Added notification pruning subtasks + criteria to Task 6.2
- M3: Added new Task 8.2a (automated DB backups — Constitution III.2 compliance)
- M8: Added scalability test subtasks + criteria to Task 7.4
- L1: Fixed Regeneration Checklist test count to 1044/843/201/150
- C2: Re-marked all Phase 9 Improvement tasks as [ ] with NOT IMPLEMENTED warnings

## Outcome

- ✅ Impact: All 21 findings from PHR-050 (/sp.analyze 003) addressed in original artifact files
- 🧪 Tests: none (documentation-only changes)
- 📁 Files: spec.md, plan.md, tasks.md updated in-place
- 🔁 Next prompts: Run /sp.implement to execute tasks; or run /sp.analyze again to verify clean
- 🧠 Reflection: The most impactful changes are Task 4.6a (undo) and Task 4.3a (counter persistence) — these add real implementation requirements. Phase 9 false-completion fix is important for accurate progress tracking.

## Evaluation notes (flywheel)

- Failure modes observed: L4 fix was initially targeted at plan.md but the ai/credits reference was in spec.md FR-007 — corrected mid-session
- Graders run and results (PASS/FAIL): None automated
- Prompt variant (if applicable): Follow-up to PHR-050
- Next experiment: Run /sp.analyze 003 again to confirm zero remaining findings
