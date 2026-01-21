# Feature Specification: Perpetua Flow Backend API

**Feature Branch**: `003-perpetua-backend`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "Perpetua Flow Backend - Python FastAPI PostgreSQL Neon Serverless with Authentication, Tasks, Notes, AI Integration, Subscriptions, and Achievements"

## Overview

Perpetua Flow Backend provides the server-side infrastructure for a task management and productivity application. The backend serves as the authoritative data source, handling user authentication, task lifecycle management, notes, AI-powered features, subscription billing, and a gamification system with achievements and streaks.

### Core Principles

1. **Data must never be lost** - This is the highest invariant
2. All timestamps stored in UTC - Frontend handles localization
3. Backend behavior must be deterministic, explicit, and auditable
4. No implicit state transitions - All non-user-triggered changes emit events
5. User intent always succeeds unless it violates a hard invariant
6. Automation failure must not block user actions
7. **AI failures must not corrupt user data** - AI operations are advisory until confirmed

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Authentication via Google OAuth (Priority: P1)

A new user visits Perpetua Flow and wants to sign up using their Google account. They click "Sign in with Google," authorize the application, and are automatically logged in with a new account created. Returning users follow the same flow and access their existing data.

**Why this priority**: Authentication is the gateway to all features. Without secure user authentication, no other functionality can be accessed or protected.

**Independent Test**: Can be fully tested by completing the OAuth flow with Google and verifying token issuance. Delivers secure access to the application.

**Acceptance Scenarios**:

1. **Given** a new user, **When** they complete Google OAuth authorization, **Then** a new account is created and they receive access and refresh tokens
2. **Given** an existing user, **When** they complete Google OAuth authorization, **Then** they receive new tokens and access their existing data
3. **Given** an access token has expired, **When** a valid refresh token is provided, **Then** new tokens are issued
4. **Given** an invalid or expired refresh token, **When** token refresh is attempted, **Then** the request fails with 401 and `refresh_required` flag

---

### User Story 2 - Task Creation and Management (Priority: P1)

A user wants to create, view, update, and complete tasks to manage their daily activities. They can set priorities, due dates, descriptions, and estimated durations. Tasks can be marked complete manually or auto-complete when all subtasks finish.

**Why this priority**: Task management is the core value proposition. Users must be able to create and manage tasks for the application to be useful.

**Independent Test**: Can be fully tested by creating a task, updating its properties, adding subtasks, and completing it. Delivers the fundamental productivity value.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a task with title, priority, and due date, **Then** the task is persisted and assigned a unique identifier
2. **Given** a task with incomplete subtasks, **When** the user completes all subtasks, **Then** the parent task auto-completes with `completed_by = auto`
3. **Given** a task with incomplete subtasks, **When** the user force-completes the parent task, **Then** all subtasks are marked complete and `completed_by = force`
4. **Given** an archived task, **When** a user attempts to complete it, **Then** the request is rejected with 409 CONFLICT

---

### User Story 3 - Recurring Task Templates (Priority: P2)

A user wants to set up recurring tasks (daily, weekly, monthly) that automatically generate new instances when the current one is completed. They can edit recurrence patterns and choose whether changes apply to future instances only or the template itself.

**Why this priority**: Recurring tasks are essential for habit tracking and routine management, but users need basic task management first.

**Independent Test**: Can be fully tested by creating a recurring task template, completing an instance, and verifying the next instance is generated.

**Acceptance Scenarios**:

1. **Given** a recurring task template, **When** a user completes the current instance, **Then** the next instance is automatically generated based on the recurrence rule
2. **Given** a recurring instance, **When** a user edits the recurrence, **Then** they are prompted to apply changes to future instances or template only
3. **Given** a generation failure, **When** the next instance cannot be created, **Then** the completion is not rolled back, the error is logged, and retry is scheduled

---

### User Story 4 - Subtask Management (Priority: P2)

