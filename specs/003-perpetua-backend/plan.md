# Implementation Plan: Perpetua Flow Backend API

**Branch**: `003-perpetua-backend` | **Date**: 2026-01-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-perpetua-backend/spec.md`

## Summary

Build a production-grade Python FastAPI backend for Perpetua Flow task management application. The backend provides RESTful APIs for user authentication (Google OAuth), task/subtask management with recurring templates, notes with voice recording, AI-powered features (chat, subtask generation, note conversion), subscription billing via Checkout.com, and a gamification system with achievements and streaks. All data is persisted in PostgreSQL (Neon Serverless) with Alembic migrations.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel (Pydantic + SQLAlchemy), Alembic, PyJWT, httpx, python-dateutil, openai-agents, deepgram-sdk
**Storage**: PostgreSQL (Neon Serverless) with multiple schemas (auth, tasks, notes, billing, achievements, activity)
**Testing**: pytest with pytest-asyncio, httpx for async testing, factory-boy for fixtures
**Target Platform**: Railway (persistent container), Linux-based
**Project Type**: Web application (backend API service)
**Performance Goals**: 95% of API responses < 500ms, AI chat responses < 5s for 95%, 99.5% uptime
**Constraints**: 1000 concurrent users, < 500ms p95 latency for CRUD, zero data loss, all timestamps UTC
**Scale/Scope**: Single-tenant SaaS, 13 user stories (P1-P4), ~40 API endpoints, 13 database entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Specification is supreme authority** | PASS | Comprehensive spec exists with 69 functional requirements |
| **II. Phase discipline (no spec, no code)** | PASS | Spec and data model complete before implementation |
| **III. Data integrity - no user data loss** | PASS | Tombstone recovery, optimistic locking, audit logs designed |
| **III. Undo guarantee** | PASS | Tombstone system provides recovery for 3 most recent deletions |
| **IV. AI is not trusted authority** | PASS | All AI actions require user confirmation (FR-034) |
| **IV. AI cannot change/delete tasks by default** | PASS | AI returns suggestions; backend validates and requires confirmation |
| **V. AI interactions logged** | PASS | Activity log captures all AI events with task ID, timestamp, actor |
| **VI. Single responsibility endpoints** | PASS | API spec follows REST conventions, one purpose per endpoint |
| **VI. Mandatory endpoint documentation** | PASS | Full OpenAPI spec with schemas, errors, behaviors |
| **VII. Schema consistency (Pydantic)** | PASS | SQLModel enforces Pydantic validation on all entities |
| **VIII. TDD mandatory** | PASS | Testing strategy includes contract tests, E2E tests, mocked externals |
| **IX. Secrets in .env** | PASS | All secrets (Google OAuth, JWT keys, API keys) via environment |
| **IX. AI limits configurable via .env** | PASS | Rate limits and credit costs configurable |
| **X. Simplicity over scale** | PASS | Single database, in-process events, PostgreSQL-based job queue |

**Gate Status**: PASS - All constitutional principles satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-perpetua-backend/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output - local dev setup
├── contracts/           # Phase 1 output - OpenAPI spec
│   └── openapi.yaml     # Generated API contract
├── checklists/          # Existing
│   └── requirements.md
└── docs/                # Existing detailed docs
    ├── data-model.md    # Database entities
    ├── api-specification.md  # API endpoint details
    └── authentication.md     # OAuth/JWT flows
```

### Source Code (repository root)

