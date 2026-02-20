# Perpetua Flow Frontend - Specification

**Version**: 1.6.0 (sp.analyze Remediation v6 — H4 actor_type added to AI log schema, L1 §IX subsection refs fixed, M3 jest-axe reference corrected, M4 ConflictResolutionModal added to NFR-007, M1 NFR-005 ownership separation, M2 analytics/feedback formally deferred to Non-Goals §7–8)
**Date**: 2026-02-18
**Source**: `g:\Hackathons\GIAIC_Hackathons\02-TODO\frontend`
**Constitution**: `.specify/memory/constitution.md` v1.0.0
**Changelog**: v1.1 — Captured 12 API-contract and UX bugs from FINDINGS.md as enforceable requirements (FR-001 security, FR-002 completion/version, FR-003 subtask loading, FR-005 notes endpoints, FR-006 reminder wiring, FR-011 notifications page, FR-012 subscription endpoint, FR-013 mark-as-read endpoint; NFR-002 token security, NFR-007 responsive modals)

---

## Executive Summary

Perpetua Flow is a production-grade, single-user task management SaaS application designed to help users build lasting productivity habits through smart task management, consistency tracking, and focused work sessions. The frontend is a modern, AI-powered Next.js application that prioritizes data integrity, user experience, and maintainability.

**Core Philosophy**: Build once, evolve forever — no rewrites. Specification is the supreme authority.

---

## I. Problem Statement & System Intent

### Problem Being Solved

Users struggle to maintain consistent productivity due to:
1. **Task overload**: No clear prioritization or breakdown of complex work
2. **Broken habits**: Missing the "one day" breaks streaks and demotivates
3. **Distractions**: Inability to focus on single tasks without interruption
4. **Idea loss**: Quick thoughts get forgotten before becoming actionable
5. **Reminder fatigue**: Generic reminders lack context and timing flexibility

### Target Users

- **Primary**: Individual knowledge workers (developers, designers, writers, managers)
- **Secondary**: Students and freelancers managing personal projects
- **Tier Model**: Free (basic features), Pro (AI features, voice notes, unlimited tasks)

### Core Value Proposition

Perpetua Flow is **not just another task manager** — it's a **habit-building productivity system** that:

1. **Makes consistency achievable**: Streak tracking with "grace days" prevents demotivation
2. **Breaks down complexity**: Subtasks and AI-powered task decomposition
3. **Enforces deep work**: Focus mode with countdown timers and distraction elimination
4. **Captures fleeting thoughts**: Quick notes that convert to structured tasks
5. **Reminds intelligently**: Context-aware reminders with flexible timing

**Why this exists instead of Todoist/Asana**: Those are project management tools. Perpetua Flow is a **personal productivity coach** focused on building sustainable habits, not just tracking tasks.

---

## II. Functional Requirements

### FR-001: User Authentication (Google OAuth 2.0)

**What**: Secure authentication via Google OAuth with JWT token management

**Why**:
- Reduces friction (no password management)
- Leverages Google's security infrastructure
- Enables future cross-device sync via Google account

**Inputs**:
- Google OAuth redirect with authorization code
- Refresh token for session extension

**Outputs**:
- Access token (JWT, 15-minute TTL)
- Refresh token (rotation on use)
- User profile (email, name, avatar)

**Side Effects**:
- Token storage in **HttpOnly cookies** (MUST NOT be stored in `localStorage` — see FR-001 Security Constraint below)
- User session creation in backend
- Redirect to dashboard on success

**FR-001 Security Constraint**:
- Access and refresh tokens MUST be stored in HttpOnly cookies, not `localStorage`
- `localStorage` is accessible to any JavaScript on the page; an XSS vulnerability exposes all tokens stored there, enabling full account takeover
- HttpOnly cookies are inaccessible to JavaScript, preventing token theft via XSS
- This is a **critical security requirement** — `localStorage` token storage is NOT acceptable in production

**Success Criteria**:
- [ ] User can authenticate with Google account
- [ ] Tokens are stored in HttpOnly cookies, not accessible to JavaScript
- [ ] Tokens refresh automatically before expiration
- [ ] Logout clears all session data (cookies revoked)
- [ ] Failed auth redirects to login with error message
- [ ] No auth-related data is logged to the browser console in production

**Edge Cases**:
- Token expiration during active session → silent refresh
- Network failure during auth → retry with exponential backoff
- Revoked Google permissions → force re-authentication

**Implementation Evidence**: [`src/lib/contexts/AuthContext.tsx`](frontend/src/lib/contexts/AuthContext.tsx), [`src/lib/hooks/useAuth.ts`](frontend/src/lib/hooks/useAuth.ts)

---

### FR-002: Task Creation & Management

**What**: Full CRUD operations for tasks with rich metadata

**Why**: Core entity of the productivity system — must support complex workflows

**Task Schema** (from [`src/lib/schemas/task.schema.ts`](frontend/src/lib/schemas/task.schema.ts)):
```typescript
{
  id: string (UUID)
  user_id: string (UUID)
  template_id: string | null (UUID, for recurring instances)

  // Core fields
  title: string (1-500 chars, required)
  description: string (max 5000 chars, optional)
  priority: 'low' | 'medium' | 'high' (default: 'medium')
  due_date: datetime | null
  estimated_duration: number | null (minutes, 1-720)

  // Focus tracking
  focus_time_seconds: number (seconds spent in focus mode)

  // Completion
  completed: boolean
  completed_at: datetime | null
  completed_by: 'manual' | 'auto' | 'force' | null

  // Status flags
  hidden: boolean (soft delete)
  archived: boolean

  // Subtask aggregates (optimization for list view)
  subtask_count: number
  subtask_completed_count: number

  // Metadata
  created_at: datetime
  updated_at: datetime
  version: number (optimistic locking)
}
```

**Operations**:

1. **Create Task** (POST `/api/v1/tasks`)
   - Input: `{ title, description?, priority?, due_date?, estimated_duration? }`
   - Output: Created task with generated ID
   - Validation: Title required (1-500 chars), duration 1-720 minutes
   - Limit: 50 tasks per user (free tier), upgradable via achievements

2. **Update Task** (PATCH `/api/v1/tasks/{id}`)
   - Input: Partial task + `version` (required for optimistic locking — **MUST always be included**)
   - Output: Updated task with incremented version
   - Conflict handling: If version mismatch, return 409 with latest version
   - **Version Constraint**: The `version` field MUST be included in every `PATCH /tasks/{id}` call without exception. Omitting it causes a 400 or 409 error from the backend. This applies to all partial updates including toggling `completed`, `hidden`, and any other field.

3. **Delete Task** (DELETE `/api/v1/tasks/{id}`)
   - Soft delete: Sets `hidden: true`
   - Returns: `{ tombstone_id, recoverable_until }`
   - Recovery window: 30 days, then permanent deletion

4. **Complete Task** (POST `/api/v1/tasks/{id}/force-complete`)
   - **Sole completion endpoint** — no `/complete` or `/auto-complete` endpoints exist; the ONLY valid task completion call is `POST /api/v1/tasks/{id}/force-complete`
   - Input: `{ version: number }` — the current task version MUST be sent in the request body
   - Marks task as complete with `completed_by: 'force'`
   - Updates achievement stats (streak, lifetime count)
   - Returns: `{ data: { task, unlocked_achievements[], streak } }` (note: response is wrapped under `data` key)
   - Triggers: Achievement unlock checks, streak calculation

**Success Criteria**:
- [ ] Tasks persist across sessions
- [ ] Every `PATCH /tasks/{id}` request includes the `version` field — missing version MUST be treated as a bug
- [ ] Task completion MUST use `POST /tasks/{id}/force-complete` with `{ version }` body; calls to `/complete` or `/auto-complete` are invalid
- [ ] Completion response schema `{ data: { task, unlocked_achievements[], streak } }` is parsed correctly
- [ ] Optimistic locking prevents concurrent edit conflicts
- [ ] Deleted tasks recoverable for 30 days
- [ ] Completion triggers achievement system
- [ ] All operations complete within 2 seconds (p95)

**Edge Cases**:
- Completing task with incomplete subtasks → allowed but shows warning
- Editing task during auto-completion → version conflict handled gracefully
- Deleting recurring task instance → only instance deleted, template preserved

**Implementation Evidence**: [`src/lib/hooks/useTasks.ts`](frontend/src/lib/hooks/useTasks.ts), [`src/components/tasks/TaskCard.tsx`](frontend/src/components/tasks/TaskCard.tsx)

---

### FR-003: Subtask Management

**What**: Nested subtasks (max 10 per task) with independent completion tracking

**Why**: Break down complex tasks into manageable steps, track incremental progress

**Subtask Schema** (from [`src/lib/schemas/subtask.schema.ts`](frontend/src/lib/schemas/subtask.schema.ts)):
```typescript
{
  id: string (UUID)
  task_id: string (UUID, foreign key)
  title: string (1-200 chars, required)
  completed: boolean
  completed_at: datetime | null
  created_at: datetime
  updated_at: datetime
}
```

**Operations**:

1. **Create Subtask** (POST `/api/v1/tasks/{task_id}/subtasks`)
   - Input: `{ title }`
   - Validation: Max 10 subtasks per task (enforced by backend)
   - Error: `NESTING_LIMIT_EXCEEDED` if limit reached

2. **Update Subtask** (PATCH `/api/v1/tasks/{task_id}/subtasks/{id}`)
   - Input: `{ title?, completed? }`
   - Side effect: Updates parent task's `subtask_completed_count`

3. **Delete Subtask** (DELETE `/api/v1/tasks/{task_id}/subtasks/{id}`)
   - Hard delete (subtasks not recoverable independently)
   - Updates parent task's `subtask_count`

