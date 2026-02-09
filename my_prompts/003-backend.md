# Perpetua Flow — Backend Feature Specification (Authoritative)

Version: 2.0
Status: Canonical Source of Truth
Stack: Python + FastAPI + PostgreSQL (Neon Serverless)
Time Authority: UTC only
Frontend Auth: BetterAuth (Google OAuth)
Payment: Checkout.com
AI: OpenAI Agents SDK + Deepgram NOVA2

---

## 1. Core Principles & Invariants

1. **Data must never be lost.** This is the highest invariant.
2. All timestamps are stored in UTC. Frontend handles localization.
3. Backend behavior must be deterministic, explicit, and auditable.
4. No implicit state transitions. All non-user-triggered changes emit events.
5. User intent always succeeds unless it violates a hard invariant.
6. Automation failure must not block user actions.
7. **AI failures must not corrupt user data.** AI operations are advisory until confirmed.

---

## 2. Authentication & Authorization

### 2.1 Auth Flow
- **Frontend**: BetterAuth handles Google OAuth login flow
- **Backend**: FastAPI issues and validates JWT tokens
- Social login provider: **Google only** (at launch)

### 2.2 Token Management
- Backend issues both **access** and **refresh** tokens
- Access token expiry: **15 minutes**
- Refresh token expiry: **7 days**
- Refresh tokens are rotated on use (one-time use)

### 2.3 Authorization Rules
- All resources are strictly user-scoped
- Cross-user access MUST return `403 FORBIDDEN`
- Missing or invalid auth returns `401 UNAUTHORIZED`
- Expired access token with valid refresh: return `401` with `refresh_required` flag

---

## 3. Data Models (Logical)

### 3.1 User
- id (UUID, PK)
- email (unique)
- name
- avatar_url
- google_id (unique, for OAuth linking)
- preferences (JSONB)
- timezone (string, informational only)
- subscription_tier (free | pro)
- subscription_status (active | cancelled | grace_period | expired)
- subscription_ends_at (UTC, nullable)
- created_at
- updated_at

---

### 3.2 Task Template (Recurring Root)
Represents the recurrence definition.

- id (UUID, PK)
- user_id (FK)
- title
- description
- priority (low | medium | high)
- estimated_duration_minutes
- recurrence_rule (RRULE string)
- recurrence_description
- is_active (boolean)
- created_at
- updated_at

---

### 3.3 Task Instance
Represents a concrete task occurrence.

- id (UUID, PK)
- user_id (FK)
- template_id (FK, nullable)
- title (max 200 characters)
- description (max 1000 chars free, 2000 chars pro)
- priority
- due_date (UTC)
- completed (boolean)
- completed_at (UTC, nullable)
- completed_by (manual | auto | force)
- hidden (boolean)
- archived (boolean)
- estimated_duration_minutes
- focus_time_seconds (integer, accumulated focus mode time)
- created_at
- updated_at
- version (integer, optimistic locking)

**Invariants**
- Past instances cannot have recurrence edited.
- Archived tasks cannot be completed.
- Hidden tasks are excluded from default queries.
- Auto-completed tasks are flagged explicitly.
- Max task duration: 30 days from creation.

**Force Completion Behavior**
- When a task is force-completed (manual completion with incomplete subtasks):
  - All subtasks are automatically marked as completed
  - `completed_by` is set to `force`
  - Emits `task.force_completed` event

---

### 3.4 Subtask

- id (UUID, PK)
- task_id (FK)
- title (max 75 characters)
- completed (boolean)
- estimated_duration_minutes
- order_index (integer)
- generated_by (user | ai)
- created_at
- updated_at

**Rules**
- Max subtasks per task: **4 (free)**, **10 (pro)**
- Ordering is client-driven but server-enforced as gapless.
- When the final subtask completes, parent task auto-completes.

---

### 3.5 Reminder

- id (UUID, PK)
- task_id (FK)
- type (before | after)
- offset_seconds
- method (push | in_app)
- scheduled_for (UTC)
- sent (boolean)
- failed (boolean)
- created_at

