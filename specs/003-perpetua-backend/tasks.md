# Tasks: Perpetua Flow Backend API

**Input**: Design documents from `/specs/003-perpetua-backend/`
**Prerequisites**: plan.md, spec.md, research.md, docs/data-model.md, docs/api-specification.md, docs/authentication.md

**TDD Enforcement**: ALL tasks follow Red -> Green -> Refactor workflow. Tests MUST be written and FAIL before implementation begins.

**Organization**: Tasks are organized by phase with clear dependency ordering. Phases 1-2 are foundational, Phase 3+ are organized by user story priority.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US13) or category (Infra, Contract, Validation)
- All tasks include exact file paths relative to `backend/`

## Path Conventions

```text
backend/
├── alembic/                    # Database migrations
│   └── versions/
├── src/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Environment configuration
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLModel database models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── api/                    # API route handlers
│   ├── services/               # Business logic layer
│   ├── events/                 # In-process event system
│   ├── jobs/                   # Background job processing
│   ├── integrations/           # External service clients
│   └── middleware/             # FastAPI middleware
├── tests/
│   ├── conftest.py
│   ├── factories/
│   ├── contract/
│   ├── integration/
│   └── unit/
├── worker/
│   └── main.py
├── pyproject.toml
├── alembic.ini
├── Dockerfile
├── Dockerfile.worker
└── .env.example
```

---

## Phase 1: Foundation - Project Setup (30 tasks)

**Purpose**: Project initialization, dependencies, configuration, and observability infrastructure

### Project Initialization

- [ ] T001 [P] Create backend directory structure per plan.md Project Structure
- [ ] T002 [P] Initialize pyproject.toml with Python 3.11+ and all dependencies (FastAPI, SQLModel, Alembic, PyJWT, httpx, python-dateutil, openai-agents, deepgram-sdk, slowapi)
- [ ] T003 [P] Create alembic.ini with Neon-compatible async configuration
- [ ] T004 [P] Create .env.example with all environment variables per plan.md Section 7
- [ ] T005 [P] Setup .gitignore for Python, .env, __pycache__, .pytest_cache

### Configuration & Dependencies

- [ ] T006 [Infra] Implement config.py with Pydantic Settings for all env vars in src/config.py (FR-061: configurable rate limits)
- [ ] T007 [Infra] Implement database connection with async SQLAlchemy engine in src/dependencies.py per research.md Section 3
- [ ] T008 [P] [Infra] Implement JWT key manager with RS256 and key rotation in src/dependencies.py per research.md Section 2
- [ ] T009 [P] [Infra] Create base SQLModel with common fields (id, created_at, updated_at) in src/models/base.py

### Observability Infrastructure (FR-065, FR-066, FR-067)

- [ ] T010 [P] [Infra] Implement structured JSON logging middleware with request_id, timestamp, user_id, action, outcome in src/middleware/logging.py (FR-065)
- [ ] T011 [P] [Infra] Implement Prometheus metrics middleware for request latency, error rates in src/middleware/metrics.py (FR-066)
- [ ] T012 [P] [Infra] Create health check endpoints (liveness, readiness) in src/api/health.py (FR-067)
- [ ] T012a [P] [Infra] Integration test: Readiness probe returns 503 when DB unavailable in tests/integration/test_health.py (FR-067)
- [ ] T013 [Infra] Implement request ID middleware for correlation in src/middleware/request_id.py

### Testing Infrastructure

- [ ] T014 [P] [Infra] Create pytest conftest.py with async fixtures, test database in tests/conftest.py
- [ ] T015 [P] [Infra] Setup factory-boy base classes in tests/factories/__init__.py
- [ ] T016 [P] [Infra] Create UserFactory in tests/factories/user_factory.py
- [ ] T017 [P] [Infra] Create TaskFactory in tests/factories/task_factory.py
- [ ] T018 [P] [Infra] Setup respx for HTTP mocking in tests/conftest.py

### Contract Testing Infrastructure

- [ ] T019 [P] [Contract] Setup schemathesis for API contract fuzzing in tests/contract/conftest.py
- [ ] T020 [P] [Contract] Create OpenAPI spec generator script in scripts/generate_openapi.py
- [ ] T021 [Contract] Create AI schema snapshot test framework in tests/contract/test_ai_schemas.py

### Database Migrations (All 8 migrations upfront)

- [ ] T022 [Infra] Create 001_initial_schema.py - Users, task_instances, task_templates, subtasks in alembic/versions/
- [ ] T023 [Infra] Create 002_notes_reminders.py - Notes, reminders tables in alembic/versions/
- [ ] T024 [Infra] Create 003_achievements.py - Achievement definitions, user_achievement_states in alembic/versions/
- [ ] T025 [Infra] Create 004_credits_subscriptions.py - AI credit ledger, subscriptions in alembic/versions/
- [ ] T026 [Infra] Create 005_activity_tombstones.py - Activity logs, deletion tombstones in alembic/versions/
- [ ] T027 [Infra] Create 006_notifications.py - Notifications table in alembic/versions/
- [ ] T028 [Infra] Create 007_job_queue.py - Background job queue table in alembic/versions/
- [ ] T029 [Infra] Create 008_indexes.py - Performance indexes for all tables in alembic/versions/

**Checkpoint 1**: Foundation Ready - All migrations complete, observability infra working, contract testing ready

---

## Phase 2: Core Models & Schemas (32 tasks)

**Purpose**: SQLModel database models and Pydantic request/response schemas

### Database Models

- [ ] T030 [P] [Infra] Create User model with google_id, email, name, avatar_url, timezone, tier in src/models/user.py per data-model.md Entity 1
- [ ] T031 [P] [Infra] Create TaskInstance model with all fields including version for optimistic locking in src/models/task.py per data-model.md Entity 2 (FR-014)
- [ ] T032 [P] [Infra] Create TaskTemplate model with rrule field in src/models/task.py per data-model.md Entity 3 (FR-015)
- [ ] T033 [P] [Infra] Create Subtask model with order_index and source enum in src/models/subtask.py per data-model.md Entity 4 (FR-021)
- [ ] T034 [P] [Infra] Create Note model with voice_url, voice_duration_seconds, transcription_status in src/models/note.py per data-model.md Entity 5
- [ ] T035 [P] [Infra] Create Reminder model with type enum, offset_minutes, scheduled_at in src/models/reminder.py per data-model.md Entity 6 (FR-025)
- [ ] T036 [P] [Infra] Create AchievementDefinition model with predefined seed data in src/models/achievement.py per data-model.md Entity 7
- [ ] T037 [P] [Infra] Create UserAchievementState model with lifetime stats and unlocked_achievements in src/models/achievement.py per data-model.md Entity 8
- [ ] T038 [P] [Infra] Create AICreditLedger model with credit_type, operation, expires_at in src/models/credit.py per data-model.md Entity 9 (FR-042)
- [ ] T039 [P] [Infra] Create Subscription model with status enum and grace_period_end in src/models/subscription.py per data-model.md Entity 10
- [ ] T040 [P] [Infra] Create ActivityLog model with entity_type, action, source, metadata in src/models/activity.py per data-model.md Entity 11 (FR-052)
- [ ] T041 [P] [Infra] Create DeletionTombstone model with entity_data JSON in src/models/tombstone.py per data-model.md Entity 12 (FR-062)
- [ ] T042 [P] [Infra] Create Notification model with type enum, read status in src/models/notification.py per data-model.md Entity 13
- [ ] T043 [P] [Infra] Create JobQueue model with SKIP LOCKED fields in src/models/job_queue.py per research.md Section 4
- [ ] T044 [P] [Infra] Create RefreshToken model for session management in src/models/auth.py per authentication.md
- [ ] T045 [P] [Infra] Create IdempotencyKey model for request deduplication in src/models/idempotency.py per research.md Section 12 (FR-059)

### Pydantic Request/Response Schemas

- [ ] T046 [P] [Infra] Create auth schemas (TokenResponse, RefreshRequest, GoogleCallbackRequest) in src/schemas/auth.py
- [ ] T047 [P] [Infra] Create task schemas (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse) in src/schemas/task.py (FR-007, FR-058)
- [ ] T048 [P] [Infra] Create subtask schemas (SubtaskCreate, SubtaskUpdate, SubtaskResponse) in src/schemas/subtask.py
- [ ] T049 [P] [Infra] Create note schemas (NoteCreate, NoteUpdate, NoteResponse, NoteConvertResponse) in src/schemas/note.py
- [ ] T050 [P] [Infra] Create reminder schemas (ReminderCreate, ReminderUpdate, ReminderResponse) in src/schemas/reminder.py
- [ ] T051 [P] [Infra] Create AI schemas (ChatRequest, ChatResponse, SubtaskGenerationResponse, TranscriptionResponse) in src/schemas/ai.py
- [ ] T052 [P] [Infra] Create achievement schemas (AchievementResponse, UserStatsResponse, EffectiveLimitsResponse) in src/schemas/achievement.py
- [ ] T053 [P] [Infra] Create subscription schemas (SubscriptionResponse, CheckoutSessionResponse) in src/schemas/subscription.py
- [ ] T054 [P] [Infra] Create notification schemas (NotificationResponse, NotificationListResponse) in src/schemas/notification.py
- [ ] T055 [P] [Infra] Create common schemas (PaginationParams, PaginatedResponse, ErrorResponse) in src/schemas/common.py (FR-060)