```text
backend/
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Environment configuration
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── subtask.py
│   │   ├── note.py
│   │   ├── reminder.py
│   │   ├── achievement.py
│   │   ├── credit.py
│   │   ├── subscription.py
│   │   ├── activity.py
│   │   ├── tombstone.py
│   │   └── notification.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── note.py
│   │   ├── ai.py
│   │   └── common.py
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── router.py           # Main router aggregation
│   │   ├── auth.py
│   │   ├── users.py            # User profile endpoints (FR-070)
│   │   ├── tasks.py
│   │   ├── subtasks.py
│   │   ├── notes.py
│   │   ├── reminders.py
│   │   ├── ai.py
│   │   ├── achievements.py
│   │   ├── subscription.py
│   │   ├── notifications.py
│   │   ├── recovery.py
│   │   ├── focus.py
│   │   ├── ws_voice.py         # WebSocket voice transcription endpoint
│   │   └── health.py
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   ├── note_service.py
│   │   ├── ai_service.py
│   │   ├── credit_service.py
│   │   ├── achievement_service.py
│   │   ├── subscription_service.py
│   │   ├── notification_service.py
│   │   └── activity_service.py
│   ├── events/                 # In-process event system
│   │   ├── __init__.py
│   │   ├── bus.py              # Event bus implementation
│   │   ├── types.py            # Event type definitions
│   │   └── handlers.py         # Event handlers
│   ├── jobs/                   # Background job processing
│   │   ├── __init__.py
│   │   ├── queue.py            # PostgreSQL SKIP LOCKED queue
│   │   ├── worker.py           # Job worker implementation
│   │   └── tasks/              # Job type implementations
│   │       ├── reminder_job.py
│   │       ├── streak_job.py
│   │       ├── credit_expiry_job.py
│   │       └── subscription_job.py
│   ├── integrations/           # External service clients
│   │   ├── __init__.py
│   │   ├── google_oauth.py
│   │   ├── ai_agent.py             # OpenAI Agents SDK integration
│   │   ├── deepgram_client.py
│   │   └── checkout_client.py
│   └── middleware/             # FastAPI middleware
│       ├── __init__.py
│       ├── auth.py             # JWT validation
│       ├── rate_limit.py       # Rate limiting
│       ├── request_id.py       # Request correlation
│       └── error_handler.py    # Global error handling
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── factories/              # Test data factories
│   │   ├── __init__.py
│   │   ├── user_factory.py
│   │   └── task_factory.py
│   ├── contract/               # API contract tests
│   │   ├── test_auth_contract.py
│   │   └── test_tasks_contract.py
│   ├── integration/            # Integration tests
│   │   ├── test_auth_flow.py
│   │   ├── test_task_lifecycle.py
│   │   └── test_ai_features.py
│   └── unit/                   # Unit tests
│       ├── test_credit_service.py
│       ├── test_achievement_service.py
│       └── test_streak_calculation.py
├── worker/                     # Separate worker service
│   ├── __init__.py
│   └── main.py                 # Worker entry point
├── pyproject.toml              # Project dependencies
├── alembic.ini                 # Alembic configuration
├── Dockerfile                  # API container
├── Dockerfile.worker           # Worker container
└── .env.example                # Environment template
```

**Structure Decision**: Web application structure with separate `backend/` directory. Backend consists of two Railway services: API server and background job worker. Both share the same codebase but have different entry points.

## Complexity Tracking

> No constitution violations requiring justification. Design follows simplicity principles:
> - Single database (not microservices)
> - In-process event bus (not external message queue)
> - PostgreSQL-based job queue (not Redis/RabbitMQ)
> - Single environment (production + local dev)

## Architecture Decisions

### AD-001: Authentication Strategy

**Decision**: Frontend (BetterAuth) handles Google OAuth code exchange; backend receives and verifies Google ID tokens, then issues own JWT tokens

**Rationale**:
- Frontend (BetterAuth) handles OAuth UI flow and code-to-token exchange with Google
- Backend receives the Google ID token from frontend and verifies it using Google's public JWKS
- Backend then issues its own JWT tokens (RS256, 15-min access / 7-day refresh)
- Refresh token rotation prevents replay attacks
- Clear separation: frontend owns OAuth complexity, backend is stateless token verifier

**Flow**:
1. User clicks "Sign in with Google" → BetterAuth initiates OAuth
2. Google redirects with authorization code → BetterAuth exchanges for Google ID token
3. Frontend sends Google ID token to `POST /api/v1/auth/google/callback`
4. Backend verifies ID token signature against Google's JWKS
5. Backend creates/updates user, issues access + refresh tokens

**Alternatives Rejected**:
- Backend handles code exchange: Would duplicate BetterAuth's OAuth logic
- Passing through Google tokens: Would couple backend to Google's token lifecycle
- Session-based auth: Would require session storage, breaks stateless API design

**Refresh Token Storage** (PLAN-R2):
- Refresh tokens stored in `refresh_tokens` table with: token_hash, user_id, expires_at, revoked_at
- Tokens are hashed (SHA-256) before storage; raw token never persisted
- On rotation: old token marked revoked, new token created
- Revoked tokens retained 7 days for audit, then purged
- Single active refresh token per user (new login revokes previous)

### AD-002: Background Job Processing

**Decision**: PostgreSQL-based queue with SKIP LOCKED pattern

