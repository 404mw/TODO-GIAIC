# Phase 1: Data Model

**Feature**: Perpetua Flow - Frontend Application
**Date**: 2026-01-07
**Status**: Complete

## Overview

This document defines all entities, their fields, relationships, validation rules, and state transitions for the Perpetua Flow application. All entities map 1:1 to Zod schemas in `frontend/src/schemas/`.

---

## Entity Definitions

### 1. Task

**Purpose**: Represents a user's to-do item with metadata for organization, prioritization, and progress tracking.

**Schema Location**: `schemas/task.schema.ts`

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated | Collision-resistant, offline-friendly (FR-001) |
| `title` | `string` | Yes | 1-200 chars | - | Primary display name |
| `description` | `string` | No | 0-1000 chars | `""` | Markdown supported; hard limit enforced (Limits table) |
| `tags` | `string[]` | No | Each tag 1-30 chars | `[]` | Freeform with autocomplete from history (Clarification session) |
| `priority` | `enum` | Yes | `"low" \| "medium" \| "high"` | `"medium"` | Affects sorting and streak tracking (FR-001, FR-029) |
| `estimatedDuration` | `number` | No | 1-720 minutes (12 hours max) | `null` | Estimation only, no time tracking (FR-009, Non-Goals 1) |
| `reminders` | `Reminder[]` | No | See Reminder sub-schema | `[]` | Future: Browser notifications (FR-068) |
| `recurring` | `RecurrenceRule \| null` | No | See RecurrenceRule sub-schema | `null` | Generate next instance on completion (FR-069, FR-070) |
| `hidden` | `boolean` | No | - | `false` | Soft-hide without deletion (FR-005, FR-006) |
| `completed` | `boolean` | No | - | `false` | Marks task as done |
| `completedAt` | `string` (ISO 8601) | No | Valid ISO timestamp | `null` | Set when `completed` transitions to `true` |
| `createdAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-generated | Immutable after creation |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated | MSW updates on every mutation |
| `parentTaskId` | `string` (UUID) \| `null` | No | Must reference existing Task if set | `null` | Always `null` for tasks (only sub-tasks have parents) |

**Relationships**:
- **One-to-many** with Sub-task: A Task can have 0-10 Sub-tasks (enforced by Limits)
- **Many-to-one** with User Profile: A User owns many Tasks (implicit, not enforced client-side with MSW)

**Validation Rules**:
- `title` must not be empty string (trimmed)
- `estimatedDuration` cannot exceed 720 minutes (12 hours) to prevent unrealistic Focus Mode sessions
- `tags` array max 20 items (prevents UI clutter)
- If `parentTaskId` is set, entity is actually a Sub-task (see Sub-task entity)

**State Transitions**:
```
[Created] → completed = false, hidden = false
  ↓
[Active] → User can edit, add sub-tasks, activate Focus Mode
  ↓
[Completed] → completed = true, completedAt = now()
  ↓
[Hidden] → hidden = true (can be unhidden from Settings)
```

**Invariants**:
- Once `completedAt` is set, it should not change (immutable timestamp)
- `updatedAt` must be >= `createdAt`
- `estimatedDuration` must be positive integer or `null`

---

### 2. Sub-task

**Purpose**: Represents a child task that contributes to parent task progress. Cannot exist independently.

**Schema Location**: `schemas/subtask.schema.ts`

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated | Unique identifier |
| `title` | `string` | Yes | 1-200 chars | - | Primary display name |
| `completed` | `boolean` | No | - | `false` | Marks sub-task as done |
| `completedAt` | `string` (ISO 8601) | No | Valid ISO timestamp | `null` | Set when `completed` transitions to `true` |
| `createdAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-generated | Immutable after creation |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated | MSW updates on every mutation |
| `parentTaskId` | `string` (UUID) | Yes | Must reference existing Task | - | **Required**: Sub-tasks cannot be orphaned (FR-008) |

**Relationships**:
- **Many-to-one** with Task: A Sub-task belongs to exactly one Task
- **No nesting**: Sub-tasks cannot have their own sub-tasks (FR-002, Non-Goals 2)

