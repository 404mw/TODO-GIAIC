---
id: 055
title: Update plan v1.2 remediations
stage: plan
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.plan update 003 as per updated 003 specs and @remediation-plan.md
labels: ["plan", "notes-standalone", "remediation", "constitution-check", "v1.2"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
tests:
  - null
---

## Prompt

update 003 as per updated 003 specs and @remediation-plan.md

## Response snapshot

Updated `specs/003-perpetua-backend/plan.md` from v1.0 to v1.2 to align with:
1. `spec.md` v1.2 (Notes standalone redesign — FR-012)
2. `remediation-plan.md` findings F1, F3, B3

**Changes applied:**
- Version bumped to 1.2
- Layer 2 API: Notes description → "Standalone notes (user-owned, not task-scoped; deprecated task-scoped endpoints return 410 Gone)"
- Layer 3 Service: Added NoteService description (standalone, voice note credits, transcription, convert, tombstone, archive guard); AIService rate limit description updated to reference config settings (no hardcoded values)
- Layer 4 Model: Added Note model definition (user_id, no task_id, voice fields, transcription_status); removed `notes` relationship from TaskInstance (v1.2 design note added)
- Layer 5 DB: Updated notes table description (user_id FK, no task_id, features listed)
- **Layer 6 Request Schemas (new section)**: Added NoteCreate with conditional min_length via `model_validator` (F1 — allows empty content when voice_url is set); added error codes table (F1b)
- **Constitution Check (new section)**: Full table with checks I–X; IX.4 marked ✅ PASS (F3 — ai_task_block_threshold and ai_task_warning_threshold confirmed in config.py and read via self.settings.* in ai_service.py)
- **Conclusion test count (B3)**: "843 unit, 201 integration, 150 contract" → "843 unit + 201 integration; ~150 of the integration tests are schema contract tests via schemathesis"

**Note**: setup-plan.ps1 overwrote the working-tree plan.md with the blank template before this session; HEAD was restored from git and all v1.2 changes were re-applied from scratch based on spec.md and remediation-plan.md.

## Outcome

- ✅ Impact: plan.md v1.2 now consistent with spec.md v1.2 and all three remediation-plan.md findings resolved
- 🧪 Tests: No code changes; plan documentation only
- 📁 Files: specs/003-perpetua-backend/plan.md (modified)
- 🔁 Next prompts: Run /sp.tasks to regenerate tasks.md for v1.2; verify NoteCreate schema in code matches conditional validation pattern
- 🧠 Reflection: setup-plan.ps1 overwrites the existing plan.md with the template — avoid running this on features with existing plans unless intentionally starting fresh

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 clobbered working-tree plan.md; git restore from HEAD recovered it but lost unstaged edits
- Graders run and results (PASS/FAIL): Manual grep verification of all key changes — PASS
- Prompt variant (if applicable): null
- Next experiment: Add a guard in setup-plan.ps1 to skip copy if plan.md already has content (non-template)
