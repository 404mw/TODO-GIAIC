# Perpetua Flow Frontend — Reusable Intelligence

**Version**: 1.0 (Extracted from Implementation)
**Date**: 2026-02-18
**Source**: `g:\Hackathons\GIAIC_Hackathons\02-TODO\frontend` (171 source files)
**Related**: [`spec.md`](./spec.md), [`plan.md`](./plan.md), [`tasks.md`](./tasks.md)

> This document captures **tacit knowledge** embedded in the codebase — patterns worth encoding as reusable skills, architectural decisions with their rationale, and lessons that prevent future mistakes.

---

## I. Extracted Skills (Persona + Questions + Principles)

### Skill 1: Schema-First API Validation (Zod)

**Persona**: You are a TypeScript-first API client engineer who eliminates type drift by making runtime and compile-time types identical.

**Questions to ask before implementing API integration**:
1. Does this endpoint return `{data: T}`, `{data: T[], pagination: {...}}`, or a custom envelope (e.g., `{task: T}`)?
2. Are there optional fields that the backend might omit vs. truly absent fields?
3. What constitutes a valid state? (e.g., is `null` allowed on `completed_at`?)
4. Does the schema need to be used for both request validation AND response parsing?

**Principles**:
- **Schema = Type**: Never write `interface Task` separately from `z.object({...})`; use `z.infer<typeof TaskSchema>` always
- **Validate at boundary**: Parse every API response with `schema.parse(data)` — fail loudly in dev, throw `ApiError` in production
- **Generic wrappers**: Define `DataResponseSchema<T>` and `PaginatedResponseSchema<T>` once; compose them everywhere
- **Null vs. Optional**: Use `z.nullable()` for fields that exist but can be null; use `.optional()` only for fields truly absent in some shapes
- **Export both**: Always export `const FooSchema` and `type Foo = z.infer<typeof FooSchema>` in the same file

**Pattern** (from [`src/lib/schemas/task.schema.ts`](frontend/src/lib/schemas/task.schema.ts)):
```typescript
export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(500),
  due_date: z.string().datetime().nullable(),  // exists but can be null
  description: z.string().max(5000).default(''),  // omitted = default
})
export type Task = z.infer<typeof TaskSchema>

// Generic wrapper — define once, use everywhere
export const TaskResponseSchema = DataResponseSchema(TaskSchema)
export type TaskResponse = z.infer<typeof TaskResponseSchema>
```

**When to apply**: Any project with a typed API contract (REST or GraphQL)
**Contraindications**: Prototypes where schema churn is extreme (add Zod once schema stabilises)

---

### Skill 2: Dual-State Task Completion (Optimistic UI)

**Persona**: You are a UX-focused frontend engineer who makes interactions feel instant while maintaining data integrity.

**Questions to ask before implementing optimistic updates**:
1. What is the visual state before the API confirms? (green checkbox, strikethrough, removed from list)
2. What rollback looks like on error — does user lose context or stay on same page?
3. Is the action idempotent? (safe to retry on network failure)
4. Does the optimistic state conflict with server-sent reality on refetch?

**Principles**:
- **Separate optimistic and committed state**: Never mutate server state cache directly; use a parallel Zustand store for "pending" IDs
- **Instant visual, async commit**: Show the result immediately; API is a background confirmation, not a gate
- **Always rollback**: `onError` callback MUST revert the optimistic store — never leave UI in a phantom state
- **Clear on refetch**: When TanStack Query refetches (after invalidation), the real server state replaces optimistic; no special cleanup needed
- **Idempotency key**: Always send `Idempotency-Key: crypto.randomUUID()` on mutations to prevent double-submission on retry

**Pattern** (from [`src/lib/stores/pending-completions.store.ts`](frontend/src/lib/stores/pending-completions.store.ts) + `useTasks.ts`):
```typescript
// Store: tracks "pending" task IDs (user clicked but API not confirmed)
const usePendingStore = create<{
  pendingIds: Set<string>
  togglePending: (id: string) => void
  hasPending: (id: string) => boolean
}>((set, get) => ({
  pendingIds: new Set(),
  togglePending: (id) => set(state => {
    const next = new Set(state.pendingIds)
    next.has(id) ? next.delete(id) : next.add(id)
    return { pendingIds: next }
  }),
  hasPending: (id) => get().pendingIds.has(id),
}))

// Component usage
function handleComplete(taskId: string) {
  togglePending(taskId)  // instant visual feedback

  completeTask.mutate(taskId, {
    onSuccess: () => togglePending(taskId), // remove pending on confirm
    onError: ()  => togglePending(taskId), // rollback on failure
  })
}
```

