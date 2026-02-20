---
id: 011
title: Scan Frontend Test Coverage Report
stage: misc
date: 2026-02-19
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: scan frontend tests and return structured coverage report
labels: ["testing","coverage","jest","frontend","audit"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - tests/unit/utils/date.test.ts
  - tests/unit/utils/recurrence.test.ts
  - tests/unit/components/RecurrencePreview.test.tsx
  - tests/unit/components/ReminderForm.test.tsx
  - tests/unit/components/Sidebar.test.tsx
  - tests/unit/components/SubTaskList.test.tsx
  - tests/unit/components/TaskForm.test.tsx
  - tests/integration/navigation.test.tsx
  - tests/integration/reminder-notification.test.tsx
  - tests/integration/task-creation.test.tsx
tests:
  - tests/unit/utils/date.test.ts
  - tests/unit/utils/recurrence.test.ts
  - tests/unit/components/RecurrencePreview.test.tsx
  - tests/unit/components/ReminderForm.test.tsx
  - tests/unit/components/Sidebar.test.tsx
  - tests/unit/components/SubTaskList.test.tsx
  - tests/unit/components/TaskForm.test.tsx
  - tests/integration/navigation.test.tsx
  - tests/integration/reminder-notification.test.tsx
  - tests/integration/task-creation.test.tsx
---

## Prompt

Scan the frontend directory at `g:/Hackathons/GIAIC_Hackathons/02-TODO/frontend` for all test files and return a structured report.

**What I need:**
1. List every test file path (relative to `frontend/`) with pattern `**/__tests__/**/*.test.*` or `**/*.test.ts`, `**/*.test.tsx`, `**/*.spec.ts`, `**/*.spec.tsx`
2. For each test file, read it and list:
   - The file path
   - What it tests (brief description)
   - Which functional requirement or component it covers (e.g., auth, tasks, notes, subtasks, focus, achievements, reminders, AI, command palette)
3. List any areas/FRs that have NO test coverage at all

Return a comprehensive JSON-like structured report I can use to update a tasks.md file. Include every test file found.

Also check if there's a jest.config.ts or jest.config.js and package.json to understand the test setup.

## Response snapshot

10 test files found across unit (7) and integration (3) categories. Full structured report delivered with covered areas and uncovered FRs identified. Jest config uses next/jest with jsdom environment, testMatch `tests/**/*.test.{js,jsx,ts,tsx}`. MSW is installed but disabled due to Windows ES module issues.

Covered FRs: reminders (T083-T086), recurrence (FR-069/070/073, T102-T105), tasks/subtasks (T066-T070), sidebar/navigation/focus (T051-T054).

Uncovered: auth, notes, achievements, focus timer, AI subtask generation, command palette, credits/subscription, API hooks/services, date utils (partial), store logic (all stores), schema validation.

## Outcome

- Impact: Comprehensive test coverage audit produced; identified 14+ untested component/feature areas for tasks.md update
- Tests: 10 test files read and analysed; no tests were run
- Files: Read-only scan; no files modified
- Next prompts: Update tasks.md with missing test task entries; add tests for auth, notes, achievements, focus timer, AI, command palette
- Reflection: Coverage is sparse (10 files for ~50 source components/hooks/utils); coverage thresholds are set very low (10% statements) confirming active development phase

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment: run `jest --coverage` to get actual line-level coverage percentages
