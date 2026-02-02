---
id: "022"
title: "Implement Phase 9 Event System and Background Jobs"
stage: green
date: 2026-01-25
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: system
command: /sp.implement 003 phase-9
labels: ["events", "jobs", "background-processing", "infrastructure"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/events/bus.py
  - backend/src/events/types.py
  - backend/src/events/handlers.py
  - backend/src/events/__init__.py
  - backend/src/jobs/queue.py
  - backend/src/jobs/worker.py
  - backend/src/jobs/__init__.py
  - backend/src/jobs/tasks/__init__.py
  - backend/src/jobs/tasks/streak_job.py
  - backend/src/jobs/tasks/credit_job.py
  - backend/src/jobs/tasks/subscription_job.py
  - backend/worker/main.py
  - backend/Dockerfile.worker
  - backend/tests/unit/events/test_event_bus.py
  - backend/tests/unit/jobs/test_queue.py
  - backend/tests/unit/jobs/test_streak_job.py
  - backend/tests/unit/jobs/test_credit_job.py
  - backend/tests/integration/test_event_flow.py
  - backend/tests/integration/test_job_execution.py
tests:
  - tests/unit/events/test_event_bus.py
  - tests/unit/jobs/test_queue.py
  - tests/unit/jobs/test_streak_job.py
  - tests/unit/jobs/test_credit_job.py
  - tests/integration/test_event_flow.py
  - tests/integration/test_job_execution.py
---

## Prompt

```text
003 phase-9
```

## Response

### Phase 9 Implementation Complete - Event System & Background Jobs

Successfully implemented Phase 9 (24 tasks: T197-T220) for the Perpetua Flow Backend API.

#### Event System (T197-T200)

1. **Event Bus** ([bus.py](backend/src/events/bus.py))
   - In-process synchronous event dispatch per plan.md AD-003
   - Handler registration with subscribe decorator
   - Error isolation between handlers
   - Global singleton with reset for testing

2. **Event Types** ([types.py](backend/src/events/types.py))
   - 16 event types covering all domain events
   - Task, Subtask, Note, AI, Subscription, Achievement, Reminder events
   - Automatic event_type string generation from class names

3. **Activity Log Handler** ([handlers.py](backend/src/events/handlers.py))
   - FR-052: Immutable audit trail for all events
   - Event-to-activity mapping for all entity types
   - Handler registration on application startup

#### Background Job Queue (T201-T204)

1. **JobQueueManager** ([queue.py](backend/src/jobs/queue.py))
   - PostgreSQL SKIP LOCKED pattern per research.md Section 4
   - Atomic job claiming prevents double-processing
   - Exponential backoff retry logic
   - Dead letter queue for failed jobs
   - Stale lock release mechanism

2. **JobWorker** ([worker.py](backend/src/jobs/worker.py))
   - Polling-based job execution
   - T220: Job monitoring metrics (success/failure/retry counts)
   - Graceful shutdown with signal handling

#### Worker Service (T205-T206)

1. **Worker Entry Point** ([worker/main.py](backend/worker/main.py))
   - T205: Signal handling for SIGINT/SIGTERM
   - T219: Daily job scheduler for UTC 00:00 jobs
   - Automatic scheduling of streak, credit, subscription jobs

2. **Dockerfile.worker** ([Dockerfile.worker](backend/Dockerfile.worker))
   - T206: Railway-ready container configuration

#### All 5 Job Types (T207-T211)

1. **reminder_fire** - T207: Already existed in reminder_job.py
2. **streak_calculate** - T208: Daily streak calculation (FR-043, SC-007)
3. **credit_expire** - T209: Credit expiration/grants (FR-040, FR-041)
4. **subscription_check** - T210: Grace period handling (FR-049, FR-050)
5. **recurring_task_generate** - T211: Already existed

#### Unit Tests (T212-T216)

- T212: Event dispatch handler invocation
- T213: SKIP LOCKED prevents double-processing
- T214: Job retry on failure
- T215: Streak UTC boundary handling (SC-007)
- T216: Credit expiration at UTC midnight

#### Integration Tests (T217-T218)

- T217: Event to activity log flow
- T218: Job execution end-to-end

#### Model Updates

- Added `consumed`, `expired`, `source_id` fields to AICreditLedger
- Added `retry_count`, `last_retry_at`, `last_payment_at`, `grace_warning_sent` to Subscription

### Checkpoint 9 Reached

Event System & Jobs Ready - All background processing operational.

### Next Steps

- Phase 10: AI Chat Widget (US6) - AI assistant with streaming chat
