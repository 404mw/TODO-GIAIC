# Quickstart: Perpetua Flow Backend

**Feature**: 003-perpetua-backend
**Date**: 2026-01-19

This guide covers local development setup for the Perpetua Flow backend API.

---

## Prerequisites

- **Python**: 3.11+ ([pyenv](https://github.com/pyenv/pyenv) recommended)
- **PostgreSQL**: 15+ (local or [Neon](https://neon.tech) free tier)
- **Docker**: Optional, for containerized development
- **Git**: For version control

---

## 1. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/your-org/perpetua-flow.git
cd perpetua-flow

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -e ".[dev]"
```

---

## 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

```bash
# Database (local PostgreSQL or Neon)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/perpetua_dev

# JWT Keys (generate with: openssl genrsa -out private.pem 2048)
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...your private key...
-----END RSA PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
...your public key...
-----END PUBLIC KEY-----"
JWT_ALGORITHM=RS256
JWT_ACCESS_EXPIRY_MINUTES=15
JWT_REFRESH_EXPIRY_DAYS=7

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# External Services (use test/mock keys for local dev)
OPENAI_API_KEY=sk-test-key
DEEPGRAM_API_KEY=test-key
CHECKOUT_SECRET_KEY=sk_test_key
CHECKOUT_WEBHOOK_SECRET=whsec_test

# Rate Limits
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

# Development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 3. Generate JWT Keys

Generate RSA key pair for JWT signing:

```bash
# Generate private key
openssl genrsa -out private.pem 2048

# Extract public key
openssl rsa -in private.pem -pubout -out public.pem

# View keys (copy to .env)
cat private.pem
cat public.pem
```

---

## 4. Database Setup

### Option A: Local PostgreSQL

```bash
# Create database
createdb perpetua_dev

# Or with Docker
docker run -d \
  --name perpetua-postgres \
  -e POSTGRES_DB=perpetua_dev \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/perpetua_dev
```

### Option B: Neon Serverless (Recommended)

1. Create account at [neon.tech](https://neon.tech)
2. Create new project "perpetua-dev"
3. Copy connection string to `.env`

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Run Migrations

```bash
# Apply all migrations
alembic upgrade head

# Check current migration
alembic current

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description"
```

---

## 5. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable "Google+ API" (for profile access)
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Application type: "Web application"
6. Authorized redirect URIs:
   - `http://localhost:3000/auth/callback` (frontend dev)
   - `http://localhost:8000/api/v1/auth/google/callback` (backend dev)
7. Copy Client ID and Secret to `.env`

---

## 6. Running the Application

### Development Server

```bash
# Start FastAPI with hot reload
uvicorn src.main:app --reload --port 8000

# Or with more options
uvicorn src.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level debug
```

### Background Worker

```bash
# In separate terminal
python -m worker.main
```

### Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## 7. API Documentation

Once running, access the interactive docs:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

---

## 8. Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run specific test file
pytest tests/unit/test_credit_service.py -v

# Run tests matching pattern
pytest -k "test_task" -v
```

### Test Database

Tests use a separate database:

```bash
# Create test database
createdb perpetua_test

# Or set TEST_DATABASE_URL in .env
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/perpetua_test
```

---

## 9. Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type check
mypy src

# All checks (pre-commit)
pre-commit run --all-files
```

---

## 10. Common Development Tasks

### Create New API Endpoint

1. Add route in `src/api/{resource}.py`
2. Add schemas in `src/schemas/{resource}.py`
3. Add service logic in `src/services/{resource}_service.py`
4. Add tests in `tests/`
5. Run tests: `pytest -v`

### Add New Database Model

1. Create model in `src/models/{entity}.py`
2. Import in `src/models/__init__.py`
3. Generate migration: `alembic revision --autogenerate -m "Add {entity}"`
4. Review migration in `alembic/versions/`
5. Apply: `alembic upgrade head`

### Add Background Job

1. Create job in `src/jobs/tasks/{job_name}_job.py`
2. Register job type in `src/jobs/queue.py`
3. Add tests in `tests/unit/test_{job_name}_job.py`

---

## 11. Project Structure Reference

```
backend/
├── alembic/                 # Database migrations
├── src/
│   ├── api/                 # Route handlers
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── events/              # Event bus
│   ├── jobs/                # Background jobs
│   ├── integrations/        # External APIs
│   ├── middleware/          # FastAPI middleware
│   ├── config.py            # Settings
│   └── main.py              # Application entry
├── tests/
│   ├── conftest.py          # Fixtures
│   ├── contract/            # API contracts
│   ├── integration/         # E2E tests
│   └── unit/                # Unit tests
├── worker/                  # Background worker
├── pyproject.toml           # Dependencies
├── alembic.ini              # Alembic config
└── .env.example             # Environment template
```

---

## 12. Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection string
psql "postgresql://postgres:password@localhost:5432/perpetua_dev"
```

### Migration Issues

```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head

# Check migration history
alembic history
```

### JWT Issues

```bash
# Verify key pair matches
openssl rsa -in private.pem -pubout | diff - public.pem
```

### Port Already in Use

```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

---

## 13. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `JWT_PRIVATE_KEY` | Yes | - | RSA private key (PEM) |
| `JWT_PUBLIC_KEY` | Yes | - | RSA public key (PEM) |
| `GOOGLE_CLIENT_ID` | Yes | - | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | - | OAuth client secret |
| `OPENAI_API_KEY` | No | - | OpenAI API key |
| `DEEPGRAM_API_KEY` | No | - | Deepgram API key |
| `DEBUG` | No | false | Enable debug mode |
| `LOG_LEVEL` | No | INFO | Logging level |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |

---

## Next Steps

1. Run the development server
2. Test authentication flow
3. Create sample tasks via API
4. Run test suite
5. Review API documentation

For full API specification, see [docs/api-specification.md](docs/api-specification.md).