**Rules**
- Max 5 reminders per task.
- Relative reminders auto-recalculate on due date change.
- Absolute reminders remain unchanged.
- Reminders on recovered tasks MUST NOT retroactively fire.
- Supported methods: `push` (browser push notification), `in_app` (notification bell)
- Email/SMS NOT supported at launch.

---

### 3.6 Note

- id (UUID, PK)
- user_id (FK)
- content (max 2000 characters)
- voice_recording_url (nullable)
- voice_duration_seconds (nullable)
- created_at
- updated_at

**Limits**
- Max notes: **10 (free)**, **25 (pro)**

**Note → Task Conversion (via LLM)**
- LLM generates both title and structured description from note content
- Costs **1 AI credit**
- Backend receives: note_id + user confirmation
- Backend calls AI, returns suggested title + description
- User confirms → normal task creation request

---

### 3.7 Achievement Definition (Static)

| Achievement ID | Trigger | Perk |
|----------------|---------|------|
| `streak_3` | 3-day login streak | +1 daily free AI credit |
| `streak_7` | 7-day login streak | +2 daily free AI credits |
| `streak_15` | 15-day login streak | +3 daily free AI credits |
| `streak_30` | 30-day login streak | +4 daily free AI credits |
| `tasks_5` | 5 tasks completed (lifetime) | +15 max tasks |
| `tasks_10` | 10 tasks completed (lifetime) | +20 max tasks |
| `tasks_25` | 25 tasks completed (lifetime) | +25 max tasks |
| `tasks_50` | 50 tasks completed (lifetime) | +25 max tasks |
| `focus_3` | 3 tasks completed in focus mode | +2 subtasks per task |
| `focus_10` | 10 tasks completed in focus mode | +4 subtasks per task |
| `notes_convert_5` | 5 notes converted to tasks | +5 max notes |
| `notes_convert_10` | 10 notes converted to tasks | +5 max notes |
| `notes_convert_15` | 15 notes converted to tasks | +5 max notes |
| `voice_5min` | 5 minutes in voice mode | Badge only |
| `voice_15min` | 15 minutes in voice mode | Badge only |
| `voice_25min` | 25 minutes in voice mode | Badge only |

**Achievement Rules**
- Task completion achievements use **cumulative lifetime** count
- **Perks are permanent once earned** — streak breaks do NOT revoke earned perks
- Focus mode completion: task must have ≥50% of estimated_duration spent in focus mode
- Pro users get achievement perks instantly (no badge)

---

### 3.8 User Achievement State

- user_id (PK)
- current_streak (integer)
- longest_streak (integer)
- total_tasks_completed (integer)
- total_focus_tasks_completed (integer)
- total_notes_converted (integer)
- total_voice_minutes (integer)
- unlocked_achievements (JSONB array of achievement IDs)
- effective_limits (JSONB, computed from base + perks)
- updated_at

**Effective Limits Computation**
```
max_tasks = base_limit + sum(task_achievement_perks)
max_subtasks = base_limit + sum(focus_achievement_perks)
max_notes = base_limit + sum(note_achievement_perks)
daily_ai_credits = base_limit + sum(streak_achievement_perks)
```

---

### 3.9 Activity Log

- id (UUID, PK)
- user_id (FK)
- type (string)
- source (user | ai | system)
- entity_type (task | note | subtask | etc)
- entity_id (UUID)
- metadata (JSONB)
- created_at

**Log Types**
- `task.created`, `task.updated`, `task.completed`, `task.deleted`
- `subtask.created`, `subtask.completed`
- `note.created`, `note.converted`
- `ai.chat_message`, `ai.subtask_generated`, `ai.note_converted`
- `achievement.unlocked`
- `subscription.changed`

Retention: **30 days**, rolling window.

---

### 3.10 Deletion Tombstone

- id (UUID, PK)
- user_id
- entity_type
- entity_id
- serialized_payload (JSONB)
- deleted_at

