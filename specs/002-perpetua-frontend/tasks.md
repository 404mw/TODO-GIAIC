# Tasks: Perpetua Flow Frontend

**Input**: Design documents from `/specs/002-perpetua-frontend/`
**Prerequisites**: [plan.md](./plan.md) ✅, [spec.md](./spec.md) ✅ (v1.5.0 — sp.analyze remediations v5: template endpoints Appendix A, T099 path fix, AI credit env-absent, T177 route transition, T112 Phase 14 slot, T171 → Phase 14, T175/T176 → Phase 15)
**Tests**: V1 test suite exists and passes (`frontend/tests/`). Tests are not formally mapped to task IDs.
Use `/sp.tasks` with `--tdd` flag to generate test-mapped tasks for new phases.
V1 test-to-spec mapping is documented in Phase 16. Constitution §VIII deviation recorded in `spec.md` §X.5.
**Organization**: Phases 1–13 represent initial implementation (structurally complete — code exists; T112 reopened per sp.analyze C3; T157-T159 reclassified to Phase 14 per sp.analyze C2); Phase 14 is the Bug Fix Sprint + reclassified a11y + navigation guard; Phase 15 is Observability (NFR-006); Phase 16 is Test Coverage documentation

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which functional requirement this belongs to (US1–US13)
- Paths use `frontend/src/` prefix per plan.md Layer Structure
- `[X]` = done (initial implementation); `[ ]` = open (bug fix or missing feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project skeleton, tooling, and base configuration

- [X] T001 Initialize Next.js 16 project with TypeScript 5 via `npx create-next-app@latest frontend --typescript --tailwind --app`
- [X] T002 Install all dependencies from plan.md: `npm install @tanstack/react-query zustand zod @radix-ui/react-dialog framer-motion fuse.js rrule date-fns lucide-react`
- [X] T003 [P] Install dev dependencies: `npm install -D msw jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom @types/jest`
- [X] T004 [P] Configure `tsconfig.json` with strict mode, path aliases (`@/*` → `src/*`), and `moduleResolution: bundler`
- [X] T005 [P] Configure `eslint.config.js` with Next.js preset and import ordering rules
- [X] T006 Configure `jest.config.ts` with jsdom environment, MSW server setup, and module aliases matching tsconfig
- [X] T007 [P] Configure `tailwind.config.ts` with dark mode class strategy, custom fonts (Geist), and content paths
- [X] T008 [P] Configure `next.config.ts` with security headers (X-Frame-Options, CSP, HSTS), bundle analyzer integration
- [X] T009 Create `.env.local` template with `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID` — add `.env.local` to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure every user story depends on: API client, schemas, auth context, layout shell, MSW mocks

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create `frontend/src/lib/schemas/common.schema.ts` — define shared enums: `PrioritySchema` (`low|medium|high`), `CompletedBySchema` (`manual|auto|force`), `UserTierSchema` (`free|pro`), `TranscriptionStatusSchema` (`pending|completed|failed`)
- [X] T011 [P] Create `frontend/src/lib/schemas/response.schema.ts` — define `DataResponseSchema<T>` (`{data: T}`) and `PaginatedResponseSchema<T>` (`{data: T[], pagination: {page, per_page, total, total_pages}}`) generic wrappers
- [X] T012 Create `frontend/src/lib/api/client.ts` — implement `ApiError` class (status, code, message, details, request_id) and `apiClient` with `get`, `post`, `patch`, `put`, `delete` methods; inject `Authorization: Bearer` header from auth token storage; add `Idempotency-Key: crypto.randomUUID()` on mutating methods; handle both error formats `{"error":{...}}` and `{"code":...,"message":...}`; validate response against optional Zod schema
- [X] T013 Create `frontend/src/lib/contexts/AuthContext.tsx` — `AuthProvider` with `user: User|null`, `isAuthenticated`, `isLoading`, `logout()`, `refetch()`, `refreshTokenIfNeeded()`; on mount for protected routes (`/dashboard/*`) call `/users/me` using stored token; handle `TOKEN_EXPIRED` by attempting refresh; skip fetch on public routes
- [X] T014 Create `frontend/src/lib/hooks/useAuth.ts` — `useAuth()` hook that reads `AuthContext`, throws if used outside `AuthProvider`
- [X] T015 [P] Create `frontend/src/lib/hooks/useToast.ts` — wrapper around Radix `Toast` or internal toast store, exposing `toast(message, options)` function
- [X] T016 [P] Create `frontend/src/lib/hooks/useLocalStorage.ts` — `useLocalStorage<T>(key, defaultValue)` hook with SSR guard (`typeof window === 'undefined'`)
- [X] T017 [P] Create `frontend/src/lib/hooks/useReducedMotion.ts` — `useReducedMotion()` hook using `window.matchMedia('(prefers-reduced-motion: reduce)')`
- [X] T018 Create `frontend/src/app/layout.tsx` (root layout) — wrap with `AuthProvider`, `QueryClientProvider` (TanStack Query), `ToastProvider` (Radix); load Geist font; set `<html lang="en">`
- [X] T019 Create `frontend/src/app/dashboard/layout.tsx` — protected layout with `Sidebar` + `Header` components; redirect to `/login` if `!isAuthenticated && !isLoading`
- [X] T020 [P] Create `frontend/src/components/layout/Sidebar.tsx` — left nav with links to `/dashboard`, `/dashboard/tasks`, `/dashboard/notes`, `/dashboard/focus`, `/dashboard/achievements`, `/dashboard/settings`; use `useSidebarStore` for collapsed state; persist collapsed in localStorage
- [X] T021 [P] Create `frontend/src/components/layout/Header.tsx` — top bar with user avatar, user name, logout button; use `useAuth()` to get user; dropdown menu via Radix `DropdownMenu`
- [X] T022 Create `frontend/src/lib/stores/sidebar.store.ts` — Zustand store: `{ isCollapsed: boolean, toggle: () => void }`; persist to `localStorage`
- [X] T023 [P] Create `frontend/src/lib/stores/notification.store.ts` — Zustand store: `{ toasts: Toast[], addToast(msg, type), removeToast(id) }`
- [X] T024 [P] Create `frontend/src/components/ui/` — Radix UI wrappers: `Button.tsx`, `Input.tsx`, `Dialog.tsx`, `Badge.tsx`, `Card.tsx`, `Select.tsx`, `Popover.tsx`, `Toast.tsx`; apply Tailwind utility classes; export variants via `class-variance-authority`
- [X] T025 Create `frontend/src/mocks/server.ts` — MSW Node server (`setupServer(...handlers)`); **not used in Jest** (app is in production, tests use `jest.fn()` mocks instead); kept as optional dev tooling
- [X] T026 Create `frontend/src/mocks/browser.ts` — MSW browser worker (`setupWorker(...handlers)`); **not required** (live API available); opt-in via `NEXT_PUBLIC_MSW_ENABLED=true` for offline development only
- [X] T027 Create `frontend/src/mocks/handlers/index.ts` — re-exports all handler files; useful as API contract documentation; not a test dependency

**Checkpoint**: API client, auth context, and layout shell ready — user story implementation can begin

---

## Phase 3: User Story 1 — Authentication (FR-001) 🎯 MVP

**Goal**: User can sign in with Google, session persists, tokens refresh silently, logout clears state

**Independent Test**: Open `/login` → click "Sign in with Google" → redirected to `/dashboard` → refresh page → still authenticated → click logout → redirected to `/login`

### Implementation

- [X] T028 [US1] Create `frontend/src/lib/schemas/user.schema.ts` — `UserSchema` (id, google_id, email, name, avatar_url, timezone, tier); `UpdateUserRequestSchema` (name?, timezone?); `UserResponseSchema = DataResponseSchema(UserSchema)`; export all types
- [X] T029 [US1] Create `frontend/src/lib/schemas/auth.schema.ts` — `AuthResponseSchema` (access_token, refresh_token, token_type, expires_in); `RefreshTokenRequestSchema` (refresh_token); export all types
- [X] T030 [US1] Create `frontend/src/lib/services/auth.service.ts` — `authService.exchangeCode(code)` calling `POST /auth/google/callback`; `authService.refreshTokens(token)` calling `POST /auth/refresh`; `authService.logout(token)` calling `POST /auth/logout`; responses NOT wrapped in `DataResponse`
- [X] T031 [US1] Create `frontend/src/lib/services/users.service.ts` — `usersService.getCurrentUser()` calling `GET /users/me` returning `UserResponseSchema`; `usersService.updateProfile(data)` calling `PATCH /users/me`
- [X] T032 [US1] Create `frontend/src/app/login/page.tsx` — centered card with `@react-oauth/google` `GoogleLogin` button; on success call `authService.exchangeCode(code)`, store tokens securely (see T135 for HttpOnly cookie migration), redirect to `/dashboard`; show error state on failure
- [X] T033 [US1] Create `frontend/src/app/auth/callback/page.tsx` — handle OAuth redirect; parse `?code=` param; call `authService.exchangeCode(code)`; store tokens; redirect to `/dashboard`
- [X] T034 [US1] Create `frontend/src/mocks/data/user.fixture.ts` — export `userFixture: User` with realistic test data (UUID, email, name, avatar)
- [X] T035 [US1] Create `frontend/src/mocks/handlers/user.handlers.ts` — `GET /api/v1/users/me` returning `{data: userFixture}`; `PATCH /api/v1/users/me` merging body with fixture; `POST /api/v1/auth/google/callback` returning mock tokens; `POST /api/v1/auth/refresh` returning rotated mock tokens; `POST /api/v1/auth/logout` returning 200

**Checkpoint**: Auth flow complete — can sign in, persist session, refresh tokens, and logout

---

## Phase 4: User Story 2 — Task Management (FR-002) 🎯 MVP

**Goal**: User can create, read, update, delete, and complete tasks with full metadata (priority, due date, estimated duration, version locking)

**Independent Test**: Create task → view in list → open detail → edit title → mark complete → view in completed list → soft-delete → confirm hidden; all without subtasks or reminders

### Implementation

- [X] T036 [US2] Create `frontend/src/lib/schemas/task.schema.ts` — full `TaskSchema` (id, user_id, template_id, title, description, priority, due_date, estimated_duration, focus_time_seconds, completed, completed_at, completed_by, hidden, archived, subtask_count, subtask_completed_count, created_at, updated_at, **version**); `TaskDetailSchema` extending with `subtasks[]` and `reminders[]`; `TaskTemplateSchema`; `CreateTaskRequestSchema` (title required, rest optional); `UpdateTaskRequestSchema` (all optional, **version required — must always be included**); `ForceCompleteTaskRequestSchema` (**version** required); `ForceCompleteResponseSchema` (`{data: {task: TaskSchema, unlocked_achievements: [{id, name, perk_type, perk_value}][], streak: number}}`); `TaskDeleteResponseSchema` (`{data: {tombstone_id, recoverable_until}}`)
- [X] T037 [US2] Create `frontend/src/mocks/data/tasks.fixture.ts` — export `tasksFixture: Task[]` with 5+ tasks covering all priorities, one completed, one with due_date in past, one with subtask_count > 0
- [X] T038 [US2] Create `frontend/src/mocks/handlers/tasks.handlers.ts` — in-memory task store; `GET /api/v1/tasks` with filters (completed, priority, hidden, archived); `GET /api/v1/tasks/:id`; `POST /api/v1/tasks`; `PATCH /api/v1/tasks/:id` (validate version field present — reject 400 if missing); `DELETE /api/v1/tasks/:id` (soft-delete: set hidden=true); `POST /api/v1/tasks/:id/force-complete` with body `{version}` (set completed, increment version, return `{data:{task, unlocked_achievements, streak}}`); 100-500ms simulated latency; return 404 with `{error: {code:"RESOURCE_NOT_FOUND"}}` for missing tasks; return 409 with `{error: {code:"VERSION_CONFLICT"}}` on version mismatch
- [X] T039 [P] [US2] Create `frontend/src/lib/hooks/useTasks.ts` — `useTasks(filters?)` querying `GET /tasks` with URLSearchParams; `useTask(id)` querying `GET /tasks/:id`; `useCreateTask()` mutating `POST /tasks` invalidating `['tasks']`; `useUpdateTask()` mutating `PATCH /tasks/:id` — **version field MUST always be included in the mutation payload**; `useDeleteTask()` mutating `DELETE /tasks/:id`; **`useForceCompleteTask()` mutating `POST /tasks/:id/force-complete` with body `{version: number}` and response parsed against `ForceCompleteResponseSchema` — `{data:{task, unlocked_achievements[], streak}}`**; no `useCompleteTask` or `useAutoCompleteTask` — these endpoints do not exist
- [X] T040 [US2] Create `frontend/src/lib/stores/pending-completions.store.ts` — Zustand: `{ pendingIds: Set<string>, togglePending(id), hasPending(id), clearAll() }`; used for optimistic checkbox UI
- [X] T041 [P] [US2] Create `frontend/src/components/tasks/TaskCard.tsx` — display task card with: priority color left-border (red/yellow/green), checkbox using `pending-completions.store` for optimistic state (green bg when pending), title with strikethrough if completed, description (2-line clamp), priority badge, subtask count (`subtask_count/subtask_completed_count` from schema), estimated_duration, due_date with color coding (red=overdue, yellow=<24h), focus mode button (on hover, top-right, navigates to `/dashboard/focus`), expand/collapse subtasks section; click navigates to `/dashboard/tasks/:id`
- [X] T042 [P] [US2] Create `frontend/src/components/tasks/TaskProgressBar.tsx` — progress bar showing `subtask_completed_count / subtask_count * 100`%; animated fill; accessible `role="progressbar"` with aria-valuenow/min/max
- [X] T043 [US2] Create `frontend/src/components/tasks/TaskList.tsx` — grid of `TaskCard` components; accepts `tasks: Task[]`; empty state with "No tasks yet" illustration; loading skeleton (3 placeholder cards); error state with retry button
- [X] T044 [US2] Create `frontend/src/components/tasks/TaskForm.tsx` — controlled form for create/edit: title input (required, 1-500), description textarea (0-5000), priority select (low/medium/high), due_date picker (datetime-local), estimated_duration number input (1-720 min); validate with Zod `CreateTaskRequestSchema` on submit; show field-level validation errors
- [X] T045 [US2] Create `frontend/src/lib/stores/new-task-modal.store.ts` — Zustand: `{ isOpen: boolean, open(), close() }`
- [X] T046 [US2] Create `frontend/src/components/tasks/NewTaskModal.tsx` — Radix `Dialog` wrapping `TaskForm`; on submit call `useCreateTask().mutate()`; show loading spinner during mutation; close on success; use `new-task-modal.store` for open/close
- [X] T047 [US2] Create `frontend/src/app/dashboard/tasks/page.tsx` — call `useTasks({ completed: false })` and render `TaskList`; floating "+ New Task" button triggering `NewTaskModal`; tab bar for All/Active/Completed; pass `completed: true` for completed tab
- [X] T048 [US2] Create `frontend/src/app/dashboard/tasks/new/page.tsx` — full-page `TaskForm` as alternative to modal; redirect to `/dashboard/tasks/:id` on success
- [X] T049 [US2] Create `frontend/src/app/dashboard/tasks/[id]/page.tsx` — call `useTask(id)`; display full task detail (`TaskDetailView`); show 404 error boundary if task not found
- [X] T050 [US2] Create `frontend/src/components/tasks/TaskDetailView.tsx` — full task view: title (editable inline), description, priority badge, due date, estimated duration, focus time, completed_at, version; inline edit saves via `useUpdateTask()` — **version field MUST always be included**; "Complete" button calls `useForceCompleteTask({ taskId: task.id, version: task.version })`; "Delete" button with confirmation dialog calls `useDeleteTask()`; toggle `completed` and `hidden` MUST include `version: task.version`; show undo toast on delete (30-day recovery); reminders section wired to real API (see T128)
- [X] T051 [US2] Create `frontend/src/components/tasks/TaskMetadata.tsx` — reusable metadata row component (icon + label + value) used in `TaskDetailView` and `TaskCard`
- [X] T052 [US2] Create `frontend/src/app/dashboard/tasks/[id]/edit/page.tsx` — `TaskForm` pre-filled with existing task data; submit calls `useUpdateTask()` **with version field**; redirect to task detail on success
- [X] T053 [US2] Create `frontend/src/app/dashboard/tasks/completed/page.tsx` — call `useTasks({ completed: true })`; render `TaskList` with completed tasks; "Clear All" button for bulk archive
- [X] T054 [US2] Create `frontend/src/app/dashboard/page.tsx` — dashboard home: "Today's Tasks" (due today), streak counter from achievements, quick-add note input, recent activity

**Checkpoint**: Full task CRUD working — user can create, read, update, delete, and complete tasks

---

## Phase 5: User Story 3 — Subtask Management (FR-003) P2

**Goal**: User can add up to 10 subtasks per task, check them off, and see aggregate progress

**Independent Test**: Open task detail → add 3 subtasks → check 2 → progress bar shows 66% → task card shows "2/3 subtasks" → delete 1 → limit allows adding another → try add 11th → error shown

### Implementation

- [X] T055 [US3] Create `frontend/src/lib/schemas/subtask.schema.ts` — `SubtaskSchema` (id, task_id, title, completed, completed_at, created_at, updated_at); `CreateSubtaskRequestSchema` (title 1-200); `UpdateSubtaskRequestSchema` (title?, completed?); `DataResponseSchema(SubtaskSchema)` variants
- [X] T056 [US3] Create `frontend/src/mocks/data/subtasks.fixture.ts` — export `subtasksFixture: Subtask[]` referencing task IDs from `tasksFixture`; mix completed and incomplete
- [X] T057 [US3] Update `frontend/src/mocks/handlers/tasks.handlers.ts` (created in T038) — add subtask handlers to existing file: `GET /api/v1/tasks/:id/subtasks`; `POST /api/v1/tasks/:id/subtasks` (enforce max 10, return `NESTING_LIMIT_EXCEEDED` on overflow); `PATCH /api/v1/tasks/:id/subtasks/:subtaskId`; `DELETE /api/v1/tasks/:id/subtasks/:subtaskId`
- [X] T058 [US3] Create `frontend/src/lib/hooks/useSubtasks.ts` — `useSubtasks(taskId, options?: {enabled?: boolean})` querying `GET /tasks/:id/subtasks`; **`enabled` option MUST be forwarded to the underlying `useQuery({ enabled: options?.enabled ?? true })`**; `useCreateSubtask()` mutating `POST /tasks/:id/subtasks`, `onSuccess` invalidates **`['subtasks', variables.taskId]` and `['tasks', variables.taskId]`** — **MUST use camelCase `taskId`, not snake_case `task_id` (which would be `undefined`)** ; `useUpdateSubtask()` mutating `PATCH /tasks/:id/subtasks/:id`, same camelCase invalidation; `useDeleteSubtask()` mutating `DELETE /tasks/:id/subtasks/:id`
- [X] T059 [P] [US3] Create `frontend/src/components/tasks/SubTaskList.tsx` — list of subtask rows each with: checkbox (toggle via `useUpdateSubtask()`), title, delete button; optimistic checkbox toggle; show "0/N subtasks" header; loading state while toggling
- [X] T060 [P] [US3] Create `frontend/src/components/tasks/AddSubTaskForm.tsx` — inline `<input>` + submit button; validate title not empty; call `useCreateSubtask()`; show `NESTING_LIMIT_EXCEEDED` error inline when at 10 subtasks; clear input on success
- [X] T061 [US3] Create `frontend/src/components/tasks/AISubtasksGenerator.tsx` — "✨ Generate subtasks" button (Pro only); calls `POST /api/v1/tasks/:id/ai/subtasks`; shows loading state; renders returned suggestions as checkboxes; "Accept All" saves all via `useCreateSubtask()`; individual accept/reject per suggestion; decrement AI credits display; disabled if `effective_limits.daily_ai_credits === 0`
- [X] T062 [US3] Integrate `SubTaskList` + `AddSubTaskForm` into `TaskDetailView` (`frontend/src/components/tasks/TaskDetailView.tsx`) — below task metadata; collapse/expand section; pass task.id to both
- [X] T063 [US3] Integrate subtask expand/collapse into `TaskCard.tsx` — **`useSubtasks(task.id, { enabled: isExpanded })` MUST be called with `enabled: isExpanded` so subtasks are NOT fetched for collapsed cards**; fall back to `task.subtask_count` / `task.subtask_completed_count` for progress display in collapsed view (no extra API call)
  > ⚠️ **Code exists but has bug** — plan.md §XI.3 confirms implementation calls `useSubtasks(task.id)` **unconditionally**; acceptance criteria not verified per preamble ([X] = code exists, not correctness); fixed by T122

**Checkpoint**: Subtasks fully functional with progress tracking and AI generation (Pro)

---

## Phase 6: User Story 4 — Focus Mode (FR-004) P2

**Goal**: User can enter full-screen distraction-free mode for a task, run a countdown timer, and have focus time recorded on task completion

**Independent Test**: Click focus icon on task → full-screen view opens → timer counts down from estimated_duration → pause/resume works → mark complete → task updated with focus_time_seconds → return to task list

### Implementation

- [X] T064 [US4] Create `frontend/src/lib/stores/focus-mode.store.ts` — Zustand: `{ isActive: boolean, currentTaskId: string|null, startTime: Date|null, pausedAt: Date|null, elapsedSeconds: number, activate(taskId), deactivate(), pause(), resume() }`; `elapsedSeconds` accumulates only while not paused
- [X] T065 [US4] Create `frontend/src/components/focus/FocusTimer.tsx` — countdown from `task.estimated_duration * 60` seconds; display as `MM:SS`; animated ring SVG (reduced-motion: plain text fallback); pause/resume button; "Complete Task" button; "Exit" button with confirmation (unsaved focus time warning); update store `elapsedSeconds` every second via `setInterval`; write `focus_elapsed_seconds_${taskId}` to `localStorage` on every second tick so focus time survives reload; on mount read from `localStorage` and restore `elapsedSeconds` if `focusModeStore.currentTaskId` matches the stored key
- [X] T066 [US4] Create `frontend/src/components/focus/FocusTaskView.tsx` — full-screen layout: task title (large), description, subtask checklist (toggle subtasks without leaving focus), `FocusTimer` bottom-center; keyboard: `Escape` shows exit confirmation, `Space` pauses/resumes; prevent scroll; `overflow-hidden` on body
- [X] T067 [US4] Create `frontend/src/app/dashboard/focus/page.tsx` — render `FocusTaskView`; redirect to `/dashboard/tasks` if `!focusModeStore.isActive`; on "Complete Task" call `useForceCompleteTask({ taskId, version: task.version })` then `focusModeStore.deactivate()`; PATCH task with `focus_time_seconds: store.elapsedSeconds` and `version` before completing; show achievement unlock toast if returned
- [X] T068 [US4] Update `frontend/src/components/tasks/TaskCard.tsx` — focus icon button (eye icon, top-right, visible on hover): call `focusModeStore.activate(task.id)` then `router.push('/dashboard/focus')`; only show for incomplete tasks

**Checkpoint**: Focus mode fully functional with timer, pause/resume, and focus time tracking

---

## Phase 7: User Story 5 — Quick Notes (FR-005) P2

**Goal**: User can capture quick notes, view them in a list, archive old ones, and convert notes to tasks in one click

**Independent Test**: Open notes → add note "Call dentist tomorrow" → note appears in list → click "Convert to Task" → task created with note content as description → note marked archived → archived note visible in settings

### Implementation

- [X] T069 [US5] Create `frontend/src/lib/schemas/note.schema.ts` — `NoteSchema` (id, user_id, **no task_id — notes are user-owned standalone entities, not nested under tasks**, content 1-2000, archived, voice_url, voice_duration_seconds, transcription_status, created_at, updated_at); `CreateNoteRequestSchema` (content); `UpdateNoteRequestSchema` (content?, archived?); response wrappers
- [X] T070 [US5] Create `frontend/src/mocks/data/notes.fixture.ts` — export `notesFixture: Note[]` with 5 notes (some archived, one with voice_url)
- [X] T071 [US5] Create `frontend/src/mocks/handlers/notes.handlers.ts` — **`GET /api/v1/notes`** with `archived` query param filter; **`POST /api/v1/notes`** (standalone, no taskId in path); **`PATCH /api/v1/notes/:id`** (not PUT); `DELETE /api/v1/notes/:id`; `POST /api/v1/notes/:id/convert` → creates task from note content, marks note archived, returns `{data: {task, note}}`; enforce max-20 notes per user limit for free tier; **no task-scoped note handlers** — notes are standalone, not nested under tasks (UPDATE-02)
- [X] T072 [US5] Create `frontend/src/lib/hooks/useNotes.ts` — **`useNotes()`** (no taskId param) querying `GET /api/v1/notes` — returns all notes for the authenticated user; `?archived=true` query param for archived notes; **`useCreateNote()` mutating `POST /api/v1/notes` — task-scoped `POST /tasks/:id/notes` MUST NOT be called**; **`useUpdateNote()` mutating `PATCH /api/v1/notes/${noteId}` — MUST use `apiClient.patch`, NOT `apiClient.put`**; `useDeleteNote()` mutating `DELETE /api/v1/notes/${noteId}`; `useConvertNote()` mutating `POST /api/v1/notes/${noteId}/convert`; invalidate `['notes']` and `['tasks']` on convert success (UPDATE-02)
- [X] T073 [P] [US5] Create `frontend/src/components/notes/NoteCard.tsx` — note card: content (5-line clamp), relative timestamp, "Convert to Task" button (calls `useConvertNote()`), "Archive" button, "Delete" button; archived notes shown with muted styling; voice_url → audio player element if present
- [X] T074 [P] [US5] Create `frontend/src/components/notes/QuickNoteInput.tsx` — single-line text input with "Add Note" button; auto-expand to textarea after 50 chars; submit on Enter or button click; validates 1-2000 chars; clear on success; character counter (1800+ shows warning); calls `useCreateNote({ content })` — **no `taskId` prop needed** (notes are standalone per UPDATE-02)
- [X] T075 [US5] Create `frontend/src/app/dashboard/notes/page.tsx` — `QuickNoteInput` at top; `NoteCard` grid for active notes; empty state; loading skeleton
- [X] T076 [US5] Create `frontend/src/app/dashboard/settings/archived-notes/page.tsx` — list of archived notes; "Unarchive" and "Delete" actions per note

**Checkpoint**: Notes capture, conversion to tasks, and archiving all functional

---

## Phase 8: User Story 6 — Achievement System (FR-008) P3

**Goal**: User earns achievements for task completion milestones, streaks, focus sessions, and note conversions; achievements unlock perks that increase limits

**Independent Test**: Complete 5 tasks → "First Steps" achievement fires → toast with achievement name and perk → `/achievements` page shows unlocked badge + progress toward next

### Implementation

- [X] T077 [US6] Create `frontend/src/lib/schemas/achievement.schema.ts` — `AchievementDefinitionSchema` (id/code, name, message, category, threshold, perk_type, perk_value); `UserAchievementStateSchema` (lifetime_tasks_completed, current_streak, longest_streak, focus_completions, notes_converted, **daily_ai_credits_used**, unlocked_achievements[]); `AchievementStatsSchema`; `AchievementProgressSchema` (id, name, current, threshold, unlocked); `EffectiveLimitsSchema` (max_tasks, max_notes, daily_ai_credits); `AchievementDataSchema` (stats, unlocked[], progress[], effective_limits); `AchievementUnlockSchema` (achievement_id, achievement_name, perk?)
  > ℹ️ `daily_ai_credits_used` added per sp.analyze M4: spec FR-009 references this field as the AI consumption counter; `EffectiveLimitsSchema.daily_ai_credits` is the cap, `daily_ai_credits_used` is the usage counter — both required
- [X] T078 [US6] Create `frontend/src/mocks/handlers/achievements.handlers.ts` — `GET /api/v1/achievements/me` returning `{data: {stats, unlocked, progress, effective_limits}}`; calculate effective_limits dynamically from unlocked perks; simulate `current_streak: 3` and `longest_streak: 7` in fixture
- [X] T079 [US6] Create `frontend/src/lib/hooks/useAchievements.ts` — `useAchievements()` querying `/achievements/me`; `useAchievementNotifications.ts` subscribing to `useForceCompleteTask` mutation results and triggering toast on `unlocked_achievements.length > 0`; **on `onSuccess` of `useForceCompleteTask`, if `unlocked_achievements.length > 0`, invalidate `['achievements', 'me']` immediately so `useEffectiveLimits()` recalculates and perks apply without logout (FR-008 "Perks apply immediately" criterion — sp.analyze M2)**
- [X] T080 [P] [US6] Create `frontend/src/components/achievements/AchievementCard.tsx` — achievement tile: name, message, category badge, progress bar (`current/threshold`), locked/unlocked state (grayscale when locked), perk description if unlocked; animation on unlock (Framer Motion scale+glow, skip if reduced-motion)
- [X] T081 [P] [US6] Create `frontend/src/components/achievements/StreakDisplay.tsx` — current streak with flame icon; longest streak secondary; last_completion_date; "grace period active" indicator if last completion was yesterday
- [X] T082 [US6] Create `frontend/src/components/achievements/AchievementUnlockToast.tsx` — Radix `Toast` with gold border, trophy icon, achievement name + perk description; auto-dismiss after 6 seconds; no motion if reduced-motion; triggered via `useAchievementNotifications`
- [X] T083 [US6] Create `frontend/src/app/dashboard/achievements/page.tsx` — `StreakDisplay` header; progress summary (lifetime tasks, focus sessions, notes converted); `AchievementCard` grid organized by category (Tasks / Streaks / Focus / Notes); highlight newly unlocked
- [X] T084 [US6] Update `frontend/src/app/dashboard/page.tsx` (dashboard home) — add `StreakDisplay` widget; show "X tasks to next achievement" progress hint

**Checkpoint**: Achievement system unlocks on task completion, perks apply, streak tracked

---

## Phase 9: User Story 7 — Reminder System (FR-006) P3

**Goal**: Reminders fire as browser notifications and in-app toasts at the configured time (relative or absolute), and are never re-triggered after delivery

**Independent Test**: Create task with due_date = now+2min → add reminder "-1 minute" → wait 1 min → browser notification appears + in-app toast → refresh → reminder marked as fired → no re-trigger

### Implementation

- [X] T085 [US7] Create `frontend/src/lib/schemas/reminder.schema.ts` — `ReminderSchema` (id, task_id, user_id, type `relative|absolute`, offset_minutes, scheduled_at, fired, fired_at, created_at, updated_at); `CreateReminderRequestSchema`; `UpdateReminderRequestSchema`
- [X] T086 [US7] Create `frontend/src/mocks/data/reminders.fixture.ts` — export `remindersFixture: Reminder[]` with one unfired relative reminder (offset -15) linked to a task with due_date
- [X] T087 [US7] Create `frontend/src/mocks/handlers/reminders.handlers.ts` — **`GET /api/v1/reminders`** (only unfired by default); **`POST /api/v1/tasks/:taskId/reminders`** (task-scoped create); **`DELETE /api/v1/reminders/:id`** (reminder-scoped delete); `POST /api/v1/reminders/:id/fire` (set fired=true, fired_at=now)
- [X] T088 [US7] Create `frontend/src/lib/hooks/useReminders.ts` — `useReminders(taskId?)` querying reminders; **`useCreateReminder()` mutating `POST /api/v1/tasks/${taskId}/reminders`**; **`useDeleteReminder()` mutating `DELETE /api/v1/reminders/${reminderId}`**; invalidate `['reminders']`
- [X] T089 [US7] Create `frontend/src/components/reminders/ReminderForm.tsx` — offset preset buttons (-15, -30, -60, -1440 min) + custom absolute datetime; show current reminders list with delete button; call `useCreateReminder()`; validate max 3 reminders per task
- [X] T090 [US7] Integrate `ReminderForm` into `TaskDetailView.tsx` (`frontend/src/components/tasks/TaskDetailView.tsx`) — "Reminders" section below subtasks; show existing reminders as chips with delete (×) button; **reminder API calls MUST be wired to `useCreateReminder` and `useDeleteReminder` — stub/placeholder implementations that show toasts without making API calls are NOT acceptable; error feedback MUST be shown on failure**
- [X] T091 [US7] Create `frontend/public/service-worker.js` — SW v1.0.x; listen for `SET_API_URL`, `START_REMINDER_POLLING`, `STOP_REMINDER_POLLING` postMessages; on `START`: `setInterval(checkReminders, 60000)` + immediate check; `checkReminders` fetches `/reminders` + `/tasks`, calculates trigger times (`due_date + offset_minutes*60000` or `scheduled_at`), skips `fired=true`; shows `self.registration.showNotification()` with `requireInteraction: true, data.url = /dashboard/tasks/:id`; posts `{type: 'REMINDER_DUE', reminder, task}` to all clients; POSTs `/reminders/:id/fire`; `notificationclick` handler focuses/navigates existing tab or opens new
- [X] T092 [US7] Create `frontend/src/lib/hooks/useNotifications.ts` — register SW, request `Notification.permission`, send `SET_API_URL` + `START_REMINDER_POLLING` postMessages on dashboard mount, `STOP_REMINDER_POLLING` on public page mount; listen for `REMINDER_DUE` postMessages and call `notificationStore.addToast()`

**Checkpoint**: Reminders fire on schedule, never repeat, browser + toast dual delivery works

---

## Phase 10: User Story 8 — Recurring Tasks (FR-007) P3

**Goal**: User can create a task template with an RRule recurrence pattern; completing an instance auto-generates the next due instance

**Independent Test**: Create weekly Monday template → complete this week's instance → next Monday instance appears in task list → pause template → complete instance → no new instance generated

### Implementation

- [X] T093 [US8] Add `TaskTemplateSchema` to `frontend/src/lib/schemas/task.schema.ts` — (id, user_id, title, description, priority, estimated_duration, rrule, next_due, active, created_at, updated_at)
- [X] T094 [US8] Create `frontend/src/lib/utils/recurrence.ts` — `parseRRule(rruleString): RRule`; `getNextOccurrence(rrule, after?: Date): Date|null`; `humanizeRRule(rrule): string` (e.g., "Every Monday"); `validateRRule(str): {valid: boolean, error?: string}`; use `rrule` npm package
- [X] T095 [P] [US8] Create `frontend/src/components/recurrence/RecurrenceEditor.tsx` — UI for building RRule: frequency tabs (Daily/Weekly/Monthly/Custom); day-of-week picker for weekly; "starts on" date picker; preview of next 3 occurrences using `getNextOccurrence()`; raw RRULE string preview (collapsible for power users); calls `onChange(rruleString)` on change
- [X] T096 [P] [US8] Create `frontend/src/components/recurrence/RecurrencePreview.tsx` — read-only humanized display of an rrule string: "Every Monday" with next occurrence date; uses `humanizeRRule()` + `getNextOccurrence()`
- [X] T097 [US8] Add recurrence fields to `frontend/src/components/tasks/TaskForm.tsx` — "Make recurring?" toggle; when enabled, mount `RecurrenceEditor` and include `rrule` in task create payload; `template_id` shown as read-only for existing recurring instances
- [X] T098 [US8] Update `useForceCompleteTask` in `frontend/src/lib/hooks/useTasks.ts` — after successful completion, if `task.template_id` is set, invalidate `['tasks']` to fetch the newly-generated next instance from backend
- [ ] T099 [US8] Create `frontend/src/app/dashboard/tasks/page.tsx` update — add "Templates" tab; show `TaskTemplateSchema` list from `GET /api/v1/templates` (**not** `/task-templates` — corrected per sp.analyze v5 H1; see spec Appendix A); pause/resume button per template (`PATCH /api/v1/templates/{id}` with `{ active: false }`); "View instances" link
  > **Path correction (v1.5.0)**: Original task referenced `GET /api/v1/task-templates` — this was incorrect. API.md §Templates confirms the correct path is `GET /api/v1/templates`. PATCH and DELETE endpoints are required by FR-007 but not yet in API.md — confirm with backend team before implementing pause/delete features.
  > ⚠️ **Reopened (sp.analyze v6 H2, 2026-02-20)**: T099 was incorrectly marked `[X]`. The `GET /api/v1/templates` list tab may be structurally present, but `PATCH /api/v1/templates/{id}` (pause/resume) and `DELETE /api/v1/templates/{id}` are required by FR-007 and are **not yet confirmed in API.md**. T099 cannot be marked complete until: (a) backend team confirms PATCH/DELETE endpoints, (b) API.md is updated, and (c) pause/delete UI is implemented against confirmed endpoints. Only the GET list portion may be considered done.

**Checkpoint**: Recurring tasks auto-generate next instance on completion

---

## Phase 11: User Story 9 — AI Features (FR-009) P3 (Pro)

**Goal**: Pro users can generate subtasks via AI, get priority recommendations, and parse notes with natural language date/priority extraction

**Independent Test**: Pro user → task detail → "✨ Generate subtasks" → 5 suggestions returned → accept 3 → saved → AI credit decremented by 1; free user → button disabled

### Implementation

- [X] T100 [US9] Create `frontend/src/lib/schemas/ai.schema.ts` — `AISubtaskSuggestionSchema` (title, estimated_duration?); `AISubtaskResponseSchema` (data: {suggestions: AISubtaskSuggestion[]}); `AIPriorityResponseSchema` (data: {priority, reasoning}); `AINoteParseResponseSchema` (data: {title, description?, due_date?, priority?, estimated_duration?})
- [X] T101 [US9] Create `frontend/src/mocks/handlers/ai.handlers.ts` — `POST /api/v1/tasks/:id/ai/subtasks` returning 5 mock suggestions; `POST /api/v1/tasks/:id/ai/priority` returning `{priority: 'high', reasoning: '...'}`; `POST /api/v1/notes/:id/parse` returning parsed note metadata; decrement `daily_ai_credits_used` on each call
- [X] T102 [US9] Create `frontend/src/lib/hooks/useAI.ts` — `useGenerateSubtasks(taskId)` mutation; `useGetPriorityRecommendation(taskId)` mutation; `useParseNote(noteId)` mutation; each uses `apiClient.post` with respective schemas; surface `ApiError` with code `CREDITS_EXHAUSTED` for 402 responses
- [X] T103 [US9] Update `frontend/src/components/tasks/AISubtasksGenerator.tsx` — hook up to real `useGenerateSubtasks()`; check `effective_limits.daily_ai_credits > 0` before enabling button; show "X credits remaining" badge; call `useCreateSubtask()` for each accepted suggestion
- [X] T104 [US9] Add note parsing to `frontend/src/components/notes/NoteCard.tsx` — "Smart Convert" button (Pro, calls `useParseNote()` before `useConvertNote()`); shows preview of parsed fields (title, due_date, priority) in a confirmation popover before creating task; falls back to plain convert for free tier

**Checkpoint**: AI features (subtask generation, note parsing) functional for Pro users; gracefully disabled for free

---

## Phase 12: User Story 10 — Command Palette (FR-010) P4

**Goal**: Power user can open command palette with Cmd+K, fuzzy-search commands, navigate with arrows, execute with Enter

**Independent Test**: Press Cmd+K → palette opens → type "foc" → "Start Focus Mode" option highlighted → press Enter → focus mode activates for first incomplete task → press Escape → palette closes

### Implementation

- [X] T105 [US10] Create `frontend/src/lib/stores/command-palette.store.ts` — Zustand: `{ isOpen: boolean, query: string, selectedIndex: number, open(), close(), setQuery(q), setSelectedIndex(n) }`
- [X] T106 [US10] Create `frontend/src/lib/commands/task-commands.ts` — command definitions: `{ id, name, icon, category, aliases, action(router, stores) }`; categories: Navigation, Tasks, Notes, Focus; commands include "Go to Tasks", "New Task", "Start Focus Mode", "New Note", "Go to Achievements"; `action` callbacks use `router.push()` or store dispatch
- [X] T107 [US10] Create `frontend/src/components/layout/CommandPalette.tsx` — Radix `Dialog` triggered by store; `<input>` for search query; Fuse.js `new Fuse(commands, {keys:['name','aliases'], threshold: 0.4})`; filtered results list with keyboard nav (ArrowUp/Down, Enter to execute, Escape to close); highlight matched characters; group by category; max 8 results; accessible `role="listbox"` + `role="option"` + `aria-selected`
- [X] T108 [US10] Register global `Cmd+K` / `Ctrl+K` listener in `frontend/src/app/dashboard/layout.tsx` — `window.addEventListener('keydown', handler)` in `useEffect`; call `commandPaletteStore.open()`; cleanup on unmount
- [X] T109 [US10] Mount `CommandPalette` in `frontend/src/app/dashboard/layout.tsx` — always rendered (not conditionally) so Radix can animate open/close; controlled by `isOpen` from store

**Checkpoint**: Command palette opens, fuzzy-searches, and executes navigation + task commands

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Fix P0 gaps from spec.md §VII, accessibility, performance, and error handling

- [X] T110 [P] Fix P0 Gap 1: Move auth token to IndexedDB in `frontend/src/lib/utils/token-storage.ts` — `getToken()`, `setToken()`, `removeToken()` using `indexedDB` (with `localStorage` fallback); update `AuthContext.tsx` and `service-worker.js` to use shared IndexedDB key so SW can read auth token for reminder polling
- [X] T111 [P] Fix P0 Gap 2: Add React Error Boundary to `frontend/src/components/errors/ErrorBoundary.tsx` — class component catching render errors; fallback UI with "Something went wrong" message + "Reload" button + error details (dev only); wrap `RootLayout` children in `frontend/src/app/layout.tsx`
- [X] T181 [RED → T112] **Test ConflictResolutionModal renders and handles all three actions** — `frontend/tests/unit/components/ConflictResolutionModal.test.tsx` — MUST FAIL before T112 is applied (component file does not exist yet)
  - Identical to T156 (Phase 16) — T156 IS the RED test for T112; this entry cross-references it. Write T156 BEFORE starting T112 implementation.
  - **Acceptance criteria**: T156 test file must be authored and confirmed failing (component import error) before T112 implementation begins; zero failures after T112 is complete

- [X] T112 Fix P0 Gap 3: Add conflict resolution modal to `frontend/src/components/tasks/ConflictResolutionModal.tsx` — shown when `useUpdateTask` fails with `VERSION_CONFLICT`; display side-by-side diff (Your version vs Server version); three options: "Keep mine" (force update), "Take theirs" (discard changes), "Cancel"
  > ⚠️ **Reopened** — file `ConflictResolutionModal.tsx` confirmed absent (sp.analyze C3, 2026-02-20); prior `[X]` marker was incorrect. T124 integration task depends on this component existing first.
  - **NFR-007 responsive acceptance criteria (sp.analyze v6 M4)**:
    - [ ] Modal usable on 375 px wide viewport — diff columns stack vertically on mobile (not side-by-side); no horizontal overflow
    - [ ] All three buttons ("Keep mine", "Take theirs", "Cancel") visible and reachable without pinch-to-zoom at 375 px width
    - [ ] Modal height does not exceed `85dvh` on any screen size
- [X] T113 [P] Add `prefers-reduced-motion` guard to all Framer Motion animations — use `useReducedMotion()` hook to conditionally pass `transition={{ duration: 0 }}` or `variants={null}` across `AchievementCard`, `AchievementUnlockToast`, `FocusTimer` ring animation
- [X] T114 [P] Add rate limiting to API mutations — create `frontend/src/lib/utils/rate-limiter.ts` with `createRateLimiter(maxCalls, windowMs)` returning a guard function; wrap `useCreateTask`, `useCreateSubtask`, `useCreateNote` mutationFns with 10 calls/second limit
- [X] T115 [P] Implement optimistic updates in `useForceCompleteTask` — immediately update task in query cache before API call resolves; revert on error using `onMutate` / `onError` TanStack Query callbacks
- [X] T116 [P] Add bundle analyzer check — run `ANALYZE=true next build` in CI; fail build if main chunk > 500KB gzipped; document in `README.md`
- [X] T117 [P] Configure `next.config.ts` security headers — `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=()`, basic CSP blocking inline scripts
- [X] T118 [P] Add `frontend/src/app/dashboard/settings/hidden-tasks/page.tsx` — list of `hidden: true` tasks with "Restore" and "Permanently Delete" actions; use `useUpdateTask({ hidden: false, version: task.version })` for restore
- [X] T119 [P] Add `frontend/src/app/dashboard/profile/page.tsx` — display user avatar, name, email, timezone; edit name + timezone via `usersService.updateProfile()`; avatar from Google (read-only)
- [X] T120 [P] Add `frontend/src/app/dashboard/settings/page.tsx` — settings hub: links to hidden-tasks, archived-notes, profile; notification permission toggle (calls `Notification.requestPermission()`); theme toggle placeholder; data export button (placeholder)
- [X] T121 [P] Add onboarding tour — integrate `driver.js`; create `frontend/src/components/onboarding/OnboardingTour.tsx`; auto-start on first login (check `localStorage.onboarding_complete`); tour steps: Sidebar, Task list, New Task button, Focus mode icon, Notes; mark complete on finish

### Performance (NFR-001) — sp.analyze M1 additions

> **Moved to Phase 15** per sp.analyze v5 M2 remediation (2026-02-20) — T175/T176 depend on T137 (Web Vitals reporting, Phase 15) and Sentry (T136, Phase 15). Co-locating them in Phase 15 preserves phase discipline and resolves the ambiguous Phase 13 "structurally complete" status.

*(T175–T176 definitions — see Phase 15 § NFR-001 Performance)*

### Accessibility (NFR-003)

> **Reclassified to Phase 14** per sp.analyze C2 remediation (2026-02-20) — T157–T159 are open (`[ ]`); Constitution §II.3 prohibits phase overlap. Moving these to Phase 14 preserves phase discipline. Phase 13 is now structurally complete (all remaining open items are in Phase 14+).

*(T157–T159 definitions — see Phase 14 § Accessibility)*

---

## Phase 14: Bug Fix Sprint (spec.md v1.1 — FINDINGS.md)

**Purpose**: Fix API contract violations, UX bugs, and security issues identified by cross-artifact analysis and captured as enforceable requirements in spec.md v1.1–v1.2. Each implementation task is preceded by its **RED test task** — per Constitution §VIII, the test MUST be authored and confirmed failing before the GREEN implementation begins.

**Source**: Every implementation task maps to a finding captured in spec.md v1.1/v1.2. Tests are authored first per Constitution §VIII.

---

### Accessibility (NFR-003) — Reclassified from Phase 13

> Tasks T157–T159 reclassified here to preserve Constitution §II phase discipline (sp.analyze C2).

- [X] T157 [P] [NFR-003] Integrate `jest-axe` accessibility testing — install `jest-axe`; add `axe()` assertion to `TaskCard.test`, `NewTaskModal.test`, `CommandPalette.test`, and `FocusTaskView.test` component tests; CI fails if any axe violations found — `frontend/tests/unit/components/` (covers NFR-003 "Axe DevTools reports zero violations")
- [X] T158 [P] [NFR-003] ARIA labels audit — add `aria-label` to all icon-only buttons in `TaskCard.tsx` (focus icon, delete icon), `SubTaskList.tsx` (delete icon), `NoteCard.tsx` (archive/delete icons), `Header.tsx` (user menu button); also add `aria-label="Voice note playback"` to the `<audio>` element rendered in `NoteCard.tsx` when `voice_url` is present (sp.analyze v6 L2 — audio player was outside original scope); verify `jest-axe` reports no "button without accessible name" or "audio without accessible name" violations after T157
- [X] T159 [P] [NFR-003] Keyboard-only navigation integration test — `frontend/tests/integration/accessibility.test.tsx`: verify Tab order through TaskList → TaskCard → expand → SubTaskList; verify Escape closes `NewTaskModal`; verify no keyboard trap inside `FocusTaskView`; all interactions completable without mouse (covers NFR-003 "Keyboard-only users can complete all tasks")

---

### FR-004 Backfill — Navigation Guard (H6)

- [X] T182 [P] [RED → T172] **Test focus mode navigation guard blocks Back and beforeunload** — `frontend/tests/unit/components/FocusTaskView-guard.test.tsx` — MUST FAIL before T172 is applied
  - Renders `FocusTaskView` with `focusModeStore.isActive = true`; simulates `window.dispatchEvent(new PopStateEvent('popstate'))` and asserts `window.confirm` was called; simulates `beforeunload` event and asserts it was handled; confirms no guard exists when `isActive = false`
  - **Acceptance criteria**: Test detects missing navigation guard before T172; zero guard-absent failures after

- [X] T172 [US4] **FR-004 Navigation guard — Focus mode blocks navigation away** (`frontend/src/components/focus/FocusTaskView.tsx`, `frontend/src/app/dashboard/focus/page.tsx`)
  - Register a Next.js router `beforePopState` guard while focus is active: show `window.confirm('Exit focus mode? Your progress will be saved.')` — return `false` if user cancels, `true` to allow navigation
  - Add `window.addEventListener('beforeunload', handler)` for tab/browser close while focus is active; cleanup both handlers on `focusModeStore.deactivate()` or component unmount
  - **Acceptance criteria (FR-004)**:
    - [ ] Clicking browser Back while in focus mode shows confirmation dialog
    - [ ] Confirming "Leave" allows navigation and calls `focusModeStore.deactivate()`
    - [ ] Cancelling "Stay" keeps the user in focus mode with timer running
    - [ ] Closing the tab/window while focus is active shows `beforeunload` prompt

---

### Critical Fixes (404 on every call / request flood)

- [X] T163 [P] [RED → T122, T130] **Test `useSubtasks` conditional fetch + camelCase invalidation** — `frontend/tests/unit/hooks/useSubtasks.test.ts` — MUST FAIL before T122/T130 are applied
  - `useSubtasks(taskId, { enabled: false })` fires zero network requests; `useCreateSubtask` `onSuccess` invalidates `['subtasks', taskId]` (camelCase) not `['subtasks', undefined]`; `useUpdateSubtask` same camelCase invalidation
  - **Acceptance criteria**: Test suite reports ≥3 failures before T122 + T130 are applied; zero failures after

- [X] T122 [P] [US3] [GREEN] **BUG-01A — Guard subtask fetch with `enabled: isExpanded`** (`frontend/src/lib/hooks/useSubtasks.ts` + `frontend/src/components/tasks/TaskCard.tsx`)
  - Update `useSubtasks` signature to `useSubtasks(taskId: string, options?: { enabled?: boolean })` and forward `enabled: options?.enabled ?? true` to `useQuery`
  - Update `TaskCard.tsx` to call `useSubtasks(task.id, { enabled: isExpanded })` so subtasks are **only fetched when the card is expanded**
  - **Acceptance criteria (from FR-003)**:
    - [ ] Rendering 25 task cards does NOT fire 25 `GET /tasks/{id}/subtasks` requests on initial load
    - [ ] `GET /tasks/{id}/subtasks` fires exactly once per card when that card is expanded
    - [ ] Collapsed card still shows aggregated count from `task.subtask_count` / `task.subtask_completed_count` with no API call
    - [ ] `useSubtasks(taskId, { enabled: false })` must not fire any network request

- [X] T161 [P] [RED → T123] **Test `useForceCompleteTask` endpoint + response schema** — `frontend/tests/unit/hooks/useTasks-forceComplete.test.ts` — MUST FAIL before T123 is applied
  - Calls `POST /tasks/{id}/force-complete` with `{ version }` in body; response parsed against `ForceCompleteResponseSchema`; confirms no `useCompleteTask` or `useAutoCompleteTask` export exists in `useTasks.ts`
  - **Acceptance criteria**: Test reports ≥2 failures before T123; zero failures after

- [X] T123 [US2] [GREEN] **BUG-06A — Fix `useForceCompleteTask` endpoint and response schema** (`frontend/src/lib/hooks/useTasks.ts` + `frontend/src/lib/schemas/task.schema.ts`)
  - Remove `useCompleteTask` and `useAutoCompleteTask` — these call non-existent endpoints
  - Implement `useForceCompleteTask({ taskId, version })` calling `POST /api/v1/tasks/${taskId}/force-complete` with body `{ version }`
  - Add/update `ForceCompleteResponseSchema`:
    ```ts
    z.object({
      data: z.object({
        task: TaskSchema,
        unlocked_achievements: z.array(z.object({ id: z.string(), name: z.string(), perk_type: z.string(), perk_value: z.number() })),
        streak: z.number(),
      }),
    })
    ```
  - **Acceptance criteria (from FR-002)**:
    - [ ] No call to `/tasks/{id}/complete` or `/tasks/{id}/auto-complete` exists in the codebase — these return 404
    - [ ] Completion calls `POST /tasks/{id}/force-complete` with `{ version }` body
    - [ ] Response `{ data: { task, unlocked_achievements[], streak } }` is parsed correctly by the schema
    - [ ] `onSuccess` invalidates `['tasks']` and `['tasks', taskId]`

- [X] T162 [P] [RED → T124] **Test `useUpdateTask` always includes `version` field** — `frontend/tests/unit/hooks/useTasks-version.test.ts` — MUST FAIL before T124 is applied
  - Every `useUpdateTask.mutate()` call site includes `version`; mocked handler returns 400 when `version` is missing from request body
  - **Acceptance criteria**: Test finds ≥1 missing-version path before T124; zero missing-version paths after

- [X] T124 [US2] [GREEN] **BUG-06B — Ensure `version` is passed in all `updateTask.mutateAsync` calls** (`frontend/src/components/tasks/TaskDetailView.tsx` + all other call sites)
  - Audit every call to `updateTask.mutateAsync()` / `useUpdateTask().mutate()` across the codebase
  - Add `version: task.version` to every call that is missing it, including: toggling `completed`, toggling `hidden`, inline title/description edits, edit page submit, restore from hidden-tasks page
  - **Acceptance criteria (from FR-002)**:
    - [ ] Every `PATCH /tasks/{id}` request body includes the `version` field — grep for `updateTask.mutate` confirms no call omits it
    - [ ] Backend responds 200 (not 400 or 409) on all task update operations
    - [ ] Conflict resolution modal appears when server returns 409 (**T112 must be built first** — file was absent; T112 is now `[ ]` open)

- [X] T173 [P] [RED → T125] **Test notes standalone migration** — `frontend/tests/unit/hooks/useNotes-standalone.test.ts` — MUST FAIL before T125 is applied
  - Confirms: `useCreateNote()` calls `POST /api/v1/notes` (not task-scoped); `useNotes()` calls `GET /api/v1/notes` (no taskId param); `useUpdateNote()` uses `apiClient.patch` not `apiClient.put`; `QuickNoteInput` renders without `taskId` prop
  - **Acceptance criteria**: Test reports ≥3 wrong-endpoint/method failures before T125; zero failures after

- [X] T125 [US5] [GREEN] **BUG-07 / UPDATE-02 — Migrate notes to standalone `/api/v1/notes` endpoints** (`frontend/src/lib/hooks/useNotes.ts`, `frontend/src/mocks/handlers/notes.handlers.ts`, `frontend/src/components/notes/QuickNoteInput.tsx`, `frontend/src/app/dashboard/notes/page.tsx`)
  - Architecture decision (UPDATE-02): notes are **standalone entities** — remove all task-scoped note paths
  - `useNotes()`: query `GET /api/v1/notes` — **no `taskId` param**; `?archived=true` for archived notes
  - `useCreateNote({ content })`: mutate `POST /api/v1/notes` — remove `taskId` from all call sites
  - `useUpdateNote({ noteId, data })`: mutate `PATCH /api/v1/notes/${noteId}` — `apiClient.patch` (not `apiClient.put`)
  - Update MSW handlers: add `GET /api/v1/notes` and `POST /api/v1/notes` handlers; remove task-scoped note handlers (`/tasks/:id/notes`)
  - Remove `taskId` prop from `QuickNoteInput` and any other note creation components
  - **Acceptance criteria (from FR-005 v1.2)**:
    - [ ] Note creation calls `POST /api/v1/notes` — no call to `POST /api/v1/tasks/{task_id}/notes` exists
    - [ ] Note list calls `GET /api/v1/notes` — no call to `GET /api/v1/tasks/{task_id}/notes` exists
    - [ ] Note update calls `PATCH /api/v1/notes/{note_id}` — `PUT /notes/{id}` MUST NOT be called
    - [ ] `QuickNoteInput` has no `taskId` prop dependency
    - [ ] Backend responds 200/201 (not 404) on all note operations

---

### High Severity Fixes

- [X] T164 [P] [RED → T126] **Test reminder wiring in `TaskDetailView`** — `frontend/tests/unit/components/TaskDetailView-reminders.test.tsx` — MUST FAIL before T126 is applied
  - `handleAddReminder` calls `useCreateReminder.mutateAsync` with task payload; success toast appears only after promise resolves; error toast shown on rejection; no commented-out API calls
  - **Acceptance criteria**: Test reports stub/no-API-call failures before T126; zero failures after

- [X] T126 [US7] [GREEN] **BUG-06C — Wire reminder API calls in `TaskDetailView`** (`frontend/src/components/tasks/TaskDetailView.tsx`)
  - Import `useCreateReminder` and `useDeleteReminder` from `useReminders.ts`
  - Replace any stub/commented-out reminder handlers with real mutation calls:
    - `handleAddReminder`: call `createReminder.mutateAsync({ taskId: task.id, ...reminder })`
    - `handleDeleteReminder`: call `deleteReminder.mutateAsync(reminderId)`
  - Show destructive error toast on failure; do not show false-positive success toast
  - **Acceptance criteria (from FR-006)**:
    - [ ] Adding a reminder fires `POST /api/v1/tasks/{task_id}/reminders` with the reminder payload
    - [ ] Deleting a reminder fires `DELETE /api/v1/reminders/{reminder_id}`
    - [ ] No stub implementation: success toast only appears after the API call resolves successfully
    - [ ] Error toast ("Failed to add/delete reminder") appears on API failure
    - [ ] No commented-out API calls remain in `TaskDetailView.tsx`

- [X] T165 [P] [RED → T127] **Test subscription upgrade endpoint** — `frontend/tests/unit/hooks/useSubscription.test.ts` — MUST FAIL before T127 is applied
  - Subscription upgrade calls `POST /api/v1/subscription/upgrade`; mocked 200 response triggers success toast and redirect; confirms no call to `/subscription/checkout` or `/subscription/purchase-credits`
  - **Acceptance criteria**: Test catches wrong endpoint before T127; zero wrong-endpoint failures after

- [X] T127 [US12] [GREEN] **BUG-08 — Fix subscription upgrade endpoint** (`frontend/src/lib/hooks/useSubscription.ts` + `frontend/src/services/payment.service.ts`)
  - Change all calls from `POST /subscription/checkout` → `POST /subscription/upgrade`
  - Remove `POST /subscription/purchase-credits` — endpoint does not exist
  - Remove `checkout_url` redirect logic (not documented in API.md for `/subscription/upgrade`)
  - On success: show toast "Upgraded to Pro!" and redirect to `/dashboard`
  - **Acceptance criteria (from FR-012)**:
    - [ ] Subscription upgrade calls `POST /api/v1/subscription/upgrade`
    - [ ] No call to `/subscription/checkout` or `/subscription/purchase-credits` in codebase (grep confirms)
    - [ ] User sees confirmation toast on successful upgrade
    - [ ] User sees error toast on failure

---

### Medium Severity Fixes

- [X] T171 [P] [US11/US13] **Create `frontend/src/lib/schemas/notification.schema.ts`** — `NotificationSchema` (id: UUID, user_id: UUID, title: string, message: string, read: boolean, task_id: string|null, created_at: datetime, updated_at: datetime); `DataResponseSchema(NotificationSchema)` and `PaginatedResponseSchema(NotificationSchema)` wrappers; exported types used by `useNotifications.ts` (T092 — update imports), `/dashboard/notifications` page (T128), and mark-as-read hook (T129)
  > **Reclassified from Phase 9** per sp.analyze v5 M1 (2026-02-20) — T171 is tagged [US11/US13] and is only needed by Phase 14 tasks T128 and T129; placing it here preserves phase discipline. Must be completed before T128 and T129.

- [X] T174 [P] [RED → T128] **Test notifications page route renders** — `frontend/tests/integration/notifications-page.test.tsx` — MUST FAIL before T128 is applied
  - Renders `/dashboard/notifications` route; asserts component is not undefined/404; asserts `useNotifications()` hook is called; asserts loading skeleton renders while fetching; asserts empty state renders when `data.length === 0`
  - **Acceptance criteria**: Test reports missing-component failures before T128; zero failures after

- [X] T128 [US11] **BUG-05 — Create missing `/dashboard/notifications` page** (`frontend/src/app/dashboard/notifications/page.tsx`)
  - Create the page at the exact route `/dashboard/notifications` using the existing `useNotifications()` hook
  - Show loading spinner while fetching; empty state when no notifications; list all notifications in reverse-chronological order using existing notification display component(s)
  - **Acceptance criteria (from FR-011)**:
    - [ ] Route `/dashboard/notifications` renders without 404
    - [ ] "View all" link in `NotificationDropdown` navigates to this page successfully
    - [ ] Page shows all notifications for the authenticated user
    - [ ] Loading state shown while fetching
    - [ ] Empty state shown when `data.length === 0`

- [X] T166 [P] [RED → T129] **Test mark-notification-as-read endpoint** — `frontend/tests/unit/hooks/useNotifications-read.test.ts` — MUST FAIL before T129 is applied
  - Mark-as-read calls `PATCH /api/v1/notifications/{id}/read` with no body; `PATCH /notifications/{id}` with `{ read: true }` body MUST NOT be called; notification read state updates immediately in UI
  - **Acceptance criteria**: Test detects wrong endpoint before T129; zero wrong-endpoint failures after

- [X] T129 [US13] [GREEN] **Fix mark-notification-as-read endpoint** (`frontend/src/lib/hooks/useNotifications.ts`)
  - Change `PATCH /notifications/{id}` with body `{ read: true }` → `PATCH /notifications/{id}/read` with **no body**
  - **Acceptance criteria (from FR-013)**:
    - [ ] Mark-as-read calls `PATCH /api/v1/notifications/{id}/read` (path-based action)
    - [ ] No call to `PATCH /notifications/{id}` with `{ read: true }` body exists (returns 404)
    - [ ] Notification read state updates in UI immediately after successful call

- [X] T130 [P] [US3] [GREEN] **BUG-02 — Fix cache invalidation key from `task_id` to `taskId`** (`frontend/src/lib/hooks/useSubtasks.ts`) *(RED: T163 above)*
  - In `useCreateSubtask` `onSuccess`: change `variables.task_id` → `variables.taskId` for both `['subtasks', ...]` and `['tasks', ...]` invalidations
  - In `useUpdateSubtask` `onSuccess`: same fix
  - **Acceptance criteria (from FR-003)**:
    - [ ] After creating a subtask, `['subtasks', taskId]` cache (not `['subtasks', undefined]`) is invalidated
    - [ ] No duplicate stale entries visible in React Query DevTools after subtask mutation
    - [ ] Subtask list refreshes correctly after add/update without stale data alongside fresh data

- [ ] T183 [P] [RED → T131] **Test NewTaskModal responsive layout at 375 px** — `frontend/tests/unit/components/NewTaskModal-mobile.test.tsx` — MUST FAIL before T131 is applied
  - Render `NewTaskModal` with jsdom viewport set to 375 px width; assert `DialogContent` has no fixed `min-width` > 375 px class; assert `RecurrenceEditor` is hidden behind a toggle element on small viewport; assert all form fields are visible without horizontal scroll
  - **Acceptance criteria**: Test detects fixed-width overflow before T131; zero overflow failures after

- [ ] T131 [US2] **BUG-04 — Mobile-responsive `NewTaskModal`** (`frontend/src/components/tasks/NewTaskModal.tsx`)
  - Update `DialogContent` className to `"sm:max-w-[600px] w-[calc(100vw-2rem)] max-h-[85dvh] overflow-y-auto"`
  - Add `showAdvanced` state; hide `RecurrenceEditor` behind a "Show advanced options" toggle on small screens (visible by default on `sm:` breakpoint and above):
    ```tsx
    <button type="button" className="text-xs text-muted-foreground underline sm:hidden"
      onClick={() => setShowAdvanced(v => !v)}>
      {showAdvanced ? 'Hide' : 'Show'} advanced options
    </button>
    <div className={showAdvanced ? 'block' : 'hidden sm:block'}>
      <RecurrenceEditor ... />
    </div>
    ```
  - **Acceptance criteria (from NFR-007)**:
    - [ ] Modal fully usable on 375 px wide viewport (iPhone SE) — no horizontal overflow
    - [ ] All inputs and buttons reachable without pinch-to-zoom
    - [ ] `RecurrenceEditor` collapses on mobile and expands on tap without layout breakage
    - [ ] Modal height does not exceed 85dvh on any screen

---

### Low Severity Fixes

- [ ] T184 [P] [RED → T132] **Test NotificationDropdown mousedown listener only active when open** — `frontend/tests/unit/components/NotificationDropdown-listener.test.tsx` — MUST FAIL before T132 is applied
  - Spy on `document.addEventListener`; render `NotificationDropdown` with `isOpen = false`; assert `mousedown` listener was NOT attached; set `isOpen = true`; assert listener IS attached; close dropdown; assert listener was removed
  - **Acceptance criteria**: Test detects always-on listener before T132; listener correctly conditional after

- [ ] T132 [P] **BUG-01B — Guard `NotificationDropdown` mousedown listener** (`frontend/src/components/layout/NotificationDropdown.tsx`)
  - Move the `document.addEventListener('mousedown', handleClickOutside)` inside a `useEffect` guarded by `if (!isOpen) return` so the listener only attaches when the dropdown is open:
    ```tsx
    useEffect(() => {
      if (!isOpen) return
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [close, isOpen])
    ```
  - **Acceptance criteria**:
    - [ ] `mousedown` listener is NOT active when dropdown is closed
    - [ ] Clicking anywhere on the page when dropdown is closed causes no re-render cascade
    - [ ] Clicking outside the dropdown when open still closes it correctly

- [ ] T185 [P] [RED → T133] **Test PendingCompletionsBar wraps on 375 px viewport** — `frontend/tests/unit/components/PendingCompletionsBar-mobile.test.tsx` — MUST FAIL before T133 is applied
  - Render `PendingCompletionsBar` at 375 px viewport width; assert text and buttons are both visible (not cut off); assert no horizontal scrollbar is present; assert buttons stack vertically rather than overflow horizontally
  - **Acceptance criteria**: Test detects layout overflow before T133; zero overflow failures after

- [ ] T133 [P] **BUG-03 — Mobile-responsive `PendingCompletionsBar`** (`frontend/src/components/layout/PendingCompletionsBar.tsx`)
  - Change the flex container from `flex items-center justify-between gap-4` → `flex flex-wrap items-center justify-between gap-2`
  - Add `flex-1 min-w-0 truncate sm:whitespace-normal` to the warning text paragraph
  - Wrap buttons in `flex flex-col sm:flex-row gap-2 shrink-0`
  - **Acceptance criteria (from NFR-007)**:
    - [ ] Warning text and buttons visible without horizontal scrolling on 375 px width
    - [ ] Buttons stack vertically on narrow screens without overflow
    - [ ] Layout correct on desktop (side-by-side) and mobile (stacked)

---

### Security Fixes

- [ ] T179 [P] [RED → T134] **Test localStorage-free auth after HttpOnly cookie migration** — `frontend/tests/unit/contexts/AuthContext-cookies.test.ts` — MUST FAIL before T134 is applied
  - After login, `localStorage.getItem('auth_token')` returns `null`; after login, `localStorage.getItem('refresh_token')` returns `null`; API calls succeed without a manual `Authorization` header being injected (cookies send automatically); logout clears all auth cookies
  - **Acceptance criteria**: Test detects localStorage token presence before T134; zero localStorage token findings after T134

- [ ] T134 [US1] **S-01 — Migrate auth tokens from `localStorage` to HttpOnly cookies** (`frontend/src/lib/contexts/AuthContext.tsx`, `frontend/src/lib/api/client.ts`, `frontend/src/lib/services/auth.service.ts`)
  - Remove `localStorage.getItem('auth_token')` / `localStorage.setItem('auth_token')` and equivalent `refresh_token` keys
  - Tokens MUST be stored in HttpOnly cookies (set by backend on auth response) — JavaScript must not be able to read them
  - If backend does not yet set cookies, coordinate with backend team to add `Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict` to auth response headers
  - Update `apiClient` to use cookie-based auth (remove manual `Authorization` header injection; rely on browser sending cookies automatically with `credentials: 'include'`)
  - Update `service-worker.js` to fetch token from IndexedDB (per T110) or via `/auth/me` since it cannot read HttpOnly cookies
  - **Acceptance criteria (from FR-001 / NFR-002)**:
    - [ ] `localStorage` contains no `auth_token` or `refresh_token` keys after login
    - [ ] `document.cookie` does not expose the access or refresh tokens (HttpOnly not visible to JS)
    - [ ] API calls still succeed with cookie-based auth
    - [ ] Logout clears all auth cookies
    - [ ] No XSS vector can extract tokens via JavaScript

- [ ] T178 [P] **H3 — Add AI credit env vars to `.env.local` template and env validator** (`frontend/.env.local` template, `frontend/src/lib/utils/env-validator.ts` or equivalent startup check)
  - Add `FREE_TIER_AI_CREDITS`, `PRO_TIER_AI_CREDITS`, `AI_CREDIT_RESET_HOUR`, and `AI_MODEL_ID` to the `.env.local` template (created by T009 — T009 is already [X] but was incomplete)
  - Ensure the startup env validator (Constitution §IX — env validation is mandatory) blocks startup with a clear error if any of these four vars are absent
  - **Acceptance criteria (from FR-009 / Constitution §IX)**:
    - [ ] `.env.local` template contains `FREE_TIER_AI_CREDITS`, `PRO_TIER_AI_CREDITS`, `AI_CREDIT_RESET_HOUR`, `AI_MODEL_ID` with placeholder/example values
    - [ ] Starting the app without any one of these vars causes an immediate, descriptive startup error (not a silent runtime failure)
    - [ ] No hardcoded AI credit defaults exist in application code

- [ ] T180 [P] [RED → T135] **Test absence of unguarded console.log in production build** — `frontend/tests/unit/utils/console-log-audit.test.ts` — MUST FAIL before T135 is applied
  - Use `jest.spyOn(console, 'log')` in a test that simulates auth events and payment flows; assert console.log was NOT called in `process.env.NODE_ENV === 'production'` mode; alternatively, grep-based test fails if `console.log` appears without a `process.env.NODE_ENV` guard in AuthContext.tsx or payment.service.ts
  - **Acceptance criteria**: Test detects ≥1 unguarded console.log call before T135; zero unguarded calls after

- [ ] T135 [P] **S-03 — Remove production `console.log` statements for auth and payment data** (`frontend/src/lib/contexts/AuthContext.tsx`, `frontend/src/services/payment.service.ts`, `frontend/src/lib/services/auth.service.ts`)
  > **Coordination note (U5)**: T135 also covers `auth.service.ts` (T030) which was not in the original scope. T138 (Phase 15 structured logger) supersedes T135 for replacing calls with `logger.*` — complete T135 first (remove/guard raw calls), then T138 extends with structured logging. Do NOT defer T135 in favour of T138.
  - Audit all `console.log` calls in `AuthContext.tsx` and `payment.service.ts`
  - Remove calls that log auth events, token values, or payment data; or guard them with `if (process.env.NODE_ENV === 'development')`
  - **Acceptance criteria (from NFR-002)**:
    - [ ] `AuthContext.tsx` has no unguarded `console.log` calls in production build
    - [ ] `payment.service.ts` has no unguarded `console.log` calls in production build
    - [ ] `NEXT_PUBLIC_NODE_ENV !== 'development'` build produces zero auth/payment log output

---

### NFR-004 Gaps — Autosave & Form Persistence

These tasks address C2 (critical coverage gap): NFR-004 mandates autosave and form-state persistence with zero prior task coverage.

- [ ] T167 [P] [NFR-004] [RED] **Test debounced autosave in `TaskDetailView`** — `frontend/tests/unit/hooks/useTaskAutosave.test.ts` — MUST FAIL before T168
  - Custom hook `useTaskAutosave(task, updateTask)` debounces 5 000 ms; mock timer confirms API call fires after 5 s idle; rapid edits do NOT fire multiple calls; no call fires on mount
  - **Acceptance criteria**: Test reports autosave-absent failures before T168; zero failures after

- [ ] T168 [P] [NFR-004] [GREEN] **Implement debounced autosave in `TaskDetailView`** (`frontend/src/components/tasks/TaskDetailView.tsx`)
  - Create `frontend/src/lib/hooks/useTaskAutosave.ts` — accepts `task: Task` and `updateTask` mutation; `setTimeout(fn, 5000)` on each field change, clears previous; on fire: `updateTask.mutate({ id: task.id, title, description, version: task.version })`; cancels on unmount
  - Integrate into `TaskDetailView` inline-edit handlers
  - **Acceptance criteria (NFR-004)**: Autosave fires exactly once per 5-second idle; no 400/409 from missing `version`; no data loss between save intervals

- [ ] T169 [P] [NFR-004] [RED] **Test `TaskForm` draft localStorage persistence** — `frontend/tests/unit/components/TaskForm-draft.test.tsx` — MUST FAIL before T170
  - Renders `TaskForm`, types title + description, re-mounts, asserts pre-filled values from `localStorage`; confirms draft cleared on successful submit
  - **Acceptance criteria**: Test detects no-draft-persistence before T170; zero failures after

- [ ] T170 [P] [NFR-004] [GREEN] **Persist `TaskForm` draft state to `localStorage`** (`frontend/src/components/tasks/TaskForm.tsx`)
  - On each field change write `{ title, description, priority, due_date, estimated_duration }` to `localStorage` under key `task-form-draft` via `useLocalStorage` hook (T016)
  - On mount, restore draft if key present; show "Draft restored" chip with "Discard" button; clear `task-form-draft` on successful submit
  - **Acceptance criteria (NFR-004)**: Draft survives browser refresh; cleared on successful task creation; no stale draft bleeds into a second create flow

---

## Phase 14 Execution Order (Recommended Fix Order)

Fix in this order — earlier fixes unblock manual testing of later ones. **Within each pair: RED test MUST be authored and confirmed failing before the GREEN implementation begins** (Constitution §VIII TDD).

| Priority | RED Test | GREEN Impl | Spec Ref | Finding |
|----------|----------|-----------|----------|---------|
| 0 — P0 PREREQ | **T181** (= T156) | **T112** | NFR-004 / FR-002 | ConflictResolutionModal — **Phase 13 reopened task; MUST complete before T124** (file confirmed absent); T156 is RED test — sp.analyze v6 H5 |
| 1 — NFR-003 | — | T157, T158, T159 | NFR-003 | A11y (reclassified from Phase 13) |
| 2 — NFR-011/013 | — | T171 | FR-011/FR-013 | notification.schema.ts — must precede T128/T129 (reclassified from Phase 9) |
| 3 — CRITICAL | T163 | T122 + T130 | FR-003 | BUG-01A + BUG-02 |
| 4 — CRITICAL | T161 | T123 | FR-002 | BUG-06A |
| 5 — CRITICAL | T162 | T124 | FR-002 | BUG-06B (T112 at priority 0 must be done first) |
| 6 — CRITICAL | T173 | T125 | FR-005 | BUG-07 / UPDATE-02 (T173 added — sp.analyze C1) |
| 7 — HIGH | T164 | T126 | FR-006 | BUG-06C |
| 8 — HIGH | T165 | T127 | FR-012 | BUG-08 |
| 9 — HIGH | **T182** | T172 | FR-004 | Navigation guard (sp.analyze H6); T182 is RED test — sp.analyze v6 H5 |
| 10 — MEDIUM | T174 | T128 | FR-011 | BUG-05 (T171 must precede; T174 added — sp.analyze C1) |
| 11 — MEDIUM | T166 | T129 | FR-013 | NOTIF (T171 must precede) |
| 12 — MEDIUM | (T163) | T130 | FR-003 | BUG-02 |
| 13 — MEDIUM | **T183** | T131 | NFR-007 | BUG-04; T183 is RED test — sp.analyze v6 H5 |
| 14 — LOW | **T184** | T132 | — | BUG-01B; T184 is RED test — sp.analyze v6 H5 |
| 15 — LOW | **T185** | T133 | NFR-007 | BUG-03; T185 is RED test — sp.analyze v6 H5 |
| 16 — SECURITY | **T179** | T134 | FR-001 / NFR-002 | S-01; T179 is RED test — sp.analyze v6 H5 |
| 17 — SECURITY | **T180** | T135 | NFR-002 | S-03; T180 is RED test — sp.analyze v6 H5 |
| 18 — NFR-004 | T167 | T168 | NFR-004 | Autosave |
| 19 — NFR-004 | T169 | T170 | NFR-004 | Form draft |
| 20 — H3 ENV | — | **T178** | NFR-002 / Constitution §IX | AI credit env vars backfill — add to .env.local + startup validator — sp.analyze v6 H3 |

---

## Phase 15: Observability + Performance Monitoring (NFR-006, NFR-001)

**Purpose**: Set up Sentry error tracking, Web Vitals reporting, structured logging (NFR-006), and performance CI gates (NFR-001). T175/T176 moved here from Phase 13 per sp.analyze v5 M2 (co-locating them with their dependencies T136/T137).

> **Dependency note (M5)**: T138 (structured logger) depends on **T135 (Phase 14)** being complete first. T135 removes/guards raw `console.log` calls in AuthContext and payment.service; T138 then extends those files with structured logger calls. Do NOT begin T138 until T135 is verified done and merged.

- [ ] T136 [P] [NFR-006] Set up Sentry in `frontend/` — `npm install @sentry/nextjs`; configure via `NEXT_PUBLIC_SENTRY_DSN` env var; add `sentry.client.config.ts` and `sentry.server.config.ts`; wrap root layout with Sentry error boundary; upload source maps in CI (`sentry-cli`); verify error captured in Sentry dashboard on test throw
- [ ] T137 [P] [NFR-006] Web Vitals reporting in `frontend/src/app/layout.tsx` — add `reportWebVitals()` export; track LCP, FID, CLS, TTFB; send metrics to Sentry performance monitoring or a `/api/vitals` analytics endpoint; add `NEXT_PUBLIC_VITALS_ENDPOINT` env var
- [ ] T138 [NFR-006] *(depends T135 — see note above)* Structured logger utility in `frontend/src/lib/utils/logger.ts` — `logger.info()`, `logger.warn()`, `logger.error()` wrapping `console.*`; guard all calls with `if (process.env.NODE_ENV !== 'production')`; replace unguarded `console.log` calls in `AuthContext.tsx` and `payment.service.ts` (overlaps T135); export `logger` as singleton
- [ ] T160 [P] [NFR-006 / Constitution §V] Log every AI interaction as a structured event — in `frontend/src/lib/hooks/useAI.ts`, add `onSuccess` callbacks to `useGenerateSubtasks`, `useGetPriorityRecommendation`, and `useParseNote`; each calls `Sentry.addBreadcrumb({ category: 'ai', message: action_type, data: { entity_id, actor_type: 'ai', credits_used } })` and `logger.info('ai_interaction', { entity_id, user_id, action_type, actor_type: 'ai', credits_used, timestamp: new Date().toISOString() })` using the logger from T138; **`entity_id` = `taskId` for subtask/priority calls; `noteId` for note-parsing calls**; **`actor_type: 'ai'` is a constant — satisfies Constitution §V.2 "actor identity (user or AI)" requirement** (sp.analyze v6 H4)

### NFR-001 Performance Monitoring — moved from Phase 13

- [ ] T175 [P] [NFR-001] Lighthouse CI gate — install `@lhci/cli`; add `.lighthouserc.json` with `assertions: { "categories:performance": ["error", {"minScore": 0.9}], "categories:accessibility": ["error", {"minScore": 0.9}], "categories:best-practices": ["error", {"minScore": 0.9}] }`; add `lhci autorun` step to CI pipeline after build; fail CI if any score drops below threshold; document in `README.md`
- [ ] T176 [P] [NFR-001] Web Vitals threshold alerts — in `reportWebVitals()` callback (T137), add conditional alerting: `if (metric.name === 'LCP' && metric.value > 2500) logger.warn('lcp_threshold_exceeded', ...)`, same pattern for CLS > 0.1 and FID > 100ms; surface as Sentry performance alerts; ensures NFR-001 thresholds are actively monitored, not just collected
- [ ] T177 [P] [NFR-001] Route transition timing — instrument Next.js `router.events` with `performance.measure()` on `routeChangeStart`/`routeChangeComplete`; log duration via `logger.warn('route_transition_slow', { from, to, durationMs })` if `durationMs > 500`; satisfies NFR-001 "Route transitions < 500ms" measurement criterion (`frontend/src/app/dashboard/layout.tsx` — add useEffect with router.events listener)
  > **Acceptance criteria (NFR-001)**: Route transition measurement active in production builds; slow transitions (>500ms) appear as Sentry breadcrumbs via T160's logger pattern; no performance regression introduced by the measurement instrumentation itself

---

## Phase 16: Test Coverage

**Purpose**: Document V1 test suite in tasks.md (Constitution §VIII) and add missing tests for uncovered components and hooks. V1 tests exist and pass — this phase maps them to task IDs and identifies gaps.

> **V1 Test Status (UPDATE-14)**: All tests in the "Existing V1 Tests" group below are already written and passing in `frontend/tests/`. They are not mapped to implementation task IDs. This phase provides that mapping. Missing tests must be written before their related feature is considered production-ready per Constitution §VIII.
>
> **Test approach**: App is in production — all tests use `jest.fn()` mocks directly. MSW is not used in the test suite and is not needed (live API exists). Write all new tests (T149–T156) with `jest.fn()` mock pattern, consistent with V1 tests.

### Existing V1 Tests (All Pass — Mapped to Task IDs)

- [X] T139 [P] [US2] Test: `TaskForm` renders all required fields and submits with UUID validation — `frontend/tests/unit/components/TaskForm.test.tsx` (covers T044 — `TaskForm.tsx`)
- [X] T140 [P] [US3] Test: `SubTaskList` progress calculation (0%/33%/100%) and delete confirmation flow — `frontend/tests/unit/components/SubTaskList.test.tsx` (covers T059 — `SubTaskList.tsx`)
- [X] T141 [P] [US7] Test: `ReminderForm` validates due date required and preset offset buttons submit correct `offsetMinutes` — `frontend/tests/unit/components/ReminderForm.test.tsx` (covers T089 — `ReminderForm.tsx`)
- [X] T142 [P] [US8] Test: `RecurrencePreview` shows N occurrences for daily/weekly/bi-weekly/monthly and handles invalid rule — `frontend/tests/unit/components/RecurrencePreview.test.tsx` (covers T096 — `RecurrencePreview.tsx`)
- [X] T143 [P] [US8] Test: Recurrence utils — `onTaskComplete` generates next instance for daily/weekly/bi-weekly; `parseRecurrenceRule` validates patterns; `isRecurrenceEnded` checks COUNT and UNTIL — `frontend/tests/unit/utils/recurrence.test.ts` (covers T094 — `recurrence.ts`)
- [X] T144 [P] [US7] Test: `calculateReminderTriggerTime` with all offset values, null due date, invalid date, and timezone consistency — `frontend/tests/unit/utils/date.test.ts` (covers reminder trigger logic in `date.ts`)
- [X] T145 [P] Test: `Sidebar` renders all nav links with icons, collapse button toggles state, and state persists in `localStorage` — `frontend/tests/unit/components/Sidebar.test.tsx` (covers T020 — `Sidebar.tsx`, T022 — `sidebar.store.ts`)
- [X] T146 [P] Test: Navigation integration — active route highlights correct link; only one link highlighted at a time; Focus Mode state hides sidebar — `frontend/tests/integration/navigation.test.tsx` (covers T020, T064)
- [X] T147 [P] [US7] Test: Reminder notification integration — SW detects due reminder, permission denied falls back to in-app toast, 60s polling interval, notification click navigates to task — `frontend/tests/integration/reminder-notification.test.tsx` (covers T091 — `service-worker.js`, T092 — `useNotifications.ts`)
- [X] T148 [P] [US2] Test: `TaskList` filters hidden tasks from default view, shows them in `showHidden` mode, allows hide/unhide actions — `frontend/tests/integration/task-creation.test.tsx` (covers T043 — `TaskList.tsx`, T118 — hidden tasks page)

### Missing Tests (Required — Not Yet Written)

- [ ] T149 [P] [US1] Test: `AuthContext` auto-refreshes expired tokens via `refreshTokenIfNeeded()`; skips `/users/me` on public routes; clears state on logout — `frontend/tests/unit/hooks/useAuth.test.ts` (covers T013 — `AuthContext.tsx`)
- [ ] T150 [P] [US2] Test: `TaskCard` renders correct priority border color, optimistic checkbox pending state turns green, due date colored red when overdue and yellow when <24h — `frontend/tests/unit/components/TaskCard.test.tsx` (covers T041 — `TaskCard.tsx`)
- [ ] T151 [P] [US2] Test: `useUpdateTask` always includes `version` field in PATCH body; missing version triggers 400 error; server 409 `VERSION_CONFLICT` opens `ConflictResolutionModal` — `frontend/tests/unit/hooks/useTasks.test.ts` (covers T039 — `useTasks.ts`, T112 — `ConflictResolutionModal.tsx`)
- [ ] T152 [P] [US5] Test: `NoteCard` archive and "Convert to Task" buttons call correct standalone endpoints (`POST /api/v1/notes`, `POST /api/v1/notes/:id/convert`); `QuickNoteInput` submits without `taskId` prop — `frontend/tests/unit/components/NoteCard.test.tsx` (covers T073 — `NoteCard.tsx`, T074 — `QuickNoteInput.tsx`)
- [ ] T153 [P] [US6] Test: `AchievementCard` shows progress bar at correct percentage, renders locked state in grayscale, renders unlocked with perk; `AchievementUnlockToast` auto-dismisses after 6 seconds — `frontend/tests/unit/components/AchievementCard.test.tsx` (covers T080 — `AchievementCard.tsx`, T082 — `AchievementUnlockToast.tsx`)
- [ ] T154 [P] [US9] Test: `AISubtasksGenerator` button disabled when `effective_limits.daily_ai_credits === 0`; credits badge shows remaining count; "Accept All" calls `useCreateSubtask` for each suggestion — `frontend/tests/unit/components/AISubtasksGenerator.test.tsx` (covers T061 — `AISubtasksGenerator.tsx`)
- [ ] T155 [P] [US10] Test: `CommandPalette` opens on Cmd+K, fuzzy-searches commands, keyboard navigation (ArrowUp/Down) moves selected index, Enter executes action, Escape closes — `frontend/tests/integration/command-palette.test.tsx` (covers T107 — `CommandPalette.tsx`)
- [ ] T156 [P] Test: `ConflictResolutionModal` shows side-by-side diff (Your version vs Server version); "Keep mine" calls force update; "Take theirs" discards changes; "Cancel" dismisses — `frontend/tests/unit/components/ConflictResolutionModal.test.tsx` (covers T112 — `ConflictResolutionModal.tsx`)

### Phase 14 Bug-Fix Tests

> T161–T166 are co-located in **Phase 14** (Red→Green pairs) per Constitution §VIII TDD. See Phase 14 Critical/High/Medium sections for the full definitions; they are not duplicated here.

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
- **Phase 14 (Bug Fix Sprint)**: Can begin immediately — fixes existing broken implementation; T122–T130 are blocking for production use; T157–T159 (NFR-003 a11y) reclassified here from Phase 13 per sp.analyze C2; T112 (ConflictResolutionModal) reopened and must be completed before T124
- **Phase 15 (Observability)**: Depends on Phase 2 (API client must exist) and Phase 13 (stable app shell — now complete after T157-T159 reclassified to Phase 14); Sentry/Web Vitals require a working application
- **Phase 16 (Test Coverage)**: Independent — V1 tests ([X]) exist already; missing tests ([ ]) can be written any time after their target component is built

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
| US11 Notifications Page | US7 (useNotifications hook) | — |
| US12 Subscription | US1 (auth) | — |
| US13 Mark-as-read | US7 (useNotifications hook) | — |

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

### Parallel Group D: Bug Fix Sprint (Phase 14, immediate priority)
```
T122 — Guard useSubtasks enabled  ← Developer A
T123 — Fix force-complete endpoint ← Developer B
T125 — Migrate notes to standalone /api/v1/notes ← Developer C
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
- **v0.9**: **Bug Fix Sprint (Phase 14)** → production-ready API contracts

### P0 Gaps (Must Fix Before Public Launch)
- **T110**: SW token access (reminders broken without this)
- **T111**: Error boundary (crashes without this)
- **T112**: Conflict resolution UI (data integrity without this) — **REOPENED** (file absent, was incorrectly [X]; must complete before T124)
- **T122**: Guard subtask fetch (API flood breaks UX for testing everything else)
- **T123**: Force-complete endpoint (task completion broken for all users)
- **T124**: Version field (all task updates fail with 400/409)
- **T125**: Notes architecture (notes non-functional until migrated to standalone `/api/v1/notes`)
- **T134**: Token security (critical vulnerability in production)

---

## Notes

- `[P]` = different files, no shared state dependencies — safe to parallelize
- `[USN]` = maps task to functional requirement from `spec.md` v1.1
- Every schema change must also update MSW fixtures/handlers to match
- Commit after each phase checkpoint to enable clean rollback
- `frontend/` path prefix omitted in descriptions for brevity but all paths are relative to repo root
- **Total task count: 185 tasks across 16 phases** (121 original + 14 bug-fix-impl + 6 bug-fix-tests-in-phase14 + 4 NFR-004-gap + 7 observability/perf + 21 test-coverage + 3 a11y tasks + 3 new sp.analyze C1/H4/H6 tasks [T171-T173] + 4 new sp.analyze v5 tasks [T174-T177] + 8 new sp.analyze v6 tasks [T178-T185: 1 env-vars backfill + 7 RED test pairs for H5])
- Phase 13 → Phase 15 reclassification: T175–T176 (NFR-001 performance CI gate and Web Vitals alerts — moved to Phase 15 per sp.analyze v5 M2; depend on T136/T137 which are Phase 15)
- Phase 13 → Phase 14 reclassification: T157–T159 (NFR-003 accessibility — moved to preserve Constitution §II phase discipline — sp.analyze C2)
- Phase 9 → Phase 14 reclassification: T171 (notification.schema.ts — moved per sp.analyze v5 M1; consumed by T128/T129 in Phase 14)
- Phase 14 additions: T161–T166 (RED tests); T167–T170 (NFR-004 autosave + form-persist gap); T171 (reclassified from Phase 9); T172 (FR-004 navigation guard); T173 (RED → T125); T174 (RED → T128)
- Phase 14 execution table: T112 added at priority 0 (sp.analyze v5 H2 — was missing despite being T124 prerequisite); T171 added at priority 2; T178-T185 added at priorities 16-20 (sp.analyze v6 H3/H5 — RED tests + env-vars backfill)
- sp.analyze v6 additions: T178 (H3 AI credit env vars), T179-T180 (H5 RED for T134/T135), T181 (H5 RED for T112 — cross-ref T156), T182 (H5 RED for T172), T183-T185 (H5 RED for T131-T133); T099 reopened (H2); T112 responsive criteria added (M4); T158 audio ARIA expanded (L2)
- Phase 15 additions: T160 (Constitution §V AI logging); T175/T176 (reclassified from Phase 13); T177 (NFR-001 route transition measurement — sp.analyze v5 M4)
- Phase 16 test tasks: 10 existing V1 tests ([X] T139–T148) + 8 component/hook tests ([ ] T149–T156)
- T112 status: Corrected from [X] to [ ] — `ConflictResolutionModal.tsx` confirmed absent (sp.analyze C3)
- T099 path: Corrected from `/task-templates` to `/templates` per API.md (sp.analyze v5 H1)
- Test approach: All tests use `jest.fn()` mocks directly. MSW is NOT used in the test suite (live API exists; MSW is optional dev tooling only via `NEXT_PUBLIC_MSW_ENABLED=true`). Write all tests with the `jest.fn()` mock pattern consistent with V1 tests (T139–T148).
- Phase 14 acceptance criteria are the canonical verification source — cross-reference against `spec.md` v1.1 sections cited per task
