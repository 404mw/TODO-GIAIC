---
id: 003
title: Deep Bug Analysis Frontend
stage: misc
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: developer
command: deep read-only analysis of frontend codebase for 8 reported bugs
labels: ["bug-analysis","api-mismatch","frontend","security","ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/lib/api/client.ts
  - frontend/src/lib/hooks/useTasks.ts
  - frontend/src/lib/hooks/useNotes.ts
  - frontend/src/lib/hooks/useSubtasks.ts
  - frontend/src/lib/hooks/useNotifications.ts
  - frontend/src/lib/hooks/useSubscription.ts
  - frontend/src/components/tasks/TaskCard.tsx
  - frontend/src/components/tasks/TaskDetailView.tsx
  - frontend/src/components/tasks/NewTaskModal.tsx
  - frontend/src/components/tasks/AddSubTaskForm.tsx
  - frontend/src/components/tasks/SubTaskList.tsx
  - frontend/src/components/notes/NoteEditor.tsx
  - frontend/src/components/layout/NotificationDropdown.tsx
  - frontend/src/components/layout/PendingCompletionsBar.tsx
  - frontend/src/components/layout/DashboardLayout.tsx
  - frontend/src/components/layout/Header.tsx
  - frontend/src/lib/services/payment.service.ts
  - frontend/src/lib/stores/notification.store.ts
  - frontend/src/lib/stores/pending-completions.store.ts
  - frontend/src/lib/contexts/AuthContext.tsx
  - frontend/src/app/(public)/pricing/page.tsx
  - frontend/src/app/dashboard/notes/page.tsx
  - frontend/src/app/dashboard/layout.tsx
  - API.md
tests:
  - "none run (read-only analysis)"
---

## Prompt

You are performing a deep read-only analysis of a Next.js/TypeScript frontend codebase. The project is at `g:\Hackathons\GIAIC_Hackathons\02-TODO`. The frontend is a Next.js app.

Please explore and analyze the following reported bugs. For each bug, find the relevant code, identify the root cause, and document the fix needed. Cross-reference with the API.md at the project root.

**Reported Issues:**
1. Clicking anywhere on the screen sends API requests to the backend (likely stray event handlers or useEffect with no proper dependencies)
2. Duplicate subtask requests being sent
3. Confirmation modal (appears after marking task) not optimized for mini/small screens
4. Task creation modal needs small screen optimization + no option to add subtasks during creation
5. Notification tab shows 404 instead of opening in full screen
6. Task creation works but nothing else (edit, mark complete, delete, add reminder) doesn't work
7. Notes creation doesn't work
8. /pricing payment doesn't work

## Response snapshot

Comprehensive findings report delivered covering all 8 bugs with root cause analysis, API mismatches, file paths, line numbers, security concerns, and fix recommendations. Key findings: API endpoint mismatches (complete/auto-complete don't exist, notes POST to wrong URL), stray event listener in NotificationDropdown always attached, incomplete subtask cache-key bug causing duplicate requests, reminder API call stubbed out, no notifications full-page route, payment endpoint names speculative (not in API.md).

## Outcome

- Impact: Identified 8 bugs with root causes; 5 are API contract violations, 2 are UX gaps, 1 is a stray listener bug
- Tests: none run (read-only analysis)
- Files: 24 files analyzed
- Next prompts: Fix each bug category starting with API endpoint corrections in useTasks.ts and useNotes.ts
- Reflection: The most critical issues are the non-existent API endpoints (complete, auto-complete for tasks; direct /notes POST for notes). These will silently fail for all users.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment: Implement fixes starting with useTasks.ts endpoint corrections