### AI Agent Pydantic Schemas (for openai-agents output_type)

- [ ] T056 [P] [Infra] Create SubtaskSuggestion and SubtaskGenerationResult schemas in src/schemas/ai_agents.py per research.md Section 5
- [ ] T057 [P] [Infra] Create ActionSuggestion schema for chat agent in src/schemas/ai_agents.py
- [ ] T058 [P] [Infra] Create TaskSuggestion schema for note conversion agent in src/schemas/ai_agents.py

### Enums

- [ ] T059 [P] [Infra] Create all enums (TaskPriority, CompletedBy, ReminderType, CreditType, SubscriptionStatus, etc.) in src/schemas/enums.py
- [ ] T060 [Infra] Export all models in src/models/__init__.py
- [ ] T061 [Infra] Export all schemas in src/schemas/__init__.py

**Checkpoint 2**: Models & Schemas Ready - All database models and API schemas defined

---

## Phase 3: User Story 1 - User Authentication via Google OAuth (Priority: P1 - MVP) (28 tasks)

**Goal**: Authenticate users via Google OAuth and issue JWT tokens (FR-001 to FR-006)

**Independent Test**: Complete OAuth flow with Google, verify token issuance, test refresh flow

### RED: Write FAILING Tests First

- [ ] T062 [P] [US1] Test: Google OAuth callback creates new user in tests/unit/services/test_auth_service.py
- [ ] T063 [P] [US1] Test: Google OAuth callback returns existing user in tests/unit/services/test_auth_service.py
- [ ] T064 [P] [US1] Test: Access token JWT contains correct claims (sub, email, tier) in tests/unit/services/test_auth_service.py
- [ ] T065 [P] [US1] Test: Refresh token rotation issues new tokens in tests/unit/services/test_auth_service.py
- [ ] T066 [P] [US1] Test: Invalid refresh token returns 401 in tests/unit/services/test_auth_service.py
- [ ] T067 [P] [US1] Test: Expired access token returns 401 with refresh_required flag in tests/integration/test_auth_flow.py (FR-006)
- [ ] T068 [P] [US1] Contract test: POST /auth/google/callback schema validation in tests/contract/test_auth_contract.py

### GREEN: Implement Authentication

- [ ] T069 [US1] Implement GoogleOAuthClient with JWKS caching in src/integrations/google_oauth.py per research.md Section 1 (FR-001)
- [ ] T070 [US1] Implement ID token verification with audience validation in src/integrations/google_oauth.py
- [ ] T071 [US1] Implement AuthService.create_or_update_user in src/services/auth_service.py
- [ ] T072 [US1] Implement AuthService.generate_tokens (access + refresh) with RS256 in src/services/auth_service.py (FR-002, FR-003)
- [ ] T073 [US1] Implement AuthService.refresh_tokens with rotation in src/services/auth_service.py (FR-003)
- [ ] T074 [US1] Implement AuthService.revoke_refresh_token for logout in src/services/auth_service.py
- [ ] T075 [US1] Implement auth middleware for JWT validation in src/middleware/auth.py (FR-004)
- [ ] T076 [US1] Implement get_current_user dependency in src/dependencies.py

### API Endpoints

- [ ] T077 [US1] Implement POST /api/v1/auth/google/callback endpoint in src/api/auth.py per api-specification.md Section 2.1
- [ ] T078 [US1] Implement POST /api/v1/auth/refresh endpoint in src/api/auth.py per api-specification.md Section 2.2 (per plan.md AD-001 Refresh Token Storage)
- [ ] T078a [US1] Implement GET /api/v1/users/me endpoint in src/api/users.py per api-specification.md Section 3.1
- [ ] T078b [US1] Implement PATCH /api/v1/users/me endpoint in src/api/users.py per api-specification.md Section 3.2 (FR-070)
- [ ] T078c [P] [US1] Test: User profile update validates timezone and name in tests/unit/services/test_user_service.py (FR-070)
- [ ] T079 [US1] Implement POST /api/v1/auth/logout endpoint in src/api/auth.py per api-specification.md Section 2.3
- [ ] T080 [US1] Implement GET /api/v1/.well-known/jwks.json endpoint in src/api/auth.py per authentication.md

### Rate Limiting

- [ ] T081 [US1] Implement rate limiting middleware with slowapi in src/middleware/rate_limit.py (FR-061)
- [ ] T082 [US1] Apply 10 req/min rate limit to auth endpoints in src/api/auth.py (FR-061)

### REFACTOR

- [ ] T083 [US1] Add structured logging to auth flow in src/services/auth_service.py
- [ ] T084 [US1] Add metrics for auth operations (login_success, login_failure, token_refresh) in src/services/auth_service.py
- [ ] T085 [US1] Add CSRF protection to OAuth state parameter in src/integrations/google_oauth.py
- [ ] T086 [US1] Add integration test for full OAuth flow in tests/integration/test_auth_flow.py

### Error Handling

- [ ] T087 [US1] Implement global error handler with standard error response in src/middleware/error_handler.py per api-specification.md Section 11
- [ ] T088 [US1] Implement 401 UNAUTHORIZED responses with proper codes in src/middleware/auth.py (FR-004)
- [ ] T089 [US1] Implement 403 FORBIDDEN for cross-user access in src/dependencies.py (FR-005)

**Checkpoint 3**: MVP Auth Ready - Users can authenticate via Google OAuth and update profile (SC-001: <10s sign-in)

---

## Phase 4: User Story 2 - Task Creation and Management (Priority: P1 - MVP) (37 tasks)

**Goal**: Full task CRUD with subtasks, auto-completion, and optimistic locking (FR-007 to FR-014)

**Independent Test**: Create task, add subtasks, complete subtasks to trigger auto-completion, verify version conflicts

### RED: Write FAILING Tests First (Task CRUD)

- [ ] T090 [P] [US2] Test: Create task with title, priority, due_date in tests/unit/services/test_task_service.py (FR-007)
- [ ] T091 [P] [US2] Test: Task title validation 1-200 chars in tests/unit/services/test_task_service.py
- [ ] T092 [P] [US2] Test: Description max length enforced by tier in tests/unit/services/test_task_service.py (FR-007)
- [ ] T093 [P] [US2] Test: Update task with optimistic locking returns 409 on stale version in tests/unit/services/test_task_service.py (FR-014)
- [ ] T094 [P] [US2] Test: Complete task sets completed_at and completed_by in tests/unit/services/test_task_service.py (FR-008)
- [ ] T095 [P] [US2] Test: Auto-complete task when all subtasks complete in tests/unit/services/test_task_service.py (FR-009)
- [ ] T096 [P] [US2] Test: Force-complete marks all subtasks complete in tests/unit/services/test_task_service.py (FR-010)
- [ ] T097 [P] [US2] Test: Cannot complete archived task returns 409 in tests/unit/services/test_task_service.py (FR-011)
- [ ] T098 [P] [US2] Test: Soft delete sets hidden flag in tests/unit/services/test_task_service.py (FR-012)
- [ ] T099 [P] [US2] Test: Hard delete creates tombstone in tests/unit/services/test_task_service.py (FR-012)
- [ ] T100 [P] [US2] Contract test: Task CRUD endpoints schema validation in tests/contract/test_tasks_contract.py

### RED: Write FAILING Tests First (Subtasks)

- [ ] T101 [P] [US2] Test: Create subtask with correct order_index in tests/unit/services/test_task_service.py
- [ ] T102 [P] [US2] Test: Free user limited to 4 subtasks in tests/unit/services/test_task_service.py (FR-019)
- [ ] T103 [P] [US2] Test: Pro user limited to 10 subtasks in tests/unit/services/test_task_service.py (FR-019)
- [ ] T104 [P] [US2] Test: Reorder subtasks maintains gapless indices in tests/unit/services/test_task_service.py (FR-020)
- [ ] T105 [P] [US2] Test: Subtask source tracked (user vs ai) in tests/unit/services/test_task_service.py (FR-021)

### GREEN: Implement Task Service

- [ ] T106 [US2] Implement TaskService.create_task with tier-based validation in src/services/task_service.py
- [ ] T107 [US2] Implement TaskService.get_task with user ownership check in src/services/task_service.py
- [ ] T108 [US2] Implement TaskService.list_tasks with pagination and filters in src/services/task_service.py (FR-060)
- [ ] T109 [US2] Implement TaskService.update_task with optimistic locking in src/services/task_service.py (FR-014)
- [ ] T110 [US2] Implement TaskService.complete_task with completion tracking in src/services/task_service.py (FR-008)
- [ ] T111 [US2] Implement TaskService.force_complete_task in src/services/task_service.py (FR-010)
- [ ] T112 [US2] Implement TaskService.soft_delete_task in src/services/task_service.py (FR-012)
- [ ] T113 [US2] Implement TaskService.hard_delete_task with tombstone in src/services/task_service.py (FR-012)
- [ ] T114 [US2] Implement subtask auto-completion check in src/services/task_service.py (FR-009)

### GREEN: Implement Subtask Methods

