---
id: "067"
title: Apply spec remediations v3 all issues
stage: spec
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.specify update 003 spec as per attached file
labels: ["spec","remediation","notes","streaming","notifications","achievements","nfr"]
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

update 003 spec as per attached file

(Attached file: REMEDIATIONS-003-v3.md — cross-artifact analysis v3, PHR-065, 2026-02-23)

## Response snapshot

Applied all spec.md-targeted remediations from REMEDIATIONS-003-v3.md:

- **C2** (CRITICAL): Verified — test count math already correct in spec.md. No edit needed.
- **M2** (MEDIUM): `DELETE /api/v1/notes/{id}` response updated to `{deleted_id, tombstone_id}` at FR-012 Endpoints.
- **M3** (MEDIUM): Two clarifications applied:
  1. FR-008 Notes category: changed "notes converted to tasks" → "convert-endpoint calls — stat incremented when suggestion returned, not at task creation"
  2. FR-012 Side Effects: expanded `notes_converted` line to explain *intent-to-convert* vs *task-creation-confirmed* semantics.
- **M5** (MEDIUM, Option A): FR-016 Side Effects: changed "may be pruned" → "**MUST** be pruned after 30 days by a scheduled background job (co-located with daily credit reset — see Task 6.2)"
- **L1** (LOW): NFR-001 performance targets qualifier updated to distinguish single-instance (verified) from multi-instance (pending Task 4.3a + 7.4).
- **L2** (LOW): FR-004 Streaming Variant expanded with explicit `Content-Type`, `event: chunk` format, `event: final` format, and full field list.
- **L3** (LOW): `GET /api/v1/notes/{id}` annotated: "returns note regardless of archived status".
- **L4** (LOW): `GET /api/v1/notes` annotated: "default (no param): returns all notes regardless of archived status".

Items not in scope (require implementation, not spec text):
- C1: backend/docs/API.md Notes section — separate doc update task
- H1/H2/M1: Code + test implementation tasks

## Outcome

- ✅ Impact: 7 spec.md edits applied; spec now accurately reflects implementation behavior for Notes archived semantics, DELETE response shape, streaming SSE format, notifications pruning policy, achievement stat semantics, and NFR verification status.
- 🧪 Tests: No tests run (spec-only change)
- 📁 Files: specs/003-perpetua-backend/spec.md
- 🔁 Next prompts: Apply C1 (API.md Notes section rewrite) via doc update; implement H1/H2/M1 via /sp.implement
- 🧠 Reflection: Remediation file was well-structured with precise old→new diffs; all trivial-effort items applied cleanly in a single pass.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Apply C1 (API.md) as a separate targeted edit pass
