---
id: "079"
title: "remediation edits v6 all 21 issues"
stage: misc
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: suggest concrete remediation edits for spec.md, plan.md, tasks.md and API.md in a new .md file at the project root
labels: ["remediations","spec","plan","tasks","api-docs","constitution","003"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - REMEDIATIONS-003-v6.md
tests:
  - null
---

## Prompt

suggest concrete remediation edits for spec.md, plan.md, tasks.md and API.md in a new .md file at the project root

## Response snapshot

Created `REMEDIATIONS-003-v6.md` at project root.

Covers all 21 findings from PHR-078 analysis across 4 files:

**C2 (API.md — 5 sub-edits):**
- C2a: Streaming final event: `suggested_action` → `suggested_actions` (plural); remove `text` field from final event
- C2b: confirm-action request shape: align with spec FR-004 (`action_type` + `task_id` + `data` top-level, no `confirmation_token`); fix error codes to match spec taxonomy
- C2c: GET /ai/credits response: unify field names to match GET /credits/balance (`daily_credits` → `daily`, etc.)
- C2d: Add missing GET /notes and GET /notes/{id} response schemas
- C2e: Update API.md version to 1.1.0 and last-updated date

**C3 (spec.md):** FR-007 subscription renewal ✅ → ⏸; Acceptance Test 2 steps 5-6 marked pending
**C4 (spec.md):** Add FR-016 pruning criterion as ⏸ pending Task 6.2 M7
**C5 (spec.md):** FR-009 auto-stop criterion split into ✅ (manual stop) + ⏸ (auto-stop pending Task 5.5)
**H1 (constitution.md):** Ratify V.2 transcription null-task_id exception with formal amendment block
**H3 (plan.md):** Fix notification pruning background job caption from "Implemented" to "Partially Implemented — pending M7"
**M1 (spec.md):** focus_duration validation range + behavior clarification
**M2 (spec.md):** FR-013 tombstone limit scope — shared cross-entity pool
**M3 (spec.md):** FR-007 Pro→Free downgrade behavior for subscription credits
**M4 (spec.md):** FR-016 reminder_fired type marked as Phase 9
**M5 (spec.md):** FR-013 version reset applies to all VersionedModel entities
**L1-L6 (spec.md + plan.md):** Due date clarification, action_id usage, model_validator note, soft→tombstone rename, notes_converted cross-ref

## Outcome

- ✅ Impact: REMEDIATIONS-003-v6.md created with exact OLD/NEW text blocks for all 21 findings; organized by priority; includes application order and code-required callouts
- 🧪 Tests: None (documentation file only)
- 📁 Files: REMEDIATIONS-003-v6.md (created)
- 🔁 Next prompts: Apply edits to each artifact, then re-run /sp.analyze 003 to verify zero CRITICAL findings
- 🧠 Reflection: Key insight from analysis — API.md confirm-action shape discrepancy (confirmation_token in API.md vs action_type+task_id+data in spec) requires implementation verification before blind apply; flagged with ⚠️ in file.

## Evaluation notes (flywheel)

- Failure modes observed: REMEDIATIONS-003-v5.md was listed as untracked in git status but didn't exist on disk; treated as not present and created v6
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment: Apply C2 (API.md) first as it's lowest effort + highest compliance impact, then C5 + H3 (trivial status fixes)