**Rationale**:
- No additional infrastructure (Redis/RabbitMQ) required
- PostgreSQL already deployed; leverages existing connection pool
- SKIP LOCKED provides proper job locking for concurrent workers
- Sufficient for expected scale (< 1000 concurrent users)

**Alternatives Rejected**:
- Redis Queue (RQ): Additional infrastructure, unnecessary for scale
- Celery + RabbitMQ: Overkill complexity for current requirements

### AD-003: Event System

**Decision**: In-process synchronous event bus

**Rationale**:
- Simpler than external message broker
- Sufficient for single-instance API deployment
- Easy to test and debug
- Can upgrade to async/external later if needed

**Alternatives Rejected**:
- External event bus (Kafka/NATS): Unnecessary infrastructure complexity
- Async in-process: Adds complexity without clear benefit at current scale

### AD-004: AI Integration Pattern

**Decision**: AI returns structured suggestions; backend validates and requires user confirmation

**Rationale**:
- Enforces constitutional principle: AI cannot change state without consent
- Backend validates AI output before presenting to user
- Clear audit trail of AI suggestions vs confirmed actions

### AD-005: API Versioning

**Decision**: URL path versioning (/api/v1/)

**Rationale**:
- Explicit version in URL for clarity
- Easy to support multiple versions during migration
- Frontend can target specific version

### AD-006: API Deprecation Policy (FR-069a, FR-069b)

**Decision**: Minimum 90-day deprecation notice with RFC 8594 Deprecation headers

**Policy**:
- Backward compatibility maintained within a major version (no field removals, type changes)
- Minimum 90-day notice before any endpoint removal within a major version
- Deprecated endpoints return `Deprecation` header with sunset date per RFC 8594
- Breaking changes require new major version (/api/v2/)

**Implementation**:
- Middleware adds `Deprecation: @{sunset-date}` header for deprecated endpoints
- Documentation clearly marks deprecated endpoints with migration guidance
- Sunset dates announced in API changelog and developer notifications

## External Service Integration

### Google OAuth
- Verify ID tokens using Google's public keys
- Cache JWKS with 24-hour TTL
- Extract email, name, avatar from verified token

### OpenAI Agents SDK (openai-agents)
- Server-side only (never expose API keys to frontend)
- Agent-based architecture with tool definitions for structured task operations
- Built-in function calling and structured output for subtask generation
- SSE streaming for chat responses via agent run streaming
- Timeout: 30 seconds per agent run
- Tracing and observability built-in via SDK

### Deepgram NOVA2
- **Real-time streaming transcription** via WebSocket relay (see WebSocket Endpoints below)
- Backend acts as relay: client WebSocket → backend → Deepgram WebSocket
- Max 300 seconds audio per session (FR-036)
- 5 credits per minute billing (FR-033)
- Pro tier only for voice features

### WebSocket Endpoints

#### Voice Streaming (`/api/v1/ws/voice/transcribe`)

Real-time voice-to-text transcription via WebSocket relay to Deepgram.

**Flow**:
1. Client establishes WebSocket connection to backend (JWT auth via query param or first message)
2. Backend establishes WebSocket connection to Deepgram NOVA2
3. Client streams audio chunks (WebM/Opus format) → Backend relays to Deepgram
4. Deepgram returns partial/final transcripts → Backend relays to client
5. On session end, backend calculates duration and deducts credits

**Message Protocol**:
```json
// Client → Server: Audio chunk (binary)
// Client → Server: Control message
{ "type": "end_stream" }

// Server → Client: Transcript
{ "type": "transcript", "text": "...", "is_final": false }

// Server → Client: Session complete
{ "type": "complete", "credits_used": 5, "duration_seconds": 60 }

// Server → Client: Error
{ "type": "error", "code": "INSUFFICIENT_CREDITS", "message": "..." }
```

**Audio Format Requirements** (PLAN-R1):
- Format: WebM container with Opus codec
- Sample rate: 48kHz (Deepgram NOVA2 optimal)
- Channels: Mono (1 channel)
- Chunk size: 100-200ms of audio per WebSocket frame (recommended)
- Max frame size: 32KB
- Silence detection: Client should not send empty audio frames

**Constraints**:
- Pro tier required (403 for free users)
- Credit check before stream starts
- Max 300 seconds (5 minutes) per session
- Graceful handling of disconnects (partial transcripts preserved)