A user wants to break down complex tasks into smaller, manageable subtasks. They can add up to 4 subtasks (free tier) or 10 subtasks (pro tier), reorder them, and track completion individually.

**Why this priority**: Subtasks enable users to tackle larger projects incrementally, improving task completion rates.

**Independent Test**: Can be fully tested by adding subtasks to a task, reordering them, and completing them individually.

**Acceptance Scenarios**:

1. **Given** a task with fewer than the maximum allowed subtasks, **When** a user adds a subtask, **Then** it is created with the next order index
2. **Given** a free user with 4 subtasks on a task, **When** they try to add another, **Then** the request is rejected with limit exceeded error
3. **Given** multiple subtasks, **When** a user reorders them, **Then** the order indices are updated to maintain gapless ordering

---

### User Story 5 - Notes with Voice Recording (Priority: P2)

A user wants to capture quick thoughts as text notes or voice recordings. Notes can later be converted to tasks using AI assistance (costs 1 credit). Voice transcription is available for Pro users only.

**Why this priority**: Notes provide a quick-capture mechanism that feeds into the task system, increasing user engagement.

**Independent Test**: Can be fully tested by creating a text note, then converting it to a task with AI assistance.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a text note, **Then** it is persisted with content up to 2000 characters
2. **Given** a Pro user, **When** they record a voice note, **Then** it is transcribed and stored with the audio URL
3. **Given** a note and sufficient AI credits, **When** the user requests conversion to task, **Then** AI suggests a title and description for user confirmation

---

### User Story 6 - AI Chat Widget (Priority: P3)

A user wants to interact with an AI assistant to help manage their tasks. The AI can answer questions about tasks, create new tasks, edit existing ones, and provide productivity suggestions. All actions require user confirmation.

**Why this priority**: AI integration enhances productivity but is an enhancement over core functionality.

**Independent Test**: Can be fully tested by sending chat messages and confirming AI-suggested actions.

**Acceptance Scenarios**:

1. **Given** a user with available AI credits, **When** they send a chat message, **Then** they receive a response and 1 credit is deducted
2. **Given** an AI action suggestion, **When** the user confirms it, **Then** the action is executed on their behalf
3. **Given** a user with 0 credits, **When** they try to chat, **Then** they receive INSUFFICIENT_CREDITS error

---

### User Story 7 - Auto Subtask Generation (Priority: P3)

A user wants AI to suggest subtasks for their task based on the title and description. The AI generates up to the user's subtask limit, costing 1 credit regardless of count.

**Why this priority**: AI subtask generation reduces cognitive load but requires stable task and AI infrastructure first.

**Independent Test**: Can be fully tested by requesting subtask generation for a task and reviewing the suggestions.

**Acceptance Scenarios**:

1. **Given** a task with title and description, **When** user requests subtask generation, **Then** AI generates up to the user's limit of subtasks
2. **Given** a free user, **When** subtasks are generated, **Then** maximum 4 subtasks are returned regardless of AI output

---

### User Story 8 - Reminder System (Priority: P3)

A user wants to set reminders for their tasks that notify them before or after the due date. Reminders can be delivered as push notifications or in-app notifications.

**Why this priority**: Reminders help users stay on track but are supplementary to core task management.

**Independent Test**: Can be fully tested by creating a reminder and verifying notification delivery at the scheduled time.

**Acceptance Scenarios**:

1. **Given** a task with a due date, **When** user adds a "before" reminder, **Then** it is scheduled for the specified offset before due date
2. **Given** a task's due date changes, **When** the reminder is relative type, **Then** the scheduled time is recalculated
3. **Given** a recovered (restored) task, **When** it has past reminders, **Then** those reminders do NOT retroactively fire

---

### User Story 9 - Achievement System (Priority: P3)

A user earns achievements by completing tasks, maintaining streaks, using focus mode (see FR-045 for completion criteria), and converting notes. Achievements unlock permanent perks like increased limits and bonus AI credits.

**Why this priority**: Gamification drives engagement but requires stable core features to track progress.

