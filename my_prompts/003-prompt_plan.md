Generate an implementation plan for the Perpetua Flow Backend API.

## Feature Context
- **Feature Branch**: 003-perpetua-backend
- **Spec Location**: specs/003-perpetua-backend/spec.md
- **Authoritative Spec**: 003-backend.md (root)
- **Frontend Contract**: frontend/docs/API_CONTRACTS.md (needs updates to align with backend spec)

## Technology Stack (Confirmed)
- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic
- **Background Jobs**: PostgreSQL-based queue (SKIP LOCKED pattern)
- **Events**: In-process event bus (synchronous)
- **Deployment**: Railway (persistent container)
- **IaC**: Pulumi/Terraform for Railway + Neon provisioning

## Architecture Decisions (Pre-confirmed)

### Database
- Single database with multiple schemas (auth, tasks, billing, etc.)
- Alembic for migrations with SQLModel models

### Authentication
- Frontend (BetterAuth) sends Google ID token
- Backend verifies with Google, issues own JWT (15min access, 7-day refresh)
- Refresh tokens rotate on use (one-time)

### Background Processing
- Hybrid approach: API handles light async, separate worker for heavy jobs
- PostgreSQL queue with SKIP LOCKED for job processing
- Worker runs as separate Railway service

### AI Integration
- OpenAI Agents SDK (server-side only)
- AI returns structured suggestions; backend validates and executes
- Chat supports SSE streaming for token-by-token responses
- Voice transcription (Deepgram) is batch-only, not streaming

### Testing
- E2E tests with test database and dummy data
- Contract testing to ensure frontend/backend alignment
- Mocked external services (OpenAI, Deepgram, Checkout.com)

### Infrastructure
- Railway: Two services (API + Worker)
- Single environment (production), local for dev
- IaC includes: Railway project/services, Neon database, environment secrets

## Scope: Full Spec Implementation

All user stories P1-P4:
1. User Authentication via Google OAuth (P1)
2. Task Creation and Management (P1)
3. Recurring Task Templates (P2)
4. Subtask Management (P2)
5. Notes with Voice Recording (P2)
6. AI Chat Widget (P3)
7. Auto Subtask Generation (P3)
8. Reminder System (P3)
9. Achievement System (P3)
10. Pro Subscription Management (P4)
11. AI Credit System (P4)
12. Focus Mode Tracking (P4)
13. Task Deletion and Recovery (P4)

## Required Plan Outputs

### 1. Database Schema Design
- All tables across schemas (auth, tasks, notes, billing, achievements, activity)
- Indexes for query performance
- Foreign key relationships and constraints

### 2. API Endpoint Design
Design all endpoints including those missing from frontend contract:

**Auth**
- POST /api/v1/auth/google
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

**Tasks** (align with spec, update frontend contract)
- Full CRUD with spec-compliant fields

**AI Endpoints** (new)
- POST /api/v1/ai/chat (SSE streaming)
- POST /api/v1/ai/subtasks
- POST /api/v1/ai/convert-note

**Voice** (new)
- POST /api/v1/voice/transcribe

**Credits** (new)
- GET /api/v1/credits
- GET /api/v1/credits/history

**Subscription** (new)
- GET /api/v1/subscription
- POST /api/v1/subscription/checkout
- POST /api/v1/subscription/cancel
- POST /api/v1/webhooks/checkout (webhook handler)

**Notifications** (new)
- GET /api/v1/notifications
- PATCH /api/v1/notifications/:id/read
- POST /api/v1/notifications/read-all
- POST /api/v1/push/subscribe
- DELETE /api/v1/push/unsubscribe

**Recovery** (new)
- GET /api/v1/recovery/tombstones
- POST /api/v1/recovery/:id/restore

**Focus Mode** (new)
- POST /api/v1/focus/start
- POST /api/v1/focus/end

### 3. Background Job Design
- Job types: reminders, streak calculation, credit expiry, subscription renewal
- Queue schema and worker implementation
- Retry and failure handling

### 4. Event System Design
- Event types and payload schemas
- In-process event bus implementation
- Event handlers (achievement checks, activity logging, notifications)

### 5. External Service Integration
- Google OAuth verification
- OpenAI Agents SDK integration pattern
- Deepgram NOVA2 batch transcription
- Checkout.com webhook handling with signature verification

### 6. Infrastructure as Code
- Pulumi/Terraform for Railway (API service, Worker service)
- Neon database provisioning
- Environment variable and secret management

### 7. Contract Alignment
- Document all frontend contract changes needed
- Generate OpenAPI spec from FastAPI for frontend consumption

### 8. Testing Strategy
- Test database setup and fixtures
- E2E test structure
- Contract test implementation
- External service mocking approach

## Constraints & Non-Goals

**Constraints**:
- All timestamps UTC
- Strong consistency for direct reads, eventual for aggregates
- Rate limits: 100/min general, 20/min AI, 10/min auth
- No email/SMS notifications at launch

**Non-Goals**:
- Kubernetes deployment
- Multi-region setup
- Real-time WebSocket features (except SSE for AI chat)
- Mobile push notifications (browser only)

## Success Criteria Reference
- 95% of API responses < 500ms
- AI chat responses < 5s for 95%
- 99.5% uptime
- Zero data loss under normal operation