**Progress Calculation**:
- `progress = (subtask_completed_count / subtask_count) * 100`
- Shown in task card and detail view
- Real-time update on subtask toggle

**Deferred Fetch Requirement**:
- Subtask data MUST only be fetched when the task card is expanded/open, not on initial render
- Fetching subtasks unconditionally for every task card in a list causes one background request per card, flooding the API (e.g., 25 tasks = 25 simultaneous requests)
- The query hook MUST accept an `enabled` option and forward it to the underlying data-fetching layer; the task card MUST pass `enabled: isExpanded`

**Cache Invalidation Requirement**:
- After creating or updating a subtask, cache invalidation MUST reference the `taskId` key using **camelCase** (e.g., `['subtasks', taskId]`)
- Using the snake_case variant `task_id` resolves to `undefined` at the call site, causing invalidation of the wrong cache entry and leaving stale data visible alongside fresh data

**Success Criteria**:
- [ ] Subtask creation respects 10-per-task limit
- [ ] Subtask data is NOT fetched for collapsed task cards — only fetched when a card is expanded
- [ ] After subtask creation/update, cache for the correct parent task is invalidated (using camelCase `taskId`)
- [ ] Progress bar updates immediately on subtask toggle
- [ ] Parent task shows aggregated progress in list view
- [ ] Deleting parent task cascades to subtasks

**Implementation Evidence**: [`src/lib/hooks/useSubtasks.ts`](frontend/src/lib/hooks/useSubtasks.ts), [`src/components/tasks/SubTaskList.tsx`](frontend/src/components/tasks/SubTaskList.tsx)

---

### FR-004: Focus Mode

**What**: Distraction-free, full-screen task view with countdown timer

**Why**: Deep work requires eliminating distractions and time-boxing effort

**Focus Mode State** (from [`src/lib/stores/focus-mode.store.ts`](frontend/src/lib/stores/focus-mode.store.ts)):
```typescript
{
  isActive: boolean
  currentTaskId: string | null
  startTime: Date | null
}
```

**Workflow**:

1. **Activation**:
   - User clicks focus icon on task card
   - Stores task ID and start time in Zustand store
   - Navigates to `/dashboard/focus` full-screen route
   - Starts countdown based on `task.estimated_duration`

2. **Focus Session**:
   - Full-screen UI with task title, description, subtasks
   - Countdown timer (visual + numeric)
   - Escape key to exit (keyboard shortcut)
   - Pause button (stops timer, preserves state)

3. **Completion**:
   - Manual complete button
   - Auto-exit when timer reaches zero
   - Records `focus_time_seconds` on task
   - Updates achievement stat `focus_completions`

4. **Exit**:
   - Returns to task list with focus time saved
   - Preserves incomplete status if not manually completed
   - Clears focus mode state in Zustand

**Success Criteria**:
- [ ] Focus mode blocks navigation away (confirmation dialog)
- [ ] Timer accuracy within 1 second
- [ ] Focus time recoverable on browser reload — elapsed seconds written to `localStorage` every second tick and restored on mount if `currentTaskId` matches
- [ ] Escape key always exits (no trap)
- [ ] Achievement "Focus Master" unlocked after 50 focus completions

**Edge Cases**:
- Browser tab becomes inactive → timer pauses (intentional)
- Network failure during focus → time tracked locally, synced on reconnect
- Task deleted by another device → graceful exit with saved time

**Implementation Evidence**: [`src/app/dashboard/focus/page.tsx`](frontend/src/app/dashboard/focus/page.tsx), [`src/components/focus/FocusTimer.tsx`](frontend/src/components/focus/)

---

### FR-005: Quick Notes

**What**: Rapid text capture with one-click conversion to tasks

**Why**: Capture fleeting thoughts before they're forgotten, reduce friction to action

**Note Schema** (from [`src/lib/schemas/note.schema.ts`](frontend/src/lib/schemas/note.schema.ts)):
```typescript
{
  id: string (UUID)
  user_id: string (UUID)
  // No task_id — notes are user-owned standalone entities, not nested under tasks
  content: string (1-2000 chars, required)
  archived: boolean

  // Pro features
  voice_url: string | null (Pro only)
  voice_duration_seconds: number | null (1-300)
  transcription_status: 'pending' | 'completed' | 'failed' | null

  created_at: datetime
  updated_at: datetime
}
```

**API Endpoint Constraints**:
- Notes are **user-owned standalone entities** — they are NOT nested under tasks
- All CRUD operations use the top-level `/api/v1/notes` resource
- Update operations MUST use `PATCH`, not `PUT` — the API does not expose a `PUT /notes/{id}` endpoint

**Operations**:

1. **Create Note** (POST `/api/v1/notes`)
   - Input: `{ content }`
   - Note is created for the authenticated user; no task context needed
   - Side effect: Increments `notes_created` stat (achievement tracking)
   - Limit: 20 notes per user (free), unlimited (pro)

2. **List Notes** (GET `/api/v1/notes`)
   - Returns all notes for the authenticated user (excludes archived by default)
   - Query params: `?archived=true` to include archived notes
   - Ordered: reverse-chronological (`created_at DESC`)

3. **Update Note** (PATCH `/api/v1/notes/{note_id}`)
   - Input: `{ content? }`
   - HTTP method MUST be `PATCH` — `PUT /notes/{id}` does not exist

4. **Delete Note** (DELETE `/api/v1/notes/{note_id}`)
   - Hard delete

5. **Archive Note** (PATCH `/api/v1/notes/{note_id}`)
   - Input: `{ archived: true }`
   - Archived notes hidden from main view, accessible in settings

6. **Convert to Task** (POST `/api/v1/notes/{id}/convert`)
   - Parses note content for task metadata:
     - Priority keywords: "urgent", "important" → high priority
     - Duration hints: "30 min", "2 hours" → estimated_duration
     - Date patterns: "tomorrow", "next Monday" → due_date (AI-powered, Pro only)
   - Creates task with note content as description
   - Marks note as archived (not deleted)
   - Increments `notes_converted` achievement stat

**Voice Notes (Pro Feature)**:
- User records audio (max 5 minutes)
- Uploaded to backend, transcribed via Whisper API
- Transcription appears as note content when `transcription_status: 'completed'`
- Used for hands-free capture

**Success Criteria**:
- [ ] Note creation calls `POST /api/v1/notes` — task-scoped endpoints MUST NOT be used
- [ ] Note list calls `GET /api/v1/notes` — returns notes for authenticated user
- [ ] Note updates use `PATCH /api/v1/notes/{note_id}` — `PUT` method MUST NOT be used
- [ ] Note creation < 500ms (p95)
- [ ] Conversion preserves all note content
- [ ] AI parsing accuracy > 80% for common patterns (Pro)
- [ ] Voice transcription accuracy > 90% (Pro)
- [ ] Achievement "Note Master" unlocked after 100 conversions

**Edge Cases**:
- Empty note → validation error
- Note conversion during network failure → queued locally, synced on reconnect
- Voice upload timeout → retry with exponential backoff

**Implementation Evidence**: [`src/lib/hooks/useNotes.ts`](frontend/src/lib/hooks/useNotes.ts), [`src/components/notes/NoteCard.tsx`](frontend/src/components/notes/)

---

### FR-006: Reminder System (Dual Notification)

**What**: Browser + in-app notifications with relative/absolute timing

**Why**: Users need timely prompts without constant app checking