- [ ] T115 [US2] Implement TaskService.create_subtask with limit check in src/services/task_service.py (FR-019)
- [ ] T116 [US2] Implement TaskService.update_subtask in src/services/task_service.py
- [ ] T117 [US2] Implement TaskService.delete_subtask with reordering in src/services/task_service.py
- [ ] T118 [US2] Implement TaskService.reorder_subtasks in src/services/task_service.py (FR-020)

### API Endpoints

- [ ] T119 [US2] Implement GET /api/v1/tasks with pagination and filters in src/api/tasks.py per api-specification.md Section 3.1
- [ ] T120 [US2] Implement GET /api/v1/tasks/:id with subtasks and reminders in src/api/tasks.py per api-specification.md Section 3.2
- [ ] T121 [US2] Implement POST /api/v1/tasks with idempotency in src/api/tasks.py per api-specification.md Section 3.3 (FR-059)
- [ ] T122 [US2] Implement PATCH /api/v1/tasks/:id with PATCH semantics in src/api/tasks.py per api-specification.md Section 3.4 (FR-058)
- [ ] T123 [US2] Implement POST /api/v1/tasks/:id/force-complete in src/api/tasks.py per api-specification.md Section 3.5
- [ ] T124 [US2] Implement DELETE /api/v1/tasks/:id in src/api/tasks.py per api-specification.md Section 3.6

### Subtask API Endpoints

- [ ] T125 [US2] Implement POST /api/v1/tasks/:task_id/subtasks in src/api/subtasks.py per api-specification.md Section 4.1
- [ ] T126 [US2] Implement PATCH /api/v1/subtasks/:id in src/api/subtasks.py per api-specification.md Section 4.2
- [ ] T127 [US2] Implement PUT /api/v1/tasks/:task_id/subtasks/reorder in src/api/subtasks.py per api-specification.md Section 4.3
- [ ] T128 [US2] Implement DELETE /api/v1/subtasks/:id in src/api/subtasks.py per api-specification.md Section 4.4

### REFACTOR

- [ ] T129 [US2] Add integration test for full task lifecycle in tests/integration/test_task_lifecycle.py
- [ ] T130 [US2] Add metrics for task operations in src/services/task_service.py
- [ ] T130a [P] [US2] Test: Task creation fails if due_date > created_at + 30 days in tests/unit/services/test_task_service.py (FR-013)
- [ ] T130b [US2] Implement 30-day max duration validation in src/services/task_service.py (FR-013)

**Checkpoint 4**: MVP Core Ready - Full task CRUD with subtasks working (SC-004: 99.9% success rate)

---

## Phase 5: User Story 4 - Subtask Management (Priority: P2) (8 tasks)

**Goal**: Enhanced subtask management with tier limits (FR-019 to FR-021)

**Independent Test**: Add subtasks to task, verify limits enforced, reorder subtasks

**Note**: Core subtask functionality implemented in Phase 4. This phase adds integration tests and refinements.

### Integration & Validation

- [ ] T131 [P] [US4] Integration test: Subtask limit enforcement across tiers in tests/integration/test_subtask_limits.py
- [ ] T132 [P] [US4] Integration test: Subtask ordering persistence after reorder in tests/integration/test_subtask_ordering.py
- [ ] T133 [US4] Add effective_subtask_limit calculation with achievement perks in src/services/task_service.py
- [ ] T134 [US4] Implement subtask completion handler for auto-complete check in src/events/handlers.py

### REFACTOR

- [ ] T135 [US4] Extract subtask limit logic to dedicated utility in src/lib/limits.py
- [ ] T136 [US4] Add validation for cascading delete of subtasks in src/services/task_service.py
- [ ] T137 [US4] Add metrics for subtask operations in src/services/task_service.py
- [ ] T138 [US4] Document subtask API behaviors in OpenAPI spec

**Checkpoint 5**: Subtask Management Ready - Complete subtask CRUD with tier enforcement

---

## Phase 6: User Story 3 - Recurring Task Templates (Priority: P2) (20 tasks)

**Goal**: RRULE-based recurring tasks with completion-triggered generation (FR-015 to FR-018)

**Independent Test**: Create recurring task template, complete instance, verify next instance generated

### RED: Write FAILING Tests First

- [ ] T139 [P] [US3] Test: Create recurring task template with RRULE in tests/unit/services/test_recurring_service.py (FR-015)
- [ ] T140 [P] [US3] Test: RRULE parsing for daily/weekly/monthly patterns in tests/unit/utils/test_rrule.py (FR-015)
- [ ] T141 [P] [US3] Test: Next instance generated on completion in tests/unit/services/test_recurring_service.py (FR-016)
- [ ] T142 [P] [US3] Test: Completion not rolled back if generation fails in tests/unit/services/test_recurring_service.py (FR-017)
- [ ] T143 [P] [US3] Test: Cannot edit recurrence on past instances in tests/unit/services/test_recurring_service.py (FR-018)
- [ ] T144 [P] [US3] Test: Calculate next due date with RRULE.after() in tests/unit/utils/test_rrule.py

### GREEN: Implement Recurring Tasks

- [ ] T145 [US3] Implement rrule utility functions in src/lib/rrule.py per research.md Section 10
- [ ] T146 [US3] Implement RecurringTaskService.create_template in src/services/recurring_service.py
- [ ] T147 [US3] Implement RecurringTaskService.generate_next_instance in src/services/recurring_service.py (FR-016)
- [ ] T148 [US3] Implement completion handler that triggers generation in src/events/handlers.py
- [ ] T149 [US3] Implement RecurringTaskService.update_template with future-only option in src/services/recurring_service.py (FR-018)

### Background Job for Recurring Task Generation

- [ ] T150 [US3] Implement recurring_task_generate job type in src/jobs/tasks/recurring_job.py
- [ ] T151 [US3] Add job scheduling on task completion in src/services/task_service.py
- [ ] T152 [US3] Add retry logic for failed generation in src/jobs/tasks/recurring_job.py (FR-017)

### API Endpoints (Templates)

- [ ] T153 [US3] Implement GET /api/v1/templates in src/api/templates.py
- [ ] T154 [US3] Implement POST /api/v1/templates in src/api/templates.py
- [ ] T155 [US3] Implement PATCH /api/v1/templates/:id in src/api/templates.py
- [ ] T156 [US3] Implement DELETE /api/v1/templates/:id in src/api/templates.py

### REFACTOR

- [ ] T157 [US3] Add integration test for recurring task lifecycle in tests/integration/test_recurring_lifecycle.py
- [ ] T158 [US3] Add human-readable RRULE description utility in src/lib/rrule.py

**Checkpoint 6**: Recurring Tasks Ready - Templates generate instances on completion

---

## Phase 7: User Story 5 - Notes with Voice Recording (Priority: P2) (18 tasks)

**Goal**: Text and voice notes with tier-based limits (FR-022 to FR-024)

**Independent Test**: Create text note, verify Pro-only voice note creation

**US5 Split Note**: This phase implements core note CRUD with text notes and tier limits. AI-powered note conversion (Phase 12) and voice transcription (Phase 13) depend on Phase 10's AI infrastructure being completed first.

### RED: Write FAILING Tests First

- [ ] T159 [P] [US5] Test: Create text note with content validation in tests/unit/services/test_note_service.py (FR-023)
- [ ] T160 [P] [US5] Test: Free user limited to 10 notes in tests/unit/services/test_note_service.py (FR-022)
- [ ] T161 [P] [US5] Test: Pro user limited to 25 notes in tests/unit/services/test_note_service.py (FR-022)
- [ ] T162 [P] [US5] Test: Voice note requires Pro tier in tests/unit/services/test_note_service.py (FR-024)
- [ ] T163 [P] [US5] Test: Voice recording max 300 seconds in tests/unit/services/test_note_service.py (FR-036)
- [ ] T164 [P] [US5] Contract test: Note CRUD endpoints in tests/contract/test_notes_contract.py

### GREEN: Implement Note Service

- [ ] T165 [US5] Implement NoteService.create_note with tier limits in src/services/note_service.py (FR-022)
- [ ] T166 [US5] Implement NoteService.get_note with ownership check in src/services/note_service.py
- [ ] T167 [US5] Implement NoteService.list_notes with pagination in src/services/note_service.py
- [ ] T168 [US5] Implement NoteService.update_note in src/services/note_service.py
- [ ] T169 [US5] Implement NoteService.delete_note in src/services/note_service.py
- [ ] T170 [US5] Add effective_note_limit with achievement perks in src/services/note_service.py

### API Endpoints

- [ ] T171 [US5] Implement GET /api/v1/notes in src/api/notes.py per api-specification.md Section 5.1
- [ ] T172 [US5] Implement POST /api/v1/notes in src/api/notes.py per api-specification.md Section 5.2
- [ ] T173 [US5] Implement PATCH /api/v1/notes/:id in src/api/notes.py
- [ ] T174 [US5] Implement DELETE /api/v1/notes/:id in src/api/notes.py

### REFACTOR

- [ ] T175 [US5] Add integration test for note lifecycle in tests/integration/test_note_lifecycle.py
- [ ] T176 [US5] Add metrics for note operations in src/services/note_service.py

**Checkpoint 7**: Notes Ready - Text notes with tier limits working

---

## Phase 8: User Story 8 - Reminder System (Priority: P3) (22 tasks)

**Goal**: Task reminders with relative timing and dual notification delivery (FR-025 to FR-028)

**Independent Test**: Create reminder 15 min before due, verify notification fires at correct time

