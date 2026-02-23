---
id: 062
title: Update plan.md v1.2 standalone notes remediation
stage: plan
date: 2026-02-23
surface: agent
model: claude-sonnet-4-6
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: 404mw
command: /sp.plan update 003 plan as per updated spec and attached file
labels: ["plan","notes-standalone","v1.2","remediations","architecture"]
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

update 003 plan as per updated spec and attached file

## Response snapshot

Ran `/sp.plan` workflow for feature 003-perpetua-backend:

1. Executed `setup-plan.ps1 -Json` — script copied blank template over the existing plan.md (which had committed v1.0 content).
2. Recovered committed plan.md content from `git show HEAD:specs/003-perpetua-backend/plan.md`.
3. Read spec.md (v1.2), REMEDIATIONS-003-v2.md, constitution.md, and tasks.md for full context.
4. Composed updated plan.md (v1.2) applying the following changes from spec v1.2 + REMEDIATIONS-003-v2.md:

**Changes applied**:
- **Version/date**: 1.0 → 1.2, 2026-02-17 → 2026-02-23; added spec link in header
- **Layer 2** (API): Notes router description updated from "Task notes" → "User notes (standalone, v1.2)"; Tasks router notes the 410 Gone stubs for deprecated endpoints
- **Layer 3** (Service): NoteService section fully rewritten for standalone notes; AIService updated for confirm-action, note conversion, configurable thresholds; CreditService notes FREE_TIER_DAILY_CREDITS = 10 and missing monthly renewal (Task 4.2a)
- **Layer 4** (Model): TaskInstance.notes relationship removed; User.notes relationship added; Note model code block added (standalone with archived, voice_url, voice_duration_seconds, transcription_status)
- **Layer 5** (Database): notes table description updated (user-scoped, no task_id); v1.2 migration notes added; ix_note_user_id noted
- **Layer 6 (NEW)**: Schema Contracts section added with NoteCreate (I1b fix applied: `# 1–MAX_AUDIO_DURATION_SECONDS; None for non-voice notes\n# (MAX_AUDIO_DURATION_SECONDS config default = 300)`), NoteUpdate, NoteResponse, TaskSuggestionResponse; error codes for notes
- **Pattern 6** (Soft Delete): Task snapshot excludes notes (they have own tombstone lifecycle); note recovery tolerates legacy task_id in snapshot (migration tolerance per FR-013)
- **Data Flow**: Voice Note Creation Flow (Pro Only) section added; AI chat flow updated with configurable threshold reference
- **Module Breakdown**: NoteService module entry added; AIService updated (confirm-action, note conversion, scalability gap Task 4.3a); CreditService notes monthly renewal gap
- **Conclusion**: Test count corrected (843 unit + 201 integration, ~150 contract subset); standalone notes + undo exception added to key architectural decisions

**REMEDIATIONS-003-v2.md item applied to plan.md**:
- I1b (Item #4): NoteCreate `voice_duration_seconds` comment corrected from `(default: 300)` to clarified annotation

## Outcome

- ✅ Impact: plan.md updated to v1.2 reflecting Notes standalone redesign (FR-012 REVISED) and all REMEDIATIONS-003-v2.md items relevant to plan.md; Layer 6 schema contracts section added
- 🧪 Tests: No tests run (plan document update only)
- 📁 Files: specs/003-perpetua-backend/plan.md
- 🔁 Next prompts: `/sp.implement` to execute open tasks (Task 3.7d voice pipeline, Task 4.2a monthly renewal, Task 4.3a AI session counter DB-backing, Task 3.7b GET /notes/{id} resolution)
- 🧠 Reflection: setup-plan.ps1 overwrites the existing plan.md with blank template — recovered via git show HEAD. Going forward, sp.plan should check if plan.md already has content and diff/update rather than clobber.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 unconditionally copies blank template over existing plan.md (lost working-tree modifications since last commit); recovered via git
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add guard to setup-plan.ps1 — if plan.md has >50 lines of content, skip copy and print warning instead of clobbering
