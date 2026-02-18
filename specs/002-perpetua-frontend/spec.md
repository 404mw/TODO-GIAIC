# Perpetua Flow Frontend - Specification

**Version**: 1.0 (Reverse Engineered from Implementation)
**Date**: 2026-02-18
**Source**: `g:\Hackathons\GIAIC_Hackathons\02-TODO\frontend`
**Constitution**: `.specify/memory/constitution.md` v1.0.0

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
- Token storage in `localStorage`
- User session creation in backend
- Redirect to dashboard on success

**Success Criteria**:
- [ ] User can authenticate with Google account
- [ ] Tokens refresh automatically before expiration
- [ ] Logout clears all session data
- [ ] Failed auth redirects to login with error message

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
   - Input: Partial task + `version` (required for optimistic locking)
   - Output: Updated task with incremented version
   - Conflict handling: If version mismatch, return 409 with latest version

3. **Delete Task** (DELETE `/api/v1/tasks/{id}`)
   - Soft delete: Sets `hidden: true`
   - Returns: `{ tombstone_id, recoverable_until }`
   - Recovery window: 30 days, then permanent deletion

4. **Complete Task** (POST `/api/v1/tasks/{id}/force-complete`)
   - Marks task as complete with `completed_by: 'force'`
   - Updates achievement stats (streak, lifetime count)
   - Returns: `{ task, unlocked_achievements[], streak }`
   - Triggers: Achievement unlock checks, streak calculation

**Success Criteria**:
- [ ] Tasks persist across sessions
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

**Success Criteria**:
- [ ] Subtask creation respects 10-per-task limit
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
- [ ] Focus time persisted even if browser crashes
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

**Operations**:

1. **Create Note** (POST `/api/v1/notes`)
   - Input: `{ content }`
   - Side effect: Increments `notes_created` stat (achievement tracking)
   - Limit: 20 notes per user (free), unlimited (pro)

2. **Convert to Task** (POST `/api/v1/notes/{id}/convert`)
   - Parses note content for task metadata:
     - Priority keywords: "urgent", "important" → high priority
     - Duration hints: "30 min", "2 hours" → estimated_duration
     - Date patterns: "tomorrow", "next Monday" → due_date (AI-powered, Pro only)
   - Creates task with note content as description
   - Marks note as archived (not deleted)
   - Increments `notes_converted` achievement stat

3. **Archive Note** (PATCH `/api/v1/notes/{id}`)
   - Input: `{ archived: true }`
   - Archived notes hidden from main view, accessible in settings

**Voice Notes (Pro Feature)**:
- User records audio (max 5 minutes)
- Uploaded to backend, transcribed via Whisper API
- Transcription appears as note content when `transcription_status: 'completed'`
- Used for hands-free capture

**Success Criteria**:
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
- [ ] New instance created within 1 minute of completion
- [ ] Template edits don't affect historical instances
- [ ] Paused templates don't generate instances
- [ ] Complex patterns (e.g., "2nd Tuesday of month") supported

**Edge Cases**:
- Completing instance before previous → generates from completion time, not original due_date
- Network failure during generation → queued, retried on reconnect
- Invalid RRule → validation error on template creation

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
   - Model: GPT-4 (Anthropic fallback)
   - Prompt engineering: "Break down this task into actionable subtasks (3-7 items)"
   - Cost: 1 AI credit per generation

2. **Priority Recommendation** (POST `/api/v1/tasks/{id}/ai/priority`):
   - Input: Task details + user's current task list
   - Output: `{ priority: 'high' | 'medium' | 'low', reasoning: string }`
   - Factors: Deadlines, dependencies, user patterns
   - Cost: 1 AI credit

3. **Note Parsing** (POST `/api/v1/notes/{id}/parse`):
   - Input: Note content
   - Output: `{ title, description, due_date?, priority?, estimated_duration? }`
   - Pattern recognition: Natural language dates, urgency keywords
   - Example: "Call dentist tomorrow urgent" → { title: "Call dentist", due_date: tomorrow, priority: 'high' }
   - Cost: 1 AI credit

**AI Credit System**:
- Free tier: 0 credits (AI disabled)
- Pro tier: 100 credits/day (resets midnight UTC)
- Credits tracked in `UserAchievementState.daily_ai_credits_used`
- Perks can increase daily limit

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
   - HttpOnly cookies for refresh tokens (future enhancement)
   - Logout clears all tokens

4. **Clickjacking Protection**:
   - `X-Frame-Options: DENY` header
   - CSP `frame-ancestors 'none'`

**Secrets Management** (per Constitution IX):
- All API keys in `.env.local` (never in code)
- `NEXT_PUBLIC_API_URL` for backend endpoint
- Environment validation on startup (blocks if missing required vars)

**Success Criteria**:
- [ ] OWASP Top 10 vulnerabilities addressed
- [ ] Security headers score A+ on securityheaders.com
- [ ] No secrets in Git history
- [ ] Dependency vulnerability scan passes (npm audit)

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
- **Uptime**: 99.5% (excludes planned maintenance)
- **Error rate**: < 1% of requests
- **Crash rate**: < 0.1% of sessions

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
- [ ] All API errors logged with request_id
- [ ] Error boundaries prevent full-page crashes
- [ ] Offline mode allows task viewing (cached data)
- [ ] Network reconnect syncs queued actions

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

