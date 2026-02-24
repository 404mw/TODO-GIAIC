---
id: "071"
title: Remediation file all 15 issues
stage: misc
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: "suggest concrete remediation edits for all issues as a .md file at the project root"
labels: ["remediation", "docs", "spec", "tasks", "api", "misc"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - REMEDIATIONS-003-v4.md
tests:
  - "none (read-only analysis + doc creation)"
---

## Prompt

suggest concrete remediation edits for all issues as a .md file at the project root

## Response snapshot

Created `REMEDIATIONS-003-v4.md` at the project root containing concrete remediation edits
for all 15 issues found in PHR-070 (/sp.analyze 003).

Key remediations included:
- C1: Full standalone Notes section replacement for `backend/docs/API.md` (all 6 endpoints + 2 x 410 stubs)
- C2: Three targeted AI section fixes in `backend/docs/API.md` (SSE format, confirm-action request body, GET /ai/credits response shape)
- C3: `renew_subscription_credits()` pseudocode for `credit_service.py` + 3 unit tests
- C4: `prune_old_notifications()` pseudocode + scheduler registration
- C5: `AISessionCounter` model + `_increment_and_check_counter()` pseudocode
- H1/H2/H3: Exact find-replace text for spec FR-013, FR-014, and Task 6.1 acceptance criteria
- M1-M4, L1-L3: Find-replace edits for spec/plan/tasks/code

Recommended application order: text fixes (H/M/L) first, then docs (C1/C2), then code (C3/C4/C5), then tests (M1).

## Outcome

- ✅ Impact: All 15 issues from PHR-070 have concrete, actionable remediation edits
- 🧪 Tests: None run; file is read-only analysis output
- 📁 Files: REMEDIATIONS-003-v4.md created at project root
- 🔁 Next prompts: Apply text remediations (H1-H3, M2-M4, L1-L3) first; then apply C1/C2 API.md updates; then implement C3/C4/C5 code changes; mark Task 7.1 items [x] as tests pass
- 🧠 Reflection: For API.md doc corrections, always read the current state first (grep for section headers, read specific sections) before writing replacement content — avoids guessing field names or response shapes that differ from spec.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment: Apply H1+H2+H3 atomically first as a fast-feedback loop; verify no new inconsistencies introduced before proceeding to larger changes