**Independent Test**: Can be fully tested by completing the required actions and verifying achievement unlock and perk application.

**Acceptance Scenarios**:

1. **Given** a user completes their 5th lifetime task, **When** achievement check runs, **Then** `tasks_5` achievement is unlocked granting +15 max tasks
2. **Given** a user has a 7-day login streak, **When** streak achievement check runs, **Then** `streak_7` achievement is unlocked granting +2 daily AI credits
3. **Given** a user's streak breaks, **When** they lose the streak, **Then** previously earned achievement perks are NOT revoked
4. **Given** an achievement is unlocked, **When** unlock occurs, **Then** the API response that triggered the unlock (e.g., task completion) MUST include an `unlocked_achievements` array containing achievement details (id, name, description, perk), enabling frontend to display a toast notification

---

### User Story 10 - Pro Subscription Management (Priority: P4)

A user wants to upgrade to Pro for increased limits, monthly AI credits, and voice features. They can manage their subscription, and the system handles payment failures gracefully with a 3-day grace period.

**Why this priority**: Monetization enables the business model but requires core features to be compelling first.

**Independent Test**: Can be fully tested by subscribing, verifying Pro features, and testing cancellation flow.

**Acceptance Scenarios**:

1. **Given** a free user, **When** they subscribe via Checkout.com, **Then** their tier changes to Pro with all Pro benefits
2. **Given** a subscription payment fails, **When** 3 retry attempts fail, **Then** account enters 3-day grace period
3. **Given** grace period expires without payment, **When** the period ends, **Then** account downgrades to free tier

---

### User Story 11 - AI Credit System (Priority: P4)

Users have AI credits that are consumed for chat messages, subtask generation, note conversion, and voice transcription. Free users get kickstart credits; Pro users get monthly credits with carryover.

**Why this priority**: Credit system enables sustainable AI usage but requires AI features to be implemented first.

**Independent Test**: Can be fully tested by consuming credits and verifying balance updates and consumption order.

**Acceptance Scenarios**:

1. **Given** a new free user, **When** their account is created, **Then** they receive 5 kickstart credits
2. **Given** a user with daily free credits and purchased credits, **When** they consume 1 credit, **Then** the daily free credit is consumed first (FIFO)
3. **Given** a Pro user at month end, **When** renewal occurs, **Then** up to 50 subscription credits carry over

---

### User Story 12 - Focus Mode Tracking (Priority: P4)

A user enters Focus Mode to work on a specific task. The system tracks time spent and counts tasks toward focus achievements per FR-045 (≥50% of estimated duration in focus).

**Why this priority**: Focus mode is a productivity enhancement that builds on task infrastructure.

**Independent Test**: Can be fully tested by starting/ending focus sessions and verifying time accumulation and achievement progress.

**Acceptance Scenarios**:

1. **Given** a user starts focus mode on a task, **When** they end the session, **Then** the duration is added to `focus_time_seconds`
2. **Given** a task with 30 min estimate, **When** user completes it with 15+ min focus time, **Then** it counts toward focus achievements

---

### User Story 13 - Task Deletion and Recovery (Priority: P4)

A user accidentally deletes an important task and wants to recover it. The system keeps tombstones for the 3 most recent deletions per user, allowing recovery.

**Why this priority**: Data recovery is a safety net that prevents data loss, supporting the core principle.

**Independent Test**: Can be fully tested by deleting tasks, verifying tombstone creation, and recovering the most recent deletions.

**Acceptance Scenarios**:

1. **Given** a user deletes a task, **When** the deletion completes, **Then** a tombstone is created with the serialized task data
2. **Given** 3 tombstones exist, **When** a 4th deletion occurs, **Then** the oldest tombstone is permanently removed
3. **Given** a recovered task, **When** it is restored, **Then** it does NOT affect streaks or re-trigger achievements

---

### Edge Cases

