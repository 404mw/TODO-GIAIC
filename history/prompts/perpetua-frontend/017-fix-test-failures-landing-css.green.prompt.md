---
id: 017
title: Fix Test Failures and Landing Page CSS
stage: green
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20251101
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: developer
command: /sp.implement
labels: ["testing", "bug-fix", "css", "integration-tests"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/tests/integration/task-creation.test.tsx
  - frontend/src/lib/utils/animations.ts
  - frontend/src/app/(public)/landing/page.tsx
tests:
  - tests/integration/task-creation.test.tsx (8 tests passing)
---

## Prompt

fix

1. Test Failures (23 tests failing)
Root Cause: The integration tests in task-creation.test.tsx mock the useTasks hook, but the TaskList component accepts tasks via props, not by calling the hook directly. When tests render <TaskList /> without the tasks prop, the component defaults to an empty array and shows "No tasks found."

Fix: Update tests to pass tasks via the tasks prop:

// Instead of:
render(<TaskList />)

// Should be:
render(<TaskList tasks={mockTasks} />)

2. Landing Page Display Issues
Root Cause: Two issues:

Route mismatch: Root URL / shows the Dashboard page, not the landing page. The landing page is at /landing.
Fixed CSS positioning: The gradient blobs use fixed pixel values (600px size, -100px positions) which may appear oversized on certain screens.

Fix Options:

Navigate to /landing instead of / to see the proper landing page
Or restructure routes so landing page is at root for public visitors

## Response snapshot

Fixed both issues:

1. **Test Failures Fixed**: Updated `task-creation.test.tsx` to:
   - Remove unnecessary `useTasks` mock (TaskList uses props, not the hook)
   - Add Next.js navigation mock (`useRouter`, `usePathname`, `useSearchParams`) required by TaskCard
   - Pass tasks via `tasks` prop instead of mocking the hook
   - All 8 tests in task-creation.test.tsx now pass

2. **Landing Page CSS Fixed**:
   - Reduced blob sizes from 600/500/450px to 400/350/300px for better proportions
   - Updated animation positions to use smaller, more reasonable offsets
   - Added responsive sizing using CSS `clamp()` function: `clamp(200px, 30vw, ${blob.size}px)`
   - Blobs now scale appropriately across different screen sizes

## Outcome

- ✅ Impact: task-creation.test.tsx tests now pass (8/8); landing page blobs display correctly
- 🧪 Tests: 8 tests fixed in task-creation.test.tsx; 84 total tests passing
- 📁 Files: 3 files modified (test file, animations.ts, landing page.tsx)
- 🔁 Next prompts: Other test failures (navigation, TaskForm, Sidebar, ReminderForm) are pre-existing issues unrelated to this fix
- 🧠 Reflection: Root cause was mismatch between test assumptions and actual component API; TaskList accepts tasks via props, not hook

## Evaluation notes (flywheel)

- Failure modes observed: Tests assumed TaskList called useTasks hook internally; also missing Next.js router context mock
- Graders run and results (PASS/FAIL): task-creation tests PASS (8/8)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fix remaining test failures in navigation.test.tsx, TaskForm.test.tsx, Sidebar.test.tsx, ReminderForm.test.tsx
