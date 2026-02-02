# Perpetua Flow Backend API

Production-grade Python FastAPI backend for the Perpetua Flow task management application.

## Overview

RESTful API providing:

- **Authentication**: Google OAuth with RS256 JWT tokens
- **Task Management**: Full CRUD with subtasks, recurring templates, optimistic locking
- **Notes**: Text and voice notes with tier-based limits
- **AI Features**: Chat assistant, subtask generation, note-to-task conversion, voice transcription
- **Gamification**: Achievements, streaks, focus tracking
- **Billing**: Pro subscriptions via Checkout.com webhooks
- **Notifications**: In-app and WebPush delivery

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.109+ |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | PostgreSQL 15+ (Neon Serverless) |
| Migrations | Alembic |
| Auth | RS256 JWT via PyJWT |
| AI | OpenAI Agents SDK |
| Voice | Deepgram NOVA2 |
| Payments | Checkout.com webhooks |
| Metrics | Prometheus |
| Logging | structlog (JSON) |
| Rate Limiting | slowapi |

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or [Neon](https://neon.tech) free tier)
- Docker (optional)

### Setup

```bash
# Clone and enter backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your values (see Environment Variables section below)

# Generate JWT keys
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
# Copy key contents to JWT_PRIVATE_KEY and JWT_PUBLIC_KEY in .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --port 8000
```

### Docker Compose

```bash
# Start all services (API + Worker + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   └── versions/            # Migration scripts
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic Settings configuration
│   ├── dependencies.py      # Dependency injection
│   ├── api/                 # Route handlers
│   │   ├── router.py        # Centralized v1 router
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tasks.py         # Task CRUD
│   │   ├── subtasks.py      # Subtask operations
│   │   ├── notes.py         # Note management
│   │   ├── ai.py            # AI features
│   │   ├── achievements.py  # Achievement system
│   │   ├── subscription.py  # Billing
│   │   └── health.py        # Health checks
│   ├── models/              # SQLModel database models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   ├── events/              # In-process event bus
│   ├── jobs/                # Background job processing
│   ├── integrations/        # External service clients
│   ├── middleware/          # Request pipeline
│   └── lib/                 # Utility libraries
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── contract/            # API contract tests
│   ├── load/                # k6 load tests
│   └── factories/           # Test data factories
├── worker/                  # Background job worker
├── docs/                    # Operational documentation
├── pyproject.toml           # Dependencies and tooling
├── Dockerfile               # API container
├── Dockerfile.worker        # Worker container
├── docker-compose.yml       # Local development stack
└── .env.example             # Environment template
```

## API Documentation

When running locally:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health**: http://localhost:8000/health/live

All API endpoints are under `/api/v1/`.

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/google/callback` | Google OAuth sign-in |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/tasks` | List tasks (paginated) |
| POST | `/api/v1/tasks` | Create task |
| PATCH | `/api/v1/tasks/:id` | Update task (optimistic locking) |
| POST | `/api/v1/ai/chat` | AI chat (SSE streaming) |
| POST | `/api/v1/ai/generate-subtasks` | AI subtask suggestions |
| GET | `/api/v1/achievements` | User achievements and stats |
| POST | `/api/v1/webhooks/checkout` | Payment webhook |

## Running Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Specific categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/contract/ -v

# Specific test
pytest tests/unit/services/test_task_service.py -v
```

### Coverage Targets

| Module | Target |
|--------|--------|
| Core services | 90%+ |
| API endpoints | 80%+ |
| Event handlers | 80%+ |
| Background jobs | 70%+ |

## Background Worker

The worker process handles async jobs via a PostgreSQL-based SKIP LOCKED queue:

```bash
# Start worker (separate terminal)
python -m worker.main
```

**Job types**: `reminder_fire`, `streak_calculate`, `credit_expire`, `subscription_check`, `recurring_task_generate`

## Environment Variables

See [.env.example](.env.example) for the complete list. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection (asyncpg) |
| `JWT_PRIVATE_KEY` | Yes | RSA private key (PEM) |
| `JWT_PUBLIC_KEY` | Yes | RSA public key (PEM) |
| `GOOGLE_CLIENT_ID` | Yes | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth client secret |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key |
| `ENVIRONMENT` | No | `development` / `staging` / `production` |

## Deployment

### Railway

```bash
# Deploy API service
railway up

# Deploy worker (separate service)
railway up --service worker
```

See `railway.toml` for configuration.

### Docker

```bash
# Build
docker build -t perpetua-api .
docker build -t perpetua-worker -f Dockerfile.worker .

# Run
docker run -p 8000:8000 --env-file .env perpetua-api
docker run --env-file .env perpetua-worker
```

## Code Quality

```bash
# Format
ruff format src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## Architecture

- **Middleware chain**: RequestID → Logging → Metrics → Auth → Idempotency → CORS → Security Headers
- **Event-driven**: In-process event bus for decoupled side effects (activity logging, achievement checks)
- **Background jobs**: PostgreSQL SKIP LOCKED queue with dedicated worker process
- **AI agents**: OpenAI Agents SDK with structured output types and 30s timeout
- **Optimistic locking**: Version field on mutable entities prevents concurrent update conflicts
- **Idempotency**: `Idempotency-Key` header for safe POST/PATCH retries

## License

MIT
