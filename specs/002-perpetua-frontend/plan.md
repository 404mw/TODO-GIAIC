# Perpetua Flow Frontend - Implementation Plan

**Version**: 1.5.0
**Date**: 2026-02-20
**Source**: `g:\Hackathons\GIAIC_Hackathons\02-TODO\frontend`
**Related**: [`spec.md`](./spec.md), [`constitution.md`](../../.specify/memory/constitution.md)

---

## Executive Summary

This document captures the architectural decisions, design patterns, and implementation strategy for the Perpetua Flow frontend — reverse-engineered from the production codebase. It serves as both **archaeological documentation** (what was built and why) and **regeneration blueprint** (how to rebuild or refactor).

**Core Architectural Principle**: Separation of concerns with clear boundaries — App Router pages orchestrate, components present, hooks manage server state, stores manage client state, schemas validate.

---

## I. Architecture Overview

### Architectural Style: Modern React SPA with Server-Side Rendering

**Classification**: Hybrid rendering (SSR for public pages, CSR for dashboard)

**Why this pattern fits**:
- **Public pages** (landing, pricing, about) → SEO critical, infrequent changes → SSR/SSG ideal
- **Dashboard** (tasks, notes, focus) → Dynamic, personalized, frequent updates → CSR with React Query ideal
- **Best of both worlds**: Fast initial load + rich interactivity

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Client)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Next.js App Router (Routing)                 │  │
│  │  ┌────────────┐  ┌──────────────────────────────────┐    │  │
│  │  │  (public)  │  │       /dashboard/*               │    │  │
│  │  │   pages    │  │   (protected routes)             │    │  │
│  │  └────────────┘  └──────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Presentation Layer (Components)              │  │
│  │  - TaskCard, TaskList, TaskDetailView                    │  │
│  │  - NoteCard, FocusTimer, AchievementCard                 │  │
│  │  - CommandPalette, Sidebar, Header                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↓                              ↓                      │
│  ┌─────────────────────┐    ┌───────────────────────────────┐ │
│  │  Server State       │    │    Client State (Zustand)     │ │
│  │  (TanStack Query)   │    │  - Focus mode store           │ │
│  │  - useTasks         │    │  - Command palette store      │ │
│  │  - useNotes         │    │  - Sidebar store              │ │
│  │  - useAchievements  │    │  - Modal stores               │ │
│  │  - useAuth          │    │  - Pending completions store  │ │
│  └─────────────────────┘    └───────────────────────────────┘ │
│           ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          API Client Layer (Fetch + Zod)                   │  │
│  │  - apiClient.get/post/patch/delete                       │  │
│  │  - Auth token injection                                  │  │
│  │  - Idempotency key generation                            │  │
│  │  - Error handling (ApiError)                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↓                              ↓                      │
│  ┌─────────────────────┐    ┌───────────────────────────────┐ │
│  │   Real Backend      │    │    MSW (Development)          │ │
│  │   (Production)      │    │  - tasks.handlers.ts          │ │
│  │   FastAPI + SQLModel│    │  - notes.handlers.ts          │ │
│  └─────────────────────┘    │  - achievements.handlers.ts   │ │
│                              └───────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Service Worker (Background)                        │  │
│  │  - Reminder polling (every 60s)                          │  │
│  │  - Browser notifications                                 │  │
│  │  - postMessage to main thread                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## II. Layer Structure & Responsibilities

### Layer 1: Routing & Page Orchestration (Next.js App Router)

**Location**: [`src/app/`](frontend/src/app/)

**Responsibility**:
- Route definitions and navigation
- Layout composition (headers, sidebars)
- Data fetching coordination (server components where beneficial)
- Middleware (auth guards for protected routes)

**Components**:
- **Public Routes** ([`src/app/(public)/`](frontend/src/app/(public)/)):
  - `/` → Landing page (SSG)
  - `/about` → About page (SSG)
  - `/pricing` → Pricing page (SSG)
  - `/privacy` → Privacy policy (SSG)
  - `/terms` → Terms of service (SSG)

- **Auth Routes** ([`src/app/auth/`](frontend/src/app/auth/)):
  - `/auth/callback` → OAuth redirect handler (server component)

- **Protected Routes** ([`src/app/dashboard/`](frontend/src/app/dashboard/)):
  - `/dashboard` → Main dashboard (task list view)
  - `/dashboard/tasks` → Task management views
  - `/dashboard/tasks/new` → New task creation page (T048)
  - `/dashboard/tasks/completed` → Completed tasks view (T053)
  - `/dashboard/tasks/[id]` → Task detail (dynamic route)
  - `/dashboard/tasks/[id]/edit` → Task edit page (T052)
  - `/dashboard/focus` → Focus mode (full-screen)
  - `/dashboard/notes` → Quick notes view
  - `/dashboard/achievements` → Achievement progress
  - `/dashboard/notifications` → Notifications list (FR-011, T128)
  - `/dashboard/settings` → User settings
  - `/dashboard/settings/hidden-tasks` → Hidden tasks management (T118)
  - `/dashboard/settings/archived-notes` → Archived notes management (T076)
  - `/dashboard/profile` → User profile

**Dependencies**: → Presentation Layer, → AuthContext

**Technology**: Next.js 16.1.1 App Router with React Server Components

**Evidence**: Directory structure [`src/app/`](frontend/src/app/)

---

### Layer 2: Presentation Layer (React Components)

**Location**: [`src/components/`](frontend/src/components/)

**Responsibility**:
- Render UI based on props
- Handle user interactions (clicks, key presses)
- Delegate state changes to hooks/stores
- Accessibility (ARIA, keyboard nav)
- Animations (Framer Motion with reduced-motion support)

**Component Organization**:

#### Feature Components
- **Tasks** ([`src/components/tasks/`](frontend/src/components/tasks/)):
  - `TaskCard.tsx` → Individual task with checkbox, metadata, focus button
  - `TaskList.tsx` → Grid/list of tasks with filtering
  - `TaskDetailView.tsx` → Full task view with subtasks, reminders
  - `TaskForm.tsx` → Create/edit task form
  - `NewTaskModal.tsx` → Modal wrapper for task creation
  - `SubTaskList.tsx` → Subtask display and management
  - `TaskProgressBar.tsx` → Visual progress indicator

- **Notes** ([`src/components/notes/`](frontend/src/components/notes/)):
  - `NoteCard.tsx` → Note display with convert-to-task button
  - `NoteList.tsx` → Grid of notes
  - `QuickNoteInput.tsx` → Inline note capture

- **Focus** ([`src/components/focus/`](frontend/src/components/focus/)):
  - `FocusTimer.tsx` → Countdown timer with pause/resume
  - `FocusTaskView.tsx` → Minimal task display during focus

- **Achievements** ([`src/components/achievements/`](frontend/src/components/achievements/)):
  - `AchievementCard.tsx` → Achievement display with progress
  - `AchievementUnlockToast.tsx` → Celebration animation
  - `StreakDisplay.tsx` → Current streak with fire emoji

- **Reminders** ([`src/components/reminders/`](frontend/src/components/reminders/)):
  - `ReminderForm.tsx` → Create reminder with timing options
  - `ReminderList.tsx` → List of task reminders

- **Recurrence** ([`src/components/recurrence/`](frontend/src/components/recurrence/)):
  - `RecurrenceEditor.tsx` → Visual RRule builder
  - `RecurrencePreview.tsx` → Human-readable recurrence description

#### Base UI Components ([`src/components/ui/`](frontend/src/components/ui/))
- Radix UI wrappers: `Dialog`, `DropdownMenu`, `Popover`, `Select`, `Toast`
- Custom components: `Button`, `Input`, `Label`, `Card`, `Badge`

#### Layout Components ([`src/components/layout/`](frontend/src/components/layout/))
- `Header.tsx` → Top navigation with user menu
- `Sidebar.tsx` → Left navigation with route links
- `CommandPalette.tsx` → Global command launcher (Cmd+K)

**Dependencies**: → Hooks (for data), → Stores (for UI state), → Schemas (for types)

**Technology**: React 19, Radix UI, Framer Motion, Tailwind CSS 4

**Evidence**: [`src/components/`](frontend/src/components/) directory structure

---

### Layer 3: State Management Layer

#### 3A: Server State (TanStack Query)

**Location**: [`src/lib/hooks/`](frontend/src/lib/hooks/)

**Responsibility**:
- Fetch data from backend API
- Cache responses (5-minute stale time)
- Optimistic updates
- Background refetching
- Error retry logic (3 attempts, exponential backoff)

**Key Hooks**:
- **`useTasks.ts`** ([`src/lib/hooks/useTasks.ts`](frontend/src/lib/hooks/useTasks.ts)):
  - `useTasks(filters?)` → List tasks with optional filters
  - `useTask(taskId)` → Single task detail
  - `useCreateTask()` → Mutation for task creation
  - `useUpdateTask()` → Mutation for task updates — **`version` field MUST always be in the payload** (optimistic locking; backend returns 400/409 without it)
  - `useDeleteTask()` → Mutation for soft delete
  - `useForceCompleteTask()` → Mutation for completion — calls `POST /tasks/{id}/force-complete` with body `{ version: number }`; response is `{ data: { task, unlocked_achievements[], streak } }` — **no `useCompleteTask` or `useAutoCompleteTask`; those endpoints do not exist**

- **`useSubtasks.ts`** ([`src/lib/hooks/useSubtasks.ts`](frontend/src/lib/hooks/useSubtasks.ts)):
  - `useSubtasks(taskId, options?: { enabled?: boolean })` → List subtasks — **`enabled` MUST be forwarded to `useQuery`; caller passes `{ enabled: isExpanded }` so collapsed cards never fire a network request**
  - `useCreateSubtask()` → Mutation; `onSuccess` invalidates `['subtasks', variables.taskId]` — **camelCase `taskId`, not `task_id`**
  - `useUpdateSubtask()` → Same invalidation rule as above
  - `useDeleteSubtask()` → Mutation for subtask deletion

- **`useNotes.ts`** ([`src/lib/hooks/useNotes.ts`](frontend/src/lib/hooks/useNotes.ts)):
  > **v1.2 architecture (UPDATE-02):** Notes are user-owned standalone entities — not nested under tasks.
  - `useNotes()` → Queries `GET /api/v1/notes` — returns all notes for the authenticated user (excludes archived by default); pass `{ archived: true }` to include archived
  - `useCreateNote()` → Mutates `POST /api/v1/notes` — input `{ content }`; no `task_id`; note is owned by authenticated user
  - `useUpdateNote()` → Mutates `PATCH /api/v1/notes/{noteId}` — **PATCH, not PUT** (405 otherwise)
  - `useDeleteNote()` → Mutation: `DELETE /api/v1/notes/{noteId}` — hard delete
  - `useArchiveNote()` → Mutation: `PATCH /api/v1/notes/{noteId}` with `{ archived: true }`
  - `useConvertNote()` → Mutation: `POST /api/v1/notes/{id}/convert` — creates task from note content, marks note archived

- **`useAchievements.ts`** ([`src/lib/hooks/useAchievements.ts`](frontend/src/lib/hooks/useAchievements.ts)):
  - `useAchievements()` → Achievement stats and progress
  - `useEffectiveLimits()` → User's current task/note limits

- **`useAuth.ts`** ([`src/lib/hooks/useAuth.ts`](frontend/src/lib/hooks/useAuth.ts)):
  - Wraps `AuthContext` for authentication state

**Query Invalidation Strategy**:
- On mutation success, invalidate related queries
- Example: `useCreateTask` success → invalidate `['tasks']` query
- Example: `useUpdateSubtask` success → invalidate `['tasks', taskId]` and `['subtasks', taskId]`

**Dependencies**: → API Client, → Schemas (for validation)

**Technology**: TanStack Query v5

**Evidence**: [`src/lib/hooks/useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) and related hooks

---

#### 3B: Client State (Zustand)

**Location**: [`src/lib/stores/`](frontend/src/lib/stores/)

**Responsibility**:
- Manage UI-only state (modals, sidebars, focus mode)
- No server interaction (that's TanStack Query's job)
- Persist to localStorage where needed

**Key Stores**:

- **`focus-mode.store.ts`** ([`src/lib/stores/focus-mode.store.ts`](frontend/src/lib/stores/focus-mode.store.ts)):
  ```typescript
  {
    isActive: boolean
    currentTaskId: string | null
    startTime: Date | null
    pausedAt: Date | null          // set on pause(), cleared on resume()
    elapsedSeconds: number        // accumulates only while not paused
    activate: (taskId: string) => void
    deactivate: () => void
    pause: () => void             // sets pausedAt = now
    resume: () => void            // accumulates gap, clears pausedAt
  }
  ```
  - `elapsedSeconds` is written to `localStorage` (`focus_elapsed_seconds_${taskId}`) every second tick and restored on mount if `currentTaskId` matches (FR-004 crash-recovery requirement)
  - Used by: `TaskCard` (activate → navigate to `/dashboard/focus`), `FocusTimer` (pause/resume/deactivate), `FocusTaskView` (read elapsedSeconds on completion)

- **`command-palette.store.ts`** ([`src/lib/stores/command-palette.store.ts`](frontend/src/lib/stores/command-palette.store.ts)):
  ```typescript
  {
    isOpen: boolean
    searchQuery: string
    selectedIndex: number
    filteredCommands: Command[]
    open: () => void
    close: () => void
    setSearchQuery: (query) => void
  }
  ```
  - Global keyboard listener for Cmd+K

- **`pending-completions.store.ts`** ([`src/lib/stores/pending-completions.store.ts`](frontend/src/lib/stores/pending-completions.store.ts)):
  ```typescript
  {
    pendingIds: Set<string>
    togglePending: (taskId) => void
    hasPending: (taskId) => boolean
    clearAll: () => void
  }
  ```
  - Visual feedback for task completion (green background before API call)

- **`sidebar.store.ts`** ([`src/lib/stores/sidebar.store.ts`](frontend/src/lib/stores/sidebar.store.ts)):
  ```typescript
  {
    isCollapsed: boolean
    toggle: () => void
  }
  ```
  - Persisted to localStorage

- **`notification.store.ts`** ([`src/lib/stores/notification.store.ts`](frontend/src/lib/stores/notification.store.ts)):
  ```typescript
  {
    toasts: Toast[]
    addToast: (message, type) => void
    removeToast: (id) => void
  }
  ```
  - Used by Service Worker postMessage handler

**Dependencies**: None (self-contained)

**Technology**: Zustand 5

**Evidence**: [`src/lib/stores/`](frontend/src/lib/stores/) directory

---

### Layer 4: API Client & Validation Layer

**Location**: [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts), [`src/lib/schemas/`](frontend/src/lib/schemas/)

**Responsibility**:
- HTTP communication with backend
- Request/response validation (Zod)
- Authentication (Bearer token injection)
- Error handling (structured ApiError)
- Idempotency (unique key per mutation)

**API Client Structure** ([`src/lib/api/client.ts`](frontend/src/lib/api/client.ts)):

```typescript
export const apiClient = {
  // All methods: async, throw ApiError on failure

  async get<T>(endpoint: string, schema?: ZodType<T>): Promise<T>
  async post<T>(endpoint: string, body: unknown, schema?: ZodType<T>): Promise<T>
  async put<T>(endpoint: string, body: unknown, schema?: ZodType<T>): Promise<T>
  async patch<T>(endpoint: string, body: unknown, schema?: ZodType<T>): Promise<T>
  async delete<T>(endpoint: string, schema?: ZodType<T>): Promise<T>
}
```

**Key Features**:

1. **Auth Token Injection** *(current — see Security Note below)*:
   ```typescript
   headers: {
     Authorization: `Bearer ${localStorage.getItem('auth_token')}`
   }
   ```
   > ⚠️ **Security Note (S-01):** Storing tokens in `localStorage` exposes them to XSS. Target architecture is HttpOnly cookies set by the backend (`Set-Cookie: access_token=…; HttpOnly; Secure; SameSite=Strict`). When migrated, this header injection is removed and the browser sends cookies automatically with `credentials: 'include'`. See Section XI.

2. **Idempotency Key** (POST/PUT/PATCH/DELETE):
   ```typescript
   headers: {
     'Idempotency-Key': crypto.randomUUID()
   }
   ```

3. **Response Handling**:
   - With schema: Validate full response, return parsed object
   - Without schema (legacy): Unwrap `DataResponse[T]` → return `T`

4. **Error Handling**:
   ```typescript
   class ApiError extends Error {
     constructor(
       public status: number,
       public code: string,
       message: string,
       public details?: unknown,
       public request_id?: string
     )
   }
   ```
   - Supports both error formats: `{"error": {...}}` and `{"code": ..., "message": ...}`

**Schema Organization** ([`src/lib/schemas/`](frontend/src/lib/schemas/)):

```
common.schema.ts       → Shared types (Priority, CompletedBy, UserTier)
task.schema.ts         → Task, TaskDetail, CreateTaskRequest, UpdateTaskRequest (version required),
                          ForceCompleteResponseSchema ({ data: { task, unlocked_achievements[], streak } })
subtask.schema.ts      → Subtask, CreateSubtaskRequest, UpdateSubtaskRequest
note.schema.ts         → Note, CreateNoteRequest, UpdateNoteRequest
reminder.schema.ts     → Reminder, CreateReminderRequest
achievement.schema.ts  → AchievementDefinition, UserAchievementState
user.schema.ts         → User, UpdateUserRequest
auth.schema.ts         → AuthResponse, RefreshTokenRequest
error.schema.ts        → ApiError schema
response.schema.ts     → DataResponse[T], PaginatedResponse[T] wrappers
notification.schema.ts → NotificationSchema (id, user_id, title, message, read, task_id|null, created_at, updated_at);
                          DataResponseSchema(NotificationSchema); PaginatedResponseSchema(NotificationSchema)
                          — used by useNotifications.ts (T092), /dashboard/notifications page (T128), mark-as-read (T129)
```

**Dependencies**: None (bottom layer, pure functions)

**Technology**: Fetch API (native), Zod 4.3.5

**Evidence**: [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts), [`src/lib/schemas/`](frontend/src/lib/schemas/)

---

### Layer 5: Cross-Cutting Concerns

#### Authentication Context

**Location**: [`src/lib/contexts/AuthContext.tsx`](frontend/src/lib/contexts/AuthContext.tsx)

**Responsibility**:
- Manage user session (login, logout, token refresh)
- Provide `user` object globally
- Automatic token refresh before expiration
- Redirect to `/login` if unauthenticated on protected routes

**State**:
```typescript
{
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  logout: () => Promise<void>
  refetch: () => Promise<void>
  refreshTokenIfNeeded: () => Promise<void>
  clearError: () => void
}
```

**Token Refresh Logic** *(current — localStorage-based)*:
1. On mount, check `localStorage` for `auth_token`
2. If exists, fetch `/users/me` to validate
3. If 401 Unauthorized, try refresh with `refresh_token`
4. If refresh succeeds, update tokens and retry
5. If refresh fails, clear tokens and redirect to `/login`

> ⚠️ **Security Note (S-01, S-03):** Tokens in `localStorage` are vulnerable to XSS. Target: HttpOnly cookies set by backend. Also, `console.log` statements in this file log auth events in production — must be removed or guarded with `process.env.NODE_ENV === 'development'`. See Section XI.

**Evidence**: [`src/lib/contexts/AuthContext.tsx`](frontend/src/lib/contexts/AuthContext.tsx)

---

#### Service Worker (Background Notifications)

**Location**: [`public/service-worker.js`](frontend/public/service-worker.js)

**Responsibility**:
- Poll backend for due reminders (every 60 seconds)
- Show browser notifications (if permission granted)
- postMessage to all open tabs (in-app toast)
- Mark reminders as delivered

**Polling Logic**:
```javascript
setInterval(async () => {
  const reminders = await fetchReminders() // GET /api/v1/reminders
  const tasks = await fetchTasks()         // GET /api/v1/tasks

  reminders.forEach(reminder => {
    if (!reminder.fired && isTriggerTimePassed(reminder, task)) {
      showNotification(task.title, task.description)
      postMessageToClients({ type: 'REMINDER_DUE', reminder, task })
      markFired(reminder.id) // POST /api/v1/reminders/{id}/fire
    }
  })
}, 60000) // 60 seconds
```

**Activation**:
- User lands on dashboard → `START_REMINDER_POLLING` message sent to SW
- User navigates to public page → `STOP_REMINDER_POLLING` message sent to SW

**Evidence**: [`public/service-worker.js`](frontend/public/service-worker.js)

---

## III. Technology Stack & Rationale

### Core Technologies

| Technology | Version | Purpose | Rationale | Alternatives Considered |
|------------|---------|---------|-----------|------------------------|
| **Next.js** | 16.1.1 | Framework | App Router SSR/SSG, API routes, built-in optimization, Vercel deployment | Remix (less mature), Gatsby (overkill for SPA-heavy app) |
| **React** | 19.2.3 | UI library | Concurrent features, Suspense, largest ecosystem | Vue (smaller ecosystem), Svelte (compile-time, but immature SSR) |
| **TypeScript** | 5.x | Type safety | Catch errors at compile-time, better DX (autocomplete) | Flow (deprecated), JSDoc (weaker type checking) |
| **Tailwind CSS** | 4.x | Styling | Utility-first rapid prototyping, tree-shaking, design system via config | CSS Modules (more boilerplate), Styled Components (runtime cost) |
| **TanStack Query** | 5.90.16 | Server state | Automatic caching, background refetch, optimistic updates, retry logic | SWR (less features), Redux (too much boilerplate), Apollo (GraphQL-specific) |
| **Zustand** | 5.0.9 | Client state | Minimal boilerplate, no providers, TypeScript-first | Redux Toolkit (overkill for UI state), Jotai (atoms too granular), Recoil (Meta-specific) |
| **Zod** | 4.3.5 | Validation | TypeScript-native, schema = type (no duplication), runtime validation | Yup (not TypeScript-first), io-ts (verbose), AJV (JSON Schema, not TS-native) |
| **Radix UI** | Various | Components | Accessible primitives, unstyled, headless, active development | Headless UI (fewer components), React Aria (verbose API), Ariakit (smaller ecosystem) |
| **MSW** | 2.12.7 | Mocking | Network-level interception (works with any HTTP client), browser + Node.js | JSON Server (separate server, no fetch interception), Mirage.js (deprecated) |
| **Framer Motion** | 12.24.12 | Animations | Declarative, reduced-motion support, spring physics | React Spring (imperative API), GSAP (not React-specific), CSS animations (less control) |
| **Fuse.js** | 7.1.0 | Search | Fuzzy search, lightweight, no backend needed | FlexSearch (more complex API), MiniSearch (less fuzzy), Algolia (overkill + cost) |
| **RRule** | 2.8.1 | Recurrence | RFC 5545 standard, complex patterns (nth weekday of month) | Custom (reinvent wheel), cron (less expressive), date-fns (no recurrence) |
| **date-fns** | 4.1.0 | Date utils | Immutable, tree-shakeable, TypeScript support | Moment.js (deprecated, large bundle), Luxon (larger API), Day.js (less tree-shakeable) |

---

### Development Tools

| Tool | Purpose | Rationale |
|------|---------|-----------|
| **Jest 30** | Unit testing | Fast, snapshot testing, parallel execution, React Testing Library integration |
| **React Testing Library 16** | Component testing | User-centric queries (accessibility-first), no implementation details |
| **ESLint 9** | Linting | Catch common errors, enforce code style, Next.js config built-in |
| **Bundle Analyzer** | Performance | Visualize bundle size, identify bloat, optimize imports |

---

## IV. Design Patterns Applied

### Pattern 1: Query Hook Abstraction (Custom Hooks)

**Location**: All hooks in [`src/lib/hooks/`](frontend/src/lib/hooks/)

**Purpose**: Encapsulate TanStack Query boilerplate, provide clean API to components

**Structure**:
```typescript
// Query Hook Pattern
export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => apiClient.get('/tasks', TaskListResponseSchema),
    enabled: filters?.enabled ?? true,
  })
}

// Mutation Hook Pattern
export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (task: CreateTaskRequest) =>
      apiClient.post('/tasks', task, TaskResponseSchema),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
```

**Benefits**:
- Components don't import `useQuery` directly (less coupling)
- Centralized query key management (prevents typos)
- Automatic invalidation logic (no manual cache updates)
- Type-safe mutations (Zod validation)

**When to apply**: All server state interactions

---

### Pattern 2: Store Pattern (Zustand Slices)

**Location**: All stores in [`src/lib/stores/`](frontend/src/lib/stores/)

**Purpose**: Manage UI state without prop drilling

**Structure**:
```typescript
import { create } from 'zustand'

interface FocusModeState {
  isActive: boolean
  currentTaskId: string | null
  activate: (taskId: string) => void
  deactivate: () => void
}

export const useFocusModeStore = create<FocusModeState>((set) => ({
  isActive: false,
  currentTaskId: null,
  activate: (taskId) => set({ isActive: true, currentTaskId: taskId, startTime: new Date() }),
  deactivate: () => set({ isActive: false, currentTaskId: null, startTime: null }),
}))
```

**Benefits**:
- No React Context providers (reduces re-renders)
- Selector-based subscriptions (only re-render when used state changes)
- Simple API (no actions, reducers, middleware)

**When to apply**: UI-only state (modals, sidebars, command palette)

**Contraindications**: Server state (use TanStack Query), form state (use React Hook Form)

---

### Pattern 3: Schema-First API Design

**Location**: [`src/lib/schemas/`](frontend/src/lib/schemas/), [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts)

**Purpose**: Single source of truth for data shapes, runtime validation

**Structure**:
```typescript
// 1. Define schema
export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(500),
  // ... all fields
})

// 2. Infer TypeScript type
export type Task = z.infer<typeof TaskSchema>

// 3. Use in API client
const task = await apiClient.get<Task>('/tasks/123', TaskSchema)
// Runtime validation: throws if response doesn't match schema
```

**Benefits**:
- Type safety: TypeScript knows exact shape
- Runtime safety: Zod validates API responses
- No type drift: Schema changes propagate automatically
- Documentation: Schema is self-documenting

**When to apply**: All API requests/responses

---

### Pattern 4: Optimistic UI with Rollback

**Location**: Pending completions store + TanStack Query mutations

**Purpose**: Instant visual feedback, revert on error

**Structure**:
```typescript
// Component
const { togglePending, hasPending } = usePendingCompletionsStore()
const forceCompleteTask = useForceCompleteTask() // POST /tasks/{id}/force-complete

function handleComplete(task: Task) {
  // 1. Optimistic update (instant green background)
  togglePending(task.id)

  // 2. API call (async) — version required for optimistic locking
  forceCompleteTask.mutate({ taskId: task.id, version: task.version }, {
    onSuccess: (data) => {
      // 3. Clear optimistic state (API succeeded)
      togglePending(task.id)
      // 4. Show achievement toast if any unlocked
      if (data.data.unlocked_achievements.length > 0) {
        triggerAchievementToast(data.data.unlocked_achievements)
      }
    },
    onError: () => {
      // 5. Rollback optimistic state (API failed)
      togglePending(task.id)
      toast('Failed to complete task', { type: 'error' })
    },
  })
}
```

**Benefits**:
- Perceived performance (feels instant)
- User stays in flow (no loading spinners)
- Graceful error handling (rollback on failure)

**When to apply**: Mutations with immediate visual feedback (checkboxes, toggles)

---

### Pattern 5: Compound Component Pattern

**Location**: Radix UI wrappers in [`src/components/ui/`](frontend/src/components/ui/)

**Purpose**: Flexible, composable components with shared context

**Structure** (Dialog example):
```typescript
// Wrapper component manages shared state
<Dialog.Root open={isOpen} onOpenChange={setOpen}>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Title</Dialog.Title>
      <Dialog.Description>Description</Dialog.Description>
      <Dialog.Close>Close</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

**Benefits**:
- Flexibility: Compose any combination of parts
- Encapsulation: Internal state managed by Root
- Accessibility: ARIA attributes handled automatically

**When to apply**: Complex components with multiple parts (modals, dropdowns, popovers)

---

### Pattern 6: Service Worker Message Bus

**Location**: [`public/service-worker.js`](frontend/public/service-worker.js), reminder notification components

**Purpose**: Background task communication with main thread

**Structure**:
```javascript
// Service Worker → Main Thread
clients.matchAll().then(clients => {
  clients.forEach(client => {
    client.postMessage({
      type: 'REMINDER_DUE',
      reminder,
      task,
    })
  })
})

// Main Thread → Service Worker
navigator.serviceWorker.controller?.postMessage({
  type: 'START_REMINDER_POLLING',
})

// Main Thread Listener
navigator.serviceWorker.addEventListener('message', (event) => {
  if (event.data.type === 'REMINDER_DUE') {
    toast(`Reminder: ${event.data.task.title}`)
  }
})
```

**Benefits**:
- Decoupled: SW and main thread independent
- Bidirectional: Both directions communicate
- Multi-tab: postMessage reaches all open tabs

**When to apply**: Background tasks (notifications, sync, caching)

---

### Pattern 7: Lazy Query Pattern (Conditional Fetching)

**Location**: Any query hook where data is only needed on user interaction

**Purpose**: Prevent N×API-request floods when multiple components mount. The canonical case is `TaskCard` — with 25 cards rendered, calling `useSubtasks(task.id)` unconditionally fires 25 simultaneous background requests.

**Structure**:
```typescript
// Hook: accept an enabled flag, forward to useQuery
export function useSubtasks(taskId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['subtasks', taskId],
    queryFn: () => apiClient.get(`/tasks/${taskId}/subtasks`, SubtasksListSchema),
    enabled: options?.enabled ?? true,  // ← CRITICAL: default true preserves detail-page behaviour
  })
}

// Caller: only fetch when the card is expanded
function TaskCard({ task }: { task: Task }) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Zero network requests until user expands the card
  const { data: subtasks } = useSubtasks(task.id, { enabled: isExpanded })

  // Show aggregate from task object (no extra call)
  const progressText = `${task.subtask_completed_count}/${task.subtask_count}`

  return (/* ... */)
}
```

**Benefits**:
- Zero wasted requests for collapsed cards
- Aggregate counts (`task.subtask_count`) show instantly from the tasks list payload
- Exact same hook API — caller opts in with `{ enabled }`, no refactoring elsewhere

**When to apply**: Any hook used inside a list component where the child data is only needed on expansion/hover/click (subtasks, reminders, note previews)

**Contraindications**: Detail pages (single task view) — `enabled` should default to `true` there

---

## V. Data Flow Patterns

### 5.1 Request Flow (User Action → API → UI Update)

**Example**: User completes a task

```
1. User clicks checkbox on TaskCard
   └→ Component: <TaskCard task={task} />