- What happens when concurrent updates occur on the same task? → Optimistic locking via version field returns 409 CONFLICT for stale updates
- How does the system handle Checkout.com webhook signature failures? → Reject the request; do not process subscription changes
- What happens when AI service (OpenAI/Deepgram) is unavailable? → Return AI_SERVICE_UNAVAILABLE error; user action is not blocked
- How does the system handle timezone edge cases for streak calculation? → All streak logic uses UTC calendar days; user timezone is informational only
- What happens when a user exceeds 10 AI requests per task? → Block further AI requests for that task with CREDIT_LIMIT_REACHED
- How does the system handle duplicate idempotency keys? → Return the original response for the duplicate request

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization

- **FR-001**: System MUST authenticate users via Google OAuth through BetterAuth on frontend
- **FR-002**: System MUST issue JWT access tokens with 15-minute expiry
- **FR-003**: System MUST issue refresh tokens with 7-day expiry that rotate on use
- **FR-004**: System MUST return 401 UNAUTHORIZED for missing or invalid authentication
- **FR-005**: System MUST return 403 FORBIDDEN for cross-user resource access attempts
- **FR-006**: System MUST return 401 with `refresh_required` flag when access token is expired but refresh token is valid
- **FR-070**: System MUST support user profile updates (name) via PATCH /api/v1/users/me

#### Task Management

- **FR-007**: System MUST support task creation with title (max 200 chars), description (max 1000 chars free / 2000 chars pro), priority, due date, and estimated duration
- **FR-008**: System MUST support task completion with completion timestamp and completion method (manual, auto, force)
- **FR-009**: System MUST auto-complete parent tasks when all subtasks are completed
- **FR-010**: System MUST force-complete all subtasks when parent task is force-completed
- **FR-011**: System MUST reject completion of archived tasks with 409 CONFLICT
- **FR-012a**: System MUST support soft deletion via hidden flag (recoverable, not shown in default lists)
- **FR-012b**: System MUST support hard deletion with tombstone creation (limited recovery window per FR-062)
- **FR-013**: System MUST enforce maximum task duration of 30 days from creation
- **FR-014**: System MUST support optimistic locking via version field

#### Recurring Tasks

- **FR-015**: System MUST support recurrence rules in RRULE format
- **FR-016**: System MUST generate next instance on completion of recurring task instance
- **FR-017**: System MUST NOT roll back completion if next instance generation fails
- **FR-018**: System MUST prevent editing recurrence on past instances

#### Subtasks

- **FR-019**: System MUST limit subtasks to 4 per task for free users, 10 for pro users
- **FR-020**: System MUST maintain gapless ordering for subtask order indices
- **FR-021**: System MUST track subtask generation source (user or AI)

#### Notes

- **FR-022**: System MUST limit notes to 10 for free users, 25 for pro users
- **FR-023**: System MUST support note content up to 2000 characters
- **FR-024**: System MUST support voice recordings with URL storage and duration tracking

#### Reminders

- **FR-025**: System MUST limit reminders to 5 per task
- **FR-026**: System MUST recalculate relative reminder times when due date changes
- **FR-027**: System MUST NOT fire reminders retroactively for recovered tasks
- **FR-028a**: Frontend manages WebPush subscription via browser API; backend stores push subscription tokens
- **FR-028b**: System MUST gracefully handle expired/invalid push tokens without blocking operations

#### AI Integration

- **FR-029**: System MUST process all AI requests server-side for security and credit enforcement
- **FR-030**: System MUST deduct 1 credit per chat message
- **FR-031**: System MUST deduct 1 credit per subtask generation (flat rate)
- **FR-032**: System MUST deduct 1 credit per note-to-task conversion
- **FR-033**: System MUST deduct 5 credits per minute for voice transcription (Pro only, see FR-036 for duration limit)
- **FR-034**: System MUST require user confirmation before executing AI-suggested actions
- **FR-035**: System MUST warn at 5 AI requests per task and block at 10 requests per task. The counter is session-scoped. Counter resets at session change.
- **FR-036**: System MUST limit voice recording to 300 seconds maximum (see also FR-033 for billing)