**Validation Rules**:
- `parentTaskId` must reference an existing Task (enforced by MSW)
- `title` must not be empty string (trimmed)
- Max 10 sub-tasks per parent task (enforced by frontend before POST)

**State Transitions**:
```
[Created] → completed = false, attached to parentTaskId
  ↓
[Active] → User can mark complete/incomplete
  ↓
[Completed] → completed = true, completedAt = now(), parent progress updates
```

**Invariants**:
- `parentTaskId` must never be `null` (enforced by schema)
- Cannot create sub-task if parent task has 10 sub-tasks already
- Deleting parent task cascades to delete all sub-tasks (MSW behavior)

**Progress Calculation** (FR-003):
```
Parent Task Progress = (Completed Sub-tasks / Total Sub-tasks) × 100
```
If total sub-tasks = 0, progress UI is hidden (FR-004).

---

### 3. Note

**Purpose**: Represents a quick capture of user thoughts, optionally voice-transcribed, that can be converted to a Task.

**Schema Location**: `schemas/note.schema.ts`

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated | Unique identifier |
| `content` | `string` | Yes | 1-1000 chars | - | Hard limit enforced (Limits table) |
| `archived` | `boolean` | No | - | `false` | Archived after conversion to Task |
| `voiceMetadata` | `VoiceMetadata \| null` | No | See VoiceMetadata sub-schema | `null` | Present if created via voice-to-text |
| `createdAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-generated | Immutable after creation |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated | MSW updates on every mutation |

**Relationships**:
- **Many-to-one** with User Profile: A User owns many Notes (implicit, not enforced client-side)

**Validation Rules**:
- `content` must not be empty string (trimmed)
- Soft limit 750 chars (warning tooltip), hard limit 1000 chars (input blocked)
- Voice recording max 60 seconds (enforced in UI before transcription)

**State Transitions**:
```
[Created] → archived = false, editable
  ↓
[Active] → User can edit content, convert to Task
  ↓
[Archived] → archived = true (after Task conversion, FR-020)
```

**Invariants**:
- If `voiceMetadata` is present, `voiceMetadata.duration` must be ≤ 60 seconds
- Archived notes excluded from default views but not deleted

---

### 4. VoiceMetadata (Sub-schema)

**Purpose**: Metadata for voice-transcribed notes.

**Schema Location**: `schemas/note.schema.ts` (nested)

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `duration` | `number` | Yes | 1-60 seconds | Recording duration (Limits table) |
| `transcriptionService` | `string` | Yes | - | e.g., "Web Speech API", "Google Cloud Speech" |
| `language` | `string` | Yes | ISO 639-1 code | e.g., "en" (English only in initial release) |
| `confidence` | `number` | No | 0-1 (percentage) | Transcription confidence score if available |

---

### 5. User Profile

**Purpose**: Represents user account information and preferences.

**Schema Location**: `schemas/user.schema.ts`

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Backend-generated | User identifier |
| `name` | `string` | Yes | 1-100 chars | - | Display name |
| `email` | `string` | Yes | Valid email format | - | Unique per user |
| `preferences` | `UserPreferences` | No | See UserPreferences sub-schema | Defaults | UI state |
| `firstLogin` | `boolean` | No | - | `true` | Triggers onboarding walkthrough (FR-044) |
| `tutorialCompleted` | `boolean` | No | - | `false` | Set after walkthrough completion |
| `createdAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Backend-generated | Immutable |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated | MSW updates on preference changes |

**Relationships**:
- **One-to-many** with Task, Note, Workflow, Achievement: A User owns all their data

**Validation Rules**:
- `email` must be valid format (RFC 5322 simplified)
- `name` must not be empty string (trimmed)

**State Transitions**:
```
[FirstLogin] → firstLogin = true, tutorialCompleted = false
  ↓
[Onboarding] → Walkthrough active
  ↓
[Active User] → firstLogin = false, tutorialCompleted = true (after walkthrough)
```

---

### 6. UserPreferences (Sub-schema)

**Purpose**: Stores UI preferences persisted in localStorage.

