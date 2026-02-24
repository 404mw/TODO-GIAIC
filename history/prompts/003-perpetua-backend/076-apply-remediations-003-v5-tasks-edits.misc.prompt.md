---
id: "076"
title: Apply REMEDIATIONS-003-v5 tasks edits
stage: misc
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: "@REMEDIATIONS-003-v5.md now work on 2 (tasks.md) not 3 (API.md) yet"
labels: ["tasks", "remediation", "documentation", "notifications", "deployment", "blockers"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - none
---

## Prompt

@REMEDIATIONS-003-v5.md 
now work on 2 (tasks.md) not 3 (API.md) yet

## Response snapshot

Applied all Section 2 tasks.md edits from REMEDIATIONS-003-v5.md. Skipped [H1] (no change needed per remediation file) and [M1] (already applied in previous session as a spec reflection).

Four edits were applied to `specs/003-perpetua-backend/tasks.md`:

1. **[H3] Overview open blockers (~L35)**: Expanded Task 4.2a and 4.3a descriptions with production impact notes; added Task 6.2 M7 notification pruning as a new blocker entry.

2. **[C2] Phase 8 heading (~L1700)**: Marked heading "⚠️ PROVISIONAL" with a warning blockquote citing Constitution II.1 and upstream open items, signaling the phase depends on unresolved decisions.

3. **[M3] Task 8.4 Acceptance Criteria (~L1807)**: Changed the passing "✅ API docs complete and accurate" criterion to a `[ ]` REOPENED state with cross-references to Tasks 3.7b and 4.6.

4. **[M2] Task 6.2 Acceptance Criteria (~L1512)**: Replaced the single [M7] placeholder item with two explicit BLOCKING items — `prune_old_notifications()` implementation and its scheduling — both tagged `[BLOCKING — FR-016 MUST]`.

## Outcome

- Impact: tasks.md updated with 4 remediation edits improving accuracy of open blockers, provisional phase warnings, and acceptance criteria for notification pruning and API docs
- Tests: none run — documentation-only changes
- Files: specs/003-perpetua-backend/tasks.md (modified)
- Next prompts: Apply Section 3 (API.md) edits from REMEDIATIONS-003-v5.md
- Reflection: Skipped [H1] (no-op per remediation) and [M1] (already applied); all remaining Section 2 items successfully landed with minimal diff

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): proceed to Section 3 API.md edits from REMEDIATIONS-003-v5.md