### RED: Write FAILING Tests First

- [ ] T177 [P] [US8] Test: Create before reminder calculates scheduled_at in tests/unit/services/test_reminder_service.py
- [ ] T178 [P] [US8] Test: Reminder limit 5 per task enforced in tests/unit/services/test_reminder_service.py (FR-025)
- [ ] T179 [P] [US8] Test: Relative reminder recalculates when due date changes in tests/unit/services/test_reminder_service.py (FR-026)
- [ ] T180 [P] [US8] Test: Recovered task does not fire past reminders in tests/unit/services/test_reminder_service.py (FR-027)
- [ ] T181 [P] [US8] Test: Reminder fires at scheduled time in tests/unit/jobs/test_reminder_job.py
- [ ] T182 [P] [US8] Contract test: Reminder endpoints in tests/contract/test_reminders_contract.py

### GREEN: Implement Reminder Service

- [ ] T183 [US8] Implement ReminderService.create_reminder with scheduled_at calculation in src/services/reminder_service.py
- [ ] T184 [US8] Implement ReminderService.update_reminder with recalculation in src/services/reminder_service.py (FR-026)
- [ ] T185 [US8] Implement ReminderService.delete_reminder in src/services/reminder_service.py
- [ ] T186 [US8] Implement reminder recalculation on task due date change in src/services/task_service.py (FR-026)
- [ ] T187 [US8] Implement skip_past_reminders flag for recovered tasks in src/services/reminder_service.py (FR-027)

### Background Job for Reminder Firing

- [ ] T188 [US8] Implement reminder_fire job type in src/jobs/tasks/reminder_job.py
- [ ] T189 [US8] Implement reminder scheduling in job queue in src/services/reminder_service.py
- [ ] T190 [US8] Implement notification creation on reminder fire in src/jobs/tasks/reminder_job.py (FR-028)

### API Endpoints

- [ ] T191 [US8] Implement POST /api/v1/tasks/:task_id/reminders in src/api/reminders.py per api-specification.md Section 6.1
- [ ] T192 [US8] Implement PATCH /api/v1/reminders/:id in src/api/reminders.py per api-specification.md Section 6.2
- [ ] T193 [US8] Implement DELETE /api/v1/reminders/:id in src/api/reminders.py per api-specification.md Section 6.3

### REFACTOR

- [ ] T194 [US8] Add integration test for reminder lifecycle in tests/integration/test_reminder_lifecycle.py
- [ ] T195 [US8] Add metrics for reminder operations in src/services/reminder_service.py
- [ ] T196 [US8] Implement push notification delivery method in src/services/notification_service.py (FR-028)

**Checkpoint 8**: Reminders Ready - Notifications fire at scheduled times (SC-012: 95% within 60s)

---

## Phase 9: Event System & Background Jobs (24 tasks)

**Goal**: In-process event bus and PostgreSQL job queue with all 5 job types

### Event System

- [ ] T197 [P] [Infra] Implement event bus with sync dispatch in src/events/bus.py per plan.md AD-003
- [ ] T198 [P] [Infra] Define event types (task.created, task.completed, task.deleted, etc.) in src/events/types.py
- [ ] T199 [P] [Infra] Implement event handler registry in src/events/bus.py
- [ ] T200 [P] [Infra] Implement activity log handler for all events in src/events/handlers.py (FR-052)

### Background Job Queue

- [ ] T201 [Infra] Implement JobQueue with SKIP LOCKED pattern in src/jobs/queue.py per research.md Section 4
- [ ] T202 [Infra] Implement job worker with polling in src/jobs/worker.py
- [ ] T203 [Infra] Implement job retry logic with max_retries in src/jobs/worker.py
- [ ] T204 [Infra] Implement dead letter handling for failed jobs in src/jobs/worker.py

### Worker Service Entry Point

- [ ] T205 [Infra] Implement worker main.py with signal handling in worker/main.py
- [ ] T206 [P] [Infra] Create Dockerfile.worker for Railway deployment

### All 5 Job Types

- [ ] T207 [P] [Infra] Implement reminder_fire job handler in src/jobs/tasks/reminder_job.py
- [ ] T208 [P] [Infra] Implement streak_calculate job (UTC 00:00 daily) in src/jobs/tasks/streak_job.py (FR-043)
- [ ] T209 [P] [Infra] Implement credit_expire job (UTC 00:00 daily) in src/jobs/tasks/credit_job.py (FR-040)
- [ ] T210 [P] [Infra] Implement subscription_check job (daily) in src/jobs/tasks/subscription_job.py (FR-049)
- [ ] T211 [P] [Infra] Implement recurring_task_generate job in src/jobs/tasks/recurring_job.py (FR-016)

### Tests for Event System & Jobs

- [ ] T212 [P] [Infra] Test: Event dispatch calls registered handlers in tests/unit/events/test_bus.py
- [ ] T213 [P] [Infra] Test: Job queue SKIP LOCKED prevents double-processing in tests/unit/jobs/test_queue.py
- [ ] T214 [P] [Infra] Test: Job retry on failure in tests/unit/jobs/test_worker.py
- [ ] T215 [P] [Infra] Test: Streak calculation UTC boundary handling in tests/unit/jobs/test_streak_job.py (SC-007)
- [ ] T216 [P] [Infra] Test: Credit expiration at UTC midnight in tests/unit/jobs/test_credit_job.py

### Integration Tests

- [ ] T217 [Infra] Integration test: Event to activity log flow in tests/integration/test_event_flow.py
- [ ] T218 [Infra] Integration test: Job execution end-to-end in tests/integration/test_job_execution.py

### Scheduled Job Configuration

- [ ] T219 [Infra] Implement daily job scheduler in worker/main.py for streak, credit, subscription jobs
- [ ] T220 [Infra] Add job monitoring metrics in src/jobs/worker.py

**Checkpoint 9**: Event System & Jobs Ready - All background processing operational

---

## Phase 10: User Story 6 - AI Chat Widget (Priority: P3) (24 tasks)

**Goal**: AI assistant with streaming chat and action suggestions (FR-029 to FR-035)

**Independent Test**: Send chat message, receive streaming response, confirm AI-suggested action

### RED: Write FAILING Tests First

- [ ] T221 [P] [US6] Test: AI chat deducts 1 credit in tests/unit/services/test_ai_service.py (FR-030)
- [ ] T222 [P] [US6] Test: AI chat returns 402 when 0 credits in tests/unit/services/test_ai_service.py
- [ ] T223 [P] [US6] Test: AI action suggestion requires confirmation in tests/unit/services/test_ai_service.py (FR-034)
- [ ] T224 [P] [US6] Test: AI request warning at 5 requests per task in tests/unit/services/test_ai_service.py (FR-035)
- [ ] T225 [P] [US6] Test: AI request blocked at 10 requests per task in tests/unit/services/test_ai_service.py (FR-035)
- [ ] T226 [P] [US6] Test: AI service unavailable returns 503 in tests/unit/services/test_ai_service.py
- [ ] T227 [P] [US6] Contract test: AI endpoints in tests/contract/test_ai_contract.py

### GREEN: Implement AI Integration

- [ ] T228 [US6] Implement AIAgentClient with openai-agents SDK in src/integrations/ai_agent.py per research.md Section 5
- [ ] T229 [US6] Define PerpetualFlowAssistant agent with suggest_action tool in src/integrations/ai_agent.py
- [ ] T230 [US6] Implement streaming chat with Runner.run_streamed() in src/integrations/ai_agent.py
- [ ] T231 [US6] Implement 30-second timeout handling in src/integrations/ai_agent.py
- [ ] T232 [US6] Implement AIService.chat with credit check in src/services/ai_service.py (FR-030)
- [ ] T233 [US6] Implement action suggestion validation in src/services/ai_service.py (FR-034)
- [ ] T234 [US6] Implement per-task AI request counter in src/services/ai_service.py (FR-035)

### API Endpoints

- [ ] T235 [US6] Implement POST /api/v1/ai/chat with SSE streaming in src/api/ai.py per api-specification.md Section 7.1
- [ ] T236 [US6] Implement POST /api/v1/ai/confirm-action in src/api/ai.py per api-specification.md Section 7.3
- [ ] T237 [US6] Implement GET /api/v1/ai/credits in src/api/ai.py per api-specification.md Section 7.5
- [ ] T238 [US6] Apply 20 req/min rate limit to AI endpoints in src/api/ai.py (FR-061)

### REFACTOR

- [ ] T239 [US6] Add respx mock for OpenAI in tests/conftest.py
- [ ] T240 [US6] Add integration test for AI chat flow in tests/integration/test_ai_features.py
- [ ] T241 [US6] Add AI interaction logging (immutable) in src/services/ai_service.py (FR-052)
- [ ] T242 [US6] Implement AI service unavailable fallback in src/integrations/ai_agent.py

**Checkpoint 10**: AI Chat Ready - Streaming chat with action suggestions (SC-005: 95% <5s)

---

## Phase 11: User Story 7 - Auto Subtask Generation (Priority: P3) (12 tasks)

**Goal**: AI-generated subtask suggestions (FR-031)

**Independent Test**: Request subtask generation for task, review suggestions

### RED: Write FAILING Tests First