**Schema Location**: `schemas/user.schema.ts` (nested)

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `sidebarOpen` | `boolean` | No | - | `true` | Sidebar expanded/collapsed (FR-036) |
| `themeTweaks` | `ThemeTweaks` | No | See ThemeTweaks sub-schema | Defaults | Minor dark theme customizations |

**Persistence**:
- Stored in `localStorage` under key `perpetua:preferences`
- Managed by Zustand `persist` middleware

---

### 7. ThemeTweaks (Sub-schema)

**Purpose**: Minor customizations within dark mode palette.

**Schema Location**: `schemas/user.schema.ts` (nested)

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `accentColor` | `string` | No | Hex color (e.g., `#3B82F6`) | `#3B82F6` (blue) | Accent for highlights, focus rings |
| `glassIntensity` | `number` | No | 0.1-0.3 (opacity) | `0.15` | Glassmorphism backdrop opacity |
| `animationSpeed` | `number` | No | 0.5-1.0 (multiplier) | `1.0` | Animation duration multiplier (respects reduced motion) |

**Validation Rules**:
- `accentColor` must be valid hex color
- Values must stay within WCAG AA contrast bounds (enforced by color picker)

---

### 8. Achievement

**Purpose**: Represents tracked metrics and milestones for motivation.

**Schema Location**: `schemas/achievement.schema.ts`

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated | Unique identifier |
| `userId` | `string` (UUID) | Yes | Must reference User | - | Owner |
| `highPrioritySlays` | `number` | No | >= 0 | `0` | Count of completed high-priority tasks (FR-029) |
| `consistencyStreak` | `ConsistencyStreak` | No | See ConsistencyStreak sub-schema | Default | Consecutive days with >= 1 completed task |
| `completionRatio` | `number` | No | 0-100 (percentage) | `0` | (Completed / Created) × 100 (FR-029) |
| `milestones` | `Milestone[]` | No | See Milestone sub-schema | `[]` | Triggered thresholds with timestamps |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated | Recalculated on task completion |

**Relationships**:
- **One-to-one** with User Profile: Each User has exactly one Achievement record

**Validation Rules**:
- `completionRatio` must be between 0-100
- Milestones are immutable once triggered (append-only)

**Metric Definitions** (FR-030):
- **High Priority Slays**: Increment by 1 for each completed task with `priority = "high"`
- **Consistency Streak**: Days with >= 1 completed task, reset at UTC midnight with 1 grace day (Clarification session)
- **Completion Ratio**: `(Total Completed Tasks / Total Created Tasks) × 100`

---

### 9. ConsistencyStreak (Sub-schema)

**Purpose**: Tracks consecutive days with task completions.

**Schema Location**: `schemas/achievement.schema.ts` (nested)

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `currentStreak` | `number` | Yes | >= 0 | Current consecutive days |
| `longestStreak` | `number` | Yes | >= 0 | All-time longest streak |
| `lastCompletionDate` | `string` (ISO 8601 date) | No | YYYY-MM-DD format | Last UTC day with completion |
| `graceDayUsed` | `boolean` | No | - | True if 1-day gap tolerated (FR-033) |

**Reset Logic** (FR-033):
```
If today - lastCompletionDate > 2 days:
  currentStreak = 0
  graceDayUsed = false
Else if today - lastCompletionDate === 2 days && !graceDayUsed:
  graceDayUsed = true  # Tolerate 1-day miss
Else if today - lastCompletionDate > 2 days && graceDayUsed:
  currentStreak = 0
  graceDayUsed = false
```

---

### 10. Milestone (Sub-schema)

**Purpose**: Represents achievement thresholds with timestamps.