### Checkout.com
- Webhook signature verification (HMAC-SHA256)
- Idempotent event processing
- 3 retry attempts on failure before grace period

## Background Job Types

| Job Type | Trigger | Description |
|----------|---------|-------------|
| `reminder_fire` | Scheduled time | Send reminder notification |
| `streak_calculate` | Daily at UTC 00:00 | Calculate daily streaks |
| `credit_expire` | Daily at UTC 00:00 | Expire daily AI credits |
| `subscription_check` | Daily | Check subscription status, handle grace periods |
| `recurring_task_generate` | On task completion | Generate next recurring task instance |

## Event Types

| Event | Payload | Handlers |
|-------|---------|----------|
| `task.created` | task_id, user_id | Activity log |
| `task.completed` | task_id, user_id, completed_by | Achievement check, streak update, activity log |
| `task.deleted` | task_id, user_id, tombstone_id | Activity log |
| `subtask.completed` | subtask_id, task_id | Auto-complete check |
| `note.converted` | note_id, task_id | Achievement check, activity log |
| `ai.chat` | user_id, credits_used | Activity log |
| `ai.subtasks_generated` | task_id, count | Activity log |
| `subscription.created` | user_id, tier | Credit grant |
| `subscription.cancelled` | user_id | Activity log |
| `achievement.unlocked` | user_id, achievement_id | Notification, activity log |

### Achievement Notification Delivery (US9 AS4 Clarification)

**Mechanism**: Achievement unlocks are delivered inline with the triggering API response.

**Implementation**:
- When an action (e.g., task completion) triggers an achievement unlock, the response includes an `unlocked_achievements` array
- The `unlocked_achievements` array contains achievement details: id, name, description, perk
- Frontend uses this data to display toast notifications
- Achievement unlock is also logged via `achievement.unlocked` event for notification bell

**Response Schema**:
```json
{
  "task": { ... },
  "unlocked_achievements": [
    {
      "id": "tasks_5",
      "name": "Task Starter",
      "description": "Complete 5 tasks",
      "perk": { "type": "max_tasks", "value": 15 }
    }
  ]
}
```

## Rate Limiting Strategy

| Endpoint Category | Limit | Window | Implementation |
|-------------------|-------|--------|----------------|
| General API | 100 requests | 1 minute | Per-user sliding window |
| AI Endpoints | 20 requests | 1 minute | Per-user sliding window |
| Auth Endpoints | 10 requests | 1 minute | Per-IP sliding window |

**Implementation**: In-memory sliding window rate limiter. Single-instance deployment; multi-instance via Redis is out-of-scope for v1.

**Deployment Scope**: Single Railway instance for v1. Multi-instance scaling with Redis-backed rate limiting is a future consideration, not in current scope.

### Per-Task AI Request Limits (FR-035 Clarification)

**Behavior**: System warns at 5 AI requests per task and blocks at 10 requests per task.

**Scope**: Counter is session-scoped. Counter resets at session change (new access token).

**Implementation**:
- Track AI request count per (task_id, session_id) in memory
- Warn threshold: 5 requests → return `ai_request_warning: true` in response
- Block threshold: 10 requests → return 429 with `AI_TASK_LIMIT_REACHED` error
- Session change (token refresh/re-login) resets all per-task counters

## Testing Strategy

### Test Categories

1. **Contract Tests**: Verify API request/response schemas match OpenAPI spec
2. **Integration Tests**: Full request flow with test database
3. **Unit Tests**: Business logic in isolation

### Test Database Setup

- Separate test database on Neon (or local PostgreSQL)
- Alembic migrations run before test suite
- Factory-boy for generating test data
- Database reset between test modules

### External Service Mocking

- `respx` for mocking httpx requests
- Mock Google OAuth token verification
- Mock OpenAI API responses
- Mock Deepgram transcription API
- Mock Checkout.com webhooks

### Test Coverage Targets

- Core business logic: 90%+
- API endpoints: 80%+
- Event handlers: 80%+
- Background jobs: 70%+

## Deployment Architecture

### Environments

| Environment | Infrastructure | Database | Purpose |
|-------------|---------------|----------|---------|
| **Local** | Docker Compose | Local PostgreSQL | Development and testing |
| **Staging** | Railway (preview branch) | Neon (staging branch) | Pre-production testing |
| **Production** | Railway (main branch) | Neon (main branch) | Live application |

### Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │            Railway                   │
                    │  ┌─────────────┐  ┌─────────────┐  │
                    │  │   API       │  │   Worker    │  │
