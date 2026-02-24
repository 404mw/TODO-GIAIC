# Perpetua Flow Backend Specification

**Version**: 1.5 (Revised — REMEDIATIONS-003-v7.md applied: R9 stuck-pending FR-012 behavior documented)
**Date**: 2026-02-24
**Source**: `/backend` codebase
**Type**: FastAPI + SQLModel/SQLAlchemy async backend

---

## Problem Statement

Modern knowledge workers struggle with task management systems that:
- Lack intelligent assistance for breaking down complex tasks
- Don't provide meaningful progress tracking and motivation
- Fail to integrate natural input methods (voice, AI chat)
- Impose rigid structures without flexibility
- Don't reward consistent usage or achievement

**Perpetua Flow** solves this by providing an AI-enhanced task management backend that combines:
- Intelligent task breakdown and organization
- Gamified achievement system with tangible benefits
- Voice-to-text transcription for natural task capture
- Flexible credit system balancing free and premium features
- Comprehensive recovery and audit capabilities

---

## System Intent

### Target Users

1. **Individual Productivity Enthusiasts** (Primary)
   - Need personal task management with AI assistance
   - Want gamification to maintain motivation
   - Value both free tier for basic usage and pro tier for advanced features

2. **Teams** (Secondary/Future)
   - Shared task spaces (out of scope in current implementation)
   - Collaboration features (planned but not implemented)

### Core Value Proposition

**"AI-powered task management that learns from you, rewards your progress, and adapts to your workflow"**

### Key Capabilities

1. **Intelligent Task Management**
   - Create, organize, prioritize tasks with subtasks
   - AI-powered subtask generation (breaks complex tasks into steps)
   - Task templates for recurring workflows
   - Focus mode with time tracking
   - Smart reminders (absolute + relative to due date)

2. **AI-Enhanced Productivity**
   - Conversational AI assistant for task guidance
   - Contextual responses based on user's current tasks
   - Voice transcription to text (Deepgram NOVA2)
   - Suggested actions with user confirmation required

3. **Gamification & Motivation**
   - Achievement system with milestone unlocks
   - Streak tracking for daily consistency
   - Perk system that increases user limits (tasks, notes, credits)
   - Visual progress indicators

4. **Flexible Monetization**
   - Credit-based AI usage (daily free + subscription + purchased)
   - Tier system (Free/Pro) with clear feature boundaries
   - Achievement unlocks that expand free tier capabilities

5. **Data Safety & Recovery**
   - 7-day recovery window for deleted tasks
   - Activity log for audit trail
   - Optimistic locking to prevent data loss from concurrent edits
   - Idempotency for safe retries

---

## Functional Requirements

### FR-001: Authentication & Authorization

**What**: Secure user authentication via Google OAuth with JWT token management

**Why**: Users need secure, passwordless authentication with session management

**Inputs**:
- Google ID token (from frontend BetterAuth flow)
- Refresh token for token renewal

**Outputs**:
- Access token (JWT, RS256, 15-minute expiry)
- Refresh token (opaque, 7-day expiry, single-use rotation)
- User profile data

**Side Effects**:
- User record created/updated in database
- Refresh token stored with revocation capability
- Session tracking for multi-device support

**Success Criteria**:
- ✅ Google token verification succeeds
- ✅ Access token contains user ID, email, tier, session ID
- ✅ Refresh token rotation prevents token reuse
- ✅ JWKS endpoint exposes public keys for frontend verification
- ✅ Token expiration triggers 401 with TOKEN_EXPIRED code

**Evidence**:
- [src/api/auth.py](../src/api/auth.py) - Auth endpoints
- [src/services/auth_service.py](../src/services/auth_service.py) - Token generation
- [src/middleware/auth.py](../src/middleware/auth.py) - JWT validation middleware

---

### FR-002: Task CRUD Operations

**What**: Create, read, update, delete tasks with tier-based limits

**Why**: Core functionality for task management

**Inputs**:
- `title`: string (1-200 chars, required)
- `description`: string (max 1000 free / 2000 pro)
- `priority`: enum ("low", "medium", "high")
- `due_date`: datetime (optional, max 30 days from the API request timestamp)
- `estimated_duration`: int (minutes, 1-720)
- `version`: int (for optimistic locking on updates)

**Outputs**:
- Task object with computed fields:
  - `subtask_count`: int
  - `subtask_completed_count`: int
  - `focus_time_seconds`: int (accumulated)
  - `completed`: bool
  - `completed_at`: datetime | null
  - `completed_by`: enum ("manual", "auto", "force")

**Force-Complete Response** (`POST /api/v1/tasks/{task_id}/force-complete`):
Returns `TaskCompletionResponse` (not the plain task object) with:
- `task`: TaskResponse (the completed task with all fields above)
- `unlocked_achievements`: list[AchievementSummary] (newly unlocked achievements triggered by this completion; may be empty)

**Side Effects**:
- Task limit checked (Free: 50 base + achievement perks, Pro: unlimited)
- Activity log entry created
- Metrics recorded (Prometheus)
- Due date validation (max 30 days)

**Success Criteria**:
- ✅ Task created with unique ID
- ✅ Version incremented on each update
- ✅ 409 CONFLICT on stale version
- ✅ 409 LIMIT_EXCEEDED when tier limit reached
- ✅ 400 due date validation error if > 30 days

**Evidence**:
- [src/api/tasks.py](../src/api/tasks.py) - Task endpoints
- [src/services/task_service.py](../src/services/task_service.py) - Business logic
- [src/models/task.py](../src/models/task.py) - Task model with validation

---

### FR-003: Subtask Management

**What**: Create and manage subtasks under parent tasks

**Why**: Break complex tasks into manageable steps

**Inputs**:
- `task_id`: UUID (parent task)
- `title`: string (1-200 chars)
- `source`: enum ("manual", "ai") - tracks how subtask was created

**Outputs**:
- Subtask object with `order_index` for sequencing
- Parent task's `subtask_count` and `subtask_completed_count` updated

**Side Effects**:
- Subtask limit checked (Free: 10 base + perks, Pro: 20 base + perks)
- Parent task auto-completed when all subtasks completed (if `CompletedBy.AUTO`)
- Order index automatically assigned

**Success Criteria**:
- ✅ Subtasks ordered by `order_index`
- ✅ 409 SUBTASK_LIMIT_EXCEEDED when limit reached
- ✅ Parent task auto-completes when last subtask completed
- ✅ Reordering supported via order_index updates

**Evidence**:
- [src/api/subtasks.py](../src/api/subtasks.py) - Subtask endpoints
- [src/models/subtask.py](../src/models/subtask.py) - Subtask model
- Auto-completion logic in [task_service.py:_check_task_completion](../src/services/task_service.py)

---

### FR-004: AI Chat Assistant

**What**: Conversational AI that provides task guidance with context awareness

