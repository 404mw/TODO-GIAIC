# Backend Data Model

**Feature**: Perpetua Flow Backend API
**Date**: 2026-01-19
**Status**: Draft

## Overview

This document defines all database entities, their fields, relationships, validation rules, and state transitions for the Perpetua Flow backend. All entities map to SQLModel/Pydantic schemas in the backend implementation.

---

## Entity Definitions

### 1. User

**Purpose**: Represents an authenticated account with profile, preferences, subscription status, and timezone.

**Table Name**: `users`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique user identifier |
| `google_id` | `string` | Yes | Unique | - | Google OAuth subject ID |
| `email` | `string` | Yes | Unique, Valid email | - | From Google profile |
| `name` | `string` | Yes | 1-100 chars | - | Display name from Google |
| `avatar_url` | `string` | No | Valid URL | `null` | Google profile picture |
| `timezone` | `string` | No | Valid IANA timezone | `UTC` | User's display timezone |
| `tier` | `enum` | Yes | `free`, `pro` | `free` | Subscription tier |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Account creation time |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last modification time |

**Relationships**:
- One-to-many with Task Instance, Task Template, Note, Reminder, Notification
- One-to-one with User Achievement State
- One-to-many with AI Credit Ledger entries
- One-to-one with Subscription

**Indexes**:
- `idx_users_google_id` on `google_id` (unique)
- `idx_users_email` on `email` (unique)

---

### 2. Task Instance

**Purpose**: A concrete task occurrence with title, description, priority, due date, completion status, and focus time tracking.

**Table Name**: `task_instances`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique task identifier |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Task owner |
| `template_id` | `UUID` | No | Foreign Key → task_templates | `null` | Source template for recurring tasks |
| `title` | `string` | Yes | 1-200 chars | - | Task name |
| `description` | `string` | No | Max 1000/2000 chars (tier) | `""` | Markdown-supported description |
| `priority` | `enum` | Yes | `low`, `medium`, `high` | `medium` | Task priority level |
| `due_date` | `timestamp` | No | Future or null | `null` | Task deadline (UTC) |
| `estimated_duration` | `integer` | No | 1-720 minutes | `null` | Time estimate in minutes |
| `focus_time_seconds` | `integer` | No | >= 0 | `0` | Accumulated focus mode time |
| `completed` | `boolean` | No | - | `false` | Completion status |
| `completed_at` | `timestamp` | No | UTC | `null` | Completion timestamp |
| `completed_by` | `enum` | No | `manual`, `auto`, `force` | `null` | How task was completed |
| `hidden` | `boolean` | No | - | `false` | Soft-delete flag |
| `archived` | `boolean` | No | - | `false` | Archive flag |
| `version` | `integer` | Yes | >= 1 | `1` | Optimistic locking version |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last modification |

**Relationships**:
- Many-to-one with User
- Many-to-one with Task Template (optional)
- One-to-many with Subtask (max 4 free / 10 pro)
- One-to-many with Reminder (max 5)

**Indexes**:
- `idx_task_instances_user_id` on `user_id`
- `idx_task_instances_user_completed` on `(user_id, completed)`
- `idx_task_instances_template_id` on `template_id`
- `idx_task_instances_due_date` on `due_date`

**Validation Rules**:
- `title` must not be empty (trimmed)
- `estimated_duration` cannot exceed 720 minutes
- `completed_at` set automatically when `completed` transitions to `true`
- Max task duration: 30 days from creation

**State Transitions**:
```
[Created] → completed = false, hidden = false, archived = false
    ↓
[Active] → User can edit, add subtasks, use focus mode
    ↓
[Completed] → completed = true, completed_at = now(), completed_by set
    ↓ (optional)
[Hidden] → hidden = true (soft delete)
    ↓ (alternative)
[Archived] → archived = true (readonly, not deleted)
```

---

### 3. Task Template

**Purpose**: A recurring task definition with recurrence rules that spawns task instances.

**Table Name**: `task_templates`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique template ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Template owner |
| `title` | `string` | Yes | 1-200 chars | - | Template name |
| `description` | `string` | No | Max 1000/2000 chars | `""` | Template description |
| `priority` | `enum` | Yes | `low`, `medium`, `high` | `medium` | Default priority |
| `estimated_duration` | `integer` | No | 1-720 minutes | `null` | Default duration |
| `rrule` | `string` | Yes | Valid RRULE format | - | Recurrence rule (RFC 5545) |
| `next_due` | `timestamp` | No | UTC | `null` | Next instance due date |
| `active` | `boolean` | No | - | `true` | Whether template generates instances |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last modification |