**Schema Location**: `schemas/achievement.schema.ts` (nested)

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `id` | `string` | Yes | Enum of predefined IDs | e.g., "streak_7", "slays_50", "ratio_90" |
| `name` | `string` | Yes | - | Display name, e.g., "Week Warrior" |
| `description` | `string` | Yes | - | Human-readable explanation |
| `unlockedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Immutable once set |

**Predefined Milestones**:
- `streak_7`: 7-day consistency streak
- `streak_30`: 30-day consistency streak
- `slays_10`: 10 high-priority tasks completed
- `slays_50`: 50 high-priority tasks completed
- `ratio_75`: 75% completion ratio
- `ratio_90`: 90% completion ratio

---

### 11. Workflow

**Purpose**: Represents a collection of related tasks organized as a user-defined sequence.

**Schema Location**: `schemas/workflow.schema.ts`

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated |
| `name` | `string` | Yes | 1-200 chars | Display name |
| `description` | `string` | No | 0-1000 chars | Optional explanation |
| `taskIds` | `string[]` (UUIDs) | Yes | Each must reference existing Task | Ordered list of task IDs |
| `createdAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-generated |
| `updatedAt` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Auto-updated |

**Relationships**:
- **Many-to-many** with Task: A Workflow references multiple Tasks, a Task can be in multiple Workflows

**Validation Rules**:
- `taskIds` array can be empty (placeholder workflow)
- Order of `taskIds` defines sequence in Workflow UI
- Deleting a Task removes its ID from all Workflows

**State Transitions**:
```
[Created] → taskIds = []
  ↓
[Populated] → User adds tasks to workflow
  ↓
[Active] → User reorders, completes tasks within workflow
```

**Note**: Workflow details are underspecified in requirements; this is a minimal viable definition.

---

### 12. Activity Log Event

**Purpose**: Represents historical user actions for audit and AI interaction logging.

**Schema Location**: `schemas/activity.schema.ts`

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Client-generated |
| `taskId` | `string` (UUID) | Yes | Must reference existing Task | Event target (Constitution V.2) |
| `eventType` | `enum` | Yes | See Event Types below | Action category |
| `actor` | `enum` | Yes | `"user" \| "ai"` | Who performed action (Constitution V.2) |
| `timestamp` | `string` (ISO 8601) | Yes | Valid ISO timestamp | Immutable (Constitution V.3) |
| `metadata` | `object` | No | JSON object | Event-specific details |

**Event Types**:
- `task_created`: Task created by user or AI
- `task_updated`: Task fields modified
- `task_completed`: Task marked complete
- `task_deleted`: Task soft-deleted (hidden)
- `subtask_added`: Sub-task added to task
- `subtask_completed`: Sub-task marked complete
- `focus_mode_activated`: Focus Mode started on task
- `focus_mode_exited`: Focus Mode manually exited or completed
- `ai_subtasks_generated`: Magic Sub-tasks invoked (future)
- `note_converted_to_task`: Note-to-Task conversion (future)

**Relationships**:
- **Many-to-one** with Task: An Activity Log Event references one Task
- **Many-to-one** with User Profile: Events belong to a User (implicit)

**Validation Rules**:
- `actor = "ai"` only allowed when AI features enabled (backend integrated)
- Events are **immutable** and **append-only** (Constitution V.3)
- Rolling window: Keep last 100 events per user (Limits table), oldest dropped silently

**Invariants**:
- `timestamp` must be in the past (cannot create future events)
- Events cannot be deleted or modified after creation

---

### 13. Reminder (Sub-schema)

**Purpose**: Represents a scheduled notification for a task.

**Schema Location**: `schemas/task.schema.ts` (nested)

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `id` | `string` (UUID) | Yes | UUID v4 format | Unique reminder ID |
| `time` | `string` (ISO 8601) | Yes | Future timestamp | When to trigger notification |
| `notified` | `boolean` | No | - | True if notification sent |

**Future Implementation**: FR-068 requires browser notification API integration.

---

### 14. RecurrenceRule (Sub-schema)

**Purpose**: Defines how a task repeats.

**Schema Location**: `schemas/task.schema.ts` (nested)

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `frequency` | `enum` | Yes | `"daily" \| "weekly" \| "monthly"` | Repeat interval |
| `interval` | `number` | Yes | >= 1 | e.g., 2 = every 2 days/weeks/months |
| `endDate` | `string` (ISO 8601 date) | No | YYYY-MM-DD, must be future | Optional recurrence cutoff |

**Future Implementation**: FR-069, FR-070 require generating next instance on completion.