2. Event handler calls mutation hook
   └→ const forceComplete = useForceCompleteTask()
   └→ forceComplete.mutate({ taskId: task.id, version: task.version })

3. Mutation hook calls API client with version
   └→ apiClient.post(`/tasks/${task.id}/force-complete`, { version: task.version }, ForceCompleteResponseSchema)

4. API client adds auth + idempotency
   └→ Headers: { Authorization: "Bearer ...", "Idempotency-Key": "uuid" }

5. Request sent to backend (or MSW in dev)
   └→ POST /api/v1/tasks/{id}/force-complete  body: { version: 3 }

6. Response validated with Zod → ForceCompleteResponseSchema
   └→ { data: { task: {...}, unlocked_achievements: [...], streak: 4 } }

7. Mutation onSuccess callback
   └→ queryClient.invalidateQueries(['tasks'])
   └→ queryClient.invalidateQueries(['tasks', task.id])
   └→ if (data.data.unlocked_achievements.length > 0) → show AchievementUnlockToast

8. TanStack Query refetches invalidated queries
   └→ useTasks() hook re-runs
   └→ useTask(task.id) hook re-runs

9. Components re-render with fresh data
   └→ TaskCard shows completed state
   └→ AchievementUnlockToast shows unlocked achievement names + perks
```

---

### 5.2 Background Sync Flow (Service Worker → API → Main Thread)

**Example**: Reminder fires in background

```
1. Service Worker polling interval triggers
   └→ setInterval(checkReminders, 60000)