**Reminder Schema** (from [`src/lib/schemas/reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts)):
```typescript
{
  id: string (UUID)
  task_id: string (UUID, foreign key)
  user_id: string (UUID)

  // Timing
  type: 'relative' | 'absolute'
  offset_minutes: number | null (relative: -15, -30, -60, -1440)
  scheduled_at: datetime | null (absolute: specific time)

  // Delivery tracking
  fired: boolean
  fired_at: datetime | null

  created_at: datetime
  updated_at: datetime
}
```

**Reminder Timing Options**:
- **Relative** (offset from due_date):
  - 15 minutes before
  - 30 minutes before
  - 1 hour before
  - 1 day before
- **Absolute**: User-specified date/time

**Reminder CRUD Operations**:
- **Create Reminder** (POST `/api/v1/tasks/{task_id}/reminders`)
  - Input: `{ type, offset_minutes? | scheduled_at? }`
  - MUST call the real API — stub implementations that show success toasts without making API calls are NOT acceptable
- **Delete Reminder** (DELETE `/api/v1/reminders/{reminder_id}`)
  - MUST call the real API — stub implementations are NOT acceptable
- Both operations MUST provide appropriate error feedback if the API call fails

**Reminder CRUD Success Criteria**:
- [ ] Creating a reminder calls `POST /api/v1/tasks/{task_id}/reminders` — placeholder/stub implementations are invalid
- [ ] Deleting a reminder calls `DELETE /api/v1/reminders/{reminder_id}` — placeholder/stub implementations are invalid
- [ ] Both operations show error feedback on API failure, not false-positive success toasts

**Delivery Mechanism** (from [`public/service-worker.js`](frontend/public/service-worker.js)):

1. **Service Worker Polling**:
   - Runs every 60 seconds when app is open
   - Fetches reminders from `/api/v1/reminders` (includes unfired only)
   - Calculates trigger time: `due_date + offset_minutes * 60000`
   - Fires reminders where `trigger_time <= now && fired === false`

2. **Dual Notification**:
   - **Browser notification**: `showNotification()` with `requireInteraction: true`
   - **In-app toast**: `postMessage()` to all open tabs
   - Both fired simultaneously (not fallback — both guaranteed)

3. **Mark Delivered**:
   - POST `/api/v1/reminders/{id}/fire`
   - Sets `fired: true, fired_at: now()`
   - Prevents duplicate notifications

**Success Criteria**:
- [ ] Reminders fire within 60-second window of trigger time
- [ ] Both browser + in-app notification always sent
- [ ] Notification persists if user not at computer (requireInteraction)
- [ ] Click notification navigates to task detail
- [ ] Fired reminders never re-trigger

**Edge Cases**:
- Browser closed → notifications missed (acceptable, user must open app)
- Permission denied → only in-app toast shown
- Multiple tabs open → toast shown in all tabs (intentional)
- Task deleted → orphaned reminders gracefully handled (no notification)

**Implementation Evidence**: [`public/service-worker.js`](frontend/public/service-worker.js), [`src/lib/hooks/useReminders.ts`](frontend/src/lib/hooks/useReminders.ts)

---

### FR-007: Recurring Tasks (RRule-based)

**What**: RFC 5545 recurrence patterns with template-based instance generation

**Why**: Daily standups, weekly reviews, monthly invoices — repeating work needs automation

**Task Template Schema** (from [`src/lib/schemas/task.schema.ts`](frontend/src/lib/schemas/task.schema.ts)):
```typescript
{
  id: string (UUID)
  user_id: string (UUID)

  // Template metadata
  title: string (1-500 chars)
  description: string (max 5000 chars)
  priority: 'low' | 'medium' | 'high'
  estimated_duration: number | null

  // Recurrence
  rrule: string (RFC 5545 RRULE format)
  next_due: datetime | null (calculated field)
  active: boolean (can be paused)

  created_at: datetime
  updated_at: datetime
}
```

**RRule Examples**:
- Daily at 9am: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0`
- Every Monday: `FREQ=WEEKLY;BYDAY=MO`
- First of month: `FREQ=MONTHLY;BYMONTHDAY=1`
- Weekdays only: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`

**Instance Generation** (completion-based):
1. User completes recurring task instance
2. Backend checks if instance is from template (`template_id != null`)
3. Parses template's `rrule` to compute next occurrence
4. Creates new task instance with:
   - Same title, description, priority, duration
   - `template_id` = original template
   - `due_date` = next computed date
   - Fresh UUID, `completed: false`
5. Updates template's `next_due` field

**Template Management**:
- Edit template → updates future instances only (past instances unchanged)
- Pause template → sets `active: false`, stops new instances
- Delete template → orphans existing instances (they remain independent)

**Success Criteria**:
- [ ] RRule parsing accuracy 100% for supported patterns
- [ ] New instance appears in task list within 1 minute of completion (backend generates instance on force-complete; frontend surfaces it via `['tasks']` query invalidation in T098 — timing SLA is backend-owned)
- [ ] Template edits don't affect historical instances
- [ ] Paused templates don't generate instances
- [ ] Complex patterns (e.g., "2nd Tuesday of month") supported

**Edge Cases**:
- Completing instance before previous → generates from completion time, not original due_date
- Network failure during generation → queued, retried on reconnect
- Invalid RRule → validation error on template creation
- Backend fails to generate next instance → if force-complete succeeds but no new recurring task appears after 2 `['tasks']` poll cycles (~30s), frontend shows informational toast: "Next recurrence will appear shortly." No blocking error; silent retry on next poll.

**Implementation Evidence**: [`src/lib/utils/recurrence.ts`](frontend/src/lib/utils/recurrence.ts), [`src/components/recurrence/RecurrenceEditor.tsx`](frontend/src/components/recurrence/RecurrenceEditor.tsx)

---

### FR-008: Achievement System (Gamification)

**What**: Milestone-based achievements that unlock perks (increased limits)

**Why**: Positive reinforcement builds habits, perks reward commitment

**Achievement Categories** (from [`src/lib/schemas/achievement.schema.ts`](frontend/src/lib/schemas/achievement.schema.ts)):
1. **Task Milestones**: Complete 5, 25, 100, 500 tasks
2. **Streak Milestones**: Maintain 7, 30, 100 day streaks
3. **Focus Milestones**: Complete 10, 50, 200 focus sessions
4. **Note Milestones**: Convert 10, 50, 200 notes to tasks

**Achievement Structure**:
```typescript
{
  id: string (code, e.g., "tasks_5")
  name: string ("First Steps")
  message: string ("You've completed your first 5 tasks!")
  category: 'tasks' | 'streak' | 'focus' | 'notes'
  threshold: number (e.g., 5)

  // Perk details
  perk_type: 'max_tasks' | 'max_notes' | 'daily_ai_credits' | null
  perk_value: number | null (e.g., +10 tasks)
}
```

**User Achievement State**:
```typescript
{
  id: string (UUID)
  user_id: string (UUID)

  // Lifetime stats
  lifetime_tasks_completed: number
  current_streak: number
  longest_streak: number
  last_completion_date: string (YYYY-MM-DD)
  focus_completions: number
  notes_converted: number

  // Unlocked achievements
  unlocked_achievements: string[] (achievement IDs)

  created_at: datetime
  updated_at: datetime
}
```

**Unlock Flow**:
1. User completes action (task, focus session, note conversion)
2. Backend increments relevant stat in `UserAchievementState`
3. Backend checks all achievement definitions for threshold matches
4. If threshold met and not already unlocked:
   - Add achievement ID to `unlocked_achievements[]`
   - Return `{ achievement_id, achievement_name, perk }`
5. Frontend displays achievement unlock toast with animation
6. Perk immediately applied to user's effective limits

**Effective Limits Calculation**:
```typescript
base_limits = tier === 'free' ? { max_tasks: 50, max_notes: 20 } : { max_tasks: 1000, max_notes: 500 }

unlocked_perks.forEach(achievement => {
  if (achievement.perk_type === 'max_tasks') {
    base_limits.max_tasks += achievement.perk_value
  }
  // ... same for max_notes, daily_ai_credits
})

return base_limits
```

**Streak Calculation** (with grace days):
- **Grace period**: 24 hours after midnight (local timezone)
- **Streak increment**: Complete any task → streak +1 if `last_completion_date` is yesterday
- **Streak reset**: Miss grace period → `current_streak = 1`
- **Longest streak**: Always preserved, never decremented

**Success Criteria**:
- [ ] Achievements unlock within 2 seconds of threshold
- [ ] Perks apply immediately (no logout required)
- [ ] Streak calculation respects user timezone
- [ ] Grace period prevents accidental streak loss
- [ ] Achievement toast displays with smooth animation

**Edge Cases**:
- Completing multiple tasks rapidly → only one unlock toast per achievement
- Offline completion → stats synced on reconnect, achievements unlock then
- Timezone change → streak calculation uses new timezone going forward

**Implementation Evidence**: [`src/lib/hooks/useAchievements.ts`](frontend/src/lib/hooks/useAchievements.ts), [`src/components/achievements/AchievementCard.tsx`](frontend/src/components/achievements/)

---

### FR-009: AI-Powered Features (Pro Tier)

**What**: AI-assisted task breakdown, priority suggestions, note parsing

**Why**: Reduce cognitive load for task planning, accelerate capture-to-action

**AI Capabilities**:

1. **Subtask Generation** (POST `/api/v1/tasks/{id}/ai/subtasks`):
   - Input: Task title + description
   - Output: 3-7 subtask suggestions
   - SDK: OpenAI Agents SDK
   - Model: Configured via `AI_MODEL_ID` environment variable. No default is hardcoded — the deployer selects the model. No fallback provider.
   - Prompt engineering: "Break down this task into actionable subtasks (3-7 items)"
   - Cost: 1 AI credit per generation

2. **Priority Recommendation** (POST `/api/v1/tasks/{id}/ai/priority`):
   - Input: Task details + user's current task list
   - Output: `{ priority: 'high' | 'medium' | 'low', reasoning: string }`
   - SDK: OpenAI Agents SDK
   - Model: Configured via `AI_MODEL_ID` environment variable. No default is hardcoded. No fallback provider.
   - Factors: Deadlines, dependencies, user patterns
   - Cost: 1 AI credit

3. **Note Parsing** (POST `/api/v1/notes/{id}/parse`):
   - Input: Note content
   - Output: `{ title, description, due_date?, priority?, estimated_duration? }`
   - SDK: OpenAI Agents SDK
   - Model: Configured via `AI_MODEL_ID` environment variable. No default is hardcoded. No fallback provider.
   - Pattern recognition: Natural language dates, urgency keywords
   - Example: "Call dentist tomorrow urgent" → { title: "Call dentist", due_date: tomorrow, priority: 'high' }
   - Cost: 1 AI credit

**AI Credit System**:
- Free tier: 0 credits (AI disabled)
- Pro tier: 100 credits/day (resets midnight UTC)
- Credits tracked in `UserAchievementState.daily_ai_credits_used`
- Perks can increase daily limit

**Credit limit configuration** (Constitution §IX — AI limits must be configurable via env):
AI credit limits MUST be set via environment variables — no hardcoded defaults in code:
- `FREE_TIER_AI_CREDITS` — daily credits for free tier users
- `PRO_TIER_AI_CREDITS` — daily credits for pro tier users
- `AI_CREDIT_RESET_HOUR` — UTC hour for daily credit reset

The values referenced in this spec (0 and 100) are illustrative examples; production values are determined by the deployment environment.

**Env-absent failure behavior** (Constitution §IX — environment validation is mandatory):
If `FREE_TIER_AI_CREDITS`, `PRO_TIER_AI_CREDITS`, or `AI_CREDIT_RESET_HOUR` are absent at startup, the environment validator MUST block startup and emit a clear error message. The application MUST NOT start with missing AI credit configuration. This prevents silent fail-open behavior where all users could receive unlimited AI credits.

**AI Logging Requirement (Constitution §V)**:
- Every AI interaction MUST be logged as a structured event: `{ entity_id, user_id, action_type, actor_type, credits_used, timestamp }`
- `entity_id` is the `task_id` for `subtask_generation` and `priority_recommendation` calls; it is the `note_id` for `note_parsing` calls
- `action_type` is one of: `subtask_generation` | `priority_recommendation` | `note_parsing`
- `actor_type: 'ai'` — constant for all AI interaction logs; satisfies Constitution §V.2 "actor identity (user or AI)" requirement by explicitly declaring the AI as the acting entity
- Delivered as a Sentry breadcrumb (`Sentry.addBreadcrumb`) and to the structured logger (T138/T160)
- Logs are append-only and must never be modified or deleted (Constitution §V.3)

> **Constitution §V alignment note**: The constitution §V.2 uses the phrase "task ID" to describe the mandatory logged entity identifier. In this context, `entity_id` is the correct abstraction — it equals `task_id` for task-scoped AI actions and `note_id` for note-scoped AI actions. Both map to the same constitutional intent: "the entity being operated on." The `entity_id` field satisfies constitution §V.2 fully.

**AI Logging Success Criteria**:
- [ ] Every call to an AI endpoint logs the event before the response is returned to the UI
- [ ] Log contains `entity_id` (task_id for subtask/priority calls; note_id for note-parsing), `user_id`, `action_type`, `actor_type: 'ai'`, `credits_used`, and ISO timestamp

**AI Safety Guardrails** (per Constitution IV):
- **AI cannot change task state** (no auto-completion)
- **AI cannot delete tasks**
- **AI suggestions are opt-in** (user must click "Generate subtasks")
- **Undo available** (user can reject suggestions before saving)

**Success Criteria**:
- [ ] Subtask suggestions relevant > 80% of the time
- [ ] Priority recommendations accurate within user's judgment
- [ ] Note parsing success rate > 85%
- [ ] AI latency < 3 seconds (p95)
- [ ] Credits reset daily at midnight UTC

**Edge Cases**:
- Credit exhaustion → clear error message, upsell to higher tier
- AI service down → graceful degradation, manual entry still works
- Offensive input → content moderation, reject with error

**Implementation Evidence**: [`src/components/tasks/AISubtasksGenerator.tsx`](frontend/src/components/tasks/AISubtasksGenerator.tsx), [`src/lib/hooks/useAI.ts`](frontend/src/lib/hooks/)

---

### FR-010: Command Palette (Power User Feature)

**What**: Keyboard-driven global command launcher (Cmd+K / Ctrl+K)

**Why**: Speed up navigation and actions for keyboard-centric users

**Command Categories**:

1. **Navigation**:
   - "Go to Dashboard" → `/dashboard`
   - "Go to Tasks" → `/dashboard/tasks`
   - "Go to Notes" → `/dashboard/notes`
   - "Go to Focus Mode" → `/dashboard/focus`
   - "Go to Achievements" → `/dashboard/achievements`

2. **Task Actions**:
   - "New Task" → Opens new task modal
   - "Search Tasks" → Fuzzy search with Fuse.js
   - "Complete Task" → Lists incomplete tasks, marks selected

3. **Quick Capture**:
   - "New Note" → Opens quick note input
   - "Start Focus" → Lists tasks, activates focus for selected

**Command Palette State** (from [`src/lib/stores/command-palette.store.ts`](frontend/src/lib/stores/command-palette.store.ts)):
```typescript
{
  isOpen: boolean
  searchQuery: string
  selectedIndex: number
  filteredCommands: Command[]
}
```

**Keyboard Shortcuts**:
- `Cmd+K` / `Ctrl+K`: Open command palette
- `Arrow Up/Down`: Navigate commands
- `Enter`: Execute selected command
- `Escape`: Close palette

**Fuzzy Search**:
- Powered by Fuse.js
- Searches command names, aliases, categories
- Example: "gota" matches "**Go** **t**o T**a**sks"
- Threshold: 0.4 (balance precision/recall)

**Success Criteria**:
- [ ] Palette opens within 100ms of keypress
- [ ] Search results update in real-time (< 50ms)
- [ ] Keyboard navigation never breaks
- [ ] Commands execute within 200ms
- [ ] Palette accessible from all dashboard pages

**Edge Cases**:
- Typing in input field → Cmd+K still opens palette (global listener)
- Command execution during network failure → queued locally
- Multiple rapid Cmd+K presses → single open (debounced)

**Implementation Evidence**: [`src/components/layout/CommandPalette.tsx`](frontend/src/components/layout/), [`src/lib/stores/command-palette.store.ts`](frontend/src/lib/stores/command-palette.store.ts)

---

### FR-011: Notifications Full-Page View

**What**: A dedicated `/dashboard/notifications` page showing the user's full notification history

**Why**: The notification dropdown links to this page; without it, "View all" clicks produce a 404. Users need a place to review older notifications not visible in the dropdown.

**Route**: `/dashboard/notifications`

**Operations**:
- **List Notifications** (GET `/api/v1/notifications`)
  - Renders all user notifications in reverse-chronological order
  - Reuses the existing `useNotifications()` hook and notification display components

**Success Criteria**:
- [ ] Route `/dashboard/notifications` MUST exist and render without a 404
- [ ] Page displays all notifications for the authenticated user
- [ ] Loading state shown while notifications are fetched
- [ ] Empty state shown when there are no notifications
- [ ] "View all" links in the notification dropdown navigate to this page successfully

**Implementation Evidence**: [`src/components/layout/NotificationDropdown.tsx`](frontend/src/components/layout/NotificationDropdown.tsx) (links to this route), [`src/lib/hooks/useNotifications.ts`](frontend/src/lib/hooks/useNotifications.ts)

---

### FR-012: Subscription Upgrade

**What**: Allow users to upgrade their subscription from Free to Pro

**Why**: Revenue-generating feature; must call the correct backend endpoint

**Operations**:
- **Upgrade** (POST `/api/v1/subscription/upgrade`)
  - MUST call `/subscription/upgrade` — the endpoint `/subscription/checkout` does NOT exist and returns 404
  - MUST NOT call the non-existent `/subscription/purchase-credits` endpoint
  - On success: show confirmation and redirect user to dashboard
  - On failure: show actionable error message

**Success Criteria**:
- [ ] Subscription upgrade calls `POST /api/v1/subscription/upgrade`
- [ ] Calls to `/subscription/checkout` MUST NOT exist in the codebase
- [ ] Calls to `/subscription/purchase-credits` MUST NOT exist in the codebase
- [ ] User sees confirmation of successful upgrade
- [ ] User sees clear error message on upgrade failure

**Implementation Evidence**: [`src/lib/hooks/useSubscription.ts`](frontend/src/lib/hooks/useSubscription.ts), [`src/services/payment.service.ts`](frontend/src/services/payment.service.ts)

---

### FR-013: Mark Notification as Read

**What**: Mark individual notifications as read

**Why**: Correct API endpoint is required; the wrong path always returns 404

**Operations**:
- **Mark as Read** (PATCH `/api/v1/notifications/{notification_id}/read`)
  - MUST call `/notifications/{id}/read` as the path — the `/read` suffix is part of the resource path, not a body field
  - MUST NOT call `PATCH /notifications/{id}` with `{ read: true }` in the body — that endpoint variant does not exist
  - No request body needed; the read action is expressed in the URL

**Success Criteria**:
- [ ] Mark-as-read calls `PATCH /api/v1/notifications/{id}/read`
- [ ] `PATCH /notifications/{id}` with a `{ read: true }` body MUST NOT be used
- [ ] Notification read state updates immediately in the UI after successful call

**Implementation Evidence**: [`src/lib/hooks/useNotifications.ts`](frontend/src/lib/hooks/useNotifications.ts)

---

## III. Non-Functional Requirements

### NFR-001: Performance

**Targets** (per Constitution X: Simplicity over scale):

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial page load (LCP) | < 2.5s | Web Vitals |
| Route transitions (Next.js) | < 500ms | Performance API |
| API response time (p95) | < 2s | Backend monitoring |
| Search latency (Fuse.js) | < 50ms | Client-side profiling |
| Focus mode timer accuracy | ±1s | Comparison with system clock |

**Optimization Strategies**:
- **Code splitting**: Next.js App Router automatic splitting
- **Image optimization**: `next/image` with AVIF/WebP
- **Bundle analysis**: `@next/bundle-analyzer` (run via `pnpm analyze`)
- **Lazy loading**: Radix UI components loaded on interaction
- **Server caching**: TanStack Query with 5-minute stale time
- **Debouncing**: Search input debounced 300ms

**Success Criteria**:
- [ ] Lighthouse score > 90 (Performance, Accessibility, Best Practices)
- [ ] Bundle size < 500KB gzipped (main chunk)
- [ ] No layout shifts (CLS < 0.1)
- [ ] All interactions < 100ms to first visual feedback

**Implementation Evidence**: [`package.json`](frontend/package.json) (`analyze` script), Web Vitals tracking in `_app.tsx`

---

### NFR-002: Security

**Threat Model**:
- **XSS**: Malicious input in task titles/descriptions
- **CSRF**: Forged API requests
- **Token theft**: Access token stolen from localStorage
- **Clickjacking**: App embedded in malicious iframe

**Mitigations**:

1. **XSS Protection**:
   - React automatic escaping (JSX)
   - Content Security Policy (CSP) headers
   - DOMPurify for user-generated HTML (if rich text added)

2. **CSRF Protection**:
   - Idempotency-Key header on all mutations (generated per request)
   - SameSite cookies (when backend sets session cookies)

3. **Token Security**:
   - Short access token TTL (15 minutes)
   - Refresh token rotation
   - **HttpOnly cookies for ALL tokens** (both access and refresh) — storing tokens in `localStorage` is NOT acceptable (see FR-001 Security Constraint)
   - `localStorage` token storage is classified as a critical vulnerability — any JavaScript running on the page (XSS, supply chain attack) can read localStorage and steal tokens
   - Logout clears all token cookies

4. **Clickjacking Protection**:
   - `X-Frame-Options: DENY` header
   - CSP `frame-ancestors 'none'`

**Secrets Management** (per Constitution IX):
- All API keys in `.env.local` (never in code)
- `NEXT_PUBLIC_API_URL` for backend endpoint
- Environment validation on startup (blocks if missing required vars)

**Production Logging Constraint**:
- Auth events, token values, payment data, and any personally identifiable information MUST NOT be logged to the browser console in production
- `console.log` calls containing auth or payment context MUST be guarded by `process.env.NODE_ENV === 'development'` or removed entirely

**Success Criteria**:
- [ ] OWASP Top 10 vulnerabilities addressed
- [ ] Tokens stored in HttpOnly cookies, never in `localStorage` or `sessionStorage`
- [ ] Security headers score A+ on securityheaders.com
- [ ] No secrets in Git history
- [ ] Dependency vulnerability scan passes (npm audit)
- [ ] No auth or payment data logged to browser console in production

**Implementation Evidence**: [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts) (Idempotency-Key), `next.config.js` (security headers)

---

### NFR-003: Accessibility (WCAG AA)

**Standards**: WCAG 2.1 Level AA compliance

**Requirements**:

1. **Keyboard Navigation**:
   - All interactive elements focusable
   - Logical tab order
   - Escape key exits modals/focus mode
   - Shortcuts don't trap users

2. **Screen Readers**:
   - Semantic HTML (`<nav>`, `<main>`, `<article>`)
   - ARIA labels on icon buttons
   - Alt text on all images
   - Live regions for toast notifications (`aria-live="polite"`)

3. **Color Contrast**:
   - Minimum 4.5:1 for text
   - 3:1 for UI components
   - Priority indicators use both color + icons

4. **Motion Sensitivity**:
   - `prefers-reduced-motion` support
   - Animations disabled if user preference set
   - Focus mode timer non-animated fallback

**Radix UI Benefits**:
- Built-in accessibility patterns
- Focus management handled automatically
- ARIA attributes correct by default

**Success Criteria**:
- [ ] Axe DevTools reports zero violations
- [ ] VoiceOver/NVDA can navigate entire app
- [ ] Keyboard-only users can complete all tasks
- [ ] Color contrast passes WebAIM checker

**Implementation Evidence**: [`src/lib/hooks/useReducedMotion.ts`](frontend/src/lib/hooks/useReducedMotion.ts), Radix UI components with built-in a11y

---

### NFR-004: Data Integrity (per Constitution III)

**Guarantees**:

1. **User data loss is unacceptable**:
   - All mutations use optimistic locking (`version` field)
   - Conflict resolution shows latest version, allows user to choose
   - Soft delete with 30-day recovery window

2. **Undo guarantee** (per Constitution III.4):
   - Undo available until next mutation
   - Toast notification with undo button
   - Undo action queued locally, sent to backend

3. **Dummy-first rule** (per Constitution III.3):
   - MSW mocks used for all development
   - No real user data in test suites
   - Seed data generated via fixtures

4. **Session durability**:
   - Task edits autosaved every 5 seconds (debounced)
   - Form state persisted in localStorage (survives refresh)
   - Network failure queues mutations, syncs on reconnect

**Success Criteria**:
- [ ] Zero data loss incidents in production
- [ ] Undo success rate 100% (when invoked before next mutation)
- [ ] Conflict resolution UI tested with concurrent edits
- [ ] All tests use dummy data (verified in CI)

**Implementation Evidence**: [`src/lib/schemas/task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) (`version` field), Zustand stores for local state persistence

---

### NFR-005: Reliability

**Targets**:
- **Uptime**: 99.5% (excludes planned maintenance) — **backend-owned; frontend cannot independently verify**
- **Error rate**: < 1% of requests — **backend-owned; frontend contributes via TanStack Query retry (T039) and error boundary (T111)**
- **Crash rate**: < 0.1% of sessions — **frontend-owned; measured via Sentry (T136)**

**Error Handling**:

1. **API Errors**:
   - All errors follow schema: `{ error: { code, message, details?, request_id? } }`
   - User-friendly messages (no stack traces)
   - Retry with exponential backoff for 5xx errors
   - Circuit breaker pattern for degraded backend

2. **Network Failures**:
   - Offline indicator in UI
   - Mutations queued in IndexedDB
   - Sync on reconnect with conflict resolution
   - TanStack Query retry logic (3 attempts)

3. **Client-Side Crashes**:
   - React Error Boundaries catch component errors
   - Sentry integration for error tracking (production)
   - Fallback UI with "Try Again" button

**Graceful Degradation**:
- AI features disabled if service down (manual entry still works)
- Reminders fall back to in-app only if notifications blocked
- Focus mode works offline (timer client-side)

**Success Criteria**:

*Frontend-owned (verifiable by frontend alone):*
- [ ] Error boundaries prevent full-page crashes (T111)
- [ ] Client-side crash rate < 0.1% of sessions — measured via Sentry (T136)
- [ ] All API errors surfaced to user with actionable message; `request_id` logged for backend correlation (T111, T039)
- [ ] Offline mode allows task viewing (cached data via TanStack Query)
- [ ] TanStack Query retries up to 3 times on 5xx before showing error state (T039)

*Backend-dependent (frontend cannot independently verify):*
- [ ] Uptime 99.5% — backend SLA; frontend shows degraded state when backend unreachable
- [ ] Server error rate < 1% — backend metric; frontend contributes by not issuing unnecessary requests (T114 rate limiter)
- [ ] ~~Network reconnect syncs queued actions~~ **[DEFERRED — see §V Non-Goals #7: IndexedDB mutation queue is an 8–10 week effort, out of current sprint scope]**
- [ ] ~~Circuit breaker for degraded backend~~ **[DEFERRED — same future sprint as IndexedDB mutation queue; §V Non-Goals #7]**

**Implementation Evidence**: [`src/lib/api/client.ts`](frontend/src/lib/api/client.ts) (ApiError class), TanStack Query retry configuration

---

### NFR-006: Observability

**Logging**:
- **Development**: Console logs with component context
- **Production**: Structured JSON logs to Sentry
- **Minimum logged fields**: timestamp, level, message, user_id, request_id

**Metrics** (Web Vitals):
- LCP (Largest Contentful Paint)
- FID (First Input Delay)
- CLS (Cumulative Layout Shift)
- Tracked via `reportWebVitals()` hook

**Error Tracking**:
- Sentry for frontend errors (React Error Boundaries)
- Error context: user_id, route, component stack
- Source maps uploaded to Sentry for production debugging

**User Feedback** *(deferred — see §V Non-Goals #8)*:
- ~~In-app feedback form (bottom-right widget)~~ **[DEFERRED — no task in current sprint; see §V Non-Goals #8]**
- ~~Issue reporting to GitHub (pre-filled template)~~ **[DEFERRED — same sprint as analytics]**

**Success Criteria**:
- [ ] All errors captured with full context
- [ ] Web Vitals tracked for 100% of users (sampled)
- [ ] ~~P95 API latency visualized in dashboard~~ **[OUT OF SCOPE current sprint — T137 covers metric collection; visualization deferred to future analytics phase]**

**Implementation Evidence**: Sentry setup in `_app.tsx`, Web Vitals hook

---

### NFR-007: Responsive Modal Dialogs

**What**: All modal dialogs must be fully usable on narrow viewports (below 480 px wide)

**Why**: Mobile users cannot interact with modals that overflow their screen or hide content behind fixed-width containers

**Affected Components**:
- Task creation modal (`NewTaskModal`)
- Completion confirmation bar / dialog (`PendingCompletionsBar`)
- Conflict resolution modal (`ConflictResolutionModal` — T112) — side-by-side diff UI must not overflow on narrow viewports
- Any other dialog triggered from dashboard pages

**Requirements**:

1. **Width**: Dialog width MUST adapt to viewport — no fixed minimum width that causes horizontal overflow on screens < 480 px
2. **Height**: Dialogs MUST NOT require vertical scrolling caused by layout overflow; internal sections may scroll, but the dialog shell must fit within viewport height (`max-height: 85dvh` or equivalent)
3. **Advanced/Optional Sections**: Content-heavy sections (e.g., recurrence editor) that cause overflow on mobile MUST be hidden behind a collapsible "Advanced options" toggle on small screens; they MAY be visible by default on larger screens
4. **Button Layout**: When action buttons + content text cannot fit side-by-side below 480 px, they MUST wrap vertically (column layout) rather than overflow or truncate
5. **Touch Targets**: All interactive elements within modals MUST have a minimum tap target of 44 × 44 px

**Success Criteria**:
- [ ] Task creation modal fully usable on 375 px wide viewport (iPhone SE size) — no horizontal overflow, all inputs and buttons reachable
- [ ] Completion confirmation bar text and action buttons visible without horizontal scrolling on 375 px width
- [ ] Advanced recurrence options collapse on mobile and expand on demand without layout breakage
- [ ] `ConflictResolutionModal` side-by-side diff readable on 375 px viewport — columns stack vertically on mobile; all three action buttons ("Keep mine", "Take theirs", "Cancel") reachable without horizontal scroll
- [ ] No modal requires pinch-to-zoom to interact with its contents

**Implementation Evidence**: [`src/components/tasks/NewTaskModal.tsx`](frontend/src/components/tasks/NewTaskModal.tsx), [`src/components/layout/PendingCompletionsBar.tsx`](frontend/src/components/layout/PendingCompletionsBar.tsx)

---

## IV. System Constraints

### External Dependencies

| Dependency | Purpose | Ownership | SLA |
|------------|---------|-----------|-----|
| Backend API | All data operations | Internal | 99.5% uptime |
| Google OAuth | Authentication | Google | 99.9% uptime (per Google SLA) |
| OpenAI API | AI features (Pro) | OpenAI | 99% uptime |
| Vercel CDN | Hosting, edge functions | Vercel | 99.99% uptime |
| Sentry | Error tracking | Sentry | 99.9% uptime |

### Technology Stack

**Fixed Dependencies** (cannot be changed without major refactor):
- **Next.js 16.1.1**: App Router, React Server Components
- **React 19.2.3**: Concurrent features, Suspense
- **TypeScript 5**: Type safety, IntelliSense
- **Tailwind CSS 4**: Utility-first styling
- **Zod 4.3.5**: Schema validation

**Replaceable Dependencies** (can be swapped):
- **TanStack Query v5**: Could swap for SWR or Apollo Client
- **Zustand 5**: Could swap for Redux Toolkit or Jotai
- **Radix UI**: Could swap for Headless UI or React Aria
- **Fuse.js 7**: Could swap for FlexSearch or MiniSearch
- **Framer Motion 12**: Could swap for React Spring

### Data Formats

- **API**: JSON (Content-Type: application/json)
- **Dates**: ISO 8601 datetime strings (UTC)
- **UUIDs**: RFC 4122 v4
- **RRule**: RFC 5545 recurrence format

### Deployment Context

- **Platform**: Vercel (serverless Next.js)
- **Region**: Global edge network (automatic)
- **Build**: Static Site Generation (SSG) for public pages, Server-Side Rendering (SSR) for dashboard
- **Environment variables**: Injected via Vercel dashboard

### Browser Support

**Minimum Versions**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Progressive Enhancement**:
- Service Worker (notifications) → fallback to in-app only
- Web Crypto API (UUID generation) → fallback to Math.random polyfill
- IndexedDB (offline queue) → fallback to memory queue

---

## V. Non-Goals & Out of Scope

### Explicitly Excluded Features

**Why these are excluded**: Scope control, focus on core value prop

1. **Multi-user collaboration**:
   - No shared tasks, projects, or teams
   - Perpetua Flow is single-user productivity tool, not project management
   - Rationale: Adds massive complexity (permissions, conflict resolution, real-time sync)

2. **Calendar integration**:
   - No sync with Google Calendar, Outlook, etc.
   - Rationale: Different mental models (time-blocking vs task lists)
   - Workaround: Users can manually copy tasks to calendar

3. **File attachments**:
   - No uploading documents, images (except voice notes for Pro)
   - Rationale: Storage costs, security scanning, file management UI
   - Workaround: Users can add links to Dropbox/Drive

4. **Custom fields**:
   - No user-defined metadata (e.g., "Client Name", "Project Code")
   - Rationale: Scope creep toward project management, reduces UX simplicity
   - Workaround: Use task description or tags (future feature)

5. **Mobile apps (native)**:
   - Web-only (Progressive Web App installable)
   - Rationale: Development cost, maintenance burden (3 codebases)
   - Mobile web experience optimized via responsive design

6. **Email integration**:
   - No "email to task" functionality
   - Rationale: Requires email server infrastructure, spam handling
   - Workaround: Users manually copy email content to notes

7. **Analytics event tracking (deferred)**:
   - No Mixpanel, Plausible, or custom analytics event instrumentation in current sprint
   - Rationale: Requires analytics provider selection, privacy policy updates, and GDPR consent flow — an independent workstream
   - Current scope: Web Vitals (T137) and Sentry error tracking (T136) only
   - Future: Add analytics as a separate sprint when provider is selected

8. **In-app feedback widget (deferred)**:
   - No in-app feedback form or GitHub issue pre-fill widget in current sprint
   - Rationale: Low-priority UX feature; requires third-party widget or custom implementation
   - Workaround: Users can open GitHub issues directly
   - Note: NFR-006 "User Feedback" section references this; it is deferred pending analytics sprint

9. **Offline-first mutation queue (deferred — not in current sprint)**:
   - NFR-005 describes IndexedDB mutation queuing and background sync on reconnect
   - This is an 8–10 week effort (see plan.md §VIII "Implement Offline-First Architecture")
   - Current sprint reliability scope: Error Boundary (T111), TanStack Query retry (3 attempts, exponential backoff)
   - Not a blocker for MVP launch; deferred to a future sprint
   - Circuit breaker pattern deferred to the same future sprint

### Planned Future Enhancements (Not in MVP)

**Backlog** (prioritized by user demand):
1. Tags/labels for tasks (color-coded, filterable)
2. Task dependencies ("Block" → Task B depends on Task A)
3. Eisenhower Matrix view (Urgent/Important quadrant)
4. Export/import (JSON, CSV for data portability)
5. Dark mode toggle (currently dark-only)
6. Custom keyboard shortcuts
7. Pomodoro timer integration (focus mode enhancement)

---

## VI. Success Criteria & Acceptance Tests

### System-Wide Success Criteria

**Functional**:
- [ ] User can complete end-to-end flow: Sign in → Create task → Complete task → View streak in < 2 minutes
- [ ] ~~All CRUD operations (tasks, subtasks, notes) work offline (queued, synced on reconnect)~~ **[DEFERRED — see §V Non-Goals #7; offline mutation queue deferred to future sprint. Current scope: error boundary, TanStack Query retry (3 attempts), autosave via T167–T168]**
- [ ] AI features (Pro) provide value > 80% of the time (measured by user acceptance rate)
- [ ] Achievement unlocks celebrate progress without being annoying

**Non-Functional**:
- [ ] Page load < 2.5s on 3G network
- [ ] Zero critical security vulnerabilities (OWASP Top 10)
- [ ] 99.5% uptime (measured monthly)
- [ ] < 0.1% client-side crash rate

**User Experience**:
- [ ] Net Promoter Score (NPS) > 50
- [ ] Task completion rate (tasks created → completed) > 70%
- [ ] Focus mode usage > 30% of active users
- [ ] User retention: 50% of users active after 30 days

---

### Critical User Journeys (Acceptance Tests)

#### Journey 1: First-Time User Onboarding

**Scenario**: New user discovers value in < 5 minutes

**Given**: User has Google account, lands on homepage

**When**:
1. Clicks "Sign in with Google"
2. Authorizes Google OAuth
3. Redirected to `/dashboard`
4. Sees onboarding tour (Driver.js)
5. Creates first task via modal
6. Marks task complete
7. Sees streak increment to Day 1 and achievement progress indicator
   (Note: "First Steps" milestone requires 5 tasks — not reachable in a single session)

**Then**:
- User understands core workflow
- Feels sense of accomplishment (gamification)
- No confusion or dead ends

**Edge Cases**:
- OAuth failure → clear error, "Try Again" button
- Onboarding tour dismissed → can restart from settings

---

#### Journey 2: Power User Daily Workflow

**Scenario**: Experienced user completes daily review in < 2 minutes

**Given**: User has 20 active tasks, 3 notes, 7-day streak

**When**:
1. Opens app (already logged in)
2. Presses `Cmd+K` to open command palette
3. Types "focus" → Selects "Start Focus Mode"
4. Completes focused task in 30 minutes
5. Exits focus mode
6. Creates 2 quick notes via sidebar
7. Converts 1 note to task
8. Reviews task list, marks 3 complete
9. Sees streak increment to 8 days

**Then**:
- All actions keyboard-driven (no mouse needed)
- Task list up-to-date
- Streak preserved (grace period)

**Edge Cases**:
- Network interruption during focus → time tracked locally, synced on reconnect
- Missed task → grace period prevents streak reset

---

#### Journey 3: AI-Assisted Task Planning (Pro)

**Scenario**: Pro user leverages AI to break down complex task

**Given**: User has Pro subscription, 50 AI credits remaining

**When**:
1. Creates task: "Plan Q1 marketing campaign"
2. Clicks "Generate Subtasks" (AI)
3. AI returns 5 subtasks:
   - Define target audience
   - Create content calendar
   - Design ad creatives
   - Set up analytics tracking
   - Schedule posts
4. User reviews, accepts 4, edits 1
5. Saves task with subtasks
6. AI credits decremented by 1

**Then**:
- Complex task broken into actionable steps
- User time saved (no manual brainstorming)
- AI credit balance accurate

**Edge Cases**:
- AI service down → error message, fallback to manual entry
- Credits exhausted → upsell modal, AI button disabled

---

#### Journey 4: Recurring Task Automation

**Scenario**: User sets up weekly standup recurring task

**Given**: User wants "Weekly standup notes" every Monday at 9am

**When**:
1. Creates task template
2. Opens recurrence editor
3. Selects "Weekly" preset
4. Picks "Monday" from day selector
5. Sets time: 09:00
6. Saves template (active)
7. Completes first instance on Monday
8. New instance auto-created for next Monday

**Then**:
- Template active, generates instances indefinitely
- Completion triggers next instance creation
- No manual recreation needed

**Edge Cases**:
- Completing instance early (Friday) → next instance still Monday (not Friday+7 days)
- Pausing template → stops future instances

---

#### Journey 5: Focus Mode Deep Work

**Scenario**: User completes 2-hour task in distraction-free mode

**Given**: User has task "Write project proposal" (estimated: 120 minutes)

**When**:
1. Clicks focus icon on task card
2. Enters full-screen focus mode
3. Countdown starts at 2:00:00
4. Works for 90 minutes
5. Pauses timer (break)
6. Resumes for 30 minutes
7. Marks task complete before timer ends
8. Exits focus mode

**Then**:
- Focus time recorded: 120 minutes (cumulative)
- Achievement "Focus Master" progress updated
- Task marked complete
- Returned to task list

**Edge Cases**:
- Browser tab closed → focus time saved, session ended
- Task deleted by another device → graceful exit with time saved

---

## VII. Known Gaps & Technical Debt

### P0: Critical Gaps (Must fix before public launch)

> **Implementation Status Note (v1.2)**: Phases 1–13 are declared "structurally complete" under the reverse-engineering methodology — code exists for all tasks but acceptance criteria have not been formally verified. Known defects are captured in Phase 14 (Bug Fix Sprint). Per Constitution §I.2, this is a documented exception. Phase 14 MUST be completed before any phase is considered production-ready. The `[X]` markers on Phases 1–13 tasks mean *code exists*, not *acceptance criteria pass*.

~~**Gap 1: Missing Token Refresh in Service Worker**~~ — **RESOLVED (T110)**

- **Resolution**: T110 moved auth token to IndexedDB (`frontend/src/lib/utils/token-storage.ts`), accessible from both SW and main thread.
- **Pending verification**: T134 (HttpOnly cookie migration) may supersede IndexedDB storage; validate token flow after T134 completes.

~~**Gap 2: No Error Boundary Around Main App**~~ — **RESOLVED (T111)**

- **Resolution**: T111 added `frontend/src/components/errors/ErrorBoundary.tsx` wrapping the root layout, providing fallback UI with "Something went wrong" + Reload button.
- ~~**Issue**: Unhandled component errors crash entire app (white screen)~~
- ~~**Evidence**: No `ErrorBoundary` wrapper in `_app.tsx`~~

**Gap 3: Optimistic Locking Not Fully Implemented (Partially Spec-Corrected in v1.1)**

- **Issue A (Spec corrected)**: Frontend `updateTask` calls omit the `version` field; also `useCompleteTask` calls a non-existent `/complete` endpoint instead of `/force-complete`. These are now enforceable requirements in FR-002.
- **Issue B (Open — T112 not built)**: Conflict resolution UI is not yet implemented — `frontend/src/components/tasks/ConflictResolutionModal.tsx` does not exist. When a 409 is returned, there is no modal offering the user a choice between their version and the server version. **T112 was incorrectly marked `[X]` in tasks.md; file confirmed absent; corrected to `[ ]` per sp.analyze remediation (2026-02-20).**
- **Evidence**: [`src/lib/schemas/task.schema.ts:108`](frontend/src/lib/schemas/task.schema.ts#L108) requires version; FR-002 now mandates it; `ConflictResolutionModal.tsx` file confirmed absent; T124 references T112 as a dependency that must be built first
- **Impact**: Concurrent edits from multiple devices will silently return 409 without user guidance
- **Recommendation**: Build T112 (`ConflictResolutionModal`) component first; T124 wires it to 409 responses from `useUpdateTask`
- **Effort**: Medium (2–3 days for T112) + Low (1 day for T124 integration)

**Gap 4: API Contract Violations (Spec-Corrected in v1.1)**

The following API mismatches were identified from code analysis and captured as requirements in this spec update. They are listed here for tracking:

| Bug | Endpoint Mismatch | Spec Section | Status |
|-----|------------------|--------------|--------|
| BUG-06A | `/tasks/{id}/complete` → `/tasks/{id}/force-complete` + `{version}` | FR-002 | Requirement added |
| BUG-06B | `PATCH /tasks/{id}` without `version` | FR-002 | Requirement strengthened |
| BUG-06C | Reminder API calls stubbed/commented-out | FR-006 | Requirement added |
| BUG-05 | `/dashboard/notifications` route missing | FR-011 | FR added |
| BUG-08 | `/subscription/checkout` → `/subscription/upgrade` | FR-012 | FR added |
| NOTIF | `PATCH /notifications/{id}` → `PATCH /notifications/{id}/read` | FR-013 | FR added |
| BUG-01A | `useSubtasks` unconditionally fetches for every card | FR-003 | Requirement added |
| BUG-02 | Cache invalidation uses `task_id` (undefined) not `taskId` | FR-003 | Requirement added |
| S-01 | Tokens in `localStorage` | FR-001 / NFR-002 | Requirement added |
| S-03 | `console.log` of auth/payment events in production | NFR-002 | Requirement added |
| BUG-03/04 | Modals not responsive below 480 px | NFR-007 | NFR added |

---

### P1: Important Gaps (Should fix within 3 months)

**Gap 5: Incomplete Accessibility Testing**

- **Issue**: No automated a11y tests in CI pipeline
- **Evidence**: No `jest-axe` integration (note: `@axe-core/react` is a dev-mode overlay; `jest-axe` is the correct test-assertion library for CI — see tasks.md T157)
- **Impact**: WCAG violations may slip through
- **Recommendation**: Add `jest-axe` to Jest tests (T157), run on every commit; optionally add `@axe-core/react` as dev-mode overlay for interactive a11y debugging
- **Effort**: Low (1-2 days)

**Gap 6: No Rate Limiting on Client**

- **Issue**: User can spam API with rapid mutations
- **Evidence**: No debouncing on task creation, subtask toggles
- **Impact**: Backend strain, potential abuse
- **Recommendation**: Add client-side rate limiting (max 10 mutations/second)
- **Effort**: Low (1 day)

**Gap 7: Missing Analytics Events**

- **Issue**: No tracking for user actions (task creation, focus mode usage)
- **Evidence**: No analytics service integration
- **Impact**: Cannot measure feature usage, optimize UX
- **Recommendation**: Add Mixpanel or Plausible events for key actions
- **Effort**: Medium (2 days)

---

### P2: Nice-to-Have Improvements

**Gap 8: No Dark Mode Toggle**

- **Issue**: App is dark-only, no light mode option
- **Evidence**: Tailwind config only has dark theme
- **Impact**: Some users prefer light mode (accessibility issue for photosensitivity)
- **Recommendation**: Add theme toggle in settings, persist in localStorage
- **Effort**: Medium (3-4 days including redesign)

**Gap 9: Command Palette Could Be Smarter**

- **Issue**: Command palette doesn't learn from user behavior
- **Evidence**: No frecency (frequency + recency) algorithm
- **Impact**: Frequently used commands not prioritized
- **Recommendation**: Track command usage, sort by frecency
- **Effort**: Low (1-2 days)

**Gap 10: No Bulk Operations**

- **Issue**: Cannot select multiple tasks and perform batch actions
- **Evidence**: No multi-select UI
- **Impact**: Tedious to delete/archive multiple tasks
- **Recommendation**: Add checkbox multi-select mode with "Delete Selected" button
- **Effort**: Medium (2-3 days)

---

## VIII. Regeneration Strategy

> **See also**: `specs/002-perpetua-frontend/plan.md §VII` for the full architectural regeneration guide with module-level detail, feature flags, and timeline estimates. This section is a summary. If plan.md §VII and spec.md §VIII diverge, the plan.md version is authoritative for architectural guidance; spec.md is authoritative for requirements.

### Option 1: Specification-First Rebuild (Recommended for Major Refactor)

**When to use**: Technology shift (e.g., React → Svelte), architecture overhaul

**Process**:
1. Use this `spec.md` as blueprint
2. Apply extracted skills from `intelligence-object.md`
3. Implement with modern best practices (fill gaps from Section VII)
4. Test-driven development using acceptance criteria from Section VI
5. Deploy alongside existing app, gradual traffic shift

**Timeline**: 6-8 months (team of 3 developers)

**Benefits**:
- Clean slate, no legacy code baggage
- Opportunity to fix architectural mistakes
- Modern dependencies, better performance

**Risks**:
- Feature parity takes time
- User disruption if not seamless migration

---

### Option 2: Incremental Refactoring (Recommended for Continuous Improvement)

**When to use**: Ongoing development, no major tech shift needed

**Process** (Strangler Pattern):
1. Identify module to refactor (e.g., focus mode)
2. Write spec for that module (reference this doc)
3. Build new implementation alongside old
4. Feature flag to control traffic split
5. A/B test new vs old
6. Deprecate old code when new proven

**Timeline**: Continuous, one module per sprint

**Benefits**:
- Zero downtime
- Gradual risk mitigation
- Can revert instantly if issues

**Risks**:
- Code duplication during transition
- Complexity of maintaining two versions

---

## IX. Appendices

### Appendix A: API Contract Reference

**Full API documentation**: `specs/002-perpetua-frontend/API.md`

**Key endpoints implemented in frontend**:

| Endpoint | Method | Schema Reference | Hook |
|----------|--------|------------------|------|
| `/auth/google/callback` | POST | [`auth.schema.ts`](frontend/src/lib/schemas/auth.schema.ts) | [`useAuth.ts`](frontend/src/lib/hooks/useAuth.ts) |
| `/users/me` | GET | [`user.schema.ts`](frontend/src/lib/schemas/user.schema.ts) | [`useAuth.ts`](frontend/src/lib/hooks/useAuth.ts) |
| `/tasks` | GET | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks` | POST | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks/{id}` | GET | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks/{id}` | PATCH | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks/{id}` | DELETE | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks/{id}/force-complete` | POST | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) | [`useTasks.ts`](frontend/src/lib/hooks/useTasks.ts) |
| `/tasks/{task_id}/subtasks` | GET/POST | [`subtask.schema.ts`](frontend/src/lib/schemas/subtask.schema.ts) | [`useSubtasks.ts`](frontend/src/lib/hooks/useSubtasks.ts) |
| `/notes` | GET/POST | [`note.schema.ts`](frontend/src/lib/schemas/note.schema.ts) | [`useNotes.ts`](frontend/src/lib/hooks/useNotes.ts) |
| `/notes/{note_id}` | PATCH/DELETE | [`note.schema.ts`](frontend/src/lib/schemas/note.schema.ts) | [`useNotes.ts`](frontend/src/lib/hooks/useNotes.ts) |
| `/tasks/{task_id}/reminders` | POST | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | [`useReminders.ts`](frontend/src/lib/hooks/useReminders.ts) |
| `/reminders/{reminder_id}` | DELETE | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | [`useReminders.ts`](frontend/src/lib/hooks/useReminders.ts) |
| `/achievements/me` | GET | [`achievement.schema.ts`](frontend/src/lib/schemas/achievement.schema.ts) | [`useAchievements.ts`](frontend/src/lib/hooks/useAchievements.ts) |
| `/reminders` | GET | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | [`useReminders.ts`](frontend/src/lib/hooks/useReminders.ts) |
| `/reminders/{id}/fire` | POST | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | Service Worker |
| `/notifications` | GET | notification.schema.ts | [`useNotifications.ts`](frontend/src/lib/hooks/useNotifications.ts) |
| `/notifications/{id}/read` | PATCH | notification.schema.ts | [`useNotifications.ts`](frontend/src/lib/hooks/useNotifications.ts) |
| `/subscription/upgrade` | POST | subscription.schema.ts | [`useSubscription.ts`](frontend/src/lib/hooks/useSubscription.ts) |
| `/templates` | GET | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) (`TaskTemplateSchema`) | [`useTaskTemplates.ts`](frontend/src/lib/hooks/useTaskTemplates.ts) |
| `/templates` | POST | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) (`TaskTemplateSchema`) | [`useTaskTemplates.ts`](frontend/src/lib/hooks/useTaskTemplates.ts) |
| `/templates/{id}/instantiate` | POST | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) (`TaskSchema`) | [`useTaskTemplates.ts`](frontend/src/lib/hooks/useTaskTemplates.ts) |
| `/templates/{id}` | PATCH | [`task.schema.ts`](frontend/src/lib/schemas/task.schema.ts) (`TaskTemplateSchema`) | [`useTaskTemplates.ts`](frontend/src/lib/hooks/useTaskTemplates.ts) |
| `/templates/{id}` | DELETE | — | [`useTaskTemplates.ts`](frontend/src/lib/hooks/useTaskTemplates.ts) |

> **Template endpoint note**: `GET /templates`, `POST /templates`, and `POST /templates/{id}/instantiate` are confirmed in `specs/002-perpetua-frontend/API.md`. `PATCH /templates/{id}` and `DELETE /templates/{id}` are required by FR-007 (edit and delete template operations) but are not yet present in API.md — these must be confirmed with the backend team and added to API.md before T097/T099 implementation. **Correction**: T099 in tasks.md incorrectly referenced `GET /api/v1/task-templates`; the correct path per API.md is `GET /api/v1/templates` (see tasks.md T099 remediation in v1.5.0).

---

### Appendix B: Data Model Diagram

**Full data model**: `specs/002-perpetua-frontend/data-model.md`

**Entity relationships** (implemented in frontend schemas):

```
User (1)
  ├─→ Tasks (*) [user_id]
  │     ├─→ Subtasks (*) [task_id]
  │     ├─→ Reminders (*) [task_id]
  │     └─→ TaskTemplate (0..1) [template_id]
  ├─→ Notes (*) [user_id]
  ├─→ UserAchievementState (1) [user_id]
  └─→ CreditDetail (*) [user_id]

TaskTemplate (1)
  └─→ Tasks (*) [template_id] (recurring instances)

AchievementDefinition (*)
  └─→ UserAchievementState.unlocked_achievements (*) [achievement_id]
```

---

### Appendix C: Technology Decision Log

**Key technology choices and rationale**:

1. **Next.js 16 over Create React App**:
   - **Rationale**: App Router SSR for SEO (public pages), API routes for BFF pattern, built-in optimization
   - **Trade-off**: Steeper learning curve vs CRA simplicity
   - **Status**: Accepted

2. **TanStack Query over Redux**:
   - **Rationale**: Server state management built-in, automatic cache invalidation, better DX
   - **Trade-off**: Less community resources vs Redux
   - **Status**: Accepted

3. **Zustand over Redux Toolkit (client state)**:
   - **Rationale**: Minimal boilerplate, no providers, TypeScript-first
   - **Trade-off**: Smaller ecosystem vs Redux DevTools maturity
   - **Status**: Accepted

4. **Zod over Yup**:
   - **Rationale**: TypeScript-native, schema = type (no duplication), better inference
   - **Trade-off**: Less mature ecosystem
   - **Status**: Accepted

5. **MSW over JSON Server**:
   - **Rationale**: Intercepts at network level (works with fetch/axios), browser + Node.js, realistic latency simulation
   - **Trade-off**: More complex setup
   - **Status**: Accepted

6. **Radix UI over Headless UI**:
   - **Rationale**: More components, better accessibility out-of-box, active development
   - **Trade-off**: Slightly larger bundle
   - **Status**: Accepted

7. **Tailwind CSS 4 over CSS Modules**:
   - **Rationale**: Utility-first rapid prototyping, design system via config, tree-shaking removes unused styles
   - **Trade-off**: Verbose class names, learning curve
   - **Status**: Accepted

---

### Appendix D: Testing Strategy

> **V1 Test Status Note**: The V1 test suite (Jest + React Testing Library) was written during initial development and passes. Tests are not yet formally mapped to spec acceptance criteria or task IDs. Mapping will be completed incrementally via `/sp.tasks` as each feature area is re-specified. Coverage target of 80% applies to the mapped set.

**Coverage target**: 80% for core logic and API interactions

**Test Types**:

1. **Unit Tests** (Jest + React Testing Library):
   - Schema validation (Zod parse success/failure)
   - Utility functions (date formatting, recurrence parsing)
   - Store actions (Zustand state transitions)
   - Component logic (without rendering)

2. **Integration Tests** (React Testing Library):
   - User interactions (click, type, submit)
   - API hooks (MSW mocked responses)
   - Route transitions (Next.js routing)

3. **E2E Tests** (Playwright - future):
   - Critical user journeys (Section VI)
   - Cross-browser compatibility
   - Auth flows with real Google OAuth

**Example Test** (from [`src/lib/schemas/task.schema.test.ts`](frontend/tests/) — should exist):
```typescript
describe('TaskSchema', () => {
  it('validates complete task', () => {
    const task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      template_id: null,
      title: 'Test task',
      description: '',
      priority: 'medium',
      due_date: null,
      estimated_duration: null,
      focus_time_seconds: 0,
      completed: false,
      completed_at: null,
      completed_by: null,
      hidden: false,
      archived: false,
      subtask_count: 0,
      subtask_completed_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: 1,
    };
    expect(() => TaskSchema.parse(task)).not.toThrow();
  });

  it('rejects invalid title length', () => {
    const task = { /* ... */, title: 'x'.repeat(501) };
    expect(() => TaskSchema.parse(task)).toThrow();
  });
});
```

---

## X. Conclusion & Next Steps

This specification represents the **authoritative source of truth** for the Perpetua Flow frontend application. All implementation, tests, and runtime behavior must align with this document (per Constitution I).

**For New Features**:
1. Update this spec.md FIRST (before writing code)
2. Get spec reviewed and approved
3. Implement feature per spec
4. Test against acceptance criteria
5. Mark spec section as "Implemented"

**For Bug Fixes**:
1. Determine if spec is wrong or implementation is wrong
2. If spec wrong: Update spec, then fix implementation
3. If implementation wrong: Fix implementation to match spec

**For Hotfixes** (Production only, per Constitution I.2):
1. Apply hotfix to protect users/data
2. Update spec immediately afterward
3. Hotfix incomplete until spec updated

**Deviation Record (Constitution §I.2 — Reverse-Engineering Exception)**

The initial implementation (Phases 1–13) was produced by reverse-engineering existing production code, not test-first development. Tests were written during the V1 build and **pass**, but are not mapped to spec FRs or task IDs. This is a documented deviation from Constitution §VIII.

- **Reason**: Codebase already existed; reverse engineering required capturing behavior before documenting.
- **Test status**: V1 test suite passes. Mapping to spec requirements will be completed via `/sp.specify` and `/sp.tasks` commands as each phase is revisited.
- **Remediation**: All Phase 14+ tasks are written test-first per Constitution §VIII. V1 test-to-spec mapping is tracked as an ongoing documentation task.
- **Status**: Partially remediated — tests exist, documentation in progress.

**Version Control**:
- Spec version: 1.6.0 (sp.analyze remediations v6 — H4 actor_type AI log field, L1 §IX subsection refs, M3 jest-axe correction, M4 ConflictResolutionModal NFR-007, M1 NFR-005 ownership, M2 analytics/feedback Non-Goals — 2026-02-20)
- Previous version: 1.5.0 (sp.analyze remediations v5 — H1 template endpoints in Appendix A + T099 path fix, M3 FR-009 env-absent startup block, M6 entity_id constitution note, L3 §VIII cross-ref, L5 FR-007 recurring edge case — 2026-02-20)
- Previous version: 1.4.0 (sp.analyze remediations v4 — C3 Gap 3 T112 status corrected, H3 entity_id AI logging, M5 circuit-breaker [DEFERRED], L2 FR-007 backend qualifier, L3 NFR-006 P95 deferred — 2026-02-20)
- Previous version: 1.2.0 (a11y coverage, AI logging, offline scope, focus crash fix — 2026-02-20)
- Previous version: 1.1.0 (bug-analysis requirements captured, 2026-02-18)
- Previous version: 1.0.0 (initial reverse-engineered, 2026-02-17)
- Major version: 2.0 (if breaking changes to data model or API contract)

---

**Specification Version**: 1.6.0
**Last Updated**: 2026-02-20
**Status**: ✅ Updated — v1.6 applies sp.analyze remediation v6: actor_type field added to AI log format (H4/FR-009), Constitution §IX subsection refs corrected (L1), jest-axe reference corrected in Gap 5 (M3), ConflictResolutionModal added to NFR-007 affected components + acceptance criteria (M4), NFR-005 reliability ownership separated between frontend/backend (M1), analytics events and in-app feedback formally deferred to Non-Goals §7–8 with NFR-006 updated (M2)