- [ ] T243 [P] [US7] Test: Subtask generation deducts 1 credit (flat) in tests/unit/services/test_ai_service.py (FR-031)
- [ ] T244 [P] [US7] Test: Generated subtasks respect user tier limit in tests/unit/services/test_ai_service.py
- [ ] T245 [P] [US7] Test: SubtaskGenerator agent returns structured output in tests/unit/integrations/test_ai_agent.py

### GREEN: Implement Subtask Generation

- [ ] T246 [US7] Define SubtaskGenerator agent with output_type in src/integrations/ai_agent.py per research.md Section 5
- [ ] T247 [US7] Implement AIService.generate_subtasks in src/services/ai_service.py (FR-031)
- [ ] T248 [US7] Implement subtask limit enforcement in generation in src/services/ai_service.py

### API Endpoints

- [ ] T249 [US7] Implement POST /api/v1/ai/generate-subtasks in src/api/ai.py per api-specification.md Section 7.2

### REFACTOR

- [ ] T250 [US7] Add integration test for subtask generation in tests/integration/test_ai_features.py
- [ ] T251 [US7] Add metrics for subtask generation in src/services/ai_service.py
- [ ] T252 [US7] Document subtask generation behavior in OpenAPI spec

**Checkpoint 11**: AI Subtasks Ready - Generate subtask suggestions

---

## Phase 12: User Story 5 Extended - Note to Task Conversion (Priority: P3) (10 tasks)

**Goal**: AI-powered note to task conversion (FR-032)

**Independent Test**: Create note, request conversion, review task suggestion

**US5 Split Note**: This phase extends US5 (Phase 7) with AI-powered note conversion. Requires Phase 10's AI infrastructure (AIService, credit consumption).

### RED: Write FAILING Tests First

- [ ] T253 [P] [US5] Test: Note conversion deducts 1 credit in tests/unit/services/test_ai_service.py (FR-032)
- [ ] T254 [P] [US5] Test: NoteConverter agent returns TaskSuggestion in tests/unit/integrations/test_ai_agent.py
- [ ] T255 [P] [US5] Test: Note archived after conversion confirmation in tests/unit/services/test_note_service.py

### GREEN: Implement Note Conversion

- [ ] T256 [US5] Define NoteConverter agent with output_type=TaskSuggestion in src/integrations/ai_agent.py
- [ ] T257 [US5] Implement AIService.convert_note_to_task in src/services/ai_service.py (FR-032)
- [ ] T258 [US5] Implement note archiving on conversion in src/services/note_service.py

### API Endpoints

- [ ] T259 [US5] Implement POST /api/v1/notes/:id/convert in src/api/notes.py per api-specification.md Section 5.3

### REFACTOR

- [ ] T260 [US5] Add integration test for note conversion in tests/integration/test_ai_features.py
- [ ] T261 [US5] Add metrics for note conversion in src/services/ai_service.py
- [ ] T262 [US5] Document conversion flow in OpenAPI spec

**Checkpoint 12**: Note Conversion Ready - AI converts notes to tasks

---

## Phase 13: Voice Transcription (Priority: P3) (12 tasks)

**Goal**: Deepgram NOVA2 transcription for Pro users (FR-033, FR-036)

**Independent Test**: Upload voice note, verify transcription returns

**US5 Split Note**: This phase extends US5 (Phase 7) with voice transcription via Deepgram. Requires Phase 10's AI infrastructure (credit consumption) and Deepgram client.

### RED: Write FAILING Tests First

- [ ] T263 [P] [US5] Test: Voice transcription requires Pro tier in tests/unit/services/test_ai_service.py
- [ ] T264 [P] [US5] Test: Transcription costs 5 credits per minute in tests/unit/services/test_ai_service.py (FR-033)
- [ ] T265 [P] [US5] Test: Max 300 seconds audio enforced in tests/unit/services/test_ai_service.py (FR-036)
- [ ] T266 [P] [US5] Test: Deepgram client handles timeout in tests/unit/integrations/test_deepgram.py

### GREEN: Implement Transcription

- [ ] T267 [US5] Implement DeepgramClient with NOVA2 model in src/integrations/deepgram_client.py per research.md Section 6
- [ ] T268 [US5] Implement AIService.transcribe_voice with credit calculation in src/services/ai_service.py (FR-033)
- [ ] T269 [US5] Implement transcription status tracking in src/services/note_service.py

### API Endpoints

- [ ] T270 [US5] Implement POST /api/v1/ai/transcribe in src/api/ai.py per api-specification.md Section 7.4

### REFACTOR

- [ ] T271 [US5] Add respx mock for Deepgram in tests/conftest.py
- [ ] T272 [US5] Add integration test for transcription in tests/integration/test_ai_features.py
- [ ] T273 [US5] Add transcription metrics in src/services/ai_service.py
- [ ] T273a [P] [US5] Test: WebSocket voice session auto-closes at 300 seconds with partial transcript in tests/integration/test_websocket_voice.py (FR-036)
- [ ] T273b [P] [US5] Test: WebSocket returns MAX_DURATION_EXCEEDED error at timeout in tests/integration/test_websocket_voice.py (FR-036)

**Checkpoint 13**: Voice Transcription Ready - Pro users can transcribe voice notes (per plan.md Audio Format Requirements)

---

## Phase 14: User Story 11 - AI Credit System (Priority: P4) (18 tasks)

**Goal**: Credit management with FIFO consumption (FR-037 to FR-042)

**Independent Test**: Verify kickstart credits, consume in FIFO order, test expiration

### RED: Write FAILING Tests First

- [ ] T274 [P] [US11] Test: New user receives 5 kickstart credits in tests/unit/services/test_credit_service.py (FR-037)
- [ ] T275 [P] [US11] Test: Pro user receives 10 daily credits in tests/unit/services/test_credit_service.py (FR-038)
- [ ] T276 [P] [US11] Test: Pro user receives 100 monthly credits in tests/unit/services/test_credit_service.py (FR-039)
- [ ] T277 [P] [US11] Test: FIFO consumption order (daily -> subscription -> purchased) in tests/unit/services/test_credit_service.py (FR-042)
- [ ] T278 [P] [US11] Test: Daily credits expire at UTC 00:00 in tests/unit/services/test_credit_service.py (FR-040)
- [ ] T279 [P] [US11] Test: Up to 50 subscription credits carry over in tests/unit/services/test_credit_service.py (FR-041)
- [ ] T280 [P] [US11] Test: Credit FIFO with race conditions in tests/unit/services/test_credit_service.py (SC-011)

### GREEN: Implement Credit Service

- [ ] T281 [US11] Implement CreditService.grant_kickstart_credits in src/services/credit_service.py (FR-037)
- [ ] T282 [US11] Implement CreditService.grant_daily_credits with expiration in src/services/credit_service.py (FR-038, FR-040)
- [ ] T283 [US11] Implement CreditService.grant_monthly_credits in src/services/credit_service.py (FR-039)
- [ ] T284 [US11] Implement CreditService.consume_credits with FIFO SQL in src/services/credit_service.py per research.md Section 11 (FR-042)
- [ ] T285 [US11] Implement CreditService.get_balance breakdown in src/services/credit_service.py
- [ ] T286 [US11] Implement carryover logic in credit_expire job in src/jobs/tasks/credit_job.py (FR-041)

### REFACTOR

- [ ] T287 [US11] Add integration test for credit lifecycle in tests/integration/test_credit_lifecycle.py
- [ ] T288 [US11] Add credit consumption metrics in src/services/credit_service.py (FR-066)
- [ ] T289 [US11] Add concurrent consumption stress test in tests/integration/test_credit_stress.py (SC-011)

**Checkpoint 14**: Credit System Ready - FIFO consumption with correct expiration (SC-011: <5s consistency)

---

## Phase 15: User Story 9 - Achievement System (Priority: P3) (18 tasks)

**Goal**: Achievements with permanent perks and streak tracking (FR-043 to FR-046)

**Independent Test**: Complete 5 tasks, verify tasks_5 achievement unlocked with +15 max tasks perk

### RED: Write FAILING Tests First

- [ ] T290 [P] [US9] Test: Streak calculation uses UTC calendar days in tests/unit/services/test_achievement_service.py (FR-043)
- [ ] T291 [P] [US9] Test: Streak increments on consecutive day completion in tests/unit/services/test_achievement_service.py
- [ ] T292 [P] [US9] Test: Streak resets after missed day in tests/unit/services/test_achievement_service.py
- [ ] T293 [P] [US9] Test: Achievement unlock is permanent in tests/unit/services/test_achievement_service.py (FR-044)
- [ ] T294 [P] [US9] Test: Perks never revoked even when streak breaks in tests/unit/services/test_achievement_service.py (FR-044)
- [ ] T295 [P] [US9] Test: Focus completion tracked (50%+ focus time) in tests/unit/services/test_achievement_service.py (FR-045)
- [ ] T296 [P] [US9] Test: Effective limits computed from base + perks in tests/unit/services/test_achievement_service.py (FR-046)
- [ ] T297 [P] [US9] Test: Streak edge cases (UTC boundary, DST) in tests/unit/services/test_achievement_service.py (SC-007)

### GREEN: Implement Achievement Service

