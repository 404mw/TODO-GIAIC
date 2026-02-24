---
id: 074
title: Remediation Edits v5 All Files
stage: misc
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: suggest concrete remediation edits for spec.md, plan.md, tasks.md and API.md in a new .md file at the project root
labels: ["remediation","spec","tasks","api-docs","documentation","analysis"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - REMEDIATIONS-003-v5.md (created)
  - backend/docs/API.md (read)
  - specs/003-perpetua-backend/spec.md (read)
  - specs/003-perpetua-backend/tasks.md (read)
  - specs/003-perpetua-backend/plan.md (read)
tests:
  - none (documentation only)
---

## Prompt

suggest concrete remediation edits for spec.md, plan.md, tasks.md and API.md in a new .md file at the project root

## Response snapshot

Created `REMEDIATIONS-003-v5.md` at the project root with precise FIND/REPLACE blocks for:

**spec.md (4 edits):**
- H1: Fix stale ✅ on "1044 tests passing" → `[ ]` PENDING
- M1: Add `FOCUS_SESSION_TIMEOUT_MINUTES` config key to FR-009 inputs + success criteria
- M4: Add p95 < 300ms target for gamification/audit endpoints in NFR-001
- M5: Clarify null task_id is acceptable in transcription activity log entries

**tasks.md (5 edits):**
- C2: Add ⚠️ PROVISIONAL marker to Phase 8 heading with explanation
- M3: Re-open Task 8.4 acceptance criterion for API.md regression
- H3: Expand open blockers list header with more explicit production impact descriptions
- M2: Upgrade Task 6.2 M7 items to [BLOCKING — FR-016 MUST] severity
- M1: Add FOCUS_SESSION_TIMEOUT_MINUTES subtask to Task 5.5

**backend/docs/API.md (4 section replacements):**
- C1a: Replace stale task-scoped Notes stub with all 6 standalone endpoints + 2 deprecated 410 stubs, full request/response schemas and error codes
- C1b: Fix AI Chat Streaming SSE event format — replace `data: [DONE]` with `event: chunk` / `event: final` structure + credit deduction semantics
- C1c: Fix Confirm AI Action request shape — `action_data` wrapper → flat `task_id` + `data`; add `action_id` to response; add all 5 error codes
- C1d: Fix GET /ai/credits response — `{"balance": {"daily_free": ...}}` → `{"daily": ..., "kickstart": ..., "total": ...}`; document as alias for /credits/balance

**plan.md:** No changes needed — already correct.

## Outcome

- ✅ Impact: REMEDIATIONS-003-v5.md created at project root; all edits are FIND/REPLACE blocks reviewable before application; no files modified
- 🧪 Tests: none (documentation changes)
- 📁 Files: REMEDIATIONS-003-v5.md (new, 1 file)
- 🔁 Next prompts: Apply edits from REMEDIATIONS-003-v5.md; then implement code tasks 4.2a, 4.3a, 6.2 M7 for the remaining open blockers
- 🧠 Reflection: The largest impact change is C1a (Notes section in API.md) — it adds a complete new section documenting 6 endpoints. The C1c (confirm-action shape) is the most functionally critical correction since frontend integration against the wrong schema would produce 422 errors.

## Evaluation notes (flywheel)

- Failure modes observed: None — all source content found via targeted reads; no hallucinated endpoints
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Apply C1d first (smallest change, just field name corrections) to validate the FIND/REPLACE format works cleanly