Only **3 most recent deletions** per user are recoverable.

---

### 3.11 AI Credit Ledger

- id (UUID, PK)
- user_id (FK)
- credit_type (daily_free | subscription | purchased | kickstart)
- amount (integer, positive for credit, negative for debit)
- balance_after (integer)
- reason (string: chat_message | voice_transcription | subtask_gen | note_convert)
- metadata (JSONB)
- expires_at (UTC, nullable — for daily credits)
- created_at

**Credit Consumption Order (FIFO)**
1. Daily free credits (expire at UTC 00:00)
2. Subscription credits (carry over up to 50)
3. Purchased credits (no expiry)

---

### 3.12 Subscription

- id (UUID, PK)
- user_id (FK)
- checkout_customer_id (string)
- checkout_subscription_id (string)
- plan (pro)
- status (active | cancelled | past_due | grace_period)
- current_period_start (UTC)
- current_period_end (UTC)
- grace_period_ends_at (UTC, nullable)
- cancelled_at (UTC, nullable)
- created_at
- updated_at

---

### 3.13 Credit Purchase

- id (UUID, PK)
- user_id (FK)
- checkout_payment_id (string)
- amount_cents (integer)
- credits_granted (integer)
- status (pending | completed | failed | refunded)
- created_at

**Credit Packages**
| Price | Credits |
|-------|---------|
| $5 | 20 |
| $10 | 45 |
| $15 | 70 |
| $20 | 100 |

**Purchase Limits**
- Max **500 credits purchased per month**
- Tracked via rolling 30-day window

---

### 3.14 Notification

- id (UUID, PK)
- user_id (FK)
- type (achievement | reminder | task_completed | system)
- title (string)
- body (string)
- read (boolean)
- action_url (string, nullable)
- created_at

**Delivery Methods**
- **In-app**: Notification bell with unread count
- **Push**: Browser push notifications (requires user permission)
- Email NOT supported at launch

---

## 4. Task Lifecycle Rules

### 4.1 Completion

- **Manual completion**:
  - Sets `completed = true`
  - Sets `completed_at = server time`
  - Emits `task.completed`

- **Auto completion**:
  - Triggered when all subtasks complete
  - Emits `task.auto_completed`
  - Counts fully toward streaks and achievements

- **Force completion** (new):
  - User completes task with incomplete subtasks
  - All subtasks auto-marked complete
  - Sets `completed_by = force`
  - Emits `task.force_completed`

### 4.2 Focus Mode Tracking

- Frontend reports focus session start/end with task_id
- Backend accumulates `focus_time_seconds` on task
- Focus mode completion threshold: **≥50% of estimated_duration_minutes**
- Tasks meeting threshold count toward focus achievements

---

### 4.3 Recurring Tasks

- Templates define recurrence.
- Instances are generated on completion.
- Editing recurrence:
  - Prompt-based choice:
    - Apply to future instances (default)
    - Apply to template only
- Failure to generate next instance:
  - Does NOT roll back completion
  - Logs error
  - Retries asynchronously

---

## 5. Streak Logic

- Streaks are computed by UTC calendar day.
- A day counts if ≥1 task completed (manual, auto, or force).
- Missing a UTC day breaks the streak.
- Streaks are stored snapshots with recomputation fallback.
- **Streak break does NOT revoke earned achievement perks.**

---

## 6. Deletion & Recovery

### 6.1 Soft Deletion
- `hidden = true`
- Excluded from default queries
- No effect on streaks

### 6.2 Hard Deletion
- Row removed
- Tombstone created
- Eligible for recovery if within last 3 deletions

### 6.3 Recovery Rules
- Restores original ID and timestamps
- Restored tasks:
  - Do NOT trigger reminders
  - Do NOT re-trigger achievements
  - Do NOT retroactively affect streaks

---

## 7. AI Integration

### 7.1 OpenAI Agents SDK

All AI processing happens **server-side** for:
- Security (API key protection)
- Credit enforcement
- Audit logging

### 7.2 AI Chat Widget

