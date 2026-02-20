---
id: 012
title: Update tasks — standalone notes, observability, test coverage
stage: tasks
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.tasks
labels: ["tasks", "notes-architecture", "observability", "test-coverage", "UPDATE-01", "UPDATE-02", "UPDATE-12", "UPDATE-14"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/tasks.md
tests:
  - frontend/tests/unit/components/TaskForm.test.tsx
  - frontend/tests/unit/components/SubTaskList.test.tsx
  - frontend/tests/unit/components/ReminderForm.test.tsx
  - frontend/tests/unit/components/RecurrencePreview.test.tsx
  - frontend/tests/unit/components/Sidebar.test.tsx
  - frontend/tests/unit/utils/recurrence.test.ts
  - frontend/tests/unit/utils/date.test.ts
  - frontend/tests/integration/navigation.test.tsx
  - frontend/tests/integration/reminder-notification.test.tsx
  - frontend/tests/integration/task-creation.test.tsx
---

## Prompt

update 002 tasks as per updated spec, plan and @SPEC_UPDATES.md (only tasks)

ask me for further clarification each question must have one recommended option

additionally, project constitution enforces TDD and tests were written and passed for V1 and exists in /frontend dir. add them in tasks.md as completed and add non existing test

## Response snapshot

Applied 14 targeted edits to `specs/002-perpetua-frontend/tasks.md`:

**SPEC_UPDATES applied (task-relevant only):**
- UPDATE-14: Header updated — replaced "Tests: Not included" with V1 test suite status note and §X.5 reference
- UPDATE-01/02: Phase 7 notes tasks (T069, T071, T072, T074) rewritten to reflect standalone `/api/v1/notes` architecture (no task_id, no task-scoped paths)
- UPDATE-02: T125 fully rewritten — from "fix to task-scoped paths" → "migrate notes to standalone /api/v1/notes"; acceptance criteria flipped accordingly
- UPDATE-12: New Phase 15 added with T136–T138 (Sentry setup, Web Vitals, structured logger)
- Clarification answers applied: T125 rewrite (not remove), Phase 7 descriptions updated, Phase 15 as new phase

**V1 Test Coverage (Constitution §VIII):**
Scanned 10 existing test files in `frontend/tests/`. Added Phase 16 with:
- T139–T148 ([X] done): 10 existing V1 tests mapped to task IDs and component targets
- T149–T156 ([ ] missing): 8 missing tests for AuthContext, TaskCard, useTasks version, NoteCard standalone, AchievementCard, AISubtasksGenerator, CommandPalette, ConflictResolutionModal

**Summary:**
- Total task count: 135 → 156 tasks across 14 → 16 phases
- Phase 15: T136–T138 (observability)
- Phase 16: T139–T156 (10 existing + 8 missing tests)

## Outcome

- ✅ Impact: tasks.md now reflects standalone notes architecture (UPDATE-02), documents V1 test suite, and adds observability + test coverage phases
- 🧪 Tests: V1 test suite (10 files, all passing) mapped to task IDs T139–T148; 8 missing tests identified as T149–T156
- 📁 Files: specs/002-perpetua-frontend/tasks.md (sole modified file)
- 🔁 Next prompts: apply SPEC_UPDATES to spec.md (UPDATE-01 through UPDATE-13); write missing tests T149–T156; implement T125 standalone notes migration
- 🧠 Reflection: Notes architecture flip (UPDATE-02) required careful reversal of T125 direction and update of all Phase 7 task descriptions — important to catch early before implementation starts

## Evaluation notes (flywheel)

- Failure modes observed: none — clarification questions correctly surfaced the T125 direction reversal before editing
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): with clarification questions + test coverage addition
- Next experiment: apply same pattern to spec.md updates via /sp.specify