2. SW fetches reminders and tasks
   └→ GET /api/v1/reminders
   └→ GET /api/v1/tasks

3. SW calculates trigger times
   └→ for each reminder: triggerTime <= now?

4. SW shows browser notification
   └→ self.registration.showNotification(...)

5. SW posts message to all tabs
   └→ clients.forEach(client => client.postMessage({ type: 'REMINDER_DUE', ... }))

6. Main thread receives message
   └→ navigator.serviceWorker.onmessage event

7. Message handler shows in-app toast
   └→ useNotificationStore.addToast({ message, type: 'reminder' })

8. SW marks reminder as delivered
   └→ POST /api/v1/reminders/{id}/fire
```

---

### 5.3 Optimistic Update Flow (Instant Feedback → Eventual Consistency)

**Example**: User marks task complete (before API responds)

```
1. User clicks checkbox
   └→ handleComplete(taskId)

2. Optimistic state update (instant)
   └→ usePendingCompletionsStore.togglePending(taskId)
   └→ TaskCard background turns green immediately

3. API call initiated (async)
   └→ completeTask.mutate(taskId)

4. User continues working (no blocking)
   └→ Task appears complete while request in-flight

5A. Success path:
   └→ API responds 200 OK
   └→ onSuccess: togglePending(taskId) // Clear optimistic state
   └→ Query invalidation triggers refetch
   └→ TaskCard re-renders with server data