**When to apply**: Toggle actions (checkboxes, likes, bookmarks), archiving, soft-delete
**Contraindications**: Destructive actions that cannot be rolled back (permanent delete); use confirmation dialog instead

---

### Skill 3: Layered Error Handling (ApiError Class)

**Persona**: You are a defensive API client engineer who ensures no error is swallowed, every failure has an actionable response, and debugging is never blocked by missing context.

**Questions to ask before implementing error handling**:
1. Does the API use one error format or multiple? (e.g., `{error: {...}}` vs `{code, message}`)
2. Which errors are user-actionable (show message) vs. system errors (log + show generic)?
3. What error codes map to specific UI states? (e.g., `TOKEN_EXPIRED` → refresh, `CREDITS_EXHAUSTED` → upsell modal)
4. Should errors be retried? (5xx: yes with backoff; 4xx: no retry)

**Principles**:
- **Typed error class**: `class ApiError extends Error { status, code, message, details, request_id }` — never throw plain strings
- **Handle both formats**: Real APIs often evolve error shapes; support both `{error: {...}}` and `{code, message}` with fallback
- **Propagate request_id**: Always extract and store `request_id` for user-reported issues (show in error UI as reference code)
- **Branch on code, not message**: `if (err.code === 'TOKEN_EXPIRED')` not `if (err.message.includes('expired'))`
- **Global 401 handler**: Intercept 401 in the client, attempt token refresh, retry original request once

**Pattern** (from [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts)):
```typescript
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
    public request_id?: string
  ) { super(message); this.name = 'ApiError' }
}

async function handleResponse<T>(response: Response, schema?: z.ZodType<T>): Promise<T> {
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new ApiError(
      response.status,
      err.code ?? err.error?.code ?? 'UNKNOWN_ERROR',
      err.message ?? err.error?.message ?? 'Request failed',
      err.details ?? err.error?.details,
      err.request_id ?? err.error?.request_id,
    )
  }
  const data = await response.json()
  return schema ? schema.parse(data) : data
}
```

**When to apply**: Every project with a REST or GraphQL API
**Contraindications**: None — always use typed error classes in typed languages

---

### Skill 4: TanStack Query Hook Abstraction

**Persona**: You are a React state management engineer who encapsulates all server-state complexity behind clean, component-friendly hooks.

**Questions to ask before writing a query hook**:
1. What is the natural key hierarchy? (`['tasks']` → `['tasks', taskId]`)
2. Which mutations should invalidate which queries? (create task invalidates `['tasks']`; update task also invalidates `['tasks', id]`)
3. Should this query be disabled by default? (e.g., only when `taskId` is known)
4. What is the stale time? (user-facing data: 5 min; real-time data: 0)

**Principles**:
- **One hook per entity operation**: `useTasks` (list), `useTask(id)` (single), `useCreateTask` (mutation) — never put all three in one hook
- **Query keys are the cache**: Treat `['tasks', filters]` as a namespaced cache address; inconsistent keys = stale data bugs
- **Invalidate specifically**: After `useCreateTask` success, invalidate `['tasks']` (the list) but NOT `['tasks', newId]` (would trigger an unnecessary fetch)
- **`enabled` guard**: Always include `enabled: !!taskId` for hooks that depend on a parameter; prevents queries with `undefined` IDs
- **Type the mutation variables**: `useMutation<Response, Error, Variables>` — never cast mutation input to `any`

**Pattern** (from [`src/lib/hooks/useTasks.ts`](frontend/src/lib/hooks/useTasks.ts)):
```typescript
// QUERY: list with filters
export function useTasks(filters?: { completed?: boolean; priority?: string }) {
  const params = new URLSearchParams()
  if (filters?.completed !== undefined) params.set('completed', String(filters.completed))
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => apiClient.get(`/tasks?${params}`, TaskListResponseSchema),
  })
}

// QUERY: single item
export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => apiClient.get(`/tasks/${taskId}`, TaskDetailResponseSchema),
    enabled: !!taskId,  // CRITICAL: prevents query with undefined id
  })
}

// MUTATION: cascade invalidation
export function useCreateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (task: CreateTaskRequest) =>
      apiClient.post('/tasks', task, TaskResponseSchema),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tasks'] })  // invalidate list only
    },
  })
}
```

**When to apply**: Every React project fetching server state
**Contraindications**: Static data that never changes (use plain `fetch` in RSC instead)

