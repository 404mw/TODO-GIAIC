Generate a comprehensive, dependency-ordered tasks.md for the Perpetua Flow Backend API.

## Feature Context

- **Feature Branch**: `003-perpetua-backend`
- **Spec Location**: `specs/003-perpetua-backend/spec.md`
- **Plan Location**: `specs/003-perpetua-backend/plan.md`
- **Research Location**: `specs/003-perpetua-backend/research.md`
- **Data Model**: `specs/003-perpetua-backend/docs/data-model.md`
- **API Specification**: `specs/003-perpetua-backend/docs/api-specification.md`
- **Authentication**: `specs/003-perpetua-backend/docs/authentication.md`
- **Output Location**: `specs/003-perpetua-backend/tasks.md`

## Technology Stack (Confirmed)

- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic
- **Background Jobs**: PostgreSQL-based queue (SKIP LOCKED pattern)
- **Events**: In-process event bus (synchronous)
- **AI Integration**: OpenAI Agents SDK (`openai-agents`) with Pydantic schemas
- **Voice Transcription**: Deepgram NOVA2 (batch API)
- **Payments**: Checkout.com webhooks
- **Deployment**: Railway (API service + Worker service)
- **Testing**: pytest, pytest-asyncio, httpx, factory-boy, respx, schemathesis

## Task Generation Requirements

### 1. TDD Enforcement (Mandatory)

ALL tasks MUST follow Red → Green → Refactor workflow:
- **RED**: Write failing tests FIRST (explicit test tasks)
- **GREEN**: Implement minimum code to pass tests
- **REFACTOR**: Improve code quality without changing behavior

Each feature area should have explicit test tasks that precede implementation tasks.

### 2. Task Granularity: Fine-Grained (~200-250 tasks)

Break down into individual, atomic tasks:
- One task per model/schema
- One task per service method
- One task per endpoint
- One task per integration client
- One task per job type
- Explicit test tasks for each component

### 3. User Story Coverage: All 13 Stories

Cover ALL user stories with P1 marked as MVP:

**P1 (MVP)**:
- US1: User Authentication via Google OAuth
- US2: Task Creation and Management

**P2**:
- US3: Recurring Task Templates
- US4: Subtask Management
- US5: Notes with Voice Recording

**P3**:
- US6: AI Chat Widget
- US7: Auto Subtask Generation
- US8: Reminder System
- US9: Achievement System

**P4**:
- US10: Pro Subscription Management
- US11: AI Credit System
- US12: Focus Mode Tracking
- US13: Task Deletion and Recovery

### 4. Phase Structure (from plan.md)

Organize tasks into these phases with clear dependencies:

**Phase 1: Foundation**
- Project setup, dependencies, configuration
- Database models and ALL migrations (single comprehensive initial migration)
- Observability infrastructure (structured logging, Prometheus metrics, health checks)
- Contract testing infrastructure (schemathesis setup)

**Phase 2: Core CRUD (MVP)**
- Authentication endpoints (Google OAuth, JWT)
- Task CRUD endpoints
- Subtask management
- Basic validation and error handling

**Phase 3: Advanced Features**
- Recurring task templates (RRULE)
- Note CRUD
- Reminder system
- Event system and handlers
- Background job infrastructure (full worker with all job types)

**Phase 4: AI Integration**
- OpenAI Agents SDK integration (`openai-agents`)
- Three agents: PerpetualFlowAssistant (chat), SubtaskGenerator, NoteConverter
- AI chat endpoint (SSE streaming via `Runner.run_streamed()`)
- Subtask generation (structured output via `output_type`)
- Note-to-task conversion (separate agent)
- Credit consumption with FIFO

**Phase 5: Gamification**
- Achievement system with predefined achievements
- Streak calculation (UTC calendar days)
- Effective limits computation
- User Achievement State tracking

**Phase 6: Billing & Notifications**
- Subscription management
- Checkout.com webhook handling with signature verification
- Notification system (in-app + push)
- Push notification infrastructure