5B. Error path:
   └→ API responds 500 Internal Server Error
   └→ onError: togglePending(taskId) // Rollback optimistic state
   └→ TaskCard reverts to incomplete (red border)
   └→ Toast: "Failed to complete task. Try again."
```

---

## VI. Module Breakdown & Ownership

### Module 1: Task Management (Core Domain)

**Purpose**: CRUD operations for tasks and subtasks

**Key Files**:
- [`src/lib/schemas/task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) → Data shape
- [`src/lib/hooks/useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) → Server state hooks
- [`src/components/tasks/TaskCard.tsx`](frontend/src/components/tasks/TaskCard.tsx) → List item UI
- [`src/components/tasks/TaskDetailView.tsx`](frontend/src/components/tasks/TaskDetailView.tsx) → Detail page UI
- [`src/app/dashboard/tasks/page.tsx`](frontend/src/app/dashboard/tasks/page.tsx) → Route orchestration

**Dependencies**:
- Subtasks module (nested management)
- Reminders module (task reminders)
- Achievements module (completion triggers unlock checks)
- Focus mode module (activate from task card)

**Complexity**: High (most feature-rich module, 10+ endpoints)

**Evidence**: [`src/components/tasks/`](frontend/src/components/tasks/) directory

---

### Module 2: Focus Mode (Distraction-Free Work)

**Purpose**: Full-screen task view with countdown timer

**Key Files**:
- [`src/lib/stores/focus-mode.store.ts`](frontend/src/lib/stores/focus-mode.store.ts) → State management
- [`src/components/focus/FocusTimer.tsx`](frontend/src/components/focus/) → Countdown UI
- [`src/app/dashboard/focus/page.tsx`](frontend/src/app/dashboard/focus/page.tsx) → Full-screen route

**Dependencies**:
- Task module (display task details)
- Subtask module (show subtasks during focus)

**Complexity**: Medium (timer logic, state persistence)

**Evidence**: [`src/app/dashboard/focus/page.tsx`](frontend/src/app/dashboard/focus/page.tsx)

---

### Module 3: Quick Notes (Rapid Capture)

**Purpose**: Lightweight note-taking with task conversion

**Key Files**:
- [`src/lib/schemas/note.schema.ts`](frontend/src/lib/schemas/note.schema.ts) → Data shape
- [`src/lib/hooks/useNotes.ts`](frontend/src/lib/hooks/useNotes.ts) → Server state hooks
- [`src/components/notes/NoteCard.tsx`](frontend/src/components/notes/) → Note UI
- [`src/app/dashboard/notes/page.tsx`](frontend/src/app/dashboard/notes/page.tsx) → Route

**Dependencies**:
- Task module (conversion creates task)
- AI module (note parsing for Pro users)

**Complexity**: Low (simple CRUD, minimal logic)

**Evidence**: [`src/components/notes/`](frontend/src/components/notes/) directory

---

### Module 4: Achievements (Gamification)

**Purpose**: Milestone tracking and perk unlocking

**Key Files**:
- [`src/lib/schemas/achievement.schema.ts`](frontend/src/lib/schemas/achievement.schema.ts) → Data shape
- [`src/lib/hooks/useAchievements.ts`](frontend/src/lib/hooks/useAchievements.ts) → Server state hooks
- [`src/components/achievements/AchievementCard.tsx`](frontend/src/components/achievements/) → Achievement UI
- [`src/app/dashboard/achievements/page.tsx`](frontend/src/app/dashboard/achievements/page.tsx) → Route

**Dependencies**:
- Task module (completion increments stats)
- Focus module (focus completion tracked)
- Note module (conversion tracked)

**Complexity**: Medium (complex stat calculations, streak logic)

**Evidence**: [`src/components/achievements/`](frontend/src/components/achievements/) directory

---

### Module 5: Reminders (Notification System)

**Purpose**: Browser + in-app notifications for task due dates

**Key Files**:
- [`src/lib/schemas/reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) → Data shape
- [`src/lib/hooks/useReminders.ts`](frontend/src/lib/hooks/useReminders.ts) → Server state hooks
- [`public/service-worker.js`](frontend/public/service-worker.js) → Background polling
- Reminder form component (inline in task detail)

