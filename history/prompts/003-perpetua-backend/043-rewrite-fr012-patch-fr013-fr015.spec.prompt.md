---
id: 043
title: Rewrite FR-012, patch FR-013 + FR-015 per report Section A
stage: spec
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.specify
labels: ["spec", "notes", "standalone", "revamp", "fr-012", "fr-013", "fr-015"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
tests:
  - null
---

## Prompt

003

rewrite FR-012, patch FR-013 + FR-015 per report Section A

## Response snapshot

Updated `specs/003-perpetua-backend/spec.md` (v1.0 → v1.2) applying all three changes from ANALYSIS_REVAMP_003.md Section A:

**FR-012 rewritten** — "Task Notes" replaced with "User Notes (REVISED v1.2)":
- Removed `task_id` FK and `order_index` (notes are now user-owned, standalone)
- Uniform 2000-char content limit (replaced 5000 free / 10000 pro)
- Added `archived` bool, `voice_url`, `voice_duration_seconds`, `transcription_status` fields
- Full endpoint list: POST/GET /api/v1/notes, PATCH/DELETE /api/v1/notes/{id}, POST /api/v1/notes/{id}/convert
- Error code changed: 409 NOTE_LIMIT_EXCEEDED → 402 LIMIT_EXCEEDED
- Deprecated task-scoped endpoints documented as returning 410 Gone

**FR-013 patched** — Recovery system tombstone compatibility:
- Updated Notes bullet under Recoverable Entities to note standalone ownership
- Added migration note: tombstones before v1.2 may contain task_id; recovery service must tolerate (ignore) it

**FR-015 patched** — Subscription tier table:
- Note Content row: 5000/10000 → 2000/2000 (uniform)
- Added "Voice Notes" row (Free: ❌, Pro: ✅)
- Added annotation: "Notes are standalone (not task-scoped) from v1.2"

## Outcome

- ✅ Impact: All 4 CRITICAL issues (C2, C3, C4) and M2, M5 from the analysis report resolved at the spec level. Constitution II.2 ("No spec, no code") satisfied — spec now authorizes standalone notes before any code changes.
- 🧪 Tests: No tests modified (spec-only change)
- 📁 Files: specs/003-perpetua-backend/spec.md
- 🔁 Next prompts: `/sp.plan 003` — update Layer 4 Note model, database schema, and API router per Section B; then replace tasks.md Task 3.7 with 3.7a/b/c per Section C
- 🧠 Reflection: Targeted surgical edits to three FRs without disturbing other sections. Kept evidence links intact. Section A was complete enough to apply without clarification questions.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a (spec-only)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.plan 003 to propagate model/schema changes to plan.md