**Why**: Users need intelligent help understanding priorities and next actions

**Inputs**:
- `message`: string (user's question/request)
- `context`: object
  - `include_tasks`: bool (include user's tasks in context)
  - `task_limit`: int (how many recent tasks to include)
- `X-Task-Id` header (optional): UUID for task-specific context

**Outputs**:
- `response`: string (AI assistant's reply)
- `suggested_actions`: array of action objects:
  - `type`: enum ("complete_task", "create_subtasks", "update_task")
  - `task_id`: UUID
  - `description`: string (what the action does)
  - `data`: object (action-specific parameters)
- `credits_used`: int (always 1 for chat)
- `credits_remaining`: int
- `ai_request_warning`: bool (true if nearing session limit)

**Streaming Variant** (`POST /api/v1/ai/chat/stream`):
- Same inputs/credits as standard chat
- Response: Server-Sent Events (SSE) stream
- `Content-Type: text/event-stream`
- Chunk events: `event: chunk` with `data: {"text": "<token>"}` — one event per token
- Final event: `event: final` with `data: {"suggested_actions": [...], "credits_used": 1,
  "credits_remaining": N, "ai_request_warning": bool}` — emitted after the last chunk
- Requires Idempotency-Key; same 1-credit cost as non-streaming chat
- **Credit deduction on failure**: Credit is deducted once when the first chunk is
  sent. If the connection drops before any chunks are delivered (e.g., server crash
  after deduction), the credit is **not refunded** — consistent with the AI undo
  out-of-scope policy (Gap 5). On client retry with the same Idempotency-Key, the
  cached 1-credit response is returned; no second deduction occurs.

**Confirm Action Endpoint** (`POST /api/v1/ai/confirm-action`):
- Executes a previously suggested AI action (from chat or subtask generation)
- **Inputs**:
  - `action_type`: enum ("complete_task", "create_subtasks", "update_task")
  - `task_id`: UUID
  - `data`: object (action-specific parameters, mirrors the `data` field from suggested_actions)
  - `Idempotency-Key` header: required
- **Outputs**:
  - `result`: object (updated task, created subtasks, or updated fields — depends on action_type)
  - `action_id`: UUID (transient UUID generated per confirm call; **not persisted**; intended for
    client-side correlation only — undo for AI-confirmed mutations is intentionally out of scope,
    see Gap 5). No server-side API accepts `action_id` as input — it is not an idempotency key
    and carries no server-side state.
- **Error Codes**:
  - 400 VALIDATION_ERROR — invalid action_type or missing required data fields
  - 402 INSUFFICIENT_CREDITS — insufficient credits for subtask creation actions
  - 404 TASK_NOT_FOUND — task_id does not exist
  - 409 CONFLICT — task was mutated since suggestion was generated (stale)
  - 429 AI_TASK_LIMIT_REACHED — AI request limit exceeded for this task+session
- **Side Effects**: Executes the mutation; logs to activity log with `actor="ai"`, `task_id`,
  `timestamp`, `credits_used`, `action_type` (Constitution V.2). No `confirmed_ai_actions` table
  exists — undo for AI-confirmed mutations is intentionally excluded (see Gap 5).

**Side Effects**:
- 1 credit deducted from user balance
- AI request counter incremented (per-task per-session, limit configurable via `.env`)
- Idempotency key required (strictly enforced)
- OpenAI API call made

**Configuration** (all limits must be in `.env` / `config.py` — no hardcoded values):
- `AI_TASK_BLOCK_THRESHOLD` (default: 10) — max AI requests per task per session
- `AI_TASK_WARNING_THRESHOLD` (default: 5) — threshold for `ai_request_warning=true`

**Success Criteria**:
- ✅ Context includes user's incomplete tasks when requested
- ✅ Suggested actions require explicit user confirmation before execution
- ✅ 402 INSUFFICIENT_CREDITS if balance is zero
- ✅ 429 AI_TASK_LIMIT_REACHED after N requests per task per session (N = AI_TASK_BLOCK_THRESHOLD)
- ✅ 503 AI_SERVICE_UNAVAILABLE on OpenAI failure
- ✅ AI_TASK_BLOCK_THRESHOLD configurable via `.env`; no hardcoded limit in service code
- ✅ Confirmed action logged with `actor="ai"`, `task_id`, `timestamp` (Constitution V.2)

**Evidence**:
- [src/api/ai.py](../src/api/ai.py) - AI endpoints
- [src/services/ai_service.py](../src/services/ai_service.py) - OpenAI integration
- [src/schemas/ai.py](../src/schemas/ai.py) - AI request/response schemas

---

### FR-005: AI Subtask Generation

**What**: AI generates subtask suggestions for a given task

**Why**: Help users break down complex tasks without manual effort

**Inputs**:
- `task_id`: UUID

**Outputs**:
- `suggested_subtasks`: array of subtask suggestions
  - `title`: string (subtask name)
- `credits_used`: int (1 credit)
- `credits_remaining`: int

**Tier Limits**:
- **Free tier**: max 4 subtasks suggested (configurable via `FREE_MAX_SUBTASKS` in `.env`)
- **Pro tier**: max 10 subtasks suggested (configurable via `PRO_MAX_SUBTASKS` in `.env`)

**Side Effects**:
- 1 credit deducted
- Subtasks NOT auto-created (user must confirm via separate endpoint)
- Idempotency key required

**Success Criteria**:
- ✅ Suggestions tailored to task title/description
- ✅ Tier limit respected (FREE_MAX_SUBTASKS vs PRO_MAX_SUBTASKS)
- ✅ 404 TASK_NOT_FOUND if task doesn't exist
- ✅ Suggestions are actionable and distinct
- ✅ Tier limits configurable via `.env`; no hardcoded values in service code

**Evidence**:
- [src/api/ai.py:generate_subtasks](../src/api/ai.py)
- [src/services/ai_service.py:generate_subtasks](../src/services/ai_service.py)

---

### FR-006: Voice Transcription (Pro Only)

**What**: Transcribe audio recordings to text using Deepgram NOVA2

**Why**: Natural task capture via voice input

**Inputs**:
- `audio_url`: string (publicly accessible audio file URL)
- `duration_seconds`: int (max configurable via `.env`, default 300 = 5 minutes)

**Outputs**:
- `transcription`: string (transcribed text)
- `language`: string (detected language code, e.g., "en")
- `confidence`: float (0-1, transcription confidence score)
- `credits_used`: int (5 credits per minute, rounded up)
- `credits_remaining`: int

**Credit Calculation**:
- 45 seconds → 1 minute → 5 credits
- 90 seconds → 2 minutes → 10 credits
- 300 seconds → 5 minutes → 25 credits

**Configuration** (all limits in `.env` / `config.py`):
- `MAX_AUDIO_DURATION_SECONDS` (default: 300) — max permitted audio duration

**Side Effects**:
- Credits deducted (5 per minute)
- Deepgram API call made
- Idempotency key required

**Success Criteria**:
- ✅ 403 PRO_TIER_REQUIRED for free users
- ✅ 400 AUDIO_DURATION_EXCEEDED if duration_seconds > MAX_AUDIO_DURATION_SECONDS
- ✅ 402 INSUFFICIENT_CREDITS if not enough credits
- ✅ Transcription confidence p50 > 0.85 (measured over Deepgram NOVA2 en-US audio)
- ✅ MAX_AUDIO_DURATION_SECONDS configurable via `.env`; no hardcoded value in service code

**Evidence**:
- [src/api/ai.py:transcribe_voice](../src/api/ai.py)
- [src/integrations/deepgram_client.py](../src/integrations/deepgram_client.py)

---

### FR-007: Credit System

**What**: Multi-tier credit system for AI usage

**Why**: Monetization and fair resource allocation

**Credit Types**:

1. **Daily Free Credits**
   - Amount: 10 base + achievement perks
   - Reset: UTC midnight daily
   - Expiration: End of day
   - Priority: Used first

2. **Subscription Credits** (Pro tier)
   - Amount: 50/month base + achievement perks
   - Carryover: Up to 50 credits to next month
   - Expiration: Never (within carryover limit)
   - Priority: Used second
   - **Downgrade behavior** (Pro → Free): Existing subscription credit balance is retained
     and consumed normally at normal deduction priority (second after daily). No new
     subscription credits are granted after downgrade. When the balance reaches zero,
     no replenishment occurs.

3. **Purchased Credits**
   - Amount: Variable (one-time purchase)
   - Expiration: Never
   - Priority: Used third

4. **Kickstart Credits**
   - Amount: 5 (one-time on account creation — granted on first successful login)
   - Expiration: Never
   - Priority: Used last

**Deduction Order**: Daily → Subscription → Purchased → Kickstart

**Monthly Subscription Renewal**:
- At end of billing period, subscription credit balance is read
- Carryover: min(current_sub_balance, 50) credits roll to next period
- Fresh 50 credits added for new period
- Background job / scheduled task required

**Credit API Endpoints**:
- `GET /api/v1/credits/balance` — full balance breakdown (daily, subscription, purchased, kickstart, total)
- `GET /api/v1/credits/history` — paginated transaction history
- `GET /api/v1/ai/credits` — alias for `GET /api/v1/credits/balance`; same data, different route for AI endpoint cohesion; MUST share the same service method with no duplicate logic. Route ownership: Task 4.7 (CreditService); Task 4.6 registers the alias only.

**Error Code Note**: See FR-012 Error Codes for the intentional 402/409 split between
note and task limit-exceeded responses.

**Success Criteria**:
- ✅ Daily credits reset at UTC midnight
- ⏸ Subscription credits carry over (max 50) at period-end renewal — **pending Task 4.2a**
- ✅ 5 kickstart credits granted automatically on first user login
- ✅ Credit history tracks all transactions
- ✅ Balance breakdown shows each type separately

**Evidence**:
- [src/services/credit_service.py](../src/services/credit_service.py)
- [src/models/credit.py](../src/models/credit.py)
- [src/api/credits.py](../src/api/credits.py)

---

### FR-008: Achievement System

**What**: Gamified achievement system that unlocks perks

**Why**: Motivate consistent usage and reward milestones

**Achievement Categories**:

1. **Tasks** (lifetime tasks completed)
   - `tasks_5`: +15 max tasks
   - `tasks_25`: +25 max tasks
   - `tasks_50`: +50 max tasks
   - `tasks_100`: +100 max tasks
   - `tasks_500`: +200 max tasks

2. **Streaks** (consecutive days with completed tasks)
   - `streak_7`: +3 daily AI credits
   - `streak_30`: +5 daily AI credits
   - `streak_100`: +10 daily AI credits

3. **Focus** (tasks completed via focus mode)
   - `focus_10`: +5 max tasks
   - `focus_50`: +10 max tasks

4. **Notes** (`notes_converted` stat — incremented on each successful `POST /notes/{id}/convert`
   call, at suggestion-return time, regardless of whether the user subsequently creates a task)
   - `notes_10`: +10 max notes (threshold: 10 convert calls)

**Perk Types**:
- `max_tasks`: Increases task limit
- `max_notes`: Increases note limit
- `daily_ai_credits`: Increases daily free credits
- `max_subtasks`: Increases subtask limit per task

**Side Effects**:
- Achievements checked on task completion
- Newly unlocked achievements returned in response
- Effective limits recalculated on achievement unlock

**Success Criteria**:
- ✅ Achievements unlock automatically at thresholds
- ✅ Perks stack cumulatively
- ✅ Achievement data includes: stats, unlocked, progress, effective_limits
- ✅ Free tier users can unlock perks to approach pro tier limits

**Evidence**:
- [src/services/achievement_service.py](../src/services/achievement_service.py)
- [src/models/achievement.py](../src/models/achievement.py)
- [src/api/achievements.py](../src/api/achievements.py)

---

### FR-009: Focus Mode

**What**: Timer-based focus sessions that track time spent on tasks

**Why**: Pomodoro-style focus with automatic time accumulation

**Inputs**:
- `task_id`: UUID
- `focus_duration`: int (minutes, optional target duration; range: 1–`FOCUS_SESSION_TIMEOUT_MINUTES`
  if provided; stored as a user-set goal only — does not trigger auto-stop. Auto-stop is
  controlled exclusively by `FOCUS_SESSION_TIMEOUT_MINUTES` from `.env`.)

**Configuration** (all limits in `.env` / `config.py`):
- `FOCUS_SESSION_TIMEOUT_MINUTES` (default: 90) — maximum duration of a focus
  session before it auto-stops. Sessions stopped automatically at this limit
  have their elapsed time recorded as if manually stopped.

**Outputs**:
- `session_id`: UUID
- `started_at`: datetime
- `task`: object (task being focused on)

**Side Effects**:
- Focus session created
- Task's `focus_time_seconds` updated on session end
- Achievement `focus_completions` incremented if task completed during focus

**Success Criteria**:
- ✅ Only one active focus session per user
- ✅ Session can be stopped manually
- ⏸ Session times out automatically at `FOCUS_SESSION_TIMEOUT_MINUTES` — **pending Task 5.5** (sessions currently run indefinitely until stopped manually)
- ⏸ `FOCUS_SESSION_TIMEOUT_MINUTES` configurable via `.env`; no hardcoded value in service code — **pending Task 5.5**
- ✅ Focus time accumulated even if task not completed
- ✅ Focus-based achievements unlock

**Evidence**:
- [src/api/focus.py](../src/api/focus.py)
- [src/services/focus_service.py](../src/services/focus_service.py)
- [src/models/focus.py](../src/models/focus.py)

---

### FR-010: Task Templates

**What**: Reusable task templates for recurring workflows

**Why**: Save time recreating similar tasks

**Inputs**:
- Template creation: same fields as task + `is_template` flag
- Instantiation: `template_id` + optional field overrides

**Outputs**:
- New task instance from template
- Template link preserved in `template_id` field

**Limits**:
- **Template count**: No limit — templates are lightweight metadata and do not consume the task quota.
  This is an intentional design decision. Users may create as many templates as desired.

**Side Effects**:
- Template can include default subtasks
- Template doesn't count toward task limits
- Instantiated tasks count toward limits

**Success Criteria**:
- ✅ Templates are reusable
- ✅ No template count limit enforced
- ✅ Subtasks from template also instantiated
- ✅ Instantiated tasks are independent (not linked after creation)

**Evidence**:
- [src/api/templates.py](../src/api/templates.py)
- [src/models/task.py](../src/models/task.py) - `template_id` field

---

### FR-011: Reminders

**What**: Time-based reminders for tasks

**Why**: Ensure tasks don't get forgotten

**Reminder Types**:

1. **Absolute**
   - `scheduled_at`: datetime (exact time)
   - Use case: "Remind me at 3pm tomorrow"

2. **Relative**
   - `offset_minutes`: int (minutes before due date)
   - Use case: "Remind me 30 minutes before due"

**Delivery Methods**:
- `push`: Push notification
- `email`: Email notification (future)

**Side Effects**:
- Reminder marked as `fired` after delivery
- Multiple reminders per task supported
- Background job processes reminders

**Success Criteria**:
- ⏸ Reminders stored and queryable; delivery not implemented (out of scope — see Phase 9 improvements)
- ✅ Relative reminders calculate correct `scheduled_at` based on due_date
- ✅ Fired reminders don't fire again
- ✅ Reminders deleted when task deleted

**Error Codes**:
- `400 VALIDATION_ERROR` — missing required field (e.g., `scheduled_at` for absolute reminders)
- `400 MISSING_DUE_DATE` — relative reminder created on a task that has no `due_date` set
- `404 TASK_NOT_FOUND` — task does not exist or belongs to another user

**Evidence**:
- [src/api/reminders.py](../src/api/reminders.py)
- [src/services/reminder_service.py](../src/services/reminder_service.py)
- [src/models/reminder.py](../src/models/reminder.py)

---

### FR-012: User Notes (REVISED v1.2)

**What**: Standalone notes owned by the user (not task-scoped)

**Why**: Users need a general-purpose note capture independent of tasks,
        with optional task-conversion and voice input (Pro)

**Inputs**:
- `content`: string (0–2000 chars)
  - Required to be non-empty (≥ 1 char) **unless** `voice_url` is provided
  - When `voice_url` is present: `content` may be `""` (empty) or a user-typed label
  - **Validation rule**: enforced as a Pydantic `model_validator` (not a field-level
    annotation): `min_length=0` when `voice_url` is set; `min_length=1` otherwise.
    Field-level `min_length=0` in `NoteCreate`; the conditional check runs post-field-parse.
- `voice_url`: string | null (Pro only — URL of audio recording for transcription)
- `voice_duration_seconds`: int | null (1–MAX_AUDIO_DURATION_SECONDS, Pro only)
  > When `voice_url` is provided: `content` may be an empty string `""` or a user-typed
  > label. The background transcription task replaces `content` with the transcript when
  > `transcription_status` → "completed". If `content` was non-empty at creation, both are
  > preserved: `original_content + "\n\n---\n\n" + transcript`.

**Outputs**:
- Note object:
  - `id`: UUID
  - `user_id`: UUID
  - `content`: string (0–2000 chars; non-empty required unless `voice_url` was set at creation)
  - `archived`: bool (default: false)
  - `voice_url`: string | null (Pro only)
  - `voice_duration_seconds`: int | null — required together with `voice_url` when creating a
    voice note; range 1–MAX_AUDIO_DURATION_SECONDS seconds; `null` for non-voice notes;
    `MAX_AUDIO_DURATION_SECONDS` config default is 300 (see FR-006 / config.py)
  - `transcription_status`: enum("pending","completed","failed") | null
  - `created_at`: ISO8601 datetime
  - `updated_at`: ISO8601 datetime

**Endpoints**:
- POST /api/v1/notes          — create (201)
- GET  /api/v1/notes          — list (200, PaginatedResponse, ?archived=bool);
                                 default (no param): returns all notes regardless of archived status
- GET  /api/v1/notes/{id}     — get single note (200); returns note regardless of archived status
- PATCH /api/v1/notes/{id}    — update content/archived (200)
- DELETE /api/v1/notes/{id}   — delete (200, {deleted_id, tombstone_id})
- POST /api/v1/notes/{id}/convert — AI-suggest task from note (200, suggestion only — no auto-create, no auto-archive)

**Convert Response Schema** (`POST /api/v1/notes/{id}/convert`):
- Response: `DataResponse[TaskSuggestionResponse]` (HTTP 200)
- `TaskSuggestionResponse` fields:
  - `title`: string — AI-derived suggested task title
  - `description`: string | null — AI-derived task description (may be null for short notes)
  - `priority`: enum("low", "medium", "high") | null — suggested priority (null if indeterminate)
  - `suggested_subtasks`: array of `{ "title": string }` — AI-suggested subtask titles
    (count ≤ `FREE_MAX_SUBTASKS` for Free tier, ≤ `PRO_MAX_SUBTASKS` for Pro tier)
- Credits used: 1 (same as AI chat)
- `credits_remaining`: int
- `ai_request_warning`: bool (true if nearing session AI limit)

  > Returns 200 (not 201): no new resource is persisted. The response body contains only an
  > AI-generated suggestion object, not a created note or task.

**Limits**:
- Free tier: max 20 notes (base + perks)
- Pro tier: max 50 notes (base + perks)
- List: ordered by created_at DESC, max 50/page

**Side Effects**:
- Note limit checked on create (402 LIMIT_EXCEEDED for free tier at cap)
- Free user creating note with `voice_url` → 403 PRO_TIER_REQUIRED
- Voice note created (Pro): transcription triggered automatically as async background task;
  `transcription_status` set to "pending" immediately, updated to "completed" or "failed" when done.
  **Stuck-pending behavior**: If the process restarts while transcription is in-flight,
  the note remains in `"pending"` status indefinitely. Recovery is manual (user or admin
  sets status to `"failed"` via PATCH, or a future cleanup job resets stale pending notes
  after a configurable timeout — see Phase 9 improvements). This is a known limitation of
  using `BackgroundTasks` without a persistent job queue (Gap 2 / JobQueue planned for Phase 9).
- Convert endpoint (`POST /notes/{id}/convert`):
  - **Returns AI-suggested task structure** (title, description, priority, subtasks) — does NOT create the task
  - Does **not** auto-archive the source note — user must call `PATCH /notes/{id}` with `{"archived": true}` separately
  - Increments `notes_converted` achievement stat when suggestion is returned (at call time,
    regardless of whether the user subsequently creates the task). The stat name reflects
    *intent-to-convert* not *task-creation-confirmed*.
  - 1 credit deducted for AI suggestion; Idempotency-Key required
- Markdown content supported
- Deprecated task-scoped endpoints (`POST/GET /tasks/{task_id}/notes`) return 410 Gone
- Voice note creation (Pro, `voice_url` present): credits deducted **at note creation time**
  using FR-006 calculation (`ceil(voice_duration_seconds / 60) * 5` credits); 402
  INSUFFICIENT_CREDITS returned if balance insufficient before note is persisted.
  > Credit formula: see FR-006 for canonical definition.

**Error Codes**:
- 400 VALIDATION_ERROR — content missing or out of range
- 402 LIMIT_EXCEEDED  — note limit reached
  > **Design note**: Note limit-exceeded uses 402 (payment-gated resource — expandable
  > via Pro upgrade or achievements). Task limit-exceeded uses 409 CONFLICT (hard
  > resource conflict). This split is intentional per FR-007.
- 401 UNAUTHORIZED
- 403 FORBIDDEN       — note belongs to another user
- 403 PRO_TIER_REQUIRED — Free user attempts to create voice note
- 404 RESOURCE_NOT_FOUND
- 409 ARCHIVED        — attempt to edit **content** of an archived note (does NOT fire when setting `archived=false` to unarchive)
- 402 INSUFFICIENT_CREDITS — Pro user creates voice note without sufficient credits for the requested duration

**Success Criteria**:
- ✅ Notes created without task context
- ✅ `POST /api/v1/notes` with empty `content=""` and no `voice_url` → 400 VALIDATION_ERROR
- ✅ `POST /api/v1/notes` with empty `content=""` and valid `voice_url` (Pro) → 201 Created
- ✅ Free user creating note with voice_url receives 403 PRO_TIER_REQUIRED
- ✅ Voice notes (Pro): transcription_status starts as "pending"; async task updates it
- ✅ Archived filter works (GET /notes?archived=true returns archived only)
- ✅ Convert returns AI task suggestion without auto-creating task or auto-archiving note
- ✅ notes_converted stat incremented when convert endpoint is called (not at task creation)
- ✅ 402 (not 409) when free-tier note limit reached
- ✅ task_id column removed from database
- ✅ Deprecated task-scoped note endpoints return 410 Gone
- ✅ Archived notes can be unarchived via `PATCH /notes/{id}` with `{"archived": false}`
- ✅ DELETE /notes/{id} returns 200 with `{deleted_id, tombstone_id}` for 7-day recovery
- ✅ Voice note creation deducts credits at creation time (not after transcription completes)
- ✅ 402 INSUFFICIENT_CREDITS if Pro user lacks credits for voice note duration

**Evidence**:
- [src/api/notes.py](../src/api/notes.py)
- [src/services/note_service.py](../src/services/note_service.py)
- [src/models/note.py](../src/models/note.py)

---

### FR-013: Recovery System

**What**: 7-day recovery window for deleted items

**Why**: Prevent accidental data loss

**How It Works**:
1. DELETE operation creates tombstone record
2. Actual data hard-deleted
3. Tombstone contains serialized snapshot of deleted item
4. Recovery endpoint deserializes and recreates item
5. Tombstones auto-expire after 7 days

**Recoverable Entities**:
- Tasks (with subtasks and reminders — notes are **not** included in task tombstone
  snapshots from v1.2 onward; each note has its own tombstone lifecycle)
- Subtasks
- Notes (standalone, user_id only — no task_id in snapshot from v1.2 onward)
  - Migration: tombstones created before v1.2 may contain a task_id field; recovery service must tolerate its presence (ignore if present)

**Side Effects**:
- Tombstone limit: 3 per user — **shared pool across all entity types** (tasks, notes,
  subtasks). When creating a 4th tombstone, the oldest existing tombstone (regardless of
  entity type) is hard-deleted first, making the oldest deleted item unrecoverable.
- Recovered items get new IDs
- Activity log tracks deletion and recovery

**Success Criteria**:
- ✅ Deleted items recoverable within 7 days
- ✅ Tombstone expired after 7 days
- ✅ Recovery recreates item with original data
- ✅ Version reset to 1 on recovery — applies to **all versioned entities** (Tasks, Notes,
  Subtasks); any `version` value in the tombstone snapshot is discarded and replaced with 1

**Evidence**:
- [src/api/recovery.py](../src/api/recovery.py)
- [src/services/recovery_service.py](../src/services/recovery_service.py)
- [src/models/tombstone.py](../src/models/tombstone.py)

---

### FR-014: Activity Log

**What**: Audit trail of user actions

**Why**: Transparency and debugging

**Logged Events**:
- Task: created, updated, completed, deleted, recovered
- Subtask: created, completed, deleted
- Note: created, updated, deleted
- Credit: granted, deducted
- Achievement: unlocked
- **AI Interaction**: chat request, subtask generation, voice transcription, confirm-action executed
  > Undo for AI-confirmed mutations is intentionally out of scope (see Gap 5).
  > No `undo-action` log entries will be emitted.
  - Required fields (Constitution V.2): `task_id` (from X-Task-Id header or
    confirmed action; `null` is permitted for transcription requests where
    X-Task-Id is not provided — transcription is not task-scoped),
    `timestamp`, `actor` ("user" or "ai"), `credits_used`, `action_type`

**Outputs**:
- Activity entries with:
  - `entity_type`: string ("task", "subtask", "note", etc.)
  - `entity_id`: UUID
  - `action`: string ("created", "updated", "deleted", etc.)
  - `metadata`: JSON (entity-specific details)
  - `timestamp`: datetime

**Success Criteria**:
- ✅ All significant actions logged
- ✅ Activity log paginated
- ✅ Filterable by entity type, date range
- ✅ Activity log helps debug user issues

**Evidence**:
- [src/api/activity.py](../src/api/activity.py)
- [src/services/activity_service.py](../src/services/activity_service.py)
- [src/models/activity.py](../src/models/activity.py)

---

### FR-015: Subscription Management

**What**: Tier management (Free/Pro)

**Why**: Monetization and feature gating

**Tier Comparison**:

| Feature | Free | Pro |
|---------|------|-----|
| Max Tasks | 50 + perks | Unlimited |
| Max Subtasks/Task | 10 + perks | 20 + perks |
| Max Notes | 20 + perks | 50 + perks |
| Task Description | 1000 chars | 2000 chars |
| Note Content | 2000 chars | 2000 chars |
| Daily AI Credits | 10 + perks | 10 + perks |
| Subscription Credits | 0 | 50/month |
| Voice Transcription | ❌ | ✅ |
| Voice Notes | ❌ | ✅ |
| Credit Carryover | ❌ | ✅ (max 50) |

> **Note**: Notes are standalone (not task-scoped) from v1.2. The uniform 2000-char content limit applies to all tiers.

**Side Effects**:
- Tier checked on all tier-gated operations
- 403 PRO_TIER_REQUIRED for pro-only features

**Success Criteria**:
- ✅ Free tier sufficient for casual users
- ✅ Pro tier unlocks advanced features
- ✅ With all task+focus achievements unlocked, free-tier effective task limit = 455
  (50 base + 15 + 25 + 50 + 100 + 200 task achievements + 5 focus_10 + 10 focus_50)
- ✅ With streak_100 unlocked, free-tier effective daily AI credits = 20 (10 base + 10)

**Evidence**:
- [src/models/user.py](../src/models/user.py) - `tier` field
- [src/lib/limits.py](../src/lib/limits.py) - Limit enforcement

---

### FR-016: In-App Notifications

**What**: In-app notification inbox for system events (achievement unlocks, task completions, reminders)

**Why**: Surface important events to the user without requiring real-time delivery infrastructure

**Notification Types**:
- `achievement_unlocked` — triggered when an achievement perk is granted
- `task_completed` — triggered on task force-complete or auto-complete
- `reminder_fired` — **Phase 9 only** — triggered when a scheduled reminder fires;
  requires reminder delivery implementation (see Gap 2). Currently a defined type with
  no active emitters. No `reminder_fired` notifications will be created until Gap 2 is
  resolved.
- `system` — general system messages

**Outputs**:
- Notification object:
  - `id`: UUID
  - `user_id`: UUID
  - `type`: string (notification type)
  - `title`: string
  - `message`: string
  - `read`: bool (default: false)
  - `created_at`: ISO8601 datetime

**Endpoints**:
- GET /api/v1/notifications       — list notifications (unread first), paginated
- PATCH /api/v1/notifications/{id}/read — mark single notification as read (200)
- DELETE /api/v1/notifications/{id} — delete notification (200, {deleted_id})

**Side Effects**:
- Notifications created internally by services (AchievementService, TaskService, ReminderService)
- No external delivery mechanism (not push/email) — poll-based only
- No notification count limit; notifications **MUST** be pruned after 30 days by a
  scheduled background job (co-located with daily credit reset — see Task 6.2)

**Success Criteria**:
- ✅ Notifications created on achievement unlock and task completion
- ✅ Unread notifications appear first in list
- ✅ Mark-as-read updates `read=true`
- ✅ Deleted notifications removed immediately
- ⏸ Notifications older than 30 days pruned automatically by scheduled background job — **pending Task 6.2 M7**

**Evidence**:
- [src/models/notification.py](../src/models/notification.py)
- [src/services/notification_service.py](../src/services/notification_service.py)
- [src/api/notifications.py](../src/api/notifications.py)

---

## Non-Functional Requirements

### NFR-001: Performance

**Observed Patterns**:
- Async/await throughout (FastAPI + AsyncPG)
- Database connection pooling (pool_size=5, max_overflow=10)
- Eager loading with `selectinload()` to prevent N+1 queries
- Prometheus metrics for observability

**Targets** (contractual; single-instance verified by load tests in Task 7.4;
multi-instance verification pending Task 4.3a + Task 7.4 scalability tests):
- API response time: p95 < 200ms for CRUD operations
- Gamification / audit endpoints (`/achievements`, `/credits/history`,
  `/notifications`, `/activity`): p95 < 300ms
- AI endpoints: p95 < 3s (OpenAI-dependent; measured from API boundary)
- Database query time: p95 < 50ms

**Evidence**:
- [src/main.py:init_database](../src/main.py) - Connection pool config
- SQLAlchemy async patterns throughout services
- [src/middleware/metrics.py](../src/middleware/metrics.py) - Performance tracking

---

### NFR-002: Security

**Authentication**:
- JWT RS256 signing (asymmetric keys)
- Access token: 15 minutes expiry
- Refresh token: 7 days, single-use rotation
- JWKS endpoint for public key distribution

**Input Validation**:
- Pydantic schemas for all API inputs
- SQLModel validation at database layer
- Enum validation for controlled fields

**Security Headers** (SecurityHeadersMiddleware):
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)

**Secret Management**:
- Environment variables for secrets
- SecretStr type for sensitive config
- Keys stored in `keys/` directory (gitignored)

**Standards**:
- OWASP Top 10 considerations
- No SQL injection (parameterized queries)
- No XSS (JSON API only, no HTML rendering)

**Evidence**:
- [src/middleware/auth.py](../src/middleware/auth.py)
- [src/middleware/security.py](../src/middleware/security.py)
- [src/config.py](../src/config.py) - SecretStr usage

---

### NFR-003: Reliability

**Retry Logic**:
- No automatic retries at API level (idempotency handles client retries)
- Idempotency middleware prevents duplicate operations

**Error Handling**:
- Global error handler middleware
- Structured error responses with codes
- Request ID tracking for debugging

**Data Integrity**:
- Optimistic locking (version field) prevents lost updates
- Foreign key constraints enforce referential integrity
- Async transaction management

**Evidence**:
- [src/middleware/error_handler.py](../src/middleware/error_handler.py)
- [src/middleware/idempotency.py](../src/middleware/idempotency.py)
- Version field in [src/models/base.py:VersionedModel](../src/models/base.py)

---

### NFR-004: Scalability

**Horizontal Scaling**:
- Stateless API (JWT tokens, no session storage)
- Database pooling allows multiple app instances
- Idempotency keys stored in database (shared across instances)

**Vertical Scaling**:
- Async I/O allows high concurrency per instance
- Connection pooling optimizes database connections

**Load Capacity** (inferred):
- Single instance: ~100 RPS for CRUD operations
- Database: PostgreSQL (scales to millions of tasks)
- AI endpoints: Limited by OpenAI rate limits

**Evidence**:
- Stateless design (no in-memory session state)
- Database connection pooling
- Async FastAPI handlers

---

### NFR-005: Observability

**Logging**:
- Structured logging with structlog
- Request ID propagation
- LoggingMiddleware logs all requests/responses
- Detached instance prevention logged

**Metrics** (Prometheus):
- HTTP request rate, latency, status codes
- Task operations: create, update, delete, complete
- Credit operations: grant, deduct, balance
- Achievement unlocks
- AI usage: chat, subtask generation, transcription
- Rate limit hits
- Version conflicts

**Health Checks**:
- `/health/live`: Liveness probe (always returns 200)
- `/health/ready`: Readiness probe (checks database connection)

**Tracing**:
- Request ID middleware (X-Request-ID header)
- No distributed tracing yet (future improvement)

**Evidence**:
- [src/middleware/logging.py](../src/middleware/logging.py)
- [src/middleware/metrics.py](../src/middleware/metrics.py)
- [src/api/health.py](../src/api/health.py)
- [docs/observability.md](../docs/observability.md)

---

### NFR-006: API Documentation Standards

**What**: All additions and modifications to API endpoints must be reflected in
[`backend/docs/API.md`](../docs/API.md) as part of the same change.

**Why**: Keeps the API reference the single source of truth for frontend
integration, preventing contract drift between code and documentation.

**Coverage Requirements**:
- **New endpoints**: document request/response format, headers, error codes, and at least one example
- **Modified endpoints**: update affected sections (request shape, response fields, new error codes)
- **Deprecated endpoints**: add deprecation notice with migration guidance
- **Removed endpoints**: remove from docs or replace with tombstone entry noting 410 Gone

**Success Criteria**:
- ✅ `backend/docs/API.md` stays in sync with actual endpoint behaviour after every change
- ✅ No endpoint addition or modification is considered complete without a corresponding docs update

---

## System Constraints

### External Dependencies

1. **PostgreSQL 14+**
   - Async driver: asyncpg
   - Required features: JSONB, timezone support
   - Ownership: Infrastructure team

2. **Google OAuth**
   - Google Cloud Console project required
   - Client ID and secret needed
   - Ownership: External (Google)

3. **OpenAI API**
   - GPT-4 Turbo model (configurable)
   - API key required
   - Rate limits: Tier-dependent
   - Ownership: External (OpenAI)

4. **Deepgram API**
   - NOVA2 model for transcription
   - API key required
   - Ownership: External (Deepgram)

### Data Formats

- **API**: JSON (application/json)
- **Dates**: ISO 8601 with UTC timezone
- **IDs**: UUID v4
- **Markdown**: Subset for notes/descriptions

### Deployment Context

**Development**:
- Uvicorn with hot reload
- SQLite for tests (with async limitations)
- Swagger/ReDoc enabled

**Production** (inferred):
- Gunicorn + Uvicorn workers
- PostgreSQL with connection pooling
- Docs disabled
- HTTPS only (HSTS header enforced)

### Compliance Requirements

**GDPR** (implied):
- User data deletion via tombstone system
- Activity log for audit trail
- User owns all their data

**PCI-DSS**: Not applicable (no payment processing in backend)

---

## Non-Goals & Out of Scope

**Explicitly excluded** (inferred from absence):

1. **Real-time Collaboration**
   - No WebSocket support
   - No shared task spaces
   - Stub code suggests planned but not implemented

2. **Mobile Push Notifications**
   - Reminder `method: "push"` defined but not implemented
   - No FCM/APNS integration

3. **Email Notifications**
   - Reminder `method: "email"` defined but not implemented
   - No email service integration

4. **Recurring Tasks**
   - TaskTemplate exists but no automatic recurrence
   - No cron-like scheduling

5. **Team Features**
   - No user groups or teams
   - No task assignment to others
   - No shared workspaces

6. **File Attachments**
   - No file upload/storage
   - Only markdown notes

7. **Third-party Integrations**
   - No Slack, Trello, Jira, etc. integrations
   - No calendar sync (Google Calendar, etc.)

---

## Known Gaps & Technical Debt

### Gap 1: SQLAlchemy Async + MissingGreenlet

**Issue**: Lazy-loaded relationships accessed outside async greenlet context cause `MissingGreenlet` errors

**Evidence**:
- [MEMORY.md](../.claude/memory/MEMORY.md) - Documented pattern
- Refresh after rollback required throughout services

**Impact**:
- Runtime errors if relationships not eagerly loaded
- Verbose code with explicit `session.refresh(obj, ["rel"])` calls

**Recommendation**:
- Use `selectinload()` consistently in queries
- Add linting rule to catch lazy load access

---

### Gap 2: Incomplete Reminder Delivery

**Issue**: Reminder firing mechanism exists but delivery not implemented

**Evidence**:
- [src/models/reminder.py](../src/models/reminder.py) - `fired` field exists
- No background job or notification service

**Impact**: Reminders created but never fire

**Recommendation**:
- Implement background worker (Celery, RQ, or FastAPI BackgroundTasks)
- Integrate notification service (FCM for push, SendGrid for email)

---

### Gap 3: No Distributed Tracing

**Issue**: Request ID tracking exists but no distributed tracing

**Evidence**:
- [src/middleware/request_id.py](../src/middleware/request_id.py)
- No OpenTelemetry integration

**Impact**: Hard to debug cross-service issues (e.g., AI service calls)

**Recommendation**:
- Add OpenTelemetry instrumentation
- Integrate with Jaeger or DataDog APM

---

### Gap 4: Rate Limiting Implementation

**Issue**: Rate limiting decorators defined but enforcement unclear

**Evidence**:
- [src/middleware/rate_limit.py](../src/middleware/rate_limit.py)
- SlowAPI integration

**Impact**: Rate limits may not work as documented

**Recommendation**:
- Verify rate limiting with load tests
- Add Redis for distributed rate limiting (multi-instance)

---

### Gap 5: Undo for AI-Confirmed Actions — Intentionally Out of Scope

**Status**: Product decision — will not be implemented.

**Background**: `POST /api/v1/ai/confirm-action` executes mutations (`complete_task`,
`create_subtasks`, `update_task`) with no programmatic undo API. An undo endpoint was
considered but rejected as a product decision. Constitution III.4 has been formally amended
(2026-02-22, v1.1.0) to ratify this exception: undo is **not guaranteed** for AI-confirmed
mutations executed via this endpoint only. All other mutations retain the full undo guarantee.

**Mitigations**:
- AI actions require explicit user confirmation before execution (the confirm-action flow is the gate)
- Mutations are logged in the activity log with `actor="ai"` for auditability
- Users can manually reverse any AI-confirmed mutation through normal task/subtask CRUD endpoints
- The deletion tombstone system (FR-013) covers the highest-risk operation (deletes) regardless

**Evidence**:
- [src/api/ai.py](../src/api/ai.py) — `confirm-action` endpoint
- Product decision recorded in `REMEDIATIONS-003.md`

---

### Gap 6: Test Coverage Gaps

**Issue**: High unit test coverage (843 tests) but integration tests limited (~150)

**Evidence**: Test directory structure shows unit >> integration

**Impact**: Integration issues not caught until production

**Recommendation**:
- Add end-to-end tests for critical flows
- Add contract tests for frontend integration
- Add load tests for performance validation

---

### Gap 7: Subscription Payment Integration

**Issue**: Subscription tier exists but no payment processing

**Evidence**:
- [src/models/user.py](../src/models/user.py) - `tier` field
- No Stripe/payment integration

**Impact**: Users can't upgrade to Pro tier

**Recommendation**:
- Integrate Stripe for subscription management
- Add webhook handling for payment events
- Implement subscription lifecycle (trial, active, canceled)

---

## Success Criteria

### Functional Success

- ✅ All API endpoints return correct responses for valid inputs
- ✅ All error cases handled gracefully with appropriate status codes
- ✅ Google OAuth authentication succeeds
- ✅ JWT tokens refresh seamlessly
- ✅ Tasks created, updated, deleted with optimistic locking
- ✅ AI chat provides contextual responses
- ✅ AI subtask generation produces actionable suggestions
- ✅ Voice transcription (Pro only) converts speech to text accurately
- ✅ Credit system deducts correctly with proper priority order
- ✅ Achievement system unlocks perks at correct thresholds
- ✅ Focus mode tracks time accurately
- ✅ Deleted items recoverable within 7 days
- ✅ Activity log captures all significant actions

### Non-Functional Success

- ✅ API response time p95 < 200ms for CRUD operations
- ✅ Database queries p95 < 50ms
- [ ] 1044 tests passing — PENDING: 7 unit tests (Task 7.1) and 2 scalability
  tests (Task 7.4) remain open; closes when all Task 7.1 and 7.4 `[ ]` items
  resolve. (843 unit + 201 integration target; ~150 schemathesis contract tests
  are a subset of the 201 integration tests)
- ✅ Zero SQL injection vulnerabilities
- ✅ Zero XSS vulnerabilities
- ✅ Optimistic locking prevents lost updates
- ✅ Idempotency prevents duplicate operations
- ✅ Structured logging with request ID propagation
- ✅ Prometheus metrics exported for all key operations
- ✅ Health checks pass in production

---

## Acceptance Tests

### Test 1: Complete Task Lifecycle

**Given**: Authenticated user with no tasks

**When**:
1. Create task "Write documentation"
2. Add subtask "Research API endpoints"
3. Complete subtask
4. Add reminder for task
5. Complete task via force-complete
6. Delete task
7. Recover task

**Then**:
- ✅ Task created with unique ID
- ✅ Subtask count = 1, completed count = 0
- ✅ After subtask completion: completed count = 1
- ✅ Reminder created with scheduled_at
- ✅ Force-complete marks all incomplete subtasks as complete
- ✅ Achievement check runs on completion
- ✅ Delete creates tombstone
- ✅ Recovery recreates task with original data

---

### Test 2: AI Credit Lifecycle

**Given**: New user with kickstart credits (5)

**When**:
1. Make AI chat request (costs 1 credit)
2. Make AI subtask generation request (costs 1 credit)
3. Wait for daily reset
4. Make 10 AI chat requests (uses daily credits)
5. Upgrade to Pro tier
6. Make AI transcription request (costs 5 credits)

**Then**:
- ✅ After step 1: balance = 4 kickstart
- ✅ After step 2: balance = 3 kickstart
- ✅ After step 3: balance = 3 kickstart + 10 daily
- ✅ After step 4: balance = 3 kickstart (daily exhausted)
- ⏸ After step 5: balance = 3 kickstart + 50 subscription — **requires Task 4.2a (subscription renewal)**
- ⏸ After step 6: balance = 48 subscription + 3 kickstart — **requires Task 4.2a**
- ✅ 402 error if credits insufficient

---

### Test 3: Achievement Progression

**Given**: User with 4 completed tasks, 6-day streak

**When**:
1. Complete 1 task today (task #5, maintains streak to 7 days)
2. Skip tomorrow (breaks streak)
3. Complete 20 more tasks (total: 25)
4. Complete 3 tasks via focus mode (total focus: 3)

**Then**:
- ✅ After step 1: `tasks_5` achievement unlocked (+15 max tasks), `streak_7` unlocked (+3 daily credits)
- ✅ After step 2: current_streak = 0, longest_streak = 7
- ✅ After step 3: `tasks_25` achievement unlocked (+25 max tasks)
- ✅ After step 4: focus_completions = 3, no focus achievement yet (threshold: 10)
- ✅ Effective limits recalculate after each unlock

---

### Test 4: Optimistic Locking Conflict

**Given**: Task with version = 1

**When**:
1. User A reads task (version 1)
2. User B updates task title (version → 2)
3. User A updates task description with version 1

**Then**:
- ✅ User B update succeeds (version 1 → 2)
- ✅ User A update fails with 409 CONFLICT error
- ✅ Error message indicates stale version
- ✅ User A must refetch task and retry

---

### Test 5: Idempotency Protection

**Given**: Authenticated user

**When**:
1. Create task with Idempotency-Key: "key-123"
2. Retry same request with Idempotency-Key: "key-123"
3. Create different task with Idempotency-Key: "key-123"

**Then**:
- ✅ First request creates task, returns 201 Created
- ✅ Second request returns cached response, returns 200 OK with X-Idempotent-Replayed: true
- ✅ Third request returns cached response (same key), does NOT create new task

---

### Test 6: Tier Limit Enforcement

**Given**: Free tier user with 0 tasks

**When**:
1. Create 50 tasks (free tier base limit)
2. Unlock `tasks_5` achievement (+15 max tasks)
3. Create 15 more tasks (total: 65)
4. Attempt to create 1 more task (66th)

**Then**:
- ✅ First 50 tasks created successfully
- ✅ After achievement unlock: effective limit = 65
- ✅ Next 15 tasks created successfully
- ✅ 66th task fails with 409 LIMIT_EXCEEDED error
- ✅ Error message shows current limit and achievement recommendation

---

## Regeneration Strategy

This specification enables complete system regeneration through:

1. **Clear Requirements**: Each FR defines inputs, outputs, side effects, and success criteria
2. **Architecture Decisions**: Documented patterns (async, optimistic locking, credit system)
3. **Data Model**: Models and relationships defined
4. **API Contract**: Request/response formats specified
5. **Business Rules**: Tier limits, credit deduction order, achievement thresholds
6. **Quality Criteria**: NFRs and acceptance tests define "done"

**To regenerate**:
- Start with FR-001 (Auth) as foundation
- Build FR-002 (Tasks) as core entity
- Add FR-003-006 (AI features) incrementally
- Layer in FR-007-015 (credits, achievements, focus, etc.)
- Apply NFRs throughout
- Validate with acceptance tests

**Improvements to make**:
- Implement reminder delivery (Gap 2)
- Add distributed tracing (Gap 3)
- Integrate payment processing (Gap 6)
- Add real-time features (WebSockets for notifications)
- Expand team/collaboration features

---

## Data Model Reference

The canonical entity-relationship diagram and full column-level schema are in
[`specs/003-perpetua-backend/data-model.md`](./data-model.md).

If any model definition in this spec conflicts with `data-model.md`, this spec is
authoritative per Constitution I.1. The `data-model.md` should be updated to match.

---

**Reverse Engineered By**: Claude Sonnet 4.5
**Source Analysis Date**: 2026-02-17
**Total Files Analyzed**: 4233 Python files
**Test Coverage**: 1044 tests (843 unit + 201 integration; ~150 contract tests
are a subset of integration tests)