**Dependencies**:
- Task module (reminders linked to tasks)
- Notification store (in-app toast)

**Complexity**: High (Service Worker threading, permission handling)

**Evidence**: [`public/service-worker.js`](frontend/public/service-worker.js)

---

### Module 6: Recurrence (Recurring Tasks)

**Purpose**: RFC 5545 RRule-based task repetition

**Key Files**:
- [`src/lib/utils/recurrence.ts`](frontend/src/lib/utils/recurrence.ts) → RRule parsing
- [`src/components/recurrence/RecurrenceEditor.tsx`](frontend/src/components/recurrence/RecurrenceEditor.tsx) → Visual builder
- [`src/components/recurrence/RecurrencePreview.tsx`](frontend/src/components/recurrence/RecurrencePreview.tsx) → Human-readable text

**Dependencies**:
- Task module (templates generate instances)

**Complexity**: High (RRule complexity, edge cases like "2nd Tuesday")

**Evidence**: [`src/components/recurrence/`](frontend/src/components/recurrence/) directory

---

### Module 7: Command Palette (Power User Feature)

**Purpose**: Global keyboard-driven command launcher

**Key Files**:
- [`src/lib/stores/command-palette.store.ts`](frontend/src/lib/stores/command-palette.store.ts) → State management
- [`src/components/layout/CommandPalette.tsx`](frontend/src/components/layout/) → UI + fuzzy search
- Global keyboard listener (Cmd+K)