#### AI Credits

- **FR-037**: System MUST grant 5 kickstart credits to new accounts (one-time)
- **FR-038**: System MUST grant Pro users 10 base daily credits + achievement bonuses
- **FR-039**: System MUST grant Pro users 100 monthly subscription credits
- **FR-040**: System MUST expire daily credits at UTC 00:00
- **FR-041**: System MUST carry over up to 50 unused subscription credits
- **FR-042**: System MUST consume credits in FIFO order: daily free → subscription → purchased

#### Achievements & Streaks

- **FR-043**: System MUST calculate streaks based on UTC calendar days with ≥1 task completed
- **FR-044**: System MUST unlock achievements permanently - perks are never revoked
- **FR-045**: System MUST track focus mode completion (≥50% of estimated duration in focus)
- **FR-046**: System MUST compute effective limits from base + achievement perks

#### Subscriptions & Payments

- **FR-047**: System MUST process subscription events via Checkout.com webhooks
- **FR-048**: System MUST verify webhook signatures before processing
- **FR-049**: System MUST provide 3-day grace period after 3 failed payment attempts
- **FR-050**: System MUST downgrade to free tier when grace period expires without payment
- **FR-051**: System MUST limit credit purchases to 500 credits per month per user
- **FR-051a**: Purchased credits have no expiration date
- **FR-051b**: Purchased credits are consumed last in FIFO order (after daily free and subscription credits)

#### Activity Logging & Observability

- **FR-052**: System MUST log all task, subtask, note, AI, and subscription events
- **FR-053**: System MUST retain activity logs for 30 days (rolling window)
- **FR-054**: System MUST include source (user, AI, system) in all log entries
- **FR-065**: System MUST emit structured JSON logs for all operations (request ID, timestamp, user ID, action, outcome)
- **FR-066**: System MUST expose Prometheus-compatible metrics for request latency, error rates, and credit consumption
- **FR-067**: System MUST provide health check endpoints for liveness and readiness probes

#### Notifications

- **FR-055**: System MUST support in-app notifications via notification bell
- **FR-056**: System MUST support browser push notifications (requires permission)
- **FR-057**: System MUST track read status for notifications

#### API Behavior

- **FR-058**: System MUST use PATCH semantics where omitted fields are unchanged and null explicitly clears
- **FR-059**: System MUST require idempotency keys for POST and PATCH requests
- **FR-060**: System MUST use offset-based pagination with default 25, max 100 items
- **FR-061**: System MUST enforce per-user rate limits: 100 req/min across all general endpoints (shared bucket), 20 req/min for AI endpoints (separate bucket), 10 req/min for auth endpoints (per-IP)
- **FR-068**: System MUST use URL path versioning with all endpoints under /api/v1/ namespace
- **FR-069**: System MUST maintain backward compatibility within a major version; breaking changes require new version
- **FR-069a**: System MUST provide minimum 90-day deprecation notice for any endpoint removal within a major version
- **FR-069b**: Deprecated endpoints MUST return `Deprecation` header with sunset date per RFC 8594

#### Deletion Recovery

- **FR-062**: System MUST retain tombstones for 3 most recent deletions per user
- **FR-063**: System MUST restore original ID and timestamps on recovery
- **FR-064**: System MUST NOT trigger reminders, achievements, or streak updates for recovered tasks

### Key Entities