- Available to **all users** (free and pro)
- Costs **1 credit per message**
- **Can perform direct actions** with user confirmation:
  - Create tasks
  - Edit tasks
  - Create notes
  - Complete tasks
- Actions require explicit user confirmation before execution
- Chat context includes user's recent tasks/notes for relevance

**Rate Limits**
- 5 AI requests per task: warn user
- 10 AI requests per task: block further requests

### 7.3 Auto Subtask Generation

- Triggered: user requests subtask generation for a task
- Input: task title + description
- Output: up to user's subtask limit (4 free, 10 pro)
- Cost: **1 credit** (flat, regardless of subtask count)
- Respects user's current subtask limit — does NOT generate extras

### 7.4 Voice-to-Text (Deepgram NOVA2)

- **Pro users only**
- Two modes:
  - **Streaming**: Real-time transcription for chat widget
  - **Post-recording**: Batch processing for note creation
- Cost: **5 credits per minute** (rounded up)
- Max recording duration: **300 seconds** (5 minutes)

### 7.5 Note-to-Task Conversion

- LLM analyzes note content
- Generates: suggested title + structured description
- Cost: **1 credit**
- User must confirm before task creation

---

## 8. AI Credit System

### 8.1 Credit Types

| Type | Source | Expiry | Carryover |
|------|--------|--------|-----------|
| Kickstart | New account | Never | N/A |
| Daily Free | Daily reset | UTC 00:00 | None |
| Subscription | Monthly (Pro) | End of period | Up to 50 |
| Purchased | One-time buy | Never | Unlimited |

### 8.2 Free Tier Credits

- **Kickstart**: 5 credits (one-time, new accounts)
- **Daily free**: 0 base + achievement bonuses
- Daily credits expire at **UTC 00:00** (non-accumulative)

### 8.3 Pro Tier Credits

- **Monthly subscription**: 100 credits
- **Daily free**: 10 base + achievement bonuses
- **Carryover**: Up to 50 unused subscription credits
  - Example: 60 unused → 50 carried + 100 new = 150 total
  - Excess (10 in example) is lost

### 8.4 Credit Costs

| Action | Cost |
|--------|------|
| Chat message | 1 |
| Subtask generation | 1 |
| Note-to-task conversion | 1 |
| Voice transcription | 5/minute |

### 8.5 Credit Consumption Order

1. Daily free credits (use first, expire soonest)
2. Subscription credits (monthly allocation)
3. Purchased credits (permanent)

---

## 9. Payment Integration (Checkout.com)

### 9.1 Subscription Management

- **Plan**: Pro ($5/month recurring)
- **Cancellation**: User can cancel anytime
  - Access continues until end of billing period
  - No refunds
  - Status changes to `cancelled`
- **Downgrade**: Automatic at period end if cancelled

### 9.2 Payment Failure Handling

- Initial failure: status → `past_due`
- Retry attempts: 3 over 3 days
- After 3 days without successful payment: status → `grace_period`
- **Grace period**: 3 days
  - User retains Pro features
  - Prominent UI warning to update payment
- After grace period expires: status → `expired`, downgrade to free

### 9.3 Credit Purchases

- One-time purchases via Checkout.com
- Credits added immediately on successful payment
- Monthly purchase limit: **500 credits**
- Failed payments: no credits granted, user notified

### 9.4 Webhook Events

Backend handles:
- `subscription.created`
- `subscription.updated`
- `subscription.cancelled`
- `payment.successful`
- `payment.failed`
- `refund.created`

---

## 10. Notifications

### 10.1 Notification Types

| Type | Trigger | Delivery |
|------|---------|----------|
| Achievement | Achievement unlocked | In-app + Push |
| Reminder | Scheduled reminder time | In-app + Push |
| Task completed | Task marked done | In-app only |
| Subscription | Payment events | In-app + Push |

### 10.2 Push Notifications

- Requires user permission (browser Notification API)
- Backend stores push subscription endpoint
- Uses web-push protocol
- Falls back to in-app if push unavailable

