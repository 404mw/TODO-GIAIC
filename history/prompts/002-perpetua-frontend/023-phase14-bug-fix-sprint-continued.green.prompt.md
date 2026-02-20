---
id: 023
title: Phase 14 Bug Fix Sprint — Continued Green Implementation
stage: green
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.implement 002
labels: ["phase14","bug-fix","tdd","red-green","reminders","subscription","notifications","navigation-guard"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/tests/unit/components/TaskDetailView-reminders.test.tsx
  - frontend/src/components/tasks/TaskDetailView.tsx
  - frontend/tests/unit/hooks/useSubscription.test.ts
  - frontend/src/lib/hooks/useSubscription.ts
  - frontend/src/lib/services/payment.service.ts
  - frontend/tests/integration/notifications-page.test.tsx
  - frontend/src/app/dashboard/notifications/page.tsx
  - frontend/tests/unit/hooks/useNotifications-read.test.ts
  - frontend/src/lib/hooks/useNotifications.ts
  - frontend/tests/unit/components/FocusTaskView-guard.test.tsx
  - frontend/src/components/focus/FocusTaskView.tsx
  - specs/002-perpetua-frontend/tasks.md
tests:
  - tests/unit/components/TaskDetailView-reminders.test.tsx (4 tests — T164)
  - tests/unit/hooks/useSubscription.test.ts (3 tests — T165)
  - tests/integration/notifications-page.test.tsx (4 tests — T174)
  - tests/unit/hooks/useNotifications-read.test.ts (3 tests — T166)
  - tests/unit/components/FocusTaskView-guard.test.tsx (4 tests — T182)
---

## Prompt

/sp.implement 002

Focus on Phase 14 (Bug Fix Sprint) first. Follow the Phase 14 Execution Order table — RED test must fail before GREEN implementation begins for each pair. Work in priority order: T181/T112 first (P0 PREREQ), then a11y (T157-T159), then CRITICAL bugs (T161-T166/T122-T130), etc.

Skip T099 — blocked on backend confirming PATCH/DELETE template endpoints.

Working directory: frontend/
All tests use jest.fn() mock pattern (no MSW). Run tests with: npx jest <test-file> from the frontend/ directory.

## Response snapshot

Continued Phase 14 Bug Fix Sprint from context boundary. Implemented 5 RED/GREEN pairs:

**T164 (RED) → T126 (GREEN): Reminder wiring in TaskDetailView**
- Test: `handleAddReminder` calls `useCreateReminder.mutateAsync`; success toast only after resolve; error toast on reject; `handleDeleteReminder` calls `useDeleteReminder.mutateAsync`
- Fix: Added `useCreateReminder` and `useDeleteReminder` imports + hook calls in `TaskDetailView.tsx`; replaced both stub handlers with real `mutateAsync` calls

**T165 (RED) → T127 (GREEN): Subscription upgrade endpoint**
- Test: `useUpgradeSubscription` calls `POST /subscription/upgrade`; NOT `/subscription/checkout` or `/subscription/purchase-credits`
- Fix: Renamed `useCreateCheckoutSession` → `useUpgradeSubscription`; changed endpoint from `/subscription/checkout` → `/subscription/upgrade`; removed `checkout_url` redirect; added `router.push('/dashboard')` on success. Also cleaned up `payment.service.ts`

**T174 (RED) → T128 (GREEN): Notifications page**
- Test: Component exists; `useNotifications()` called; loading skeleton renders; empty state renders
- Fix: Created `src/app/dashboard/notifications/page.tsx` with loading skeleton, empty state "No notifications yet", and reverse-chronological list

**T166 (RED) → T129 (GREEN): Mark-as-read endpoint**
- Test: Calls `PATCH /notifications/{id}/read` (path-based); NOT `PATCH /notifications/{id}` with `{read: true}` body
- Fix: Changed `apiClient.patch('/notifications/${id}', { read: true })` → `apiClient.patch('/notifications/${id}/read', undefined)`

**T182 (RED) → T172 (GREEN): Navigation guard**
- Test: `window.confirm` called on popstate when focus active; `beforeunload` handled; no guard when inactive; guard cleaned up on unmount
- Fix: Created `FocusTaskView.tsx` with `useEffect` that registers `popstate` + `beforeunload` listeners when `isActive`, cleans up on unmount; returns null (side-effect-only component)

All 33 tests passing (18 from this session + 15 from previous). Updated tasks.md marking 25 tasks as [X].

## Outcome

- ✅ Impact: 5 Phase 14 bug pairs completed; all API contract violations fixed for reminders, subscription, notifications, and navigation guard
- 🧪 Tests: 18 new tests passing (5 RED test files × 3-4 tests each); 33 total across both sessions
- 📁 Files: 5 test files created, 5 source files modified/created, tasks.md updated (25 tasks → [X])
- 🔁 Next prompts: Remaining Phase 14: T183/T131 (NewTaskModal 375px), T184/T132 (NotificationDropdown mousedown), T185/T133 (PendingCompletionsBar mobile), T179/T134 (localStorage-free auth), T180/T135 (console.log), T178 (AI credit env vars), T167/T168 (autosave), T169/T170 (form draft)
- 🧠 Reflection: TDD discipline maintained — all RED tests confirmed failing before GREEN; `expect.anything()` doesn't match `undefined` in Jest (fixed by extracting path assertion separately)

## Evaluation notes (flywheel)

- Failure modes observed: `expect.anything()` fails for `undefined` args — use `call[0]` path check instead; `window.history.pushState` in guard triggers popstate listener recursively in jsdom — handled correctly
- Graders run and results (PASS/FAIL): All 33 tests PASS
- Prompt variant (if applicable): continuation from context boundary
- Next experiment (smallest change to try): Run full test suite to check for regressions before proceeding to T183+