**Dependencies**:
- All modules (executes commands across app)

**Complexity**: Medium (fuzzy search, keyboard nav)

**Evidence**: [`src/lib/stores/command-palette.store.ts`](frontend/src/lib/stores/command-palette.store.ts)

---

## VII. Regeneration Strategy

### Option 1: Specification-First Rebuild (Clean Slate)

**When to use**: Major technology shift (e.g., Next.js → Remix, React → Svelte)

**Process**:
1. **Start with [`spec.md`](./spec.md)** as blueprint
2. **Apply extracted skills** from [`intelligence-object.md`](./intelligence-object.md):
   - API error handling strategy
   - Schema-first validation
   - Optimistic UI patterns
   - Service Worker message bus
3. **Implement with modern best practices**:
   - Fix known gaps (Section VI of spec.md)
   - Use latest framework features
   - Apply lessons learned (documented in intelligence object)
4. **Test-driven development**:
   - Write tests from acceptance criteria (spec.md Section VI)
   - Red → Green → Refactor cycle
5. **Deploy alongside existing app**:
   - Feature flags for gradual rollout
   - A/B test new vs old
   - Monitor metrics (latency, error rate, user satisfaction)

**Timeline**: 6-8 months (team of 3 developers)

**Risks**:
- Feature parity takes time
- User disruption if migration not seamless
- Two codebases to maintain during transition

**Mitigation**:
- Strangler pattern (migrate one module at a time)
- Feature flags (instant rollback if issues)
- Comprehensive E2E tests (prevent regressions)

---

### Option 2: Incremental Refactoring (Strangler Pattern)

**When to use**: Continuous improvement, no major tech shift

**Process** (per module):

1. **Identify module** to refactor (e.g., Focus Mode)
2. **Extract spec** for that module (reference `spec.md` FR-004)
3. **Build new implementation** alongside old:
   - New route: `/dashboard/focus-v2`
   - New components: `FocusTimerV2.tsx`
   - Feature flag: `ENABLE_FOCUS_V2`
4. **A/B test** old vs new (50/50 traffic split)
5. **Measure** impact (focus completion rate, user satisfaction)
6. **Deprecate old code** when new proven
7. **Remove old code** after 30-day observation period

**Timeline**: One module per 2-week sprint

**Risks**:
- Code duplication during transition
- Complexity of maintaining two versions
- Feature flags sprawl

**Mitigation**:
- Strict timeline for deprecation (no indefinite duality)
- Automated tests for both versions
- Clear ownership (one team owns new, one maintains old)

---

## VIII. Improvement Opportunities (Future Enhancements)

### Architectural Improvements

**1. Introduce GraphQL Layer (BFF Pattern)**
- **Problem**: Over-fetching (task list fetches all fields, only need title + due_date)
- **Solution**: GraphQL BFF (Backend for Frontend) between Next.js and FastAPI
- **Benefits**: Precise data fetching, reduced bandwidth, type-safe queries
- **Effort**: High (6-8 weeks)

**2. Implement Offline-First Architecture**
- **Problem**: App unusable without network (airplane mode)
- **Solution**: IndexedDB cache with background sync, conflict resolution
- **Benefits**: Works offline, syncs when reconnected, better perceived performance
- **Effort**: High (8-10 weeks)

**3. Add Real-Time Collaboration (WebSockets)**
- **Problem**: Multi-device changes require manual refresh
- **Solution**: WebSocket connection for live updates (task completed on phone → instant update on desktop)
- **Benefits**: Multi-device consistency, no polling overhead
- **Effort**: High (10-12 weeks)
- **Note**: Out of scope per spec.md (single-user tool), but requested by users

---

### Technical Debt to Address

**1. Complete Optimistic Locking UI** (P0 from spec.md Section VII)
- Add conflict resolution modal when version mismatch
- Show diff between user's changes and server state
- Allow user to choose: Keep mine, Take theirs, Merge manually

**2. ~~Service Worker Token Management~~** (P0 from spec.md Section VII — **RESOLVED T110**)
- T110 moved auth token to IndexedDB (`frontend/src/lib/utils/token-storage.ts`), accessible from both SW and main thread.
- **Pending:** T134 (HttpOnly cookie migration) may supersede IndexedDB storage; validate token flow after T134 completes.