**Relationships**:
- Many-to-one with User
- One-to-many with Task Instance

**RRULE Examples**:
- Daily: `FREQ=DAILY;INTERVAL=1`
- Weekly on Monday: `FREQ=WEEKLY;BYDAY=MO`
- Monthly on 1st: `FREQ=MONTHLY;BYMONTHDAY=1`
- Every 2 weeks: `FREQ=WEEKLY;INTERVAL=2`

---

### 4. Subtask

**Purpose**: A child item of a task with title, completion status, and ordering.

**Table Name**: `subtasks`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique subtask ID |
| `task_id` | `UUID` | Yes | Foreign Key → task_instances | - | Parent task |
| `title` | `string` | Yes | 1-200 chars | - | Subtask name |
| `completed` | `boolean` | No | - | `false` | Completion status |
| `completed_at` | `timestamp` | No | UTC | `null` | Completion time |
| `order_index` | `integer` | Yes | >= 0 | Auto-increment | Display order |
| `source` | `enum` | Yes | `user`, `ai` | `user` | Creation source |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last modification |

**Relationships**:
- Many-to-one with Task Instance

**Constraints**:
- Max 4 subtasks per task (free tier)
- Max 10 subtasks per task (pro tier)
- `order_index` must be gapless (0, 1, 2, ...)

**Auto-Completion Logic**:
- When all subtasks of a task are completed, parent task auto-completes with `completed_by = auto`
- When parent task is force-completed, all incomplete subtasks are marked `completed` with parent's timestamp

---

### 5. Note

**Purpose**: A quick-capture text or voice recording that can be converted to a task.

**Table Name**: `notes`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique note ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Note owner |
| `content` | `string` | Yes | 1-2000 chars | - | Note text content |
| `archived` | `boolean` | No | - | `false` | Archived after task conversion |
| `voice_url` | `string` | No | Valid URL | `null` | Audio file URL (S3/R2) |
| `voice_duration_seconds` | `integer` | No | 1-300 | `null` | Recording duration |
| `transcription_status` | `enum` | No | `pending`, `completed`, `failed` | `null` | Voice transcription state |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last modification |

**Relationships**:
- Many-to-one with User

**Constraints**:
- Max 10 notes (free tier)
- Max 25 notes (pro tier)
- Voice recording max 300 seconds
- Voice transcription: Pro users only

---

### 6. Reminder

**Purpose**: A scheduled notification tied to a task's due date.

**Table Name**: `reminders`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Unique reminder ID |
| `task_id` | `UUID` | Yes | Foreign Key → task_instances | - | Associated task |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Reminder owner |
| `type` | `enum` | Yes | `before`, `after`, `absolute` | - | Reminder timing type |
| `offset_minutes` | `integer` | No | Integer (can be negative) | `null` | Minutes before/after due date |
| `scheduled_at` | `timestamp` | Yes | UTC | - | Calculated notification time |
| `method` | `enum` | Yes | `push`, `in_app` | `in_app` | Notification delivery method |
| `fired` | `boolean` | No | - | `false` | Whether notification was sent |
| `fired_at` | `timestamp` | No | UTC | `null` | When notification was sent |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |

**Relationships**:
- Many-to-one with Task Instance
- Many-to-one with User

**Constraints**:
- Max 5 reminders per task
- Relative reminders recalculate when task due date changes
- Recovered tasks do NOT retroactively fire past reminders

---

### 7. Achievement Definition

**Purpose**: Static definition of achievable milestones and their rewards.

**Table Name**: `achievement_definitions` (seed data)

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `string` | Yes | Primary Key | - | Achievement code (e.g., `tasks_5`) |
| `name` | `string` | Yes | - | - | Display name |
| `description` | `string` | Yes | - | - | How to unlock |
| `category` | `enum` | Yes | `tasks`, `streaks`, `focus`, `notes` | - | Achievement category |
| `threshold` | `integer` | Yes | > 0 | - | Required count/value |
| `perk_type` | `enum` | No | `max_tasks`, `max_notes`, `daily_credits` | `null` | Perk granted |
| `perk_value` | `integer` | No | > 0 | `null` | Perk amount |

**Predefined Achievements**:

| ID | Name | Threshold | Perk |
|----|------|-----------|------|
| `tasks_5` | Task Starter | 5 tasks | +15 max tasks |
| `tasks_25` | Task Master | 25 tasks | +25 max tasks |
| `tasks_100` | Centurion | 100 tasks | +50 max tasks |
| `streak_7` | Week Warrior | 7-day streak | +2 daily AI credits |
| `streak_30` | Monthly Master | 30-day streak | +5 daily AI credits |
| `focus_10` | Focus Initiate | 10 focus completions | +5 max notes |
| `notes_10` | Note Taker | 10 note conversions | +5 max notes |

