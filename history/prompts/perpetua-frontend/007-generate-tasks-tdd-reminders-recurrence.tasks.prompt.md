---
id: 007
title: Generate Tasks with TDD and Reminders Recurrence
stage: tasks
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: Claude Agent
command: /sp.tasks
labels: ["tasks", "tdd", "reminders", "recurrence", "red-green-refactor"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/tasks.md
tests:
  - None (task generation phase)
---

## Prompt

include Reminders & Recurrence and enforce TDD

## Response snapshot

Successfully generated comprehensive tasks.md file with strict TDD enforcement (Red-Green-Refactor workflow) and full integration of Reminders & Recurrence features per research.md decisions.

### Key Deliverables

1. **tasks.md Created** (G:\Hackathons\GIAIC_Hackathons\02-TODO\specs\002-perpetua-frontend\tasks.md)
   - **Total Tasks**: 151 tasks organized in 13 phases
   - **TDD Enforcement**: All tasks follow Red → Green → Refactor pattern
   - **Tests MUST FAIL First**: Explicit RED phase before GREEN implementation
   - **MVP Scope**: 80 tasks (Phases 1-4) for deployable core task management
   - **Reminders**: 25 tasks (Phase 5) with Service Worker polling every 60s, dual notifications
   - **Recurrence**: 20 tasks (Phase 6) with RRule library, completion-based instance generation
   - **Task Format**: `- [ ] [ID] [P?] [Story?] Description with file path`
   - **Organization**: Grouped by user story (US1-US8) for independent testing
   - **Parallel Opportunities**: ~60 tasks marked [P] for concurrent execution

2. **Phase Structure**
   - **Phase 1**: Setup (14 tasks) - Project initialization, dependencies, testing infrastructure
   - **Phase 2**: Foundational (40 tasks) - Schemas, MSW handlers, TanStack Query hooks, Zustand stores, base UI components - **BLOCKS ALL USER STORIES**
   - **Phase 3**: US8 Dashboard Layout (15 tasks) - Navigation foundation with RED-GREEN-REFACTOR
   - **Phase 4**: US1 Core Tasks (16 tasks) - MVP task CRUD with TDD
   - **Phase 5**: US1 Extended Reminders (19 tasks) - Dual notification system with TDD
   - **Phase 6**: US1 Extended Recurrence (14 tasks) - RRule integration with TDD
   - **Phase 7**: US2 Focus Mode (10 tasks) - Distraction-free mode with TDD
   - **Phase 8**: US3 Quick Notes (4 tasks) - Notes with AI UI disabled
   - **Phase 9**: US7 Global Search (3 tasks) - Fuse.js integration
   - **Phase 10**: US5 Achievements (4 tasks) - Metrics tracking
   - **Phase 11**: US6 Onboarding (4 tasks) - driver.js walkthrough
   - **Phase 12**: US4 AI Sub-tasks (2 tasks) - Magic Sub-tasks UI disabled
   - **Phase 13**: Polish (10 tasks) - Error boundaries, optimization, final testing

3. **Reminders Implementation (Phase 5) - 19 Tasks**
   - **RED Tests** (4 tasks): ReminderForm validation, calculateReminderTriggerTime, Service Worker detection, fallback
   - **GREEN Implementation** (12 tasks):
     - calculateReminderTriggerTime utility (relative timing: offsetMinutes from due date)
     - ReminderForm, ReminderList, ReminderNotification components
     - Service Worker polling logic (60s interval)
     - fetchRemindersFromMSW and fetchTasksFromMSW in Service Worker
     - dueReminders filter logic
     - Browser notification trigger (if permission granted)
     - In-app toast postMessage (always)
     - Reminders page and task detail integration
   - **REFACTOR** (3 tasks): Permission request prompt, graceful fallback, mark-as-delivered

4. **Recurrence Implementation (Phase 6) - 14 Tasks**
   - **RED Tests** (4 tasks): onTaskComplete generation, RRule parsing, COUNT limits, RecurrencePreview
   - **GREEN Implementation** (7 tasks):
     - onTaskComplete function with RRule.fromString(), RRule.after() logic
     - PATCH /api/tasks/:id handler update to trigger recurrence on completion
     - RecurrenceEditor with frequency/interval/weekday pickers
     - RecurrencePreview showing next 5 occurrences
     - WeekdayPicker component
     - TaskForm and task detail integration
   - **REFACTOR** (3 tasks): Human-readable description with RRule.toText(), preset buttons, edge case handling

5. **TDD Workflow Enforcement**
   - **RED Phase**: Write ALL tests first, verify they FAIL
   - **GREEN Phase**: Implement minimal code to pass tests
   - **REFACTOR Phase**: Improve code quality while keeping tests green
   - **Coverage Gate**: 80% minimum enforced in pre-commit hook
   - **Test Performance**: Full suite must complete <2 minutes

### Task Organization Highlights

**Independent User Stories**:
- Each story can be implemented and tested independently
- US1 (Core Tasks) is foundation for US1 Extended (Reminders, Recurrence)
- US2, US3, US7 can proceed in parallel after US1 core
- Checkpoints after each phase verify story works standalone

**Parallel Execution**:
- Phase 1 Setup: 7 parallel opportunities
- Phase 2 Foundational: 35+ parallel opportunities (schemas, handlers, hooks all independent)
- Within user stories: Tests marked [P], components marked [P] can run concurrently

**File Path Clarity**:
- Every task includes exact file path
- Follows Next.js 15 App Router structure from plan.md
- Example: `src/components/reminders/ReminderForm.tsx`
- Example: `tests/unit/components/ReminderForm.test.tsx`

### Technical Decisions (from research.md)

**Reminders**:
- Dual system: Browser notifications (if permission granted) + in-app toast (always)
- Service Worker polling: Checks MSW `/api/reminders` and `/api/tasks` every 60 seconds
- Relative timing: offsetMinutes from task due date (e.g., -15 = 15 min before, -1440 = 1 day before)
- Graceful degradation: Falls back to toast-only if browser permission denied or Service Worker unsupported
- Delivery confirmation: POST `/api/reminders/:id/delivered` to mark as sent

**Recurrence**:
- RRule library (RFC 5545 standard): Battle-tested, TypeScript support, human-readable output
- Completion-based: Next instance generated immediately when task marked complete
- Custom intervals: Supports "every 2 weeks on Tuesday" via RRule
- UI components: RecurrenceEditor with presets (Daily, Weekly, Monthly, Custom), RecurrencePreview showing next 5 occurrences
- Edge cases: Invalid dates, COUNT limits, timezone support, UNTIL dates

### Execution Strategy

**MVP First (80 tasks)**:
1. Phase 1: Setup (14 tasks)
2. Phase 2: Foundational (40 tasks) - **CRITICAL GATE**
3. Phase 3: Dashboard Layout (15 tasks)
4. Phase 4: Core Tasks (16 tasks)
5. **STOP & VALIDATE**: Test MVP independently, deploy

**Add Reminders & Recurrence (45 tasks)**:
6. Phase 5: Reminders (19 tasks)
7. Phase 6: Recurrence (14 tasks)
8. **STOP & VALIDATE**: Test independently, deploy

**Complete Full Feature Set (26 tasks)**:
9. Phases 7-12: Focus, Notes, Search, Achievements, Onboarding, AI UI
10. Phase 13: Polish
11. **FINAL RELEASE**

## Outcome

- ✅ Impact: Comprehensive tasks.md created with strict TDD enforcement, 151 tasks total, Reminders (25 tasks) & Recurrence (20 tasks) fully integrated as Phase 5-6 extensions of US1
- 🧪 Tests: None (task generation phase, no code written)
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: Begin implementation with Phase 1 Setup tasks, following strict RED-GREEN-REFACTOR workflow
- 🧠 Reflection: Task organization by user story enables independent implementation and testing. TDD workflow explicitly enforced in task descriptions (RED write failing tests → GREEN implement → REFACTOR improve). Reminders and Recurrence follow research.md decisions (Service Worker polling, RRule library, completion-based generation). All 151 tasks follow strict checklist format with [ID], [P?], [Story?], description, and file path. MVP is clearly defined (80 tasks), Reminders/Recurrence add-on is clear (45 tasks), enabling incremental delivery.

## Evaluation notes (flywheel)

- Failure modes observed: Initial markdown linting warnings (duplicate heading "RED: Write FAILING Tests First") - fixed by adding context suffixes (Tasks, Reminders, Recurrence, Focus Mode)
- Graders run and results (PASS/FAIL): Markdown linting PASS after fixes
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase 1 Setup tasks, validate TDD workflow with first component test to ensure RED-GREEN-REFACTOR cycle works as documented
