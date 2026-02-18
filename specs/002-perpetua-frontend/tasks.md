# Tasks: Perpetua Flow Frontend

**Input**: Design documents from `/specs/002-perpetua-frontend/`
**Prerequisites**: [plan.md](./plan.md) ✅, [spec.md](./spec.md) ✅
**Tests**: Not included (TDD approach available via `/sp.tasks` with `--tdd` flag)
**Organization**: Grouped by User Story (FR-001 → FR-010) to enable independent delivery

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which functional requirement this belongs to (US1–US10)
- Paths use `frontend/src/` prefix per plan.md Layer Structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project skeleton, tooling, and base configuration

- [ ] T001 Initialize Next.js 16 project with TypeScript 5 via `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] T002 Install all dependencies from plan.md: `npm install @tanstack/react-query zustand zod @radix-ui/react-dialog framer-motion fuse.js rrule date-fns lucide-react`
- [ ] T003 [P] Install dev dependencies: `npm install -D msw jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom @types/jest`
- [ ] T004 [P] Configure `tsconfig.json` with strict mode, path aliases (`@/*` → `src/*`), and `moduleResolution: bundler`
- [ ] T005 [P] Configure `eslint.config.js` with Next.js preset and import ordering rules
- [ ] T006 Configure `jest.config.ts` with jsdom environment, MSW server setup, and module aliases matching tsconfig
- [ ] T007 [P] Configure `tailwind.config.ts` with dark mode class strategy, custom fonts (Geist), and content paths
- [ ] T008 [P] Configure `next.config.ts` with security headers (X-Frame-Options, CSP, HSTS), bundle analyzer integration
- [ ] T009 Create `.env.local` template with `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID` — add `.env.local` to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure every user story depends on: API client, schemas, auth context, layout shell, MSW mocks

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create `frontend/src/lib/schemas/common.schema.ts` — define shared enums: `PrioritySchema` (`low|medium|high`), `CompletedBySchema` (`manual|auto|force`), `UserTierSchema` (`free|pro`), `TranscriptionStatusSchema` (`pending|completed|failed`)
- [ ] T011 [P] Create `frontend/src/lib/schemas/response.schema.ts` — define `DataResponseSchema<T>` (`{data: T}`) and `PaginatedResponseSchema<T>` (`{data: T[], pagination: {page, per_page, total, total_pages}}`) generic wrappers
- [ ] T012 Create `frontend/src/lib/api/client.ts` — implement `ApiError` class (status, code, message, details, request_id) and `apiClient` with `get`, `post`, `patch`, `put`, `delete` methods; inject `Authorization: Bearer` header from `localStorage.getItem('auth_token')`; add `Idempotency-Key: crypto.randomUUID()` on mutating methods; handle both error formats `{"error":{...}}` and `{"code":...,"message":...}`; validate response against optional Zod schema
- [ ] T013 Create `frontend/src/lib/contexts/AuthContext.tsx` — `AuthProvider` with `user: User|null`, `isAuthenticated`, `isLoading`, `logout()`, `refetch()`, `refreshTokenIfNeeded()`; on mount for protected routes (`/dashboard/*`) check `localStorage.auth_token`, call `/users/me`, handle `TOKEN_EXPIRED` by attempting refresh with `refresh_token`, rotate tokens on success; skip fetch on public routes
- [ ] T014 Create `frontend/src/lib/hooks/useAuth.ts` — `useAuth()` hook that reads `AuthContext`, throws if used outside `AuthProvider`
- [ ] T015 [P] Create `frontend/src/lib/hooks/useToast.ts` — wrapper around Radix `Toast` or internal toast store, exposing `toast(message, options)` function
- [ ] T016 [P] Create `frontend/src/lib/hooks/useLocalStorage.ts` — `useLocalStorage<T>(key, defaultValue)` hook with SSR guard (`typeof window === 'undefined'`)
- [ ] T017 [P] Create `frontend/src/lib/hooks/useReducedMotion.ts` — `useReducedMotion()` hook using `window.matchMedia('(prefers-reduced-motion: reduce)')`
- [ ] T018 Create `frontend/src/app/layout.tsx` (root layout) — wrap with `AuthProvider`, `QueryClientProvider` (TanStack Query), `ToastProvider` (Radix); load Geist font; set `<html lang="en">`
- [ ] T019 Create `frontend/src/app/dashboard/layout.tsx` — protected layout with `Sidebar` + `Header` components; redirect to `/login` if `!isAuthenticated && !isLoading`
- [ ] T020 [P] Create `frontend/src/components/layout/Sidebar.tsx` — left nav with links to `/dashboard`, `/dashboard/tasks`, `/dashboard/notes`, `/dashboard/focus`, `/dashboard/achievements`, `/dashboard/settings`; use `useSidebarStore` for collapsed state; persist collapsed in localStorage
- [ ] T021 [P] Create `frontend/src/components/layout/Header.tsx` — top bar with user avatar, user name, logout button; use `useAuth()` to get user; dropdown menu via Radix `DropdownMenu`
- [ ] T022 Create `frontend/src/lib/stores/sidebar.store.ts` — Zustand store: `{ isCollapsed: boolean, toggle: () => void }`; persist to `localStorage`
- [ ] T023 [P] Create `frontend/src/lib/stores/notification.store.ts` — Zustand store: `{ toasts: Toast[], addToast(msg, type), removeToast(id) }`
- [ ] T024 [P] Create `frontend/src/components/ui/` — Radix UI wrappers: `Button.tsx`, `Input.tsx`, `Dialog.tsx`, `Badge.tsx`, `Card.tsx`, `Select.tsx`, `Popover.tsx`, `Toast.tsx`; apply Tailwind utility classes; export variants via `class-variance-authority`
- [ ] T025 Create `frontend/src/mocks/server.ts` — MSW Node server for Jest using `setupServer(...handlers)`; export `server` for test setup
- [ ] T026 Create `frontend/src/mocks/browser.ts` — MSW browser worker using `setupWorker(...handlers)`; start in `_app` when `NEXT_PUBLIC_MSW_ENABLED=true`
- [ ] T027 Create `frontend/src/mocks/handlers/index.ts` — re-export all handlers from individual handler files

**Checkpoint**: API client, auth context, layout shell, and MSW ready — user story implementation can begin

---

## Phase 3: User Story 1 — Authentication (FR-001) 🎯 MVP

**Goal**: User can sign in with Google, session persists, tokens refresh silently, logout clears state

**Independent Test**: Open `/login` → click "Sign in with Google" → redirected to `/dashboard` → refresh page → still authenticated → click logout → redirected to `/login`

### Implementation

- [ ] T028 [US1] Create `frontend/src/lib/schemas/user.schema.ts` — `UserSchema` (id, google_id, email, name, avatar_url, timezone, tier); `UpdateUserRequestSchema` (name?, timezone?); `UserResponseSchema = DataResponseSchema(UserSchema)`; export all types
- [ ] T029 [US1] Create `frontend/src/lib/schemas/auth.schema.ts` — `AuthResponseSchema` (access_token, refresh_token, token_type, expires_in); `RefreshTokenRequestSchema` (refresh_token); export all types
- [ ] T030 [US1] Create `frontend/src/lib/services/auth.service.ts` — `authService.exchangeCode(code)` calling `POST /auth/google/callback`; `authService.refreshTokens(token)` calling `POST /auth/refresh`; `authService.logout(token)` calling `POST /auth/logout`; responses NOT wrapped in `DataResponse`
- [ ] T031 [US1] Create `frontend/src/lib/services/users.service.ts` — `usersService.getCurrentUser()` calling `GET /users/me` returning `UserResponseSchema`; `usersService.updateProfile(data)` calling `PATCH /users/me`
- [ ] T032 [US1] Create `frontend/src/app/login/page.tsx` — centered card with `@react-oauth/google` `GoogleLogin` button; on success call `authService.exchangeCode(code)`, store tokens in localStorage, redirect to `/dashboard`; show error state on failure
- [ ] T033 [US1] Create `frontend/src/app/auth/callback/page.tsx` — handle OAuth redirect; parse `?code=` param; call `authService.exchangeCode(code)`; store `access_token` + `refresh_token` in localStorage; redirect to `/dashboard`
- [ ] T034 [US1] Create `frontend/src/mocks/data/user.fixture.ts` — export `userFixture: User` with realistic test data (UUID, email, name, avatar)
- [ ] T035 [US1] Create `frontend/src/mocks/handlers/user.handlers.ts` — `GET /api/v1/users/me` returning `{data: userFixture}`; `PATCH /api/v1/users/me` merging body with fixture; `POST /api/v1/auth/google/callback` returning mock tokens; `POST /api/v1/auth/refresh` returning rotated mock tokens; `POST /api/v1/auth/logout` returning 200

**Checkpoint**: Auth flow complete — can sign in, persist session, refresh tokens, and logout

---

## Phase 4: User Story 2 — Task Management (FR-002) 🎯 MVP

**Goal**: User can create, read, update, delete, and complete tasks with full metadata (priority, due date, estimated duration, version locking)

**Independent Test**: Create task → view in list → open detail → edit title → mark complete → view in completed list → soft-delete → confirm hidden; all without subtasks or reminders

### Implementation

- [ ] T036 [US2] Create `frontend/src/lib/schemas/task.schema.ts` — full `TaskSchema` (id, user_id, template_id, title, description, priority, due_date, estimated_duration, focus_time_seconds, completed, completed_at, completed_by, hidden, archived, subtask_count, subtask_completed_count, created_at, updated_at, version); `TaskDetailSchema` extending with `subtasks[]` and `reminders[]`; `TaskTemplateSchema`; `CreateTaskRequestSchema` (title required, rest optional); `UpdateTaskRequestSchema` (all optional, version required); `ForceCompleteTaskRequestSchema` (version); `TaskForceCompleteResponseSchema` (`{data: {task, unlocked_achievements[], streak}}`); `TaskDeleteResponseSchema` (`{data: {tombstone_id, recoverable_until}}`)
- [ ] T037 [US2] Create `frontend/src/mocks/data/tasks.fixture.ts` — export `tasksFixture: Task[]` with 5+ tasks covering all priorities, one completed, one with due_date in past, one with subtask_count > 0
- [ ] T038 [US2] Create `frontend/src/mocks/handlers/tasks.handlers.ts` — in-memory task store; `GET /api/v1/tasks` with filters (completed, priority, hidden, archived); `GET /api/v1/tasks/:id`; `POST /api/v1/tasks`; `PATCH /api/v1/tasks/:id` (validate version field); `DELETE /api/v1/tasks/:id` (soft-delete: set hidden=true); `POST /api/v1/tasks/:id/force-complete` (set completed, return with mock unlocked_achievements); 100-500ms simulated latency; return 404 with `{error: {code:"RESOURCE_NOT_FOUND"}}` for missing tasks
- [ ] T039 [P] [US2] Create `frontend/src/lib/hooks/useTasks.ts` — `useTasks(filters?)` querying `GET /tasks` with URLSearchParams; `useTask(id)` querying `GET /tasks/:id`; `useCreateTask()` mutating `POST /tasks` invalidating `['tasks']`; `useUpdateTask()` mutating `PATCH /tasks/:id`; `useDeleteTask()` mutating `DELETE /tasks/:id`; `useForceCompleteTask()` mutating `POST /tasks/:id/force-complete`; all mutations use `TaskSchema` or relevant schema for Zod validation
- [ ] T040 [US2] Create `frontend/src/lib/stores/pending-completions.store.ts` — Zustand: `{ pendingIds: Set<string>, togglePending(id), hasPending(id), clearAll() }`; used for optimistic checkbox UI
- [ ] T041 [P] [US2] Create `frontend/src/components/tasks/TaskCard.tsx` — display task card with: priority color left-border (red/yellow/green), checkbox using `pending-completions.store` for optimistic state (green bg when pending), title with strikethrough if completed, description (2-line clamp), priority badge, subtask count (`subtask_count/subtask_completed_count` from schema), estimated_duration, due_date with color coding (red=overdue, yellow=<24h), focus mode button (on hover, top-right, navigates to `/dashboard/focus`), expand/collapse subtasks section; click navigates to `/dashboard/tasks/:id`
- [ ] T042 [P] [US2] Create `frontend/src/components/tasks/TaskProgressBar.tsx` — progress bar showing `subtask_completed_count / subtask_count * 100`%; animated fill; accessible `role="progressbar"` with aria-valuenow/min/max
- [ ] T043 [US2] Create `frontend/src/components/tasks/TaskList.tsx` — grid of `TaskCard` components; accepts `tasks: Task[]`; empty state with "No tasks yet" illustration; loading skeleton (3 placeholder cards); error state with retry button
- [ ] T044 [US2] Create `frontend/src/components/tasks/TaskForm.tsx` — controlled form for create/edit: title input (required, 1-500), description textarea (0-5000), priority select (low/medium/high), due_date picker (datetime-local), estimated_duration number input (1-720 min); validate with Zod `CreateTaskRequestSchema` on submit; show field-level validation errors
- [ ] T045 [US2] Create `frontend/src/lib/stores/new-task-modal.store.ts` — Zustand: `{ isOpen: boolean, open(), close() }`
- [ ] T046 [US2] Create `frontend/src/components/tasks/NewTaskModal.tsx` — Radix `Dialog` wrapping `TaskForm`; on submit call `useCreateTask().mutate()`; show loading spinner during mutation; close on success; use `new-task-modal.store` for open/close
- [ ] T047 [US2] Create `frontend/src/app/dashboard/tasks/page.tsx` — call `useTasks({ completed: false })` and render `TaskList`; floating "+ New Task" button triggering `NewTaskModal`; tab bar for All/Active/Completed; pass `completed: true` for completed tab
- [ ] T048 [US2] Create `frontend/src/app/dashboard/tasks/new/page.tsx` — full-page `TaskForm` as alternative to modal; redirect to `/dashboard/tasks/:id` on success
- [ ] T049 [US2] Create `frontend/src/app/dashboard/tasks/[id]/page.tsx` — call `useTask(id)`; display full task detail (`TaskDetailView`); show 404 error boundary if task not found
- [ ] T050 [US2] Create `frontend/src/components/tasks/TaskDetailView.tsx` — full task view: title (editable inline), description, priority badge, due date, estimated duration, focus time, completed_at, version; inline edit saves via `useUpdateTask()`; "Complete" button calls `useForceCompleteTask()`; "Delete" button with confirmation dialog calls `useDeleteTask()`; show undo toast on delete (30-day recovery)
- [ ] T051 [US2] Create `frontend/src/components/tasks/TaskMetadata.tsx` — reusable metadata row component (icon + label + value) used in `TaskDetailView` and `TaskCard`
- [ ] T052 [US2] Create `frontend/src/app/dashboard/tasks/[id]/edit/page.tsx` — `TaskForm` pre-filled with existing task data; submit calls `useUpdateTask()` with version field; redirect to task detail on success
- [ ] T053 [US2] Create `frontend/src/app/dashboard/tasks/completed/page.tsx` — call `useTasks({ completed: true })`; render `TaskList` with completed tasks; "Clear All" button for bulk archive
- [ ] T054 [US2] Create `frontend/src/app/dashboard/page.tsx` — dashboard home: "Today's Tasks" (due today), streak counter from achievements, quick-add note input, recent activity

**Checkpoint**: Full task CRUD working — user can create, read, update, delete, and complete tasks

---

## Phase 5: User Story 3 — Subtask Management (FR-003) P2

**Goal**: User can add up to 10 subtasks per task, check them off, and see aggregate progress

**Independent Test**: Open task detail → add 3 subtasks → check 2 → progress bar shows 66% → task card shows "2/3 subtasks" → delete 1 → limit allows adding another → try add 11th → error shown

### Implementation

- [ ] T055 [US3] Create `frontend/src/lib/schemas/subtask.schema.ts` — `SubtaskSchema` (id, task_id, title, completed, completed_at, created_at, updated_at); `CreateSubtaskRequestSchema` (title 1-200); `UpdateSubtaskRequestSchema` (title?, completed?); `DataResponseSchema(SubtaskSchema)` variants
- [ ] T056 [US3] Create `frontend/src/mocks/data/subtasks.fixture.ts` — export `subtasksFixture: Subtask[]` referencing task IDs from `tasksFixture`; mix completed and incomplete
- [ ] T057 [US3] Create `frontend/src/mocks/handlers/tasks.handlers.ts` — add to existing file: `GET /api/v1/tasks/:id/subtasks`; `POST /api/v1/tasks/:id/subtasks` (enforce max 10, return `NESTING_LIMIT_EXCEEDED` on overflow); `PATCH /api/v1/tasks/:id/subtasks/:subtaskId`; `DELETE /api/v1/tasks/:id/subtasks/:subtaskId`
- [ ] T058 [US3] Create `frontend/src/lib/hooks/useSubtasks.ts` — `useSubtasks(taskId)` querying `GET /tasks/:id/subtasks`; `useCreateSubtask()` mutating `POST /tasks/:id/subtasks`; `useUpdateSubtask()` mutating `PATCH /tasks/:id/subtasks/:id`; `useDeleteSubtask()` mutating `DELETE /tasks/:id/subtasks/:id`; all invalidate `['subtasks', taskId]` and `['tasks', taskId]`
- [ ] T059 [P] [US3] Create `frontend/src/components/tasks/SubTaskList.tsx` — list of subtask rows each with: checkbox (toggle via `useUpdateSubtask()`), title, delete button; optimistic checkbox toggle; show "0/N subtasks" header; loading state while toggling
- [ ] T060 [P] [US3] Create `frontend/src/components/tasks/AddSubTaskForm.tsx` — inline `<input>` + submit button; validate title not empty; call `useCreateSubtask()`; show `NESTING_LIMIT_EXCEEDED` error inline when at 10 subtasks; clear input on success
- [ ] T061 [US3] Create `frontend/src/components/tasks/AISubtasksGenerator.tsx` — "✨ Generate subtasks" button (Pro only); calls `POST /api/v1/tasks/:id/ai/subtasks`; shows loading state; renders returned suggestions as checkboxes; "Accept All" saves all via `useCreateSubtask()`; individual accept/reject per suggestion; decrement AI credits display; disabled if `effective_limits.daily_ai_credits === 0`
- [ ] T062 [US3] Integrate `SubTaskList` + `AddSubTaskForm` into `TaskDetailView` (`frontend/src/components/tasks/TaskDetailView.tsx`) — below task metadata; collapse/expand section; pass task.id to both
- [ ] T063 [US3] Integrate subtask expand/collapse into `TaskCard.tsx` — update existing expandable section to call `useSubtasks(task.id)` when expanded; fall back to `task.subtask_count` / `task.subtask_completed_count` for progress display in collapsed view (no extra API call)

**Checkpoint**: Subtasks fully functional with progress tracking and AI generation (Pro)

---

## Phase 6: User Story 4 — Focus Mode (FR-004) P2

**Goal**: User can enter full-screen distraction-free mode for a task, run a countdown timer, and have focus time recorded on task completion

**Independent Test**: Click focus icon on task → full-screen view opens → timer counts down from estimated_duration → pause/resume works → mark complete → task updated with focus_time_seconds → return to task list

### Implementation

- [ ] T064 [US4] Create `frontend/src/lib/stores/focus-mode.store.ts` — Zustand: `{ isActive: boolean, currentTaskId: string|null, startTime: Date|null, pausedAt: Date|null, elapsedSeconds: number, activate(taskId), deactivate(), pause(), resume() }`; `elapsedSeconds` accumulates only while not paused
- [ ] T065 [US4] Create `frontend/src/components/focus/FocusTimer.tsx` — countdown from `task.estimated_duration * 60` seconds; display as `MM:SS`; animated ring SVG (reduced-motion: plain text fallback); pause/resume button; "Complete Task" button; "Exit" button with confirmation (unsaved focus time warning); update store `elapsedSeconds` every second via `setInterval`
- [ ] T066 [US4] Create `frontend/src/components/focus/FocusTaskView.tsx` — full-screen layout: task title (large), description, subtask checklist (toggle subtasks without leaving focus), `FocusTimer` bottom-center; keyboard: `Escape` shows exit confirmation, `Space` pauses/resumes; prevent scroll; `overflow-hidden` on body
- [ ] T067 [US4] Create `frontend/src/app/dashboard/focus/page.tsx` — render `FocusTaskView`; redirect to `/dashboard/tasks` if `!focusModeStore.isActive`; on "Complete Task" call `useForceCompleteTask()` then `focusModeStore.deactivate()`; PATCH task with `focus_time_seconds: store.elapsedSeconds` before completing; show achievement unlock toast if returned
- [ ] T068 [US4] Update `frontend/src/components/tasks/TaskCard.tsx` — focus icon button (eye icon, top-right, visible on hover): call `focusModeStore.activate(task.id)` then `router.push('/dashboard/focus')`; only show for incomplete tasks

**Checkpoint**: Focus mode fully functional with timer, pause/resume, and focus time tracking

---

## Phase 7: User Story 5 — Quick Notes (FR-005) P2

**Goal**: User can capture quick notes, view them in a list, archive old ones, and convert notes to tasks in one click

**Independent Test**: Open notes → add note "Call dentist tomorrow" → note appears in list → click "Convert to Task" → task created with note content as description → note marked archived → archived note visible in settings

### Implementation

- [ ] T069 [US5] Create `frontend/src/lib/schemas/note.schema.ts` — `NoteSchema` (id, user_id, content 1-2000, archived, voice_url, voice_duration_seconds, transcription_status, created_at, updated_at); `CreateNoteRequestSchema` (content); `UpdateNoteRequestSchema` (content?, archived?); response wrappers
- [ ] T070 [US5] Create `frontend/src/mocks/data/notes.fixture.ts` — export `notesFixture: Note[]` with 5 notes (some archived, one with voice_url)
- [ ] T071 [US5] Create `frontend/src/mocks/handlers/notes.handlers.ts` — `GET /api/v1/notes` with `archived` filter; `POST /api/v1/notes`; `PATCH /api/v1/notes/:id`; `DELETE /api/v1/notes/:id`; `POST /api/v1/notes/:id/convert` → creates task from note content, marks note archived, returns `{data: {task, note}}`; enforce max-20 notes limit for free tier (check fixture length)
- [ ] T072 [US5] Create `frontend/src/lib/hooks/useNotes.ts` — `useNotes(filters?)` querying notes; `useCreateNote()`, `useUpdateNote()`, `useDeleteNote()`, `useConvertNote()` mutations; invalidate `['notes']` and `['tasks']` on `useConvertNote` success
- [ ] T073 [P] [US5] Create `frontend/src/components/notes/NoteCard.tsx` — note card: content (5-line clamp), relative timestamp, "Convert to Task" button (calls `useConvertNote()`), "Archive" button, "Delete" button; archived notes shown with muted styling; voice_url → audio player element if present
- [ ] T074 [P] [US5] Create `frontend/src/components/notes/QuickNoteInput.tsx` — single-line text input with "Add Note" button; auto-expand to textarea after 50 chars; submit on Enter or button click; validates 1-2000 chars; clear on success; character counter (1800+ shows warning)
- [ ] T075 [US5] Create `frontend/src/app/dashboard/notes/page.tsx` — `QuickNoteInput` at top; `NoteCard` grid for active notes; empty state; loading skeleton
- [ ] T076 [US5] Create `frontend/src/app/dashboard/settings/archived-notes/page.tsx` — list of archived notes; "Unarchive" and "Delete" actions per note

**Checkpoint**: Notes capture, conversion to tasks, and archiving all functional

---

## Phase 8: User Story 6 — Achievement System (FR-008) P3

**Goal**: User earns achievements for task completion milestones, streaks, focus sessions, and note conversions; achievements unlock perks that increase limits

**Independent Test**: Complete 5 tasks → "First Steps" achievement fires → toast with achievement name and perk → `/achievements` page shows unlocked badge + progress toward next

### Implementation

- [ ] T077 [US6] Create `frontend/src/lib/schemas/achievement.schema.ts` — `AchievementDefinitionSchema` (id/code, name, message, category, threshold, perk_type, perk_value); `UserAchievementStateSchema` (lifetime_tasks_completed, current_streak, longest_streak, focus_completions, notes_converted, unlocked_achievements[]); `AchievementStatsSchema`; `AchievementProgressSchema` (id, name, current, threshold, unlocked); `EffectiveLimitsSchema` (max_tasks, max_notes, daily_ai_credits); `AchievementDataSchema` (stats, unlocked[], progress[], effective_limits); `AchievementUnlockSchema` (achievement_id, achievement_name, perk?)
- [ ] T078 [US6] Create `frontend/src/mocks/handlers/achievements.handlers.ts` — `GET /api/v1/achievements/me` returning `{data: {stats, unlocked, progress, effective_limits}}`; calculate effective_limits dynamically from unlocked perks; simulate `current_streak: 3` and `longest_streak: 7` in fixture
- [ ] T079 [US6] Create `frontend/src/lib/hooks/useAchievements.ts` — `useAchievements()` querying `/achievements/me`; `useAchievementNotifications.ts` subscribing to `useForceCompleteTask` mutation results and triggering toast on `unlocked_achievements.length > 0`
- [ ] T080 [P] [US6] Create `frontend/src/components/achievements/AchievementCard.tsx` — achievement tile: name, message, category badge, progress bar (`current/threshold`), locked/unlocked state (grayscale when locked), perk description if unlocked; animation on unlock (Framer Motion scale+glow, skip if reduced-motion)
- [ ] T081 [P] [US6] Create `frontend/src/components/achievements/StreakDisplay.tsx` — current streak with flame icon; longest streak secondary; last_completion_date; "grace period active" indicator if last completion was yesterday
- [ ] T082 [US6] Create `frontend/src/components/achievements/AchievementUnlockToast.tsx` — Radix `Toast` with gold border, trophy icon, achievement name + perk description; auto-dismiss after 6 seconds; no motion if reduced-motion; triggered via `useAchievementNotifications`
- [ ] T083 [US6] Create `frontend/src/app/dashboard/achievements/page.tsx` — `StreakDisplay` header; progress summary (lifetime tasks, focus sessions, notes converted); `AchievementCard` grid organized by category (Tasks / Streaks / Focus / Notes); highlight newly unlocked
- [ ] T084 [US6] Update `frontend/src/app/dashboard/page.tsx` (dashboard home) — add `StreakDisplay` widget; show "X tasks to next achievement" progress hint

**Checkpoint**: Achievement system unlocks on task completion, perks apply, streak tracked

---

## Phase 9: User Story 7 — Reminder System (FR-006) P3

**Goal**: Reminders fire as browser notifications and in-app toasts at the configured time (relative or absolute), and are never re-triggered after delivery

**Independent Test**: Create task with due_date = now+2min → add reminder "-1 minute" → wait 1 min → browser notification appears + in-app toast → refresh → reminder marked as fired → no re-trigger

### Implementation

- [ ] T085 [US7] Create `frontend/src/lib/schemas/reminder.schema.ts` — `ReminderSchema` (id, task_id, user_id, type `relative|absolute`, offset_minutes, scheduled_at, fired, fired_at, created_at, updated_at); `CreateReminderRequestSchema`; `UpdateReminderRequestSchema`
- [ ] T086 [US7] Create `frontend/src/mocks/data/reminders.fixture.ts` — export `remindersFixture: Reminder[]` with one unfired relative reminder (offset -15) linked to a task with due_date
- [ ] T087 [US7] Create `frontend/src/mocks/handlers/reminders.handlers.ts` — `GET /api/v1/reminders` (only unfired by default); `POST /api/v1/reminders`; `DELETE /api/v1/reminders/:id`; `POST /api/v1/reminders/:id/fire` (set fired=true, fired_at=now)
- [ ] T088 [US7] Create `frontend/src/lib/hooks/useReminders.ts` — `useReminders(taskId?)` querying reminders; `useCreateReminder()`, `useDeleteReminder()` mutations; invalidate `['reminders']`
- [ ] T089 [US7] Create `frontend/src/components/reminders/ReminderForm.tsx` — offset preset buttons (-15, -30, -60, -1440 min) + custom absolute datetime; show current reminders list with delete button; call `useCreateReminder()`; validate max 3 reminders per task
- [ ] T090 [US7] Integrate `ReminderForm` into `TaskDetailView.tsx` (`frontend/src/components/tasks/TaskDetailView.tsx`) — "Reminders" section below subtasks; show existing reminders as chips with delete (×) button
- [ ] T091 [US7] Create `frontend/public/service-worker.js` — SW v1.0.x; listen for `SET_API_URL`, `START_REMINDER_POLLING`, `STOP_REMINDER_POLLING` postMessages; on `START`: `setInterval(checkReminders, 60000)` + immediate check; `checkReminders` fetches `/reminders` + `/tasks`, calculates trigger times (`due_date + offset_minutes*60000` or `scheduled_at`), skips `fired=true`; shows `self.registration.showNotification()` with `requireInteraction: true, data.url = /dashboard/tasks/:id`; posts `{type: 'REMINDER_DUE', reminder, task}` to all clients; POSTs `/reminders/:id/fire`; `notificationclick` handler focuses/navigates existing tab or opens new
- [ ] T092 [US7] Create `frontend/src/lib/hooks/useNotifications.ts` — register SW, request `Notification.permission`, send `SET_API_URL` + `START_REMINDER_POLLING` postMessages on dashboard mount, `STOP_REMINDER_POLLING` on public page mount; listen for `REMINDER_DUE` postMessages and call `notificationStore.addToast()`

**Checkpoint**: Reminders fire on schedule, never repeat, browser + toast dual delivery works

---

## Phase 10: User Story 8 — Recurring Tasks (FR-007) P3

**Goal**: User can create a task template with an RRule recurrence pattern; completing an instance auto-generates the next due instance

**Independent Test**: Create weekly Monday template → complete this week's instance → next Monday instance appears in task list → pause template → complete instance → no new instance generated

### Implementation

- [ ] T093 [US8] Add `TaskTemplateSchema` to `frontend/src/lib/schemas/task.schema.ts` — (id, user_id, title, description, priority, estimated_duration, rrule, next_due, active, created_at, updated_at)
- [ ] T094 [US8] Create `frontend/src/lib/utils/recurrence.ts` — `parseRRule(rruleString): RRule`; `getNextOccurrence(rrule, after?: Date): Date|null`; `humanizeRRule(rrule): string` (e.g., "Every Monday"); `validateRRule(str): {valid: boolean, error?: string}`; use `rrule` npm package
- [ ] T095 [P] [US8] Create `frontend/src/components/recurrence/RecurrenceEditor.tsx` — UI for building RRule: frequency tabs (Daily/Weekly/Monthly/Custom); day-of-week picker for weekly; "starts on" date picker; preview of next 3 occurrences using `getNextOccurrence()`; raw RRULE string preview (collapsible for power users); calls `onChange(rruleString)` on change
- [ ] T096 [P] [US8] Create `frontend/src/components/recurrence/RecurrencePreview.tsx` — read-only humanized display of an rrule string: "Every Monday" with next occurrence date; uses `humanizeRRule()` + `getNextOccurrence()`
- [ ] T097 [US8] Add recurrence fields to `frontend/src/components/tasks/TaskForm.tsx` — "Make recurring?" toggle; when enabled, mount `RecurrenceEditor` and include `rrule` in task create payload; `template_id` shown as read-only for existing recurring instances
- [ ] T098 [US8] Update `useForceCompleteTask` in `frontend/src/lib/hooks/useTasks.ts` — after successful completion, if `task.template_id` is set, invalidate `['tasks']` to fetch the newly-generated next instance from backend
- [ ] T099 [US8] Create `frontend/src/app/dashboard/tasks/page.tsx` update — add "Templates" tab; show `TaskTemplateSchema` list from `GET /api/v1/task-templates`; pause/resume button per template; "View instances" link

**Checkpoint**: Recurring tasks auto-generate next instance on completion

---

## Phase 11: User Story 9 — AI Features (FR-009) P3 (Pro)

**Goal**: Pro users can generate subtasks via AI, get priority recommendations, and parse notes with natural language date/priority extraction

**Independent Test**: Pro user → task detail → "✨ Generate subtasks" → 5 suggestions returned → accept 3 → saved → AI credit decremented by 1; free user → button disabled

### Implementation

- [ ] T100 [US9] Create `frontend/src/lib/schemas/ai.schema.ts` — `AISubtaskSuggestionSchema` (title, estimated_duration?); `AISubtaskResponseSchema` (data: {suggestions: AISubtaskSuggestion[]}); `AIPriorityResponseSchema` (data: {priority, reasoning}); `AINoteParseResponseSchema` (data: {title, description?, due_date?, priority?, estimated_duration?})
- [ ] T101 [US9] Create `frontend/src/mocks/handlers/ai.handlers.ts` — `POST /api/v1/tasks/:id/ai/subtasks` returning 5 mock suggestions; `POST /api/v1/tasks/:id/ai/priority` returning `{priority: 'high', reasoning: '...'}`;  `POST /api/v1/notes/:id/parse` returning parsed note metadata; decrement `daily_ai_credits_used` on each call
- [ ] T102 [US9] Create `frontend/src/lib/hooks/useAI.ts` — `useGenerateSubtasks(taskId)` mutation; `useGetPriorityRecommendation(taskId)` mutation; `useParseNote(noteId)` mutation; each uses `apiClient.post` with respective schemas; surface `ApiError` with code `CREDITS_EXHAUSTED` for 402 responses
- [ ] T103 [US9] Update `frontend/src/components/tasks/AISubtasksGenerator.tsx` — hook up to real `useGenerateSubtasks()`; check `effective_limits.daily_ai_credits > 0` before enabling button; show "X credits remaining" badge; call `useCreateSubtask()` for each accepted suggestion
- [ ] T104 [US9] Add note parsing to `frontend/src/components/notes/NoteCard.tsx` — "Smart Convert" button (Pro, calls `useParseNote()` before `useConvertNote()`); shows preview of parsed fields (title, due_date, priority) in a confirmation popover before creating task; falls back to plain convert for free tier

**Checkpoint**: AI features (subtask generation, note parsing) functional for Pro users; gracefully disabled for free

---

## Phase 12: User Story 10 — Command Palette (FR-010) P4

**Goal**: Power user can open command palette with Cmd+K, fuzzy-search commands, navigate with arrows, execute with Enter

**Independent Test**: Press Cmd+K → palette opens → type "foc" → "Start Focus Mode" option highlighted → press Enter → focus mode activates for first incomplete task → press Escape → palette closes

### Implementation

- [ ] T105 [US10] Create `frontend/src/lib/stores/command-palette.store.ts` — Zustand: `{ isOpen: boolean, query: string, selectedIndex: number, open(), close(), setQuery(q), setSelectedIndex(n) }`
- [ ] T106 [US10] Create `frontend/src/lib/commands/task-commands.ts` — command definitions: `{ id, name, icon, category, aliases, action(router, stores) }`; categories: Navigation, Tasks, Notes, Focus; commands include "Go to Tasks", "New Task", "Start Focus Mode", "New Note", "Go to Achievements"; `action` callbacks use `router.push()` or store dispatch
- [ ] T107 [US10] Create `frontend/src/components/layout/CommandPalette.tsx` — Radix `Dialog` triggered by store; `<input>` for search query; Fuse.js `new Fuse(commands, {keys:['name','aliases'], threshold: 0.4})`; filtered results list with keyboard nav (ArrowUp/Down, Enter to execute, Escape to close); highlight matched characters; group by category; max 8 results; accessible `role="listbox"` + `role="option"` + `aria-selected`
- [ ] T108 [US10] Register global `Cmd+K` / `Ctrl+K` listener in `frontend/src/app/dashboard/layout.tsx` — `window.addEventListener('keydown', handler)` in `useEffect`; call `commandPaletteStore.open()`; cleanup on unmount
- [ ] T109 [US10] Mount `CommandPalette` in `frontend/src/app/dashboard/layout.tsx` — always rendered (not conditionally) so Radix can animate open/close; controlled by `isOpen` from store

**Checkpoint**: Command palette opens, fuzzy-searches, and executes navigation + task commands

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Fix P0 gaps from spec.md §VII, accessibility, performance, and error handling

- [ ] T110 [P] Fix P0 Gap 1: Move auth token to IndexedDB in `frontend/src/lib/utils/token-storage.ts` — `getToken()`, `setToken()`, `removeToken()` using `indexedDB` (with `localStorage` fallback); update `AuthContext.tsx` and `service-worker.js` to use shared IndexedDB key so SW can read auth token for reminder polling
- [ ] T111 [P] Fix P0 Gap 2: Add React Error Boundary to `frontend/src/components/errors/ErrorBoundary.tsx` — class component catching render errors; fallback UI with "Something went wrong" message + "Reload" button + error details (dev only); wrap `RootLayout` children in `frontend/src/app/layout.tsx`
- [ ] T112 Fix P0 Gap 3: Add conflict resolution modal to `frontend/src/components/tasks/ConflictResolutionModal.tsx` — shown when `useUpdateTask` fails with `VERSION_CONFLICT`; display side-by-side diff (Your version vs Server version); three options: "Keep mine" (force update), "Take theirs" (discard changes), "Cancel"
- [ ] T113 [P] Add `prefers-reduced-motion` guard to all Framer Motion animations — use `useReducedMotion()` hook to conditionally pass `transition={{ duration: 0 }}` or `variants={null}` across `AchievementCard`, `AchievementUnlockToast`, `FocusTimer` ring animation
- [ ] T114 [P] Add rate limiting to API mutations — create `frontend/src/lib/utils/rate-limiter.ts` with `createRateLimiter(maxCalls, windowMs)` returning a guard function; wrap `useCreateTask`, `useCreateSubtask`, `useCreateNote` mutationFns with 10 calls/second limit
- [ ] T115 [P] Implement optimistic updates in `useForceCompleteTask` — immediately update task in query cache before API call resolves; revert on error using `onMutate` / `onError` TanStack Query callbacks
- [ ] T116 [P] Add bundle analyzer check — run `ANALYZE=true next build` in CI; fail build if main chunk > 500KB gzipped; document in `README.md`
- [ ] T117 [P] Configure `next.config.ts` security headers — `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=()`, basic CSP blocking inline scripts
- [ ] T118 [P] Add `frontend/src/app/dashboard/settings/hidden-tasks/page.tsx` — list of `hidden: true` tasks with "Restore" and "Permanently Delete" actions; use `useUpdateTask({ hidden: false })` for restore
- [ ] T119 [P] Add `frontend/src/app/dashboard/profile/page.tsx` — display user avatar, name, email, timezone; edit name + timezone via `usersService.updateProfile()`; avatar from Google (read-only)
- [ ] T120 [P] Add `frontend/src/app/dashboard/settings/page.tsx` — settings hub: links to hidden-tasks, archived-notes, profile; notification permission toggle (calls `Notification.requestPermission()`); theme toggle placeholder; data export button (placeholder)
- [ ] T121 [P] Add onboarding tour — integrate `driver.js`; create `frontend/src/components/onboarding/OnboardingTour.tsx`; auto-start on first login (check `localStorage.onboarding_complete`); tour steps: Sidebar, Task list, New Task button, Focus mode icon, Notes; mark complete on finish

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 ⚠️ BLOCKS everything
- **Phase 3 (US1 Auth)**: Depends on Phase 2 — can start after Foundational
- **Phase 4 (US2 Tasks)**: Depends on Phase 2 + Phase 3 (needs user context)
- **Phase 5–11 (US3–US9)**: All depend on Phase 2 + 4 (tasks are core); can proceed in parallel with each other
- **Phase 12 (US10 Command Palette)**: Depends on Phase 4 (needs tasks), Phase 6 (needs focus), Phase 7 (needs notes)
- **Phase 13 (Polish)**: Depends on all user story phases

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|-----------|----------------------|
| US1 Auth | Foundational | — |
| US2 Tasks | US1 | — |
| US3 Subtasks | US2 | US4, US5 |
| US4 Focus | US2 | US3, US5 |
| US5 Notes | US2 | US3, US4 |
| US6 Achievements | US2 (completion events) | US7, US8, US9 |
| US7 Reminders | US2 (task context) | US6, US8, US9 |
| US8 Recurrence | US2 (task schema) | US6, US7, US9 |
| US9 AI Features | US3 (subtasks), US5 (notes) | US6, US7, US8 |
| US10 Command Palette | US2, US4, US5 | US6–US9 |

### Within Each User Story

- Schemas → Fixtures → Mock Handlers → Hooks → Components → Page
- `[P]` components within a story can be built simultaneously

---

## Parallel Execution Examples

### Parallel Group A: Foundational UI (Phase 2)
```
Task: T020 – Sidebar.tsx
Task: T021 – Header.tsx
Task: T024 – UI components (Button, Input, Dialog, etc.)
```

### Parallel Group B: After Foundational
```
Task: T028–T035 (US1 Auth)      ← Developer A
Task: T036–T054 (US2 Tasks)     ← Developer B (after US1 complete)
```

### Parallel Group C: After US2 Tasks
```
Task: T055–T063 (US3 Subtasks)  ← Developer A
Task: T064–T068 (US4 Focus)     ← Developer B
Task: T069–T076 (US5 Notes)     ← Developer C
```

---

## Implementation Strategy

### MVP First (Phases 1–4 only)
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (API client, auth, layout, MSW)
3. Complete Phase 3: US1 Auth
4. Complete Phase 4: US2 Task Management (core CRUD)
5. **STOP and VALIDATE**: User can sign in, create/complete/delete tasks
6. Deploy MVP

### Incremental Delivery
- **v0.1**: Setup + Foundation → bare skeleton
- **v0.2**: Auth → login/logout working
- **v0.3**: Task CRUD → core value delivered (MVP!)
- **v0.4**: Subtasks + Focus Mode → enhanced productivity
- **v0.5**: Notes + Achievements → habit loop complete
- **v0.6**: Reminders + Recurring → automation added
- **v0.7**: AI Features (Pro) → monetisation tier
- **v0.8**: Command Palette + Polish → power-user polish

### P0 Gaps (Must Fix Before Public Launch)
- **T110**: SW token access (reminders broken without this)
- **T111**: Error boundary (crashes without this)
- **T112**: Conflict resolution UI (data integrity without this)

---

## Notes

- `[P]` = different files, no shared state dependencies — safe to parallelize
- `[USN]` = maps task to functional requirement from `spec.md`
- Every schema change must also update MSW fixtures/handlers to match
- Commit after each phase checkpoint to enable clean rollback
- `frontend/` path prefix omitted in descriptions for brevity but all paths are relative to repo root
- Total task count: **121 tasks** across **13 phases**
- Test approach: MSW mocks real API at network level — no separate unit tests needed for happy paths; add tests for schema validation and utility functions if coverage < 80%