- [ ] T298 [US9] Implement AchievementService.check_and_unlock with all achievement types in src/services/achievement_service.py
- [ ] T299 [US9] Implement AchievementService.update_streak on task completion in src/services/achievement_service.py (FR-043)
- [ ] T300 [US9] Implement AchievementService.calculate_effective_limits in src/services/achievement_service.py (FR-046)
- [ ] T301 [US9] Implement achievement unlock event handler in src/events/handlers.py (FR-044)
- [ ] T302 [US9] Implement focus completion tracking in src/services/task_service.py (FR-045)

### API Endpoints

- [ ] T303 [US9] Implement GET /api/v1/achievements in src/api/achievements.py per api-specification.md Section 8.1

### REFACTOR

- [ ] T304 [US9] Add integration test for achievement lifecycle in tests/integration/test_achievement_lifecycle.py
- [ ] T305 [US9] Add achievement notification on unlock in src/services/achievement_service.py
- [ ] T305a [P] [US9] Test: Task completion response includes unlocked_achievements array when achievement unlocked in tests/integration/test_achievement_notification.py (US9 AS4)
- [ ] T305b [US9] Implement unlocked_achievements in task completion response in src/services/task_service.py (US9 AS4, per plan.md Achievement Notification Delivery)
- [ ] T306 [US9] Add streak calculation stress test in tests/integration/test_streak_stress.py (SC-007)

**Checkpoint 15**: Achievements Ready - Permanent perks with accurate streaks (SC-007: UTC boundary accuracy)

---

## Phase 16: User Story 12 - Focus Mode Tracking (Priority: P4) (8 tasks)

**Goal**: Track focus time for achievement progress (FR-045)

**Independent Test**: Start focus session, end session, verify time accumulated

### RED: Write FAILING Tests First

- [ ] T307 [P] [US12] Test: Focus time accumulates in task.focus_time_seconds in tests/unit/services/test_focus_service.py
- [ ] T308 [P] [US12] Test: Focus completion counted when 50%+ of estimate in tests/unit/services/test_focus_service.py (FR-045)

### GREEN: Implement Focus Tracking

- [ ] T309 [US12] Implement FocusService.start_session in src/services/focus_service.py
- [ ] T310 [US12] Implement FocusService.end_session with duration calculation in src/services/focus_service.py
- [ ] T311 [US12] Implement focus completion check in task completion flow in src/services/task_service.py (FR-045)

### API Endpoints

- [ ] T312 [US12] Implement POST /api/v1/focus/start in src/api/focus.py
- [ ] T313 [US12] Implement POST /api/v1/focus/end in src/api/focus.py

### REFACTOR

- [ ] T314 [US12] Add integration test for focus tracking in tests/integration/test_focus_tracking.py

**Checkpoint 16**: Focus Mode Ready - Time tracking for achievements

---

## Phase 17: User Story 10 - Pro Subscription Management (Priority: P4) (20 tasks)

**Goal**: Subscription with Checkout.com webhooks and grace period (FR-047 to FR-051)

**Independent Test**: Subscribe via checkout, verify Pro tier, test payment failure grace period

### RED: Write FAILING Tests First

- [ ] T315 [P] [US10] Test: Webhook signature verification in tests/unit/integrations/test_checkout.py (FR-048)
- [ ] T316 [P] [US10] Test: payment_captured activates Pro tier in tests/unit/services/test_subscription_service.py (FR-047)
- [ ] T317 [P] [US10] Test: 3 payment failures trigger grace period in tests/unit/services/test_subscription_service.py (FR-049)
- [ ] T318 [P] [US10] Test: Grace period expiration downgrades to free in tests/unit/services/test_subscription_service.py (FR-050)
- [ ] T319 [P] [US10] Test: Credit purchase limit 500/month enforced in tests/unit/services/test_subscription_service.py (FR-051)
- [ ] T320 [P] [US10] Test: Webhook idempotent processing in tests/unit/services/test_subscription_service.py

### GREEN: Implement Subscription Service

- [ ] T321 [US10] Implement CheckoutClient with HMAC signature verification in src/integrations/checkout_client.py per research.md Section 7 (FR-048)
- [ ] T322 [US10] Implement SubscriptionService.handle_payment_captured in src/services/subscription_service.py (FR-047)
- [ ] T323 [US10] Implement SubscriptionService.handle_payment_declined with retry count in src/services/subscription_service.py
- [ ] T324 [US10] Implement grace period logic in src/services/subscription_service.py (FR-049)
- [ ] T325 [US10] Implement SubscriptionService.handle_subscription_cancelled in src/services/subscription_service.py
- [ ] T326 [US10] Implement tier downgrade on grace expiration in subscription_check job in src/jobs/tasks/subscription_job.py (FR-050)
- [ ] T327 [US10] Implement credit purchase with monthly limit in src/services/subscription_service.py (FR-051)

### API Endpoints

- [ ] T328 [US10] Implement GET /api/v1/subscription in src/api/subscription.py per api-specification.md Section 9.1
- [ ] T329 [US10] Implement POST /api/v1/subscription/checkout in src/api/subscription.py per api-specification.md Section 9.2
- [ ] T330 [US10] Implement POST /api/v1/subscription/cancel in src/api/subscription.py per api-specification.md Section 9.3
- [ ] T331 [US10] Implement POST /api/v1/webhooks/checkout in src/api/subscription.py per api-specification.md Section 9.4

### REFACTOR

- [ ] T332 [US10] Add respx mock for Checkout.com in tests/conftest.py
- [ ] T333 [US10] Add integration test for subscription lifecycle in tests/integration/test_subscription_lifecycle.py
- [ ] T334 [US10] Add webhook processing metrics in src/services/subscription_service.py (SC-008)

**Checkpoint 17**: Subscriptions Ready - Payment webhooks with grace period (SC-008: <30s processing)

---

## Phase 18: User Story 13 - Task Deletion and Recovery (Priority: P4) (14 tasks)

**Goal**: Tombstone-based recovery for deleted tasks (FR-062 to FR-064)

**Independent Test**: Delete task, verify tombstone created, recover task, verify original state

### RED: Write FAILING Tests First

- [ ] T335 [P] [US13] Test: Delete creates tombstone with serialized data in tests/unit/services/test_recovery_service.py (FR-062)
- [ ] T336 [P] [US13] Test: Max 3 tombstones per user (FIFO) in tests/unit/services/test_recovery_service.py (FR-062)
- [ ] T337 [P] [US13] Test: Recovery restores original ID and timestamps in tests/unit/services/test_recovery_service.py (FR-063)
- [ ] T338 [P] [US13] Test: Recovered task does not trigger achievements in tests/unit/services/test_recovery_service.py (FR-064)
- [ ] T339 [P] [US13] Test: Recovered task does not affect streaks in tests/unit/services/test_recovery_service.py (FR-064)

### GREEN: Implement Recovery Service

- [ ] T340 [US13] Implement RecoveryService.create_tombstone with FIFO limit in src/services/recovery_service.py (FR-062)
- [ ] T341 [US13] Implement RecoveryService.recover_task in src/services/recovery_service.py (FR-063)
- [ ] T342 [US13] Implement skip flags for achievements/streaks on recovery in src/services/recovery_service.py (FR-064)
- [ ] T343 [US13] Implement RecoveryService.list_tombstones in src/services/recovery_service.py

### API Endpoints

- [ ] T344 [US13] Implement GET /api/v1/tombstones in src/api/recovery.py
- [ ] T345 [US13] Implement POST /api/v1/tasks/recover/:tombstone_id in src/api/recovery.py per api-specification.md Section 3.7

### REFACTOR

- [ ] T346 [US13] Add integration test for recovery lifecycle in tests/integration/test_recovery_lifecycle.py
- [ ] T347 [US13] Add recovery metrics in src/services/recovery_service.py (SC-010)
- [ ] T348 [US13] Document recovery behavior in OpenAPI spec

**Checkpoint 18**: Recovery Ready - Tombstone-based task recovery (SC-010: <30s recovery)

---

## Phase 19: Notifications (10 tasks)

**Goal**: In-app and push notification system (FR-055 to FR-057)

### RED: Write FAILING Tests First

- [ ] T349 [P] [Infra] Test: Notification created for reminders in tests/unit/services/test_notification_service.py
- [ ] T350 [P] [Infra] Test: Notification read status tracking in tests/unit/services/test_notification_service.py (FR-057)

### GREEN: Implement Notification Service

- [ ] T351 [Infra] Implement NotificationService.create_notification in src/services/notification_service.py (FR-055)
- [ ] T352 [Infra] Implement NotificationService.list_notifications with unread filter in src/services/notification_service.py
- [ ] T353 [Infra] Implement NotificationService.mark_read in src/services/notification_service.py (FR-057)
- [ ] T354 [Infra] Implement NotificationService.mark_all_read in src/services/notification_service.py

### API Endpoints

- [ ] T355 [Infra] Implement GET /api/v1/notifications in src/api/notifications.py per api-specification.md Section 10.1
- [ ] T356 [Infra] Implement PATCH /api/v1/notifications/:id/read in src/api/notifications.py per api-specification.md Section 10.2
- [ ] T357 [Infra] Implement POST /api/v1/notifications/read-all in src/api/notifications.py per api-specification.md Section 10.3

### Push Notification Infrastructure

