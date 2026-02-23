---
id: "054"
title: Apply spec remediations and API docs NFR
stage: spec
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.specify update 003 as per @remediation-spec.md
labels: ["spec","remediation","notes","fr-012","fr-007","nfr","api-docs"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
tests:
  - none
---

## Prompt

update 003 as per @remediation-spec.md and include that all api endpoints updates/changes should be documented in @backend/docs/API.md

## Response snapshot

Applied all 6 remediations from `remediation-spec.md` to `specs/003-perpetua-backend/spec.md` and added a new NFR-006:

**F1 Edit 1a** — FR-012 Inputs: changed `content` from `string (1–2000 chars, required)` to
`string (0–2000 chars)` with three sub-bullets documenting the conditional validation rule
(`min_length=0` when `voice_url` set; `min_length=1` otherwise).

**F1 Edit 1b** — FR-012 Success Criteria: inserted two new testable ACs:
- `POST /api/v1/notes` with `content=""` and no `voice_url` → 400 VALIDATION_ERROR
- `POST /api/v1/notes` with `content=""` and valid `voice_url` (Pro) → 201 Created

**B3 Edit B3a** — Non-Functional Success Criteria: fixed test count from
`(843 unit, 201 integration, 150 contract)` to `(843 unit + 201 integration; ~150 of the
integration tests are schema contract tests run via schemathesis)`.

**B3 Edit B3b** — Metadata footer: same fix applied to `**Test Coverage**` line.

**F6 Edit F6a** — FR-012 Error Codes: added design-note blockquote under `402 LIMIT_EXCEEDED`
explaining the intentional 402 (notes) vs 409 (tasks) split.

**F6 Edit F6b** — FR-007 Error Code Note: replaced the verbose paragraph with a one-line
cross-reference to FR-012 Error Codes.

**NFR-006** — New section "API Documentation Standards" added after NFR-005 (Observability):
all endpoint additions/modifications must be reflected in `backend/docs/API.md` as part of
the same change. Includes coverage requirements for new, modified, deprecated, and removed
endpoints plus two success criteria.

## Outcome

- ✅ Impact: spec.md v1.2 now consistent with remediation-spec.md findings; content validation rule is unambiguous; test count math correct; 402/409 design note co-located with the relevant error code; API doc standard is formally captured as NFR-006
- 🧪 Tests: none run (spec-only update)
- 📁 Files: specs/003-perpetua-backend/spec.md
- 🔁 Next prompts: update plan.md and tasks.md to reference NFR-006 and the FR-012 conditional validation rule; ensure note_service and note schema implement `min_length` conditionally
- 🧠 Reflection: All remediations applied cleanly with exact FIND/REPLACE matches; no collateral edits needed

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): run /sp.analyze after plan/tasks updates to verify no new drift