**3. Comprehensive E2E Tests** (P1)
- Add Playwright test suite for critical journeys
- Run on every PR (CI integration)
- Cover: Auth flow, task CRUD, focus mode, achievement unlocks

**4. Accessibility Audit** (P1)
- Run axe-core on every component
- Add ARIA labels to all icon buttons
- Test with screen readers (VoiceOver, NVDA)

---

## IX. Compliance with Constitution

**Verification against `.specify/memory/constitution.md` v1.0.0**:

### ✅ I. Authority & Source of Truth
- **Compliance**: `spec.md` created as authoritative source
- **Evidence**: This plan references spec.md throughout
- **Status**: Fully compliant

### ✅ II. Phase Discipline
- **Compliance**: No code written before spec (reverse engineering)
- **Evidence**: Spec completed before plan
- **Status**: Compliant (retrospectively)

### ✅ III. Data Integrity & Safety
- **Compliance**:
  - Soft delete with 30-day recovery (spec.md FR-002)
  - Undo guarantee via optimistic updates (spec.md NFR-004)
  - MSW used for dev tooling; tests use `jest.fn()` mocks (no real data in either)
  - Autosave (NFR-004): T167–T168 (debounced 5s autosave); form-state persistence: T169–T170 — added in Phase 14 per sp.analyze remediation (2026-02-20)
- **Evidence**: Pending completions store, soft delete endpoints, T167–T170 (NFR-004 gap tasks)
- **Note**: NFR-004 autosave and form-state persistence had zero task coverage prior to v1.3 plan update; remediated.
- **Status**: Fully compliant (after T167–T170 added)

### ✅ IV. AI Agent Governance
- **Compliance**:
  - AI cannot change task state (FR-009 in spec.md)
  - AI suggestions opt-in (user clicks "Generate subtasks")
  - Undo available (user can reject suggestions)
- **Evidence**: AI features require explicit user action
- **Status**: Fully compliant

### ✅ V. AI Logging & Auditability
- **Compliance**: FR-009 (spec v1.2) mandates structured AI interaction logging per Constitution §V: every call to `useGenerateSubtasks`, `useGetPriorityRecommendation`, and `useParseNote` logs `{ entity_id, user_id, action_type, credits_used, timestamp }` as a Sentry breadcrumb (`Sentry.addBreadcrumb`) and via the structured logger (`logger.info`). The `entity_id` is the `task_id` for subtask/priority calls and the `note_id` for note-parsing calls.
- **Evidence**: T160 (`useAI.ts` `onSuccess` callbacks); T138 (structured logger utility from Phase 15)
- **Note**: Prior v1.1 plan incorrectly marked this N/A — corrected in v1.3 per sp.analyze remediation (2026-02-20)
- **Status**: ✅ Fully compliant — spec FR-009 AI Logging Requirement added in v1.2; T160 implements it

### ✅ VI. API Design Rules
- **Compliance**:
  - Single responsibility endpoints (spec.md Appendix A)
  - Schema-documented (all schemas in `src/lib/schemas/`)
  - No hidden side effects (idempotency keys prevent duplication)
- **Evidence**: API client structure, schema organization
- **Status**: Fully compliant

### ✅ VII. Validation & Type Safety
- **Compliance**:
  - Zod for frontend validation (all schemas)
  - Pydantic for backend validation (per backend spec)
  - Schemas define truth (Pattern 3 in Section IV)
- **Evidence**: Schema-first API design pattern
- **Status**: Fully compliant

### ⚠️ VIII. Testing Doctrine
- **Compliance**:
  - Jest + React Testing Library (spec.md Appendix D)
  - Coverage target: 80% (spec.md Appendix D)
  - Dummy data via MSW fixtures (opt-in dev tooling; tests use `jest.fn()` mocks directly)
- **Evidence**: Test strategy in spec.md Appendix D; Phase 16 (T139–T156)
- **Status**: Partially compliant — V1 tests exist and pass but are not mapped to spec FRs or task IDs. Applies to Phases 1–13 only. Phase 14+ tasks follow TDD (RED test before GREEN implementation) per Constitution §VIII — Phase 14 bug-fix tests (T161–T166) are co-located before their paired implementation tasks in Phase 14.
- **Deviation**: Documented per spec.md §X.5 (Constitution §I.2 reverse-engineering exception for initial build).

### ✅ IX. Secrets & Configuration
- **Compliance**:
  - All secrets in `.env.local` (spec.md NFR-002)
  - No hardcoded API URLs (uses `NEXT_PUBLIC_API_URL`)
  - No secrets in Git history (verified)
  - AI credit limits via env vars (`FREE_TIER_AI_CREDITS`, `PRO_TIER_AI_CREDITS`, `AI_CREDIT_RESET_HOUR`) per spec FR-009 §IX.4
- **Evidence**: Environment variable usage in API client
- **Status**: Fully compliant

### ⚠️ Accessibility (NFR-003) — Added spec v1.2
- **Compliance**: WCAG 2.1 Level AA target; `jest-axe` integration (T157); ARIA labels audit (T158); keyboard-only navigation test (T159)
- **Evidence**: T157–T159 reclassified to Phase 14 per sp.analyze remediation (2026-02-20); Radix UI components have built-in a11y patterns (structural foundation)
- **Status**: ⚠️ Partially compliant — Radix UI provides structural a11y; T157–T159 are open ([ ]) and must complete before NFR-003 is considered satisfied. Compliance cannot be claimed until axe passes CI and keyboard-only navigation is integration-tested.

### ℹ️ Offline-First Architecture — Scope Clarification (spec v1.2)
- **Status**: **DEFERRED** — spec §V Non-Goals #7 explicitly defers IndexedDB mutation queue and background sync as an 8–10 week effort outside the current sprint. Current reliability scope: Error Boundary (T111), TanStack Query retry (T039). NFR-005 offline criterion marked `[DEFERRED]` in spec.
- **Note**: NFR-004 autosave (T167–T168) is in scope and covers the ≤5-second data-loss window on crash; full offline sync is out of scope.

### ✅ X. Infrastructure Philosophy
- **Compliance**: Simplicity over scale (Next.js on Vercel, no microservices)
- **Evidence**: Single Next.js app, TanStack Query (not GraphQL), Zustand (not Redux)
- **Status**: Fully compliant

---

## X. Conclusion & Implementation Guidance

This plan documents the **architectural DNA** of the Perpetua Flow frontend — extracted from production code and distilled into regenerable patterns.

**For rebuilding**:
1. Start with spec.md (requirements)
2. Apply patterns from this plan.md (architecture)
3. Use tasks.md (systematic execution, to be created)
4. Reference intelligence-object.md (reusable skills, to be created)

**For extending**:
1. Update spec.md with new requirements
2. Add new modules to Section VI of this plan
3. Follow existing patterns (Sections IV-V)
4. Maintain Constitution compliance (Section IX)

**For refactoring**:
1. Use Strangler Pattern (Option 2 in Section VII)
2. Extract module spec from spec.md
3. Build new alongside old
4. A/B test, measure, deprecate old