- [ ] T358 [Infra] Implement push notification delivery (WebPush) in src/services/notification_service.py (FR-056)
- [ ] T358a [P] [Infra] Create PushSubscription model with user_id, endpoint, p256dh_key, auth_key in src/models/notification.py (FR-028a)
- [ ] T358b [Infra] Implement POST /api/v1/notifications/push-subscription endpoint in src/api/notifications.py (FR-028a)
- [ ] T358c [P] [Infra] Test: Expired/invalid push tokens handled gracefully in tests/unit/services/test_notification_service.py (FR-028b)

**Checkpoint 19**: Notifications Ready - In-app and push delivery with token storage

---

## Phase 20: Activity Logging & Observability (8 tasks)

**Goal**: Complete activity logging system (FR-052 to FR-054)

### Implementation

- [ ] T359 [Infra] Implement ActivityService.log_event for all entity types in src/services/activity_service.py (FR-052)
- [ ] T360 [Infra] Implement 30-day retention cleanup job in src/jobs/tasks/cleanup_job.py (FR-053)
- [ ] T361 [Infra] Ensure source field tracked (user, AI, system) in all log entries in src/services/activity_service.py (FR-054)

### API Endpoints (for audit/debugging)

- [ ] T362 [Infra] Implement GET /api/v1/activity (admin/user-scoped) in src/api/activity.py

### Observability Completion

- [ ] T363 [Infra] Verify all operations emit structured logs (FR-065)
- [ ] T364 [Infra] Verify all metrics exposed for Prometheus (FR-066)
- [ ] T365 [Infra] Add /metrics endpoint for Prometheus scraping in src/api/health.py
- [ ] T366 [Infra] Document observability setup in docs/observability.md

**Checkpoint 20**: Observability Complete - Full logging, metrics, health checks

---

## Phase 21: API Router Assembly & Middleware (8 tasks)

**Goal**: Assemble all routes with middleware chain

### Route Assembly

- [ ] T367 [Infra] Create main API router aggregating all sub-routers in src/api/router.py
- [ ] T368 [Infra] Configure /api/v1 prefix for all routes (FR-068)
- [ ] T369 [Infra] Apply rate limiting per endpoint category in src/api/router.py (FR-061)

### Middleware Chain

- [ ] T370 [Infra] Configure middleware order in src/main.py (request_id -> logging -> auth -> rate_limit)
- [ ] T371 [Infra] Implement idempotency middleware for POST/PATCH in src/middleware/idempotency.py (FR-059)

### Main Application

- [ ] T372 [Infra] Implement FastAPI app factory in src/main.py
- [ ] T373 [Infra] Add startup/shutdown events for DB pool in src/main.py
- [ ] T374 [Infra] Create Dockerfile for API service

**Checkpoint 21**: API Assembly Complete - Full API operational

---

## Phase 22: Contract Testing & Schema Validation (10 tasks)

**Goal**: Comprehensive contract testing (per-feature and cross-cutting)

### Per-Feature Contract Tests

- [ ] T375 [P] [Contract] Run schemathesis against auth endpoints in tests/contract/test_auth_fuzz.py
- [ ] T376 [P] [Contract] Run schemathesis against task endpoints in tests/contract/test_tasks_fuzz.py
- [ ] T377 [P] [Contract] Run schemathesis against AI endpoints in tests/contract/test_ai_fuzz.py
- [ ] T378 [P] [Contract] Run schemathesis against subscription endpoints in tests/contract/test_subscription_fuzz.py

### AI Schema Validation

- [ ] T379 [P] [Contract] Snapshot test for SubtaskGenerationResult schema in tests/contract/test_ai_schemas.py
- [ ] T380 [P] [Contract] Snapshot test for ActionSuggestion schema in tests/contract/test_ai_schemas.py
- [ ] T381 [P] [Contract] Snapshot test for TaskSuggestion schema in tests/contract/test_ai_schemas.py

### Contract Alignment

- [ ] T382 [Contract] Generate OpenAPI spec and commit to contracts/openapi.yaml
- [ ] T383 [Contract] Generate TypeScript types for frontend in contracts/types.ts
- [ ] T384 [Contract] Document schema evolution process in docs/schema-evolution.md

**Checkpoint 22**: Contracts Validated - All API contracts verified

---

## Phase 23: Success Criteria Validation (21 tasks)

**Goal**: Validate all 12 success criteria from spec.md

### SC-001: OAuth Sign-in Performance

- [ ] T385 [Validation] Test: OAuth sign-in completes within 10 seconds in tests/integration/test_performance.py (SC-001)

### SC-002: Load Testing

- [ ] T386 [Validation] Create k6 load test script for 1000 concurrent users in tests/load/k6_script.js (SC-002)
- [ ] T387 [Validation] Run load test and document results in docs/load-test-results.md (SC-002)

### SC-003: API Response Latency

- [ ] T388 [Validation] Test: 95% of API responses < 500ms in tests/integration/test_performance.py (SC-003)
- [ ] T389 [Validation] Create alerting rule for p95 latency > 500ms in docs/alerting-rules.yaml (SC-003)

### SC-004: Task Operation Success Rate

- [ ] T390 [Validation] Test: Task CRUD 99.9% success rate under load in tests/load/k6_script.js (SC-004)

### SC-005: AI Chat Response Time

- [ ] T391 [Validation] Test: AI chat p95 < 5 seconds in tests/integration/test_ai_performance.py (SC-005)
- [ ] T392 [Validation] Create alerting rule for AI chat p95 > 5s in docs/alerting-rules.yaml (SC-005)

### SC-006: Data Integrity

- [ ] T393 [Validation] Create data integrity test suite (transaction rollback, concurrent updates) in tests/integration/test_data_integrity.py (SC-006)

### SC-007: Streak Accuracy

- [ ] T394 [Validation] Create streak calculation test suite (UTC boundary, timezone, DST) in tests/unit/services/test_streak_accuracy.py (SC-007)

### SC-008: Webhook Processing

- [ ] T395 [Validation] Test: Webhook processing < 30 seconds in tests/integration/test_webhook_performance.py (SC-008)
- [ ] T396 [Validation] Create alerting rule for webhook processing > 30s in docs/alerting-rules.yaml (SC-008)

### SC-009: Uptime

- [ ] T397 [Validation] Document uptime monitoring strategy in docs/slo-dashboard.md (SC-009)

### SC-010: Task Recovery Time

- [ ] T398 [Validation] Test: Task recovery < 30 seconds in tests/integration/test_recovery_performance.py (SC-010)
- [ ] T399 [Validation] Create alerting rule for recovery > 30s in docs/alerting-rules.yaml (SC-010)

### SC-011: Credit Balance Accuracy

- [ ] T400 [Validation] Create credit FIFO test suite (race conditions, consumption order) in tests/integration/test_credit_accuracy.py (SC-011)

### SC-012: Push Notification Delivery

- [ ] T401 [Validation] Test: Push notifications deliver within 60s for 95% in tests/integration/test_notification_delivery.py (SC-012)
- [ ] T402 [Validation] Create alerting rule for notification delay > 60s in docs/alerting-rules.yaml (SC-012)
- [ ] T402a [Validation] Create concurrent update stress test (optimistic locking) in tests/integration/test_concurrent_updates.py (FR-014)
- [ ] T402b [Validation] Test: API v1 responses maintain backward compatibility (no field removals, type changes) in tests/integration/test_api_versioning.py (FR-069)
- [ ] T402c [Validation] Test: Deprecated endpoints return Deprecation header with sunset date in tests/integration/test_api_versioning.py (FR-069a, FR-069b per plan.md AD-006)

**Checkpoint 23**: Success Criteria Validated - All SCs passing or tracked

---

## Phase 24: Polish & Production Readiness (15 tasks)

**Purpose**: Final polish and deployment preparation

### Documentation

- [ ] T403 [P] [Polish] Create README.md with project overview and setup in backend/README.md
- [ ] T404 [P] [Polish] Create quickstart.md developer guide in specs/003-perpetua-backend/quickstart.md
- [ ] T405 [P] [Polish] Document all API behaviors in OpenAPI spec

### Code Quality

- [ ] T406 [P] [Polish] Run full test suite and verify coverage (Core: 90%, API: 80%, Events: 80%, Jobs: 70%)
- [ ] T407 [P] [Polish] Remove all debug logs, unused imports, commented code
- [ ] T408 [P] [Polish] Add docstrings to all public service methods

### Security Hardening

- [ ] T409 [P] [Polish] Security audit: Check for SQL injection, command injection vulnerabilities
- [ ] T410 [P] [Polish] Verify all secrets loaded from env vars, none hardcoded
- [ ] T411 [P] [Polish] Add security headers middleware in src/middleware/security.py

### Deployment

- [ ] T412 [Polish] Create docker-compose.yml for local development
- [ ] T413 [Polish] Create Railway configuration (railway.toml or Procfile)
- [ ] T414 [Polish] Test deployment to staging environment
- [ ] T415 [Polish] Run full E2E test against staging

### Final Validation

- [ ] T416 [Polish] Fresh clone and quickstart.md validation - verify app runs without errors
- [ ] T416a [Polish] Document API versioning and deprecation policy in docs/api-versioning.md (FR-069)

**Checkpoint 24 - PRODUCTION READY**: All features implemented, tested, and deployable

---

## Summary

**Total Tasks**: 433 tasks across 24 phases