### 10.3 Notification Page

- Dedicated `/notifications` page
- Shows all notifications (paginated, 25 per page)
- Mark as read (individual/all)
- Filter by type

---

## 11. API Behavior Guarantees

### 11.1 PATCH Semantics
- Omitted fields: unchanged
- `null`: explicit clear
- Invalid transitions return `409 CONFLICT`

### 11.2 Concurrency
- Optimistic locking via `version`
- Stale updates return `409 CONFLICT`

### 11.3 Idempotency
- Required for POST and PATCH
- Duplicate keys return original response

### 11.4 Pagination
- Offset-based pagination
- Default limit: **25 items**
- Max limit: **100 items**
- Documented as unstable under concurrent writes
- Cursor pagination reserved for future version

### 11.5 Consistency
- Strong consistency for direct reads
- Eventual consistency for aggregates (streaks, achievements, credits)

---

## 12. Rate Limiting

- Enforced server-side regardless of frontend blocking
- Violations return `429 TOO MANY REQUESTS`
- No queuing or degradation

**Limits**
- General API: 100 requests/minute
- AI endpoints: 20 requests/minute
- Auth endpoints: 10 requests/minute

---

## 13. Error Handling

### 13.1 Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "requestId": "uuid"
  }
}
```

### 13.2 AI-Specific Errors

| Code | Meaning |
|------|---------|
| `INSUFFICIENT_CREDITS` | User has no AI credits |
| `CREDIT_LIMIT_REACHED` | Per-task AI limit (10) exceeded |
| `VOICE_PRO_ONLY` | Voice feature requires Pro |
| `AI_SERVICE_UNAVAILABLE` | OpenAI/Deepgram down |

### 13.3 Payment Errors

| Code | Meaning |
|------|---------|
| `PAYMENT_FAILED` | Checkout.com payment declined |
| `SUBSCRIPTION_REQUIRED` | Pro feature accessed by free user |
| `PURCHASE_LIMIT_EXCEEDED` | Monthly 500 credit limit hit |

### 13.4 Internal Errors

- Client receives generic message + requestId
- Stack traces logged internally only

---

## 14. Events (Internal)

- task.created
- task.updated
- task.completed
- task.auto_completed
- task.force_completed
- task.deleted
- subtask.completed
- reminder.sent
- reminder.failed
- streak.updated
- achievement.unlocked
- ai.request
- ai.credits_consumed
- subscription.created
- subscription.cancelled
- subscription.expired
- payment.successful
- payment.failed
- notification.created
- notification.push_sent

Events are best-effort ordered, eventually consistent.

---

## 15. Explicitly Forbidden States

The backend MUST reject:
- Completing archived tasks
- Adding reminders to completed tasks
- Editing recurrence on past instances
- Restored tasks affecting streaks
- Restored reminders firing retroactively
- Silent auto state transitions without events
- AI actions without sufficient credits
- Voice features for free-tier users
- Credit purchases exceeding monthly limit
- Subscription actions without valid Checkout.com webhook signature

---

## 16. Data Repair

- Automated repair jobs allowed
- Manual admin repair allowed
- Repairs must be logged and auditable
- Credit balance reconciliation runs daily

---

## 17. Versioning Policy

- Core behavior changes require new API version
- No silent breaking changes
- Feature flags allowed only for non-core features

---

## 18. Frontend Integration Notes

### 18.1 Mobile Sidebar Bug Fix
- Sidebar must be hidden on mobile screens
- Implement as swipe-to-open drawer (swipe right)
- Desktop: always visible
- Breakpoint: 768px

### 18.2 Task List Pagination
- Render limit: **25 tasks**
- Load more on scroll (infinite scroll)
- Maintain scroll position on refresh

### 18.3 Dummy Data Removal
- All mock/dummy data must be removed before production
- Backend is source of truth for all data

---

## 19. Final Authority Clause

This document supersedes:
- README implications
- Frontend assumptions
- Developer intuition

If behavior is not specified here, it is not allowed.