**Phase 7: Observability & Validation**
- Alerting rule definitions
- Load testing infrastructure (k6 scripts)
- Data integrity test suites
- Streak/credit correctness test suites
- SLO dashboard configuration
- Recovery system (tombstones)
- Focus mode tracking
- Activity logging
- Rate limiting middleware
- API documentation generation

### 5. Worker Service Scope

Include FULL worker service with ALL job types in Phase 3:
- `reminder_fire` - Send reminder notifications
- `streak_calculate` - Daily streak calculation at UTC 00:00
- `credit_expire` - Daily credit expiration at UTC 00:00
- `subscription_check` - Daily subscription status and grace periods
- `recurring_task_generate` - Generate next recurring instance on completion

### 6. Database Migrations

Create ALL migrations upfront in Phase 1:
```
001_initial_schema.py - Users, task_instances, task_templates, subtasks
002_notes_reminders.py - Notes, reminders tables
003_achievements.py - Achievement definitions, user_achievement_states
004_credits_subscriptions.py - AI credit ledger, subscriptions
005_activity_tombstones.py - Activity logs, deletion tombstones
006_notifications.py - Notifications table
007_job_queue.py - Background job queue table
008_indexes.py - Performance indexes
```

Structure migrations by domain but create all before API work begins.

### 7. External Service Integrations

Each integration MUST have explicit failure mode handling:

**Google OAuth** (`integrations/google_oauth.py`):
- JWKS caching with 24h TTL
- Token verification with proper error handling
- Failure mode: Return `OAUTH_VERIFICATION_FAILED` error

**OpenAI Agents SDK** (`integrations/ai_agent.py`):
- Three agents with Pydantic output schemas
- Streaming support for chat
- Timeout: 30 seconds per agent run
- Failure mode: Return `AI_SERVICE_UNAVAILABLE` error, log failure, don't block user

**Deepgram** (`integrations/deepgram_client.py`):
- NOVA2 batch transcription
- Max 300 seconds audio
- Failure mode: Return `TRANSCRIPTION_FAILED` error with retry suggestion

**Checkout.com** (`integrations/checkout_client.py`):
- HMAC-SHA256 signature verification
- Idempotent webhook processing
- Failure mode: Reject invalid signatures, log attempt, return 400

### 8. Contract Testing Strategy

Include comprehensive contract discipline:

**Phase 1 - Contract Infrastructure**:
- Generate OpenAPI spec and commit to `contracts/openapi.yaml`
- Setup `schemathesis` for API contract fuzzing
- Create AI schema snapshot tests

**Per-Feature**:
- Each API endpoint gets a contract test
- Each AI agent gets schema validation tests

**Phase 7 - Contract Alignment**:
- Generate TypeScript types for frontend consumption
- Document schema evolution process
- Add CI checks for contract drift

### 9. Success Criteria Validation (Observability-Driven)

**Tier 1 - Implemented as Features (in main phases)**:
- FR-065: Structured JSON logging (request ID, timestamp, user ID, action, outcome)
- FR-066: Prometheus-compatible metrics (request latency, error rates, credit consumption)
- FR-067: Health check endpoints (liveness, readiness)

**Tier 2 - Dedicated Validation Tasks (Phase 7)**:
- SC-002: Load testing with k6 scripts (1000 concurrent users)
- SC-006: Data integrity test suite (transaction rollback, concurrent updates)
- SC-007: Streak calculation test suite (UTC boundary, timezone edge cases, DST)
- SC-011: Credit FIFO test suite (race conditions, consumption order)

**Tier 3 - Operational (alerting rules)**:
- SC-003: Alert rule for p95 latency > 500ms
- SC-005: Alert rule for AI chat p95 > 5s
- SC-008: Alert rule for webhook processing > 30s
- SC-010: Alert rule for task recovery > 30s
- SC-012: Alert rule for push notification delivery > 60s

### 10. AI Agent Architecture (Three Agents)

**Agent 1: PerpetualFlowAssistant** (Chat)
- Tool: `suggest_action(action_type, payload)` for task operations
- Streaming via `Runner.run_streamed()`
- Returns suggestions requiring user confirmation

**Agent 2: SubtaskGenerator** (Structured Output)
- `output_type=SubtaskGenerationResult` (Pydantic model)
- Returns list of subtask suggestions
- Respects user's tier limit

