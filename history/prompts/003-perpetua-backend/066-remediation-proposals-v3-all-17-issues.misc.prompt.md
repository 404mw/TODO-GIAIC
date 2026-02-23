---
id: "066"
title: Remediation Proposals v3 All 17 Issues
stage: misc
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: propose all remediation edits for specs, plan and tasks in a separate md file at the project root
labels: ["remediation", "spec", "plan", "tasks", "api-docs", "data-model", "proposals"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - REMEDIATIONS-003-v3.md
tests:
  - null
---

## Prompt

propose all remediation edits for specs, plan and tasks in a separate md file at the project root

## Response snapshot

Created `REMEDIATIONS-003-v3.md` at project root covering all 17 issues from PHR-065
analysis (sp.analyze 003).

Structure:
- 3 CRITICAL: C1 (API.md Notes section stale — 5 sub-edits + streaming/confirm-action fixes),
  C2 (spec.md test count math error), C3 (tasks.md Phase 7 checklist incorrectly marked done)
- 5 HIGH: H1 (Task 4.2a production blocker — implementation), H2 (Task 4.3a scalability
  blocker — implementation), H3 (TODO comment in ai_service.py prerequisite), H4 (data-model.md
  stale migration checklist), H5 (content constraint missing voice_url exception)
- 5 MEDIUM: M1 (7 unit tests unwritten), M2 (DELETE /notes response missing tombstone_id),
  M3 (notes_converted naming vs trigger), M4 (data-model.md incomplete entity coverage),
  M5 (spec "may prune" vs task mandatory)
- 4 LOW: L1–L4 (performance targets qualifier, SSE format, GET /notes/{id} archived,
  GET /notes default filter)

Each issue has exact OLD → NEW diff blocks with file paths and line numbers.
Also audited backend/docs/API.md directly and found 5 additional sub-issues under C1:
stale Notes section (old task-scoped endpoints), streaming chat missing final event format,
confirm-action request body shape mismatch, /ai/credits response shape divergence from
/credits/balance, and missing DELETE /notifications/{id}.

Summary table at end groups issues by effort: 13 trivial-effort + 4 high-effort items.

## Outcome

- ✅ Impact: Created REMEDIATIONS-003-v3.md with all 17 proposed edits. No source files modified.
- 🧪 Tests: None run (proposal-only pass)
- 📁 Files: Created REMEDIATIONS-003-v3.md; read backend/docs/API.md to audit C1 sub-issues
- 🔁 Next prompts: User reviews and approves remediation file; apply trivial items in single
  pass; schedule H1/H2 implementation tasks
- 🧠 Reflection: The API.md audit revealed C1 had more depth than initially surfaced in the
  analysis — 5 sub-issues total within the Notes + AI section. Most high-value fixes are
  trivial (13/17 are 1-3 line text changes). The two implementation blockers (H1, H2) are the
  critical path for production readiness.

## Evaluation notes (flywheel)

- Failure modes observed: C2 (test count math error) was partially resolved in current v1.2
  files; the error may exist only in an intermediate version. Provided a verification grep
  command rather than assuming it still needs fixing.
- Graders run and results (PASS/FAIL): N/A — proposal document only
- Prompt variant (if applicable): Follow-up to PHR-065 analysis
- Next experiment: Apply all trivial-effort remediations (13 items) in a single pass and
  re-run sp.analyze to verify issue count drops to 4
