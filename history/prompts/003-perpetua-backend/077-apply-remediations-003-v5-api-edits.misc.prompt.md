---
id: 077
title: Apply REMEDIATIONS-003-v5 API.md edits
stage: misc
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: "now to 3 (API.md)"
labels: ["api-docs", "remediation", "notes", "ai", "streaming", "credits"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/docs/API.md
tests:
  - none
---

## Prompt

now to 3 (API.md)

(followed by user "resume" to continue after C1a was applied)

## Response snapshot

Applied all 4 Section 3 (API.md) edits from REMEDIATIONS-003-v5.md.

- [C1a] ~L1319: Replaced stale Notes section (task-scoped stub) with full standalone Notes v1.2 documentation covering all 6 endpoints (POST/GET/GET{id}/PATCH/DELETE/convert), deprecation notices for 410 Gone endpoints, request/response shapes, and error codes.
- [C1b] ~L1035: Fixed AI Chat Streaming SSE format — replaced bare `data:` frames and `data: [DONE]` with proper `event: chunk` / `event: final` structure; documented `suggested_action` field and `ai_request_warning`.
- [C1c] ~L1156: Fixed Confirm AI Action — added required `confirmation_token` field to request; documented token semantics (single-use, must match pending action); corrected response from `DataResponse` to `TaskCompletionResponse` (`{"task": {...}}`); enriched supported actions table with `action_data` shapes; added error codes.
- [C1d] ~L1204: Fixed GET /ai/credits response schema — replaced nested `balance` object with flat `CreditBalanceResponse` fields (`daily_credits`, `subscription_credits`, `purchased_credits`, `kickstart_credits`, `total_credits`); added `kickstart_credits` field.

## Outcome

- Impact: API.md now accurately documents Notes v1.2 standalone endpoints, correct SSE streaming format with event types, correct confirmation token semantics for AI actions, and flat credit balance schema — all aligned with the implemented backend.
- Tests: none run
- Files: backend/docs/API.md (4 sections updated: Notes docs, AI Chat SSE, Confirm AI Action, AI Credits)
- Next prompts: Verify all REMEDIATIONS-003-v5.md edits are complete; cross-artifact analysis to confirm no remaining inconsistencies.
- Reflection: The edits were applied incrementally (C1a first, then resume for C1b–C1d), which allowed checkpoint verification before continuing. The Notes section replacement was the largest change, requiring full 6-endpoint coverage including 410 Gone deprecation notices.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Run cross-artifact analysis to confirm API.md is now fully aligned with spec and tasks after all v5 remediations.