**Agent 3: NoteConverter** (Structured Output)
- `output_type=TaskSuggestion` (Pydantic model)
- Converts note content to task suggestion
- Returns title, description, priority, optional due date

### 11. Task Format

Use this format for each task:
```
- [ ] [ID] [P?] [Story?] Description
```

Where:
- `[P]`: Can run in parallel (different files, no dependencies)
- `[Story]`: Which user story (US1-US13) or category (Infra, Contract, Validation)

Include:
- Exact file paths for each task
- FR/SC references where applicable
- Dependencies noted in phase structure

### 12. Project Structure Reference

```
backend/
├── alembic/
│   ├── versions/
│   └── env.py
├── src/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── api/              # API route handlers
│   ├── services/         # Business logic layer
│   ├── events/           # In-process event system
│   ├── jobs/             # Background job processing
│   ├── integrations/     # External service clients
│   └── middleware/       # FastAPI middleware
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

### 13. Key Constraints

From constitution and spec:
- All timestamps UTC
- Optimistic locking via version field
- Idempotency keys required for POST/PATCH
- Rate limits: 100/min general, 20/min AI, 10/min auth
- PATCH semantics: omitted = unchanged, null = clear
- AI cannot change state without user confirmation
- All AI interactions logged immutably
- Test coverage targets: Core logic 90%+, API 80%+, Events 80%+, Jobs 70%+

### 14. Checkpoints

Define clear checkpoints for validation:
1. **Foundation Ready** - All migrations, models, observability, contract infra
2. **MVP Ready** - Auth + Task CRUD working end-to-end
3. **Advanced Features Ready** - Recurring tasks, notes, reminders, events, jobs
4. **AI Ready** - All three agents working with credit consumption
5. **Gamification Ready** - Achievements, streaks, effective limits
6. **Billing Ready** - Subscriptions, webhooks, notifications
7. **Production Ready** - All validation tasks pass, observability complete

### 15. Dependencies & Parallel Opportunities

Note which tasks can run in parallel [P] and which have sequential dependencies.

Example parallel opportunities:
- All model definitions can be parallel
- All schema definitions can be parallel
- Test setup tasks can be parallel
- Different service implementations can be parallel (after dependencies)

Example sequential dependencies:
- Models before schemas
- Schemas before services
- Services before API endpoints
- Migrations before any database-touching code
- Event types before event handlers
- Job queue before job implementations

## Output Requirements

Generate `specs/003-perpetua-backend/tasks.md` with:

1. **Header** with metadata (input files, prerequisites, TDD enforcement note)
2. **Format documentation** explaining task notation
3. **Path conventions** listing the project structure
4. **Phase sections** (1-7) with clear task groupings
5. **Task IDs** starting at T001, sequential
6. **Checkpoint markers** after each phase
7. **Summary section** with:
   - Total task count
   - MVP task count
   - Parallel opportunities count
   - Estimated effort distribution
8. **Dependencies & Execution Order** section
9. **Implementation Strategy** section with recommended approach
10. **Key Milestones** mapped to checkpoints

## Reference: Frontend Tasks Structure

See `specs/002-perpetua-frontend/tasks.md` for format reference. Backend tasks should follow similar structure but adapted for Python/FastAPI patterns.

## Success Criteria for Task Generation

The generated tasks.md is complete when:
- [ ] All 13 user stories have associated tasks
- [ ] All 69 functional requirements (FR-001 to FR-069) are covered
- [ ] All 12 success criteria (SC-001 to SC-012) have validation tasks
- [ ] TDD structure is explicit (RED/GREEN/REFACTOR phases)
- [ ] All external integrations have failure mode tasks
- [ ] Contract testing tasks are included
- [ ] Observability tasks cover logging, metrics, health checks
- [ ] Worker service has all 5 job types
- [ ] All 8 migrations are listed
- [ ] Dependencies between tasks are clear
- [ ] Parallel opportunities are marked with [P]
- [ ] File paths are specific and accurate
- [ ] Checkpoints validate independently testable milestones