---

### 8. User Achievement State

**Purpose**: Current progress toward achievements and effective limits for a user.

**Table Name**: `user_achievement_states`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | State record ID |
| `user_id` | `UUID` | Yes | Foreign Key → users, Unique | - | User reference |
| `lifetime_tasks_completed` | `integer` | No | >= 0 | `0` | Total tasks ever completed |
| `current_streak` | `integer` | No | >= 0 | `0` | Current daily streak |
| `longest_streak` | `integer` | No | >= 0 | `0` | Best streak achieved |
| `last_completion_date` | `date` | No | UTC date | `null` | Last task completion day |
| `focus_completions` | `integer` | No | >= 0 | `0` | Tasks with 50%+ focus time |
| `notes_converted` | `integer` | No | >= 0 | `0` | Notes converted to tasks |
| `unlocked_achievements` | `json` | No | Array of achievement IDs | `[]` | Earned achievements |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last calculation |

**Relationships**:
- One-to-one with User

**Effective Limits Calculation**:
```
effective_max_tasks = base_limit + sum(task_perks)
effective_max_notes = base_limit + sum(note_perks)
effective_daily_credits = base_credits + sum(credit_perks)
```

---

### 9. AI Credit Ledger

**Purpose**: Transaction history for credit consumption with FIFO tracking.

**Table Name**: `ai_credit_ledger`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Transaction ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Credit owner |
| `credit_type` | `enum` | Yes | `kickstart`, `daily`, `subscription`, `purchased` | - | Credit source |
| `amount` | `integer` | Yes | Non-zero | - | Positive = credit, negative = debit |
| `balance_after` | `integer` | Yes | >= 0 | - | Running balance |
| `operation` | `enum` | Yes | `grant`, `consume`, `expire`, `carryover` | - | Transaction type |
| `operation_ref` | `string` | No | - | `null` | Reference (e.g., task ID, chat ID) |
| `expires_at` | `timestamp` | No | UTC | `null` | Expiration time (daily credits) |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Transaction time |

**Credit Consumption Order (FIFO)**:
1. Daily free credits (expire at UTC 00:00)
2. Subscription credits (carry over up to 50)
3. Purchased credits (never expire)

**Credit Costs**:
| Operation | Cost |
|-----------|------|
| AI Chat message | 1 credit |
| Subtask generation | 1 credit (flat) |
| Note-to-task conversion | 1 credit |
| Voice transcription | 5 credits/minute |

---

### 10. Subscription

**Purpose**: Payment and plan status for Pro tier management.

**Table Name**: `subscriptions`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Subscription ID |
| `user_id` | `UUID` | Yes | Foreign Key → users, Unique | - | Subscriber |
| `checkout_subscription_id` | `string` | Yes | Unique | - | Checkout.com subscription ID |
| `status` | `enum` | Yes | `active`, `past_due`, `grace`, `cancelled`, `expired` | - | Current status |
| `current_period_start` | `timestamp` | Yes | UTC | - | Billing period start |
| `current_period_end` | `timestamp` | Yes | UTC | - | Billing period end |
| `grace_period_end` | `timestamp` | No | UTC | `null` | Grace period expiration |
| `failed_payment_count` | `integer` | No | >= 0 | `0` | Consecutive failures |
| `cancelled_at` | `timestamp` | No | UTC | `null` | Cancellation timestamp |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Subscription start |
| `updated_at` | `timestamp` | Yes | UTC | Auto-updated | Last status change |

**Status Transitions**:
```
[active] → Payment succeeds monthly
    ↓ (payment fails)
[past_due] → 1-3 retry attempts
    ↓ (3 failures)
[grace] → 3-day grace period
    ↓ (grace expires without payment)
[expired] → Downgrade to free tier

[active] → User cancels
    ↓
[cancelled] → Access until period end, then expired
```

---

### 11. Activity Log

**Purpose**: Audit trail of user and system actions.

**Table Name**: `activity_logs`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Log entry ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | User context |
| `entity_type` | `enum` | Yes | `task`, `subtask`, `note`, `reminder`, etc. | - | Target entity type |
| `entity_id` | `UUID` | Yes | - | - | Target entity ID |
| `action` | `string` | Yes | - | - | Action performed |
| `source` | `enum` | Yes | `user`, `ai`, `system` | - | Who initiated |
| `metadata` | `json` | No | - | `{}` | Action-specific data |
| `request_id` | `UUID` | No | - | `null` | Request correlation ID |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Event timestamp |