---

## Entity Relationships Diagram

```
User Profile (1) ──── (many) Task
                         │
                         ├──── (0-10) Sub-task
                         │
User Profile (1) ──── (many) Note
User Profile (1) ──── (1) Achievement
User Profile (1) ──── (many) Activity Log Event
User Profile (1) ──── (many) Workflow

Workflow (many) ──── (many) Task (via taskIds array)

Activity Log Event (many) ──── (1) Task
```

---

## Schema Export Structure

Each schema file in `frontend/src/schemas/` follows this pattern:

```typescript
import { z } from 'zod';

// Define schema
export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  // ... all fields
});

// Export TypeScript type
export type Task = z.infer<typeof TaskSchema>;

// Export partial schemas for updates (optional fields only)
export const TaskUpdateSchema = TaskSchema.partial().omit({ id: true });
```

**Usage**:
- **MSW Handlers**: `TaskSchema.parse(requestBody)` to validate POST/PATCH requests
- **TanStack Query**: Return type is `Task` for type inference
- **Forms**: `TaskUpdateSchema` for edit forms (only changed fields sent)

---

## Validation Strategy

1. **Client-side (Pre-submit)**:
   - Form validation with `react-hook-form` + Zod resolver
   - Real-time feedback for limits (character counts, max sub-tasks, etc.)
   - Block submit if validation fails

2. **MSW Handler (Simulated Backend)**:
   - `Schema.parse(data)` throws on invalid data (simulates 400 Bad Request)
   - Relationship checks (e.g., `parentTaskId` exists)
   - Limit enforcement (e.g., max 50 tasks, max 10 sub-tasks)

3. **TanStack Query (Runtime)**:
   - Response validation with `Schema.parse(response)` to catch MSW bugs
   - Type narrowing for TypeScript safety

---

## State Transition Rules

### Task Lifecycle
```
[Draft] → User creating task (unsaved)
  ↓ (POST /api/tasks)
[Active] → completed = false, visible in lists
  ↓ (PATCH /api/tasks/:id { completed: true })
[Completed] → completed = true, completedAt set
  ↓ (PATCH /api/tasks/:id { hidden: true })
[Hidden] → Excluded from default views, recoverable from Settings
```

### Focus Mode Lifecycle
```
[Inactive] → focusModeActive = false (Zustand)
  ↓ (User clicks target icon)
[Active] → focusModeActive = true, activeTaskId set, timer starts
  ↓ (User completes task OR manually exits)
[Exited] → focusModeActive = false, activeTaskId = null, timer cleared
```

### Achievement Update Lifecycle
```
[Task Completed Event]
  ↓
[Recalculate Metrics] → Update highPrioritySlays, consistencyStreak, completionRatio
  ↓
[Check Milestones] → If threshold crossed, append new Milestone
  ↓
[Trigger Animation] → Shimmer/confetti for new milestone (FR-032)
```

---

## Data Integrity Rules

1. **No Orphaned Sub-tasks**: Sub-task `parentTaskId` must reference existing Task (FR-008)
2. **Immutable Timestamps**: `createdAt`, `completedAt`, `unlockedAt` cannot be modified after set
3. **Cascading Deletes**: Deleting Task deletes all its Sub-tasks and removes from Workflows
4. **Rolling Window**: Activity Log keeps last 100 events, oldest dropped (no user notification)
5. **Unique IDs**: All UUIDs client-generated with `crypto.randomUUID()` (v4)

---

## MSW Data Seeding

**Initial Fixtures** (for development and testing):
- 10 sample tasks (3 high priority, 4 medium, 3 low)
- 5 tasks with 2-4 sub-tasks each
- 3 completed tasks (to populate achievements)
- 5 notes (2 archived, 1 with voice metadata)
- 1 user profile with `firstLogin = true`
- 1 achievement record with 1 unlocked milestone
- 1 workflow with 3 task references
- 20 activity log events (mixed user and future AI events)

**Fixture Location**: `frontend/src/mocks/fixtures/`

---

## Next Steps

Phase 1 data modeling complete. Proceed to **API Contracts** generation.