Internet ──────────►│  │   Service   │  │   Service   │  │
                    │  │  (FastAPI)  │  │  (jobs)     │  │
                    │  └──────┬──────┘  └──────┬──────┘  │
                    │         │                │          │
                    │         └────────┬───────┘          │
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │     Neon         │                  │
                    │  ┌───────────────▼───────────────┐  │
                    │  │     PostgreSQL Database       │  │
                    │  │   (schemas: auth, tasks,      │  │
                    │  │    notes, billing, etc.)      │  │
                    │  └───────────────────────────────┘  │
                    └─────────────────────────────────────┘
```

**Note**: Single Railway instance per environment for v1. No multi-instance load balancing required.

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# JWT
JWT_PRIVATE_KEY=<RSA private key PEM>
JWT_PUBLIC_KEY=<RSA public key PEM>
JWT_ALGORITHM=RS256
JWT_ACCESS_EXPIRY_MINUTES=15
JWT_REFRESH_EXPIRY_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4-turbo

# Deepgram
DEEPGRAM_API_KEY=xxx

# Checkout.com
CHECKOUT_SECRET_KEY=sk_xxx
CHECKOUT_WEBHOOK_SECRET=whsec_xxx

# Rate Limits (configurable per constitution)
RATE_LIMIT_GENERAL=100
RATE_LIMIT_AI=20
RATE_LIMIT_AUTH=10

# AI Credits
AI_CREDIT_CHAT=1
AI_CREDIT_SUBTASK=1
AI_CREDIT_CONVERSION=1
AI_CREDIT_TRANSCRIPTION_PER_MIN=5
KICKSTART_CREDITS=5
PRO_DAILY_CREDITS=10
PRO_MONTHLY_CREDITS=100
MAX_CREDIT_CARRYOVER=50

# Feature Flags
ENABLE_VOICE_TRANSCRIPTION=true
```

## Migration Strategy

Alembic migrations in strict order:

1. `001_initial_schema.py` - Users, task_instances, task_templates, subtasks
2. `002_notes_reminders.py` - Notes, reminders tables
3. `003_achievements.py` - Achievement definitions, user_achievement_states
4. `004_credits_subscriptions.py` - AI credit ledger, subscriptions
5. `005_activity_tombstones.py` - Activity logs, deletion tombstones
6. `006_notifications.py` - Notifications table
7. `007_job_queue.py` - Background job queue table
8. `008_indexes.py` - Performance indexes

## Implementation Phases (for tasks.md)

### Phase 1: Foundation (P1 Stories)
- Project setup, dependencies, configuration
- Database models and migrations
- Authentication endpoints (Google OAuth, JWT)
- User profile endpoint (PATCH /api/v1/users/me - FR-070)
- Health check endpoints

### Phase 2: Core CRUD (P1-P2 Stories)
- Task CRUD endpoints
- Subtask management
- Note CRUD
- Basic validation and error handling

### Phase 3: Advanced Features (P2-P3 Stories)
- Recurring task templates
- Reminder system
- Event system and handlers
- Background job infrastructure

### Phase 4: AI Integration (P3 Stories)
- OpenAI client integration
- AI chat endpoint (SSE streaming)
- Subtask generation
- Note-to-task conversion
- Credit consumption
- WebSocket voice streaming relay to Deepgram (Pro only)

### Phase 5: Gamification (P3-P4 Stories)
- Achievement system
- Streak calculation
- Effective limits computation

### Phase 6: Billing & Notifications (P4 Stories)
- Subscription management
- Checkout.com webhook handling
- Notification system
- Push notification infrastructure

### Phase 7: Recovery & Polish (P4 Stories)
- Tombstone and recovery system
- Focus mode tracking
- Activity logging
- Rate limiting
- API documentation

## Next Steps

1. Generate `research.md` to resolve any remaining unknowns
2. Create `quickstart.md` for local development setup
3. Generate OpenAPI specification in `contracts/openapi.yaml`
4. Proceed to `/sp.tasks` for task generation

---

**Plan Status**: Complete
**Branch**: `003-perpetua-backend`
**Artifacts**:
- [spec.md](spec.md) - Feature specification
- [docs/data-model.md](docs/data-model.md) - Database entities
- [docs/api-specification.md](docs/api-specification.md) - API details
- [docs/authentication.md](docs/authentication.md) - Auth flows
