---
id: 045
title: ADR Notes Standalone First Class
stage: misc
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.adr
labels: ["adr", "notes", "standalone", "data-model", "architecture"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: history/adr/001-notes-standalone-first-class-entities.md
  pr: null
files:
  - history/adr/001-notes-standalone-first-class-entities.md
  - history/adr/ (directory created)
tests:
  - N/A (ADR documentation — no tests run)
---

## Prompt

notes-standalone-first-class-entities

## Response snapshot

Ran `/sp.adr notes-standalone-first-class-entities` to document the architectural decision
to redesign Notes from task-scoped nested resources to standalone user-owned entities.

**Prerequisites check**: Feature dir = `specs/003-perpetua-backend`, available docs: data-model.md, plan.md.

**ADR directory**: Did not exist — created `history/adr/`.

**create-adr.sh**: Not available — used agent-native tools.

**Decision cluster extracted from plan.md** (significance test: ALL PASS):
- Impact: Data model restructure, endpoint removal, limit changes, tombstone compatibility
- Alternatives: Task-scoped (status quo), dual ownership, atomic convert, event-sourced notes
- Scope: Cross-cutting — model/service/API/limits/tests/recovery all affected

**ADR created**:
- ID: 001
- Title: Notes Standalone First-Class Entities
- Status: Accepted
- Components: 6 sub-decisions (data model, API surface, limits, archiving, tombstones, indexes)
- Alternatives: 4 documented (A: keep task-scoped, B: dual ownership, C: auto-archive on convert, D: event-sourced)

## Outcome

- ✅ Impact: ADR-001 created documenting Notes v1.1→v1.2 redesign with 4 alternatives considered
- 🧪 Tests: N/A
- 📁 Files: history/adr/001-notes-standalone-first-class-entities.md
- 🔁 Next prompts: `/sp.tasks 003` to update tasks.md with Tasks 3.7a/b/c
- 🧠 Reflection: Decision cluster was correctly identified as single ADR (not 6 separate ADRs) — all 6 sub-decisions change together and cannot diverge.

## Evaluation notes (flywheel)

- Failure modes observed: None — clean decision cluster identification
- Graders run and results (PASS/FAIL): Significance test PASS (all 3 gates)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run tests after limits.py update to confirm coverage