- **User**: Represents an authenticated account with profile, preferences, subscription status, and timezone
- **Task Instance**: A concrete task occurrence with title, description, priority, due date, completion status, and focus time tracking
- **Task Template**: A recurring task definition with recurrence rules that spawns instances
- **Subtask**: A child item of a task with title, completion status, and ordering
- **Note**: A quick-capture text or voice recording that can be converted to a task
- **Reminder**: A scheduled notification tied to a task's due date
- **Achievement**: A milestone that grants permanent perks when unlocked
- **User Achievement State**: Current progress toward achievements and effective limits
- **AI Credit Ledger**: Transaction history for credit consumption with FIFO tracking
- **Subscription**: Payment and plan status for Pro tier management
- **Activity Log**: Audit trail of user and system actions
- **Deletion Tombstone**: Serialized deleted entity for recovery
- **Notification**: In-app or push message for user alerts

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend OAuth token exchange and user creation/lookup completes within 2 seconds; end-to-end flow (excluding user interaction with Google consent screen) completes within 10 seconds
- **SC-002**: System handles 1000 concurrent authenticated users without degradation
- **SC-003**: 95% of API responses return within 500 milliseconds
- **SC-004**: Task creation, update, and completion succeed on first attempt for 99.9% of valid requests
- **SC-005**: AI chat responses return within 5 seconds for 95% of requests
- **SC-006**: Zero data loss for user tasks, notes, and achievements under normal operation
- **SC-007**: Streak calculations are accurate to the UTC day boundary with no false breaks
- **SC-008**: Payment webhook processing completes within 30 seconds of receipt
- **SC-009**: 99.5% uptime for core API endpoints
- **SC-010**: Users can recover deleted tasks within 30 seconds of initiating recovery
- **SC-011**: Credit balances are accurate within eventual consistency window of 5 seconds
- **SC-012**: Push notifications deliver within 60 seconds of scheduled time for 95% of notifications

## Clarifications

### Session 2026-01-19

- Q: What level of observability infrastructure should the backend support? → A: Structured logging + metrics (JSON logs, Prometheus-style metrics)
- Q: What API versioning strategy should the backend use? → A: URL path versioning (/api/v1/, /api/v2/)

### Session 2026-01-20 (Refinement)

**HIGH Priority:**
- U1: Added FR-070 for user profile updates (PATCH /api/v1/users/me)
- U2: Added US9 acceptance scenario 4 for achievement notification delivery
- A1: Clarified SC-001 OAuth timing (2s backend processing, 10s end-to-end excluding user consent)

**MEDIUM Priority:**
- A2: Clarified FR-061 rate limit scope (per-user shared bucket for general, separate buckets for AI/auth, per-IP for auth)
- U3: Split FR-028 into FR-028a/FR-028b clarifying frontend WebPush responsibility and graceful token handling
- U4: Added Assumption 9 for voice audio streaming (no backend persistence)
- D1: Added FR-045 cross-references to US9 and US12 for focus completion tracking

**LOW Priority:**
- U5: Added FR-051a/FR-051b for purchased credits lifecycle (no expiration, consumed last)
- D2: Added cross-references between FR-033 and FR-036 for voice transcription requirements
- T2: Split FR-012 into FR-012a (soft deletion) and FR-012b (hard deletion with tombstone)

## Related Documentation

Detailed technical documentation is available in the [docs/](docs/) directory:

- **[Data Model](docs/data-model.md)** - Database entities, schemas, relationships, and validation rules
- **[API Specification](docs/api-specification.md)** - REST API endpoints, request/response formats, and error handling
- **[Authentication](docs/authentication.md)** - OAuth flow, JWT tokens, session management, and security measures

## Assumptions

1. Frontend (BetterAuth) handles the Google OAuth UI flow; backend receives the authorization code or token
2. Neon Serverless PostgreSQL provides sufficient performance for the expected load
3. OpenAI Agents SDK and Deepgram NOVA2 APIs are available with reasonable uptime
4. Checkout.com webhooks are delivered reliably with standard retry behavior
5. Users have modern browsers supporting Web Push API for push notifications
6. All servers run in UTC timezone configuration
7. Activity log retention of 30 days is sufficient for audit and debugging needs
8. Maximum of 3 recoverable deletions provides adequate safety net for accidental deletes
9. Audio is streamed in real time from the client to the STT provider over a WebSocket (via the backend as a relay); the backend does not persist voice recordings