**MVP Tasks (P1)**: ~102 tasks (Phases 1-4: Foundation, Models, Auth, Tasks)
- Phase 1: 30 (Foundation) - includes T012a readiness probe test
- Phase 2: 32 (Models & Schemas)
- Phase 3: 31 (US1 - Auth) - includes T078a-c for FR-070 user profile
- Phase 4: 37 (US2 - Tasks) - includes T130a/T130b for FR-013

**Task Count by Priority**:
- P1 (MVP - US1, US2): ~68 implementation tasks (+3 for FR-070, +2 for FR-013)
- P2 (US3, US4, US5, US8): ~70 tasks (+2 for FR-036 WebSocket timeout)
- P3 (US6, US7, US9): ~56 tasks (+2 for US9 AS4 achievement notification)
- P4 (US10, US11, US12, US13): ~60 tasks
- Infrastructure: ~84 tasks (+1 for T012a, +3 for FR-028a/b push tokens)
- Contract/Validation: ~33 tasks (+1 for T402a, +2 for FR-069 versioning)
- Polish: ~15 tasks (+1 for T416a API versioning docs)

**Parallel Opportunities**: ~132 tasks marked [P] can run in parallel

**User Story Coverage**:
- US1 (Auth): 31 tasks - FR-001 to FR-006, FR-070
- US2 (Tasks): 35 tasks - FR-007 to FR-014
- US3 (Recurring): 20 tasks - FR-015 to FR-018
- US4 (Subtasks): 8 tasks - FR-019 to FR-021
- US5 (Notes + Voice): 42 tasks - FR-022 to FR-024, FR-032, FR-033, FR-036
- US6 (AI Chat): 24 tasks - FR-029 to FR-035
- US7 (Auto Subtasks): 12 tasks - FR-031
- US8 (Reminders): 22 tasks - FR-025 to FR-028
- US9 (Achievements): 20 tasks - FR-043 to FR-046, US9 AS4
- US10 (Subscriptions): 20 tasks - FR-047 to FR-051
- US11 (Credits): 18 tasks - FR-037 to FR-042
- US12 (Focus Mode): 8 tasks - FR-045
- US13 (Recovery): 14 tasks - FR-062 to FR-064

**Functional Requirements Coverage**: All 71 FRs (FR-001 to FR-070, FR-069a, FR-069b)

**Success Criteria Validation**: All 12 SCs (SC-001 to SC-012)

**Background Jobs**: All 5 types
- reminder_fire (T207)
- streak_calculate (T208)
- credit_expire (T209)
- subscription_check (T210)
- recurring_task_generate (T211)

**Database Migrations**: All 8 (T022-T029)

**AI Agents**: All 3
- PerpetualFlowAssistant (T229)
- SubtaskGenerator (T246)
- NoteConverter (T256)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies - start immediately
- **Phase 2 (Models)**: Depends on Phase 1 (migrations must exist)
- **Phase 3 (Auth - US1)**: Depends on Phase 2 (User model)
- **Phase 4 (Tasks - US2)**: Depends on Phase 3 (authentication)
- **Phases 5-8**: Depend on Phase 4 (core tasks)
- **Phase 9 (Events/Jobs)**: Can start after Phase 2
- **Phases 10-13 (AI)**: Depend on Phase 9 (event system)
- **Phases 14-18**: Can proceed in parallel after Phase 4
- **Phases 19-21**: Depend on all user story phases
- **Phases 22-24**: Final validation and polish

### Critical Path

1. Phase 1 (Foundation) -> 2. Phase 2 (Models) -> 3. Phase 3 (Auth) -> 4. Phase 4 (Tasks) -> 5. MVP Ready

### Parallel Opportunities

After Phase 4 (MVP Core):
- **Track A**: Phase 5 (Subtasks) + Phase 6 (Recurring)
- **Track B**: Phase 7 (Notes) + Phase 8 (Reminders)
- **Track C**: Phase 9 (Events/Jobs) independent of user stories
- **Track D**: Phases 10-13 (AI features) after Phase 9

All [P] marked tasks within each phase can execute in parallel.

---

## Implementation Strategy

### MVP First (Phases 1-4)

1. Complete Phase 1 (Foundation) - 29 tasks
2. Complete Phase 2 (Models & Schemas) - 32 tasks
3. Complete Phase 3 (Auth - US1) - 28 tasks
4. Complete Phase 4 (Tasks - US2) - 35 tasks
5. **STOP and VALIDATE**: MVP with auth + task CRUD working (~124 tasks)

### Advanced Features (Phases 5-9)

6. Complete Phases 5-8 in parallel - Subtasks, Recurring, Notes, Reminders
7. Complete Phase 9 (Events/Jobs) - Background processing
8. **STOP and VALIDATE**: Core features with events (~210 tasks)

### AI Integration (Phases 10-13)

9. Complete Phases 10-13 - AI chat, subtasks, conversion, transcription
10. **STOP and VALIDATE**: AI features working (~260 tasks)

### Gamification & Billing (Phases 14-18)

11. Complete Phases 14-18 - Credits, Achievements, Focus, Subscriptions, Recovery
12. **STOP and VALIDATE**: Full feature set (~340 tasks)

### Production Ready (Phases 19-24)

13. Complete Phases 19-21 - Notifications, Observability, API Assembly
14. Complete Phases 22-24 - Contract testing, Validation, Polish
15. **FINAL VALIDATION**: Production-ready backend (433 tasks)

---

## Key Milestones

1. **Foundation Ready** (T029) - All migrations, models, observability
2. **MVP Auth Ready** (T089) - US1 complete, users can authenticate
3. **MVP Core Ready** (T130) - US1 + US2, basic task management
4. **Advanced Features Ready** (T196) - US3, US4, US5, US8 complete
5. **AI Ready** (T273) - All 3 agents working with credit consumption
6. **Gamification Ready** (T314) - Achievements, streaks, focus mode
7. **Billing Ready** (T348) - Subscriptions, webhooks, recovery
8. **Observability Complete** (T374) - Full logging, metrics, health
9. **Contracts Validated** (T384) - All API contracts verified
10. **Success Criteria Validated** (T402) - All SCs passing
11. **Production Ready** (T416) - Deployment-ready application

---

## Notes

- **TDD Mandatory**: RED (failing test) -> GREEN (implement) -> REFACTOR
- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] labels**: Track to user stories (US1-US13) or category (Infra, Contract, Validation)
- **All timestamps UTC**: Per constitution and spec requirements
- **Terminology**: Use "task" in API layer and user-facing docs; use "task_instance" in database models and internal code per spec.md Entity naming
- **Optimistic locking**: Version field on all mutable entities (FR-014)
- **Idempotency**: Required for all POST/PATCH requests (FR-059)
- **Rate limits**: 100/min general, 20/min AI, 10/min auth (FR-061)
- **AI confirmation**: All AI actions require user confirmation (FR-034)
- **Test coverage**: Core 90%+, API 80%+, Events 80%+, Jobs 70%+

---

**Generated**: 2026-01-19
**Updated**: 2026-01-20 (remediation edits applied)
**Spec Version**: specs/003-perpetua-backend/spec.md
**Plan Version**: specs/003-perpetua-backend/plan.md
**Research Version**: specs/003-perpetua-backend/research.md
**Data Model Version**: specs/003-perpetua-backend/docs/data-model.md
**API Spec Version**: specs/003-perpetua-backend/docs/api-specification.md

---

## Remediation Changelog (2026-01-20)

Applied remediations from `/sp.analyze 003` report:

### Spec Remediations Mirrored

| ID | FR/US | Tasks Added | Description |
|----|-------|-------------|-------------|
| SPEC-R1 | FR-035 | (existing T224, T225) | Session-scoped counter validation already covered |
| SPEC-R2 | FR-069a/b | T402b, T402c | API deprecation header validation tasks |
| SPEC-R3 | US9 AS4 | T305a, T305b | Achievement notification delivery tasks |

### Plan Remediations Mirrored

| ID | Section | Tasks Updated | Description |
|----|---------|---------------|-------------|
| PLAN-R1 | Audio Format | T273a, T273b | WebSocket timeout validation per audio requirements |
| PLAN-R2 | RefreshToken | T078 | Reference to plan.md AD-001 Refresh Token Storage |

### Task Remediations Applied

| ID | Severity | Tasks Added | Description |
|----|----------|-------------|-------------|
| TASK-R1 | HIGH | T078a, T078b, T078c | User profile endpoint (FR-070) |
| TASK-R2 | HIGH | T402b, T402c | API versioning validation (FR-069/FR-069a/FR-069b) |
| TASK-R3 | HIGH | T305a, T305b | Achievement notification (US9 AS4) |
| TASK-R4 | MEDIUM | T358a, T358b, T358c | Push token storage (FR-028a/FR-028b) |
| TASK-R5 | MEDIUM | T273a, T273b | WebSocket timeout validation (FR-036) |
| TASK-R6 | LOW | Summary | Task count updated to 433 |
| TASK-R7 | LOW | n/a | WebSocket filename already aligned in plan |

**Total New Tasks Added**: 12 (T078a-c, T273a-b, T305a-b, T358a-c, T402b-c)
**Updated Checkpoint 3**: Added "and update profile" to auth checkpoint
**Updated Checkpoint 13**: Added audio format reference
**Updated Checkpoint 19**: Added token storage reference
