---
id: 009
title: Apply SPEC_UPDATES to spec.md
stage: spec
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.specify update 002 spec as per @SPEC_UPDATES.md (only those with location `spec.md`)
labels: ["spec-update","notes-standalone","ai-model","gap-numbering","tdd-deviation","version-control"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
tests:
  - none (documentation-only change)
---

## Prompt

update 002 spec as per @SPEC_UPDATES.md (only those with location `spec.md`)

ask me for further clarifications without assuming things yourself

## Response snapshot

Applied 11 updates (UPDATE-01 through UPDATE-11 and UPDATE-14) from SPEC_UPDATES.md to specs/002-perpetua-frontend/spec.md. Asked 3 targeted clarifications before editing:

1. BUG-07 row in Gap 4 table → user chose: remove entirely
2. Journey 1 step numbering (7 vs 8 steps) → user chose: 7 steps total (SPEC_UPDATES numbering was a typo)
3. Deviation Record heading format → user chose: match existing bold-text style (no §X.N prefix)

Changes applied:
- UPDATE-01: Added `// No task_id` comment to FR-005 Note Schema
- UPDATE-02: Reversed notes from task-scoped to standalone `/api/v1/notes`; updated Appendix A note rows; removed BUG-07 from Gap 4 table
- UPDATE-03+14: Added Deviation Record section to §X; added V1 Test Status Note to Appendix D
- UPDATE-04: Added Implementation Status Note to §VII.P0 above Gap 1
- UPDATE-05: Marked Gap 1 as resolved (T110), with pending T134 verification note
- UPDATE-06: Renumbered duplicate P1/P2 Gap 4 → Gap 5 through Gap 9 → Gap 10
- UPDATE-07: Updated Version Control block to 1.2.0 planned / 1.1.0 current / 1.0.0 previous; standardized header to `1.1.0`
- UPDATE-08: Fixed API.md path (removed `contracts/` prefix)
- UPDATE-09: Fixed Journey 1 step 7 to "Sees streak increment to Day 1" + milestone note
- UPDATE-10: Replaced GPT-4/Anthropic fallback with OpenAI Agents SDK + `AI_MODEL_ID` env var on all 3 AI endpoints
- UPDATE-11: Added Credit limit configuration block with `FREE_TIER_AI_CREDITS`, `PRO_TIER_AI_CREDITS`, `AI_CREDIT_RESET_HOUR` env vars

Skipped (not spec.md targets): UPDATE-12 (tasks.md), UPDATE-13 (plan.md), UPDATE-14 tasks.md portion.

## Outcome

- ✅ Impact: spec.md updated from v1.1.0 to v1.2.0-planned; 11 spec updates applied; FR-005 now correctly reflects standalone notes architecture; AI model is env-configurable; TDD deviation documented; gap numbering fixed
- 🧪 Tests: n/a (documentation change only)
- 📁 Files: specs/002-perpetua-frontend/spec.md
- 🔁 Next prompts: `/sp.specify` or `/sp.tasks` to apply UPDATE-12 (tasks.md T136-T138), UPDATE-13 (plan.md routes), UPDATE-14 (tasks.md header)
- 🧠 Reflection: Asking clarifications before editing prevented 3 incorrect assumptions (BUG-07 disposition, step count, heading style). The SPEC_UPDATES.md document was detailed enough that only edge cases needed user input.

## Evaluation notes (flywheel)

- Failure modes observed: Step numbering ambiguity in UPDATE-09 (off-by-one in proposed change); BUG-07 row was orphaned by the architectural reversal
- Graders run and results (PASS/FAIL): grep verification PASS — all target strings present/absent as expected
- Prompt variant (if applicable): n/a
- Next experiment: Consider adding explicit "affected downstream rows" notes in SPEC_UPDATES for architectural reversals