**User Feedback**:
- In-app feedback form (bottom-right widget)
- Issue reporting to GitHub (pre-filled template)

**Success Criteria**:
- [ ] All errors captured with full context
- [ ] Web Vitals tracked for 100% of users (sampled)
- [ ] P95 API latency visualized in dashboard

**Implementation Evidence**: Sentry setup in `_app.tsx`, Web Vitals hook

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
- [ ] All CRUD operations (tasks, subtasks, notes) work offline (queued, synced on reconnect)
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
7. Sees achievement unlock: "First Steps" (5 tasks milestone)

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

**Gap 1: Missing Token Refresh in Service Worker**

- **Issue**: Service Worker cannot access localStorage to get auth token
- **Evidence**: [`public/service-worker.js:28`](frontend/public/service-worker.js#L28) comment `// TODO: Get auth token`
- **Impact**: Reminder polling fails for authenticated users (403 Unauthorized)
- **Recommendation**: Use IndexedDB for token storage, accessible from SW and main thread
- **Effort**: Medium (2-3 days)

**Gap 2: No Error Boundary Around Main App**

- **Issue**: Unhandled component errors crash entire app (white screen)
- **Evidence**: No `ErrorBoundary` wrapper in `_app.tsx`
- **Impact**: Poor UX, user must manually refresh
- **Recommendation**: Add React Error Boundary with fallback UI ("Something went wrong" + reload button)
- **Effort**: Low (1 day)

**Gap 3: Optimistic Locking Not Fully Implemented**

- **Issue**: Frontend sends `version` field, but conflict resolution UI incomplete
- **Evidence**: [`src/lib/schemas/task.schema.ts:108`](frontend/src/lib/schemas/task.schema.ts#L108) requires version, but no conflict modal
- **Impact**: Concurrent edits silently fail (user confusion)
- **Recommendation**: Add conflict resolution modal showing diff, allow user to choose version
- **Effort**: Medium (2-3 days)

---

### P1: Important Gaps (Should fix within 3 months)

**Gap 4: Incomplete Accessibility Testing**

- **Issue**: No automated a11y tests in CI pipeline
- **Evidence**: No `@axe-core/react` integration
- **Impact**: WCAG violations may slip through
- **Recommendation**: Add axe-core to Jest tests, run on every commit
- **Effort**: Low (1-2 days)

**Gap 5: No Rate Limiting on Client**

- **Issue**: User can spam API with rapid mutations
- **Evidence**: No debouncing on task creation, subtask toggles
- **Impact**: Backend strain, potential abuse
- **Recommendation**: Add client-side rate limiting (max 10 mutations/second)
- **Effort**: Low (1 day)

**Gap 6: Missing Analytics Events**

- **Issue**: No tracking for user actions (task creation, focus mode usage)
- **Evidence**: No analytics service integration
- **Impact**: Cannot measure feature usage, optimize UX
- **Recommendation**: Add Mixpanel or Plausible events for key actions
- **Effort**: Medium (2 days)

---

### P2: Nice-to-Have Improvements

**Gap 7: No Dark Mode Toggle**

- **Issue**: App is dark-only, no light mode option
- **Evidence**: Tailwind config only has dark theme
- **Impact**: Some users prefer light mode (accessibility issue for photosensitivity)
- **Recommendation**: Add theme toggle in settings, persist in localStorage
- **Effort**: Medium (3-4 days including redesign)

**Gap 8: Command Palette Could Be Smarter**

- **Issue**: Command palette doesn't learn from user behavior
- **Evidence**: No frecency (frequency + recency) algorithm
- **Impact**: Frequently used commands not prioritized
- **Recommendation**: Track command usage, sort by frecency
- **Effort**: Low (1-2 days)

**Gap 9: No Bulk Operations**

- **Issue**: Cannot select multiple tasks and perform batch actions
- **Evidence**: No multi-select UI
- **Impact**: Tedious to delete/archive multiple tasks
- **Recommendation**: Add checkbox multi-select mode with "Delete Selected" button
- **Effort**: Medium (2-3 days)

---

## VIII. Regeneration Strategy

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

**Full API documentation**: `specs/002-perpetua-frontend/contracts/API.md`

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
| `/achievements/me` | GET | [`achievement.schema.ts`](frontend/src/lib/schemas/achievement.schema.ts) | [`useAchievements.ts`](frontend/src/lib/hooks/useAchievements.ts) |
| `/reminders` | GET | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | [`useReminders.ts`](frontend/src/lib/hooks/useReminders.ts) |
| `/reminders/{id}/fire` | POST | [`reminder.schema.ts`](frontend/src/lib/schemas/reminder.schema.ts) | Service Worker |

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

**Version Control**:
- Spec version: 1.0 (initial reverse-engineered)
- Next version: 1.1 (when features added)
- Major version: 2.0 (if breaking changes to data model or API)

---

**Specification Version**: 1.0.0
**Last Updated**: 2026-02-18
**Status**: ✅ Complete (Reverse Engineered from Codebase)