---

### Skill 5: Service Worker Message Bus (Background → Foreground)

**Persona**: You are a web platform engineer implementing background processing that communicates reliably with an active browser tab.

**Questions to ask before implementing a Service Worker**:
1. Who controls start/stop? (page sends `START_POLLING`; don't auto-start to avoid polling on public pages)
2. How does SW get configuration it can't read from `localStorage`? (page sends config via postMessage)
3. What happens when the page is closed? (background tasks stop naturally; state lost)
4. How do you prevent duplicate intervals? (always `clearInterval` before setting new one)

**Principles**:
- **SW is stateless between browser sessions**: Don't rely on SW memory across page reloads; re-send config on mount
- **postMessage for config injection**: SW cannot access `localStorage`; main thread must send tokens, API URLs via `postMessage`
- **Dual notification**: Always send BOTH browser notification AND `postMessage`-triggered in-app toast — don't make one the fallback for the other; both serve different contexts
- **Stop on public pages**: `STOP_REMINDER_POLLING` when navigating away from protected routes to avoid unauthenticated API calls
- **Mark-as-delivered pattern**: After firing a notification, immediately POST to mark it delivered — prevents re-trigger on next poll cycle

**Pattern** (from [`public/service-worker.js`](frontend/public/service-worker.js)):
```javascript
// Main thread → SW: inject config + start
navigator.serviceWorker.controller?.postMessage({ type: 'SET_API_URL', url: process.env.NEXT_PUBLIC_API_URL })
navigator.serviceWorker.controller?.postMessage({ type: 'START_REMINDER_POLLING' })

// SW: listen + act
self.addEventListener('message', event => {
  if (event.data.type === 'START_REMINDER_POLLING') {
    if (pollInterval) clearInterval(pollInterval)  // prevent duplicates
    pollInterval = setInterval(checkReminders, 60_000)
    checkReminders()  // immediate first check
  }
})

// SW → Main thread: fire event
clients.matchAll({ includeUncontrolled: true }).then(tabs =>
  tabs.forEach(tab => tab.postMessage({ type: 'REMINDER_DUE', reminder, task }))
)
```

**When to apply**: Background polling, push notifications, offline sync, periodic tasks
**Contraindications**: Simple one-time background work (use Web Worker instead); data that needs localStorage access (use IndexedDB)

---

### Skill 6: Zustand Store Slice Pattern

**Persona**: You are a React state management engineer who keeps UI state minimal, co-located, and free of provider boilerplate.

**Questions to ask before creating a store**:
1. Is this server state (data from API) or UI state (modal open, selected ID, sidebar collapsed)?
2. Would React `useState` + prop drilling work for < 3 component levels? (prefer local state)
3. Does this state need to persist across page refreshes? (add `persist` middleware)
4. Does any component need to subscribe to only part of this state? (use selectors)

**Principles**:
- **One store per concern**: `focus-mode.store`, `sidebar.store`, `command-palette.store` — never one giant store
- **Actions in the store**: `activate()`, `deactivate()`, `toggle()` live in the store definition, not in components
- **Selectors prevent re-renders**: `const isActive = useFocusModeStore(s => s.isActive)` subscribes to `isActive` only; component won't re-render when `currentTaskId` changes
- **Persist with caution**: Only persist truly stable state (collapsed sidebar); never persist derived data
- **No server state**: If data comes from an API, it belongs in TanStack Query, not Zustand

**Pattern** (from [`src/lib/stores/focus-mode.store.ts`](frontend/src/lib/stores/focus-mode.store.ts)):
```typescript
interface FocusModeState {
  isActive: boolean
  currentTaskId: string | null
  startTime: Date | null
  // actions co-located in interface
  activate: (taskId: string) => void
  deactivate: () => void
}

export const useFocusModeStore = create<FocusModeState>((set) => ({
  isActive: false,
  currentTaskId: null,
  startTime: null,
  activate: (taskId) => set({ isActive: true, currentTaskId: taskId, startTime: new Date() }),
  deactivate: () => set({ isActive: false, currentTaskId: null, startTime: null }),
}))

// Usage with selector — won't re-render on currentTaskId change
const isActive = useFocusModeStore(s => s.isActive)
```

**When to apply**: Global UI state (modals, sidebars, command palette, feature toggles)
**Contraindications**: Local component state (< 3 levels); server data (use TanStack Query)

---

## II. Architecture Decisions (Inferred ADRs)

### ADR-001: TanStack Query over Redux for Server State

**Status**: Accepted (inferred from implementation)

**Context**: Needed a solution for async data fetching with caching, refetching, and mutation management in a React app.

**Decision**: TanStack Query v5

**Evidence from codebase**:
- All 15+ hooks in `src/lib/hooks/` use `useQuery`/`useMutation` — zero Redux imports
- `onSuccess` invalidation pattern used consistently across mutations
- No Redux store, no actions/reducers/selectors for server data

**Consequences — Positive**:
- Automatic cache invalidation on mutation
- Background refetching keeps data fresh
- Request deduplication (two components calling `useTasks()` = one network request)
- Built-in loading/error/success states eliminate boilerplate

**Consequences — Negative**:
- Query key management is manual (typos cause stale data)
- Less visibility into cache state than Redux DevTools (though TanStack Query DevTools help)

**Rejected alternative**: Redux Toolkit + RTK Query — more boilerplate, worse DX for this use case

---

### ADR-002: MSW over JSON Server for Development Mocking

**Status**: Accepted (inferred from implementation)

**Context**: Needed a way to develop and test frontend against a realistic backend without requiring the FastAPI backend to be running.

**Decision**: MSW (Mock Service Worker) v2

**Evidence from codebase**:
- `src/mocks/browser.ts` (browser interception), `src/mocks/server.ts` (Node.js for Jest)
- `src/mocks/handlers/` with realistic handlers including validation, latency, error cases
- `src/mocks/data/*.fixture.ts` with typed test data

**Consequences — Positive**:
- Intercepts at network level (fetch/XHR/axios all work without changes)
- Same handlers reused in both browser dev and Jest tests
- Realistic latency simulation (`delay(100-500ms)`)
- Handlers validate request body with Zod schemas — catch frontend bugs early

**Consequences — Negative**:
- Worker registration required (`mockServiceWorker.js` in public/)
- Handlers must be kept in sync with real backend (no auto-generation)
- More setup than `json-server`

**Rejected alternative**: JSON Server — separate process, doesn't intercept fetch, no request validation, no latency control

---

### ADR-003: Soft Delete over Hard Delete for Tasks

**Status**: Accepted (inferred from implementation)

**Context**: Constitution III mandates "user data loss is unacceptable" and "undo guarantee for all updates".

**Decision**: Soft delete (`hidden: true`) with 30-day recovery window and `tombstone_id`

**Evidence from codebase**:
- `TaskSchema` has `hidden: boolean` and `archived: boolean` fields
- `TaskDeleteResponseSchema` returns `{ tombstone_id, recoverable_until }`
- MSW delete handler sets `task.hidden = true` (not splice/remove)
- Settings page has `/dashboard/settings/hidden-tasks` for recovery

**Consequences — Positive**:
- Satisfies undo guarantee (spec NFR-004)
- 30-day recovery window for accidental deletions
- Audit trail preserved (task history intact)

**Consequences — Negative**:
- Hidden tasks accumulate in DB (cleanup job needed after 30 days)
- `GET /tasks` must filter `hidden: false` by default (extra query param)
- User must know to check settings for recovery

**Rejected alternative**: Hard delete — violates Constitution III.4 (undo guarantee)

---

### ADR-004: Optimistic Locking via `version` Field

**Status**: Accepted (partially — UI incomplete per spec P0 gap)

**Context**: Multiple devices (phone, laptop, desktop) can edit the same task; concurrent edits must not silently overwrite each other.

**Decision**: Every task carries a `version: number` field; `PATCH /tasks/:id` requires sending `version`; backend returns 409 if versions don't match

**Evidence from codebase**:
- `TaskSchema` has `version: z.number().int()` field
- `UpdateTaskRequestSchema` requires `version` (`.required({ version: true })`)
- Backend conflict response (inferred from spec)

**Consequences — Positive**:
- Prevents silent data loss on concurrent edits
- User always knows their write succeeded or was rejected
- No server-side locking (stateless backend)

**Consequences — Negative**:
- Client must track and send `version` on every update (easy to forget)
- Conflict resolution UI still needs to be built (P0 gap in spec)
- Version field adds payload overhead

**Rejected alternative**: Last-write-wins — violates Constitution III (data integrity guarantee)

---

## III. Patterns & Conventions

### Convention 1: File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Schema | `[entity].schema.ts` | `task.schema.ts` |
| Hook (query) | `use[Entity]s.ts` | `useTasks.ts` |
| Store | `[feature].store.ts` | `focus-mode.store.ts` |
| Component | `PascalCase.tsx` | `TaskCard.tsx` |
| Service | `[entity].service.ts` | `auth.service.ts` |
| Utility | `[feature].ts` | `recurrence.ts` |
| Fixture | `[entity]s.fixture.ts` | `tasks.fixture.ts` |
| Handler | `[entity]s.handlers.ts` | `tasks.handlers.ts` |

---

### Convention 2: Response Envelope Handling

```
GET   /users/me          → { data: User }                    ← DataResponse<T>
GET   /tasks             → { data: Task[], pagination: {...} } ← PaginatedResponse<T>
POST  /tasks/{id}/force-complete → { data: { task, unlocked_achievements[], streak } }
POST  /auth/google/callback → { access_token, refresh_token } ← NO wrapper (auth is different)
```

**Rule**: Auth endpoints (`/auth/*`) are unwrapped. Everything else uses `DataResponse<T>` or `PaginatedResponse<T>`.

---

### Convention 3: MSW Handler Error Format

Always return errors in `{ error: { code, message } }` format from MSW handlers, matching the real backend:
```typescript
return HttpResponse.json(
  { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
  { status: 404 }
)
```

---

### Convention 4: Query Key Hierarchy

```typescript
['tasks']               // all tasks (list)
['tasks', filters]      // filtered list
['tasks', taskId]       // single task
['subtasks', taskId]    // subtasks for a task
['notes']               // all notes
['notes', noteId]       // single note
['achievements']        // user achievement state
['reminders']           // all reminders
['reminders', taskId]   // reminders for a specific task
```

**Invalidation rule**: Mutation on `['tasks', id]` should also invalidate `['tasks']` (the list may show counts/progress)

---

## IV. Known Pitfalls & Anti-Patterns

### Pitfall 1: Service Worker Token Access Gap

**Problem**: Service Worker runs in a separate thread and cannot access `localStorage`. The current codebase has `// TODO: Get auth token` comments in `service-worker.js:28` — reminders fail silently for authenticated users.

**Root cause**: `getAuthToken()` in `client.ts` uses `localStorage.getItem('auth_token')`, which is unavailable in SW context.

**Fix**: Move token storage to `IndexedDB` (accessible from both SW and main thread):
```javascript
// In service-worker.js
async function getToken() {
  const db = await openDB('perpetua-auth', 1)
  return db.get('tokens', 'access_token')
}
```

**Lesson**: Never store auth tokens in `localStorage` if you need SW access. Use `IndexedDB` from day one.

---

### Pitfall 2: Missing Error Boundary Causing White Screen Crashes

**Problem**: Unhandled errors in React render throw to the root and crash the entire app with a white screen. There is no `ErrorBoundary` wrapping `RootLayout`.

**Root cause**: React does not catch errors in hooks or async code in Error Boundaries — only synchronous render errors. But render errors (null access, etc.) are common.

**Fix**: Add `ErrorBoundary` at `app/layout.tsx` level:
```tsx
// src/components/errors/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }
  static getDerivedStateFromError(error) { return { hasError: true, error } }
  render() {
    if (this.state.hasError) return <ErrorFallback error={this.state.error} />
    return this.props.children
  }
}
```

**Lesson**: Add Error Boundary as the first thing after project setup, not after the first production crash.

---

### Pitfall 3: Optimistic Updates Without Rollback

**Anti-pattern**:
```typescript
// BAD: no rollback on error
mutate(taskId, {
  onSuccess: () => togglePending(taskId)
  // no onError handler!
})
```

**Result**: If API fails, task card stays green forever (phantom state).

**Fix**: Always pair `onSuccess` and `onError` for any optimistic update:
```typescript
mutate(taskId, {
  onSuccess: () => togglePending(taskId),
  onError:   () => { togglePending(taskId); toast('Failed', { type: 'error' }) },
})
```

**Lesson**: Treat optimistic stores as temporary state that must be cleared on BOTH success and failure.

---

### Pitfall 4: Query Key Typos Causing Stale Cache

**Anti-pattern**:
```typescript
// In useTasks.ts
queryKey: ['task']  // singular

// In useUpdateTask.ts onSuccess:
invalidateQueries({ queryKey: ['tasks'] })  // plural — DIFFERENT KEY, no invalidation!
```

**Result**: After updating a task, the list doesn't refresh.

**Fix**: Export query key constants:
```typescript
// src/lib/query-keys.ts
export const QUERY_KEYS = {
  tasks: () => ['tasks'] as const,
  task: (id: string) => ['tasks', id] as const,
  subtasks: (taskId: string) => ['subtasks', taskId] as const,
} as const
```

**Lesson**: Query keys are critical infrastructure — centralize them to prevent typo-driven cache bugs.

---

### Pitfall 5: Unchecked Subtask Limit

**Anti-pattern**: Creating subtasks without checking the 10-per-task limit client-side leads to a jarring backend error after the user fills out the form.

**Pattern to follow** (from MSW handler):
```typescript
// Check limit BEFORE showing the form
const canAddSubtask = subtaskCount < 10

// In AddSubTaskForm
{!canAddSubtask && (
  <p role="alert" className="text-red-500">
    Maximum 10 subtasks per task
  </p>
)}
<button disabled={!canAddSubtask}>Add Subtask</button>
```

**Lesson**: Validate limits client-side too. Backend enforcement is the safety net, not the UX.

---

## V. Reusability Assessment

### Components Portable As-Is

| Component | Portability | Notes |
|-----------|------------|-------|
| `ApiError` class | ✅ High | Reuse in any TypeScript REST client |
| `DataResponseSchema<T>` wrapper | ✅ High | Reuse in any Zod-based API project |
| `useLocalStorage` hook | ✅ High | Standard utility, no dependencies |
| `useReducedMotion` hook | ✅ High | Standard accessibility hook |
| `ErrorBoundary` component | ✅ High | Class component, React only dependency |
| `PendingCompletionsStore` pattern | ✅ Medium | Rename for non-task context |
| Service Worker message bus | ✅ Medium | Generalise for any polling + notification scenario |

### Patterns Worth Generalising as Skills

| Pattern | Generalisation |
|---------|---------------|
| Schema-first API validation | Applies to any Zod + fetch project |
| Optimistic UI with rollback | Applies to any TanStack Query + Zustand project |
| Query hook abstraction | Applies to any TanStack Query project |
| Zustand store slice pattern | Applies to any Zustand project |
| SW message bus | Applies to any Service Worker project |

### Domain-Specific (Not Portable)

- Streak calculation logic (specific to this habit-tracking domain)
- RRule recurrence UI (specific to task recurrence)
- Achievement threshold checks (specific to gamification design)
- Focus mode countdown (could generalise as a "timer" component)

---

## VI. What to Avoid in Future Projects

### 1. `localStorage` for Anything Needed Across Threads
- **Why bad**: Service Workers, Web Workers, and SharedWorkers cannot access `localStorage`
- **Alternative**: `IndexedDB` (universal) or `sessionStorage` (same-thread only)

### 2. Mutation Without Idempotency Key
- **Why bad**: Network retries can create duplicate tasks, notes, or reminders
- **Alternative**: Always send `Idempotency-Key: crypto.randomUUID()` on POST/PUT/DELETE; backend deduplicates

### 3. `version` Field Sent Optionally Instead of Required
- **Why bad**: Forgetting to send `version` on update means the backend cannot enforce optimistic locking
- **Alternative**: Make `version` required in `UpdateRequestSchema` (`.required({ version: true })`) so TypeScript enforces it at compile time

### 4. Service Worker Polling on Public Pages
- **Why bad**: Unauthenticated users trigger 401 errors, noise in logs, wasted bandwidth
- **Alternative**: Send `STOP_REMINDER_POLLING` postMessage immediately when user navigates to public routes

### 5. Hardcoding Base URL in Service Worker
- **Why bad**: SW cannot read `process.env` — env vars are undefined at SW runtime
- **Alternative**: Main thread sends `SET_API_URL` postMessage on startup, SW stores in module-level variable

---

## VII. Metrics at Time of Extraction

| Metric | Value |
|--------|-------|
| Total source files | 171 TypeScript/TSX |
| Total pages (routes) | 25 |
| Zod schemas | 17 |
| TanStack Query hooks | 15+ |
| Zustand stores | 12 |
| Feature components | 40+ |
| MSW handlers | 9 handler files |
| Test fixtures | 5 fixture files |
| Documentation generated | 2,705 lines (spec + plan) |
| Spec-to-code ratio | ~1.8% |
| P0 gaps | 3 (SW token, error boundary, conflict UI) |
| P1 gaps | 3 (a11y, rate limiting, analytics) |
| P2 gaps | 3 (dark mode, command frecency, bulk ops) |

---

**Intelligence Object Version**: 1.0.0
**Last Updated**: 2026-02-18
**Status**: ✅ Complete