**Retention**: 30 days rolling window (auto-purge older entries)

**Indexed Actions**:
- `task_created`, `task_updated`, `task_completed`, `task_deleted`, `task_recovered`
- `subtask_created`, `subtask_completed`
- `note_created`, `note_converted`
- `ai_chat`, `ai_subtask_generation`
- `subscription_created`, `subscription_renewed`, `subscription_cancelled`

---

### 12. Deletion Tombstone

**Purpose**: Serialized deleted entity for recovery.

**Table Name**: `deletion_tombstones`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Tombstone ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Data owner |
| `entity_type` | `enum` | Yes | `task`, `note` | - | Deleted entity type |
| `entity_id` | `UUID` | Yes | - | - | Original entity ID |
| `entity_data` | `json` | Yes | - | - | Serialized entity state |
| `deleted_at` | `timestamp` | Yes | UTC | Auto-generated | Deletion time |

**Constraints**:
- Max 3 tombstones per user (FIFO - oldest dropped on 4th deletion)
- Recovered tasks restore original ID and timestamps
- Recovered tasks do NOT trigger achievements or affect streaks

---

### 13. Notification

**Purpose**: In-app or push message for user alerts.

**Table Name**: `notifications`

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `UUID` | Yes | Primary Key | Server-generated | Notification ID |
| `user_id` | `UUID` | Yes | Foreign Key → users | - | Recipient |
| `type` | `enum` | Yes | `reminder`, `achievement`, `subscription`, `system` | - | Notification category |
| `title` | `string` | Yes | Max 100 chars | - | Notification title |
| `body` | `string` | Yes | Max 500 chars | - | Notification content |
| `action_url` | `string` | No | Valid URL path | `null` | Deep link target |
| `read` | `boolean` | No | - | `false` | Read status |
| `read_at` | `timestamp` | No | UTC | `null` | When read |
| `created_at` | `timestamp` | Yes | UTC | Auto-generated | Creation time |

**Relationships**:
- Many-to-one with User

---

## Entity Relationship Diagram

```
User (1) ──────── (many) Task Instance
  │                      │
  │                      ├──── (0-4/10) Subtask
  │                      │
  │                      └──── (0-5) Reminder
  │
  ├──────── (many) Task Template
  │                      │
  │                      └──── (many) Task Instance
  │
  ├──────── (many) Note
  │
  ├──────── (1) User Achievement State
  │
  ├──────── (many) AI Credit Ledger
  │
  ├──────── (0-1) Subscription
  │
  ├──────── (many) Activity Log
  │
  ├──────── (0-3) Deletion Tombstone
  │
  └──────── (many) Notification
```

---

## Tier-Based Limits

| Resource | Free Tier | Pro Tier |
|----------|-----------|----------|
| Max Tasks | 50 (+ achievements) | 200 (+ achievements) |
| Max Subtasks/Task | 4 | 10 |
| Task Description | 1000 chars | 2000 chars |
| Max Notes | 10 (+ achievements) | 25 (+ achievements) |
| Voice Recording | N/A | 300 seconds |
| Voice Transcription | N/A | Available |
| Kickstart AI Credits | 5 (one-time) | 5 (one-time) |
| Daily AI Credits | 0 | 10 (+ achievements) |
| Monthly AI Credits | 0 | 100 |
| Credit Carryover | N/A | Up to 50 |
| Credit Purchases | 500/month | 500/month |

---

## Data Integrity Rules

1. **No Orphaned Subtasks**: Subtask `task_id` must reference existing Task Instance
2. **Immutable Timestamps**: `created_at`, `completed_at`, `deleted_at` cannot be modified after set
3. **Cascading Deletes**: Deleting Task deletes all Subtasks and Reminders
4. **Version Conflicts**: Concurrent updates return 409 CONFLICT for stale versions
5. **Unique User Subscriptions**: One active subscription per user
6. **Credit Balance Integrity**: Balance can never go negative
7. **Streak Calculation**: Based on UTC calendar days only

---

## Pydantic/SQLModel Schema Pattern

```python
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskInstanceBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: datetime | None = None
    estimated_duration: int | None = Field(default=None, ge=1, le=720)

class TaskInstance(TaskInstanceBase, table=True):
    __tablename__ = "task_instances"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    # ... additional fields

class TaskInstanceCreate(TaskInstanceBase):
    pass

class TaskInstanceUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    # ... partial update fields
```

---

## Next Steps

Data model complete. Proceed to **API Specification** documentation.