**Version Control**:
- Plan version: 1.5.0 (sp.analyze remediation v6 — version table corrected from 1.4.0 to 1.5.0, duplicate 1.4.0 entry removed, "Next version" note made conditional, 2026-02-20)
- Previous version: 1.4.0 (sp.analyze remediation v4 — header version synced, NFR-003 compliance corrected to ⚠️, version log updated)
- Previous version: 1.3.0 (AI Logging §V corrected, NFR-003 a11y added, offline scope note, NFR-004 autosave gap, §3B store definition completed, 2026-02-20)
- Previous version: 1.2.0 (standalone notes architecture, TDD deviation documented, 6 new routes added, SW token gap resolved)
- Previous version: 1.1.0 (FINDINGS.md corrections incorporated, 2026-02-18)
- Previous version: 1.0.0 (initial reverse-engineered, 2026-02-18)
- Next version: 1.6.0 — bump ONLY when BOTH conditions are verified: (1) T134 HttpOnly cookie migration merged and confirmed; (2) all Phase 14 open (`[ ]`) tasks closed. Do not bump while Phase 14 tasks remain open.
- Major version: 2.0.0 (if tech stack changes)

---

## XI. Known Defects & Architectural Corrections

> This section documents API contract violations found by cross-referencing the implementation against `API.md` v1.0.0. Each entry records **what was built**, **what is correct**, and the **architectural rule** it violates. The corresponding fix tasks are in `tasks.md` Phase 14.

---

### XI.1 API Contract Violations (404 on Every Call)

These are not bugs in logic — the endpoints simply do not exist. Every call returns 404.

| # | What the code calls | What API.md specifies | Key difference | tasks.md ref |
|---|---|---|---|---|
| C-01 | `POST /tasks/{id}/complete` | `POST /tasks/{id}/force-complete` + `{ version }` body | Wrong path, missing body | T123 |
| C-02 | `POST /tasks/{id}/auto-complete` | **Does not exist** | Phantom endpoint | T123 |
| C-05 | `PUT /notes/{id}` | `PATCH /notes/{note_id}` | Wrong HTTP method (405) | T125 |
| C-06 | `POST /subscription/checkout` | `POST /subscription/upgrade` | Wrong path | T127 |
| C-07 | `POST /subscription/purchase-credits` | **Does not exist** | Phantom endpoint | T127 |
| C-08 | `PATCH /notifications/{id}` `{read:true}` | `PATCH /notifications/{id}/read` | Action encoded in path, no body | T129 |

> **Architecture note (UPDATE-02):** C-03 (`POST /notes`) and C-04 (`GET /notes`) have been removed from this table. Notes have been redesigned as standalone user-owned entities at `/api/v1/notes` (FR-005 v1.2). The code's use of these standalone endpoints was architecturally correct — not a violation. T125 scope is reduced to the PATCH method fix only (C-05).

**Architectural rule violated (Constitution §VI.1):** *"Each API endpoint must serve exactly one purpose and must be documented."* Calling undocumented endpoints is a defect by definition.

---

### XI.2 Missing Version Field on Task Mutations

**Problem:** `PATCH /tasks/{id}` requires a `version` field for optimistic locking. The implementation omits it on `toggleCompleted`, `toggleHidden`, and inline-edit saves in `TaskDetailView.tsx`. Backend returns 400 or 409 on every call.

**Correct pattern** (applies to every `updateTask.mutateAsync` call):
```typescript
await updateTask.mutateAsync({
  id: task.id,
  completed: !task.completed,
  version: task.version,  // ← always required
})
```

**Architectural rule:** Optimistic locking (version field) is a data-integrity guarantee — violating it means concurrent edits silently overwrite each other. See Constitution §III.1 (user data loss is unacceptable).

**tasks.md ref:** T124

---

### XI.3 Unconditional Subtask Fetch (Request Flood)

**Problem:** `TaskCard.tsx` calls `useSubtasks(task.id)` unconditionally. With 25 tasks on a page, this fires 25 simultaneous `GET /tasks/{id}/subtasks` requests on every render.

**Correct pattern:** See Pattern 7 above — `useSubtasks(task.id, { enabled: isExpanded })`.

**Architectural rule:** Queries should be scoped to the data that is actually visible. Fetching hidden data is wasted bandwidth and degrades the experience for users on slow connections.

**tasks.md ref:** T122

---

### XI.4 Cache Invalidation Key Mismatch

**Problem:** In `useSubtasks.ts`, `onSuccess` callbacks use `variables.task_id` (snake_case) to invalidate cache. The mutation is called with `variables.taskId` (camelCase). `task_id` evaluates to `undefined`, so `['subtasks', undefined]` is invalidated — the wrong key. The original stale query persists alongside the fresh refetch.

**Correct pattern:**
```typescript
queryClient.invalidateQueries({ queryKey: ['subtasks', variables.taskId] })
queryClient.invalidateQueries({ queryKey: ['tasks',    variables.taskId] })
```

**Architectural rule (Pattern 1):** Centralized query key management must be consistent. A typo in a key string invalidates the wrong cache entry silently.

**tasks.md ref:** T130

---

### XI.5 Wired-But-Commented Reminder API

**Problem:** `TaskDetailView.tsx:117–153` — the `handleAddReminder` and `handleDeleteReminder` functions show success toasts but have the actual API calls commented out. Reminders appear to be saved but nothing reaches the backend.

**Correct pattern:** Import `useCreateReminder` / `useDeleteReminder` and call `.mutateAsync()`. Show success toast only after the promise resolves; show error toast on rejection.

**Architectural rule (Constitution §I.3):** *"The specification must define system states and transitions."* Showing a success state without a state transition is a phantom state — it violates data integrity.

**tasks.md ref:** T126

---

### XI.6 Missing Route: `/dashboard/notifications`

**Problem:** `NotificationDropdown.tsx:209` links to `/dashboard/notifications` but no `page.tsx` exists at that path. The link always 404s.

**Fix:** Create `frontend/src/app/dashboard/notifications/page.tsx` using the already-implemented `useNotifications()` hook.

**tasks.md ref:** T128

---

### XI.7 Security: Tokens in `localStorage`

**Risk level:** High (full account takeover via XSS)

**Current:** `auth_token` and `refresh_token` are stored in `localStorage`. Any JavaScript running on the page — including injected third-party scripts — can read them synchronously.

**Target architecture:**
- Backend sets `Set-Cookie: access_token=…; HttpOnly; Secure; SameSite=Strict`
- `apiClient` switches to `credentials: 'include'` (removes manual Authorization header)
- Service Worker reads token from IndexedDB (per T110) since it cannot read HttpOnly cookies

**CSRF implication (S-02):** Moving to cookies requires adding CSRF protection (double-submit cookie or SameSite=Strict is sufficient for same-origin requests).

**tasks.md ref:** T134

---

### XI.8 Production `console.log` Statements

**Problem:** `AuthContext.tsx` and `payment.service.ts` contain unguarded `console.log` calls that emit auth events and payment data in the production browser console.

**Fix:** Remove or guard with `if (process.env.NODE_ENV === 'development')`.

**Architectural rule (Constitution §IX.3):** *"Secrets must never be exposed to the UI or client-side code."* Console output in production is observable to anyone with DevTools open.

**tasks.md ref:** T135

---

**Plan Version**: 1.5.0
**Last Updated**: 2026-02-20
**Status**: ✅ Updated (v1.5 — sp.analyze remediation v5: notification.schema.ts added to Layer 4 schema list (L4), stale "Next version" line corrected (L1))
