# Research: Perpetua Flow Backend API

**Feature**: 003-perpetua-backend
**Date**: 2026-01-19
**Status**: Complete

## Overview

This document consolidates research findings for all technical decisions and unknowns identified during the planning phase. All items marked "NEEDS CLARIFICATION" have been resolved.

---

## 1. Authentication & Token Management

### Research Task: Google OAuth token verification best practices

**Decision**: Verify Google ID tokens directly using Google's public JWKS

**Rationale**:
- Google provides a well-documented JWKS endpoint for token verification
- ID tokens contain all necessary user claims (email, name, picture)
- No need to call Google's userinfo endpoint - reduces latency
- Token verification is stateless and cacheable

**Implementation Details**:
- JWKS URL: `https://www.googleapis.com/oauth2/v3/certs`
- Cache JWKS with 24-hour TTL (keys rotate monthly)
- Validate `iss` claim is `https://accounts.google.com`
- Validate `aud` claim matches our client ID
- Extract `sub`, `email`, `name`, `picture` from verified token

**Alternatives Considered**:
- Google's userinfo endpoint: Additional network call, higher latency
- Passing through Google access tokens: Security risk, couples to Google's token lifecycle

---

## 2. JWT Implementation

### Research Task: JWT signing algorithm and key management

**Decision**: RS256 (RSA-SHA256) with manual key rotation

**Rationale**:
- RS256 allows public key distribution for verification without exposing signing key
- Asymmetric keys provide better security for distributed systems
- 15-minute access token expiry balances security and user experience
- 7-day refresh token with rotation prevents replay attacks

**Implementation Details**:
- Generate 2048-bit RSA key pair
- Store private key in environment variable (PEM format)
- Expose public key via `/.well-known/jwks.json` endpoint
- Key ID (kid) header enables graceful key rotation
- 7-day overlap period during rotation

**Key Rotation Process**:
1. Generate new key pair, assign new kid
2. Add new public key to JWKS endpoint
3. Sign new tokens with new key
4. Accept both old and new keys for verification
5. After 7 days, remove old key from JWKS

---

## 3. Database Connection Pooling

### Research Task: Neon Serverless connection management

**Decision**: Use Neon's serverless driver with connection pooling

**Rationale**:
- Neon provides built-in connection pooling via PgBouncer
- Serverless driver handles connection lifecycle automatically
- Pooler URL format: `postgresql://user:pass@hostname/db?sslmode=require`
- Default pool size suitable for Railway deployment

**Configuration**:
```python
# SQLAlchemy async engine with Neon pooler
DATABASE_URL = "postgresql+asyncpg://user:pass@hostname/db?sslmode=require"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
```

**Connection Limits**:
- Neon Free: 100 concurrent connections
- Pool size: 5 base + 10 overflow = 15 per service
- Two services (API + Worker) = 30 total, well within limits

---

## 4. Background Job Queue Pattern

### Research Task: PostgreSQL SKIP LOCKED implementation

**Decision**: Custom PostgreSQL-based queue with advisory locks

**Rationale**:
- No additional infrastructure required
- PostgreSQL's `FOR UPDATE SKIP LOCKED` prevents double-processing
- Simpler than external message brokers for current scale
- Native PostgreSQL with proper indexing performs well

**Queue Table Schema**:
```sql
CREATE TABLE job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_job_queue_pending (status, scheduled_at, priority)
    WHERE status = 'pending'
);
```

**Worker Query**:
```sql
UPDATE job_queue
SET status = 'processing', started_at = NOW()
WHERE id = (
    SELECT id FROM job_queue
    WHERE status = 'pending'
      AND scheduled_at <= NOW()
    ORDER BY priority DESC, scheduled_at ASC
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
RETURNING *;
```

---

## 5. OpenAI Integration

### Research Task: OpenAI Agents SDK (openai-agents) for structured AI operations

**Decision**: Use OpenAI Agents SDK with agent-based architecture and tool definitions

**Rationale**:
- Agent-based architecture provides better separation of concerns
- Built-in tool definitions enable structured, validated interactions
- Native streaming support via `Runner.run_streamed()`
- Built-in tracing and observability
- Automatic context management and conversation threading
- Model: gpt-4-turbo for better instruction following

**Agent Setup**:
```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel

# Define structured output schemas
class SubtaskSuggestion(BaseModel):
    title: str

class SubtaskGenerationResult(BaseModel):
    subtasks: list[SubtaskSuggestion]

class ActionSuggestion(BaseModel):
    action_type: str  # create_task, update_task, complete_task
    payload: dict

# Define tools the agent can use
@function_tool
def suggest_action(action_type: str, payload: dict) -> dict:
    """Suggest an action for the user to confirm (create, update, complete task)."""
    return {"action_type": action_type, "payload": payload, "requires_confirmation": True}

# Create the task assistant agent
task_agent = Agent(
    name="PerpetualFlowAssistant",
    instructions=SYSTEM_PROMPT,
    model="gpt-4-turbo",
    tools=[suggest_action],
)
```

**Chat Implementation (Streaming)**:
```python
from agents import Runner

async def chat_stream(user_message: str, tasks: list[Task]):
    context = build_task_context(tasks)

    async with Runner.run_streamed(
        task_agent,
        input=f"Context:\n{context}\n\nUser: {user_message}",
    ) as stream:
        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                yield event.data
```

**Subtask Generation (Structured Output)**:
```python
from agents import Agent, Runner

subtask_agent = Agent(
    name="SubtaskGenerator",
    instructions="Generate actionable subtasks for the given task. Be specific and practical.",
    model="gpt-4-turbo",
    output_type=SubtaskGenerationResult,
)

async def generate_subtasks(task: Task, max_count: int) -> list[dict]:
    result = await Runner.run(
        subtask_agent,
        input=f"Generate up to {max_count} subtasks for:\nTask: {task.title}\nDescription: {task.description}",
    )
    return [{"title": s.title} for s in result.final_output.subtasks[:max_count]]
```

**Benefits over raw OpenAI API**:
- Cleaner separation between agent definition and execution
- Built-in output validation via Pydantic models
- Automatic retry and error handling
- Native streaming with event types
- Tracing for debugging and observability

---

## 6. Deepgram Transcription

### Research Task: Deepgram NOVA2 batch transcription

**Decision**: Use Deepgram's pre-recorded API with NOVA2 model

**Rationale**:
- NOVA2 has best accuracy for general English
- Pre-recorded (batch) API is simpler than real-time streaming
- Supports audio URLs (no need to upload binary data)
- Automatic language detection available

**Implementation**:
```python
from deepgram import Deepgram

async def transcribe_audio(audio_url: str) -> str:
    client = Deepgram(DEEPGRAM_API_KEY)
    response = await client.transcription.prerecorded(
        {"url": audio_url},
        {
            "model": "nova-2",
            "language": "en",
            "punctuate": True,
            "smart_format": True,
        }
    )
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]
```

**Pricing**: $0.0043/minute for NOVA2 → 5 credits/minute maps to $0.0215/credit

---

## 7. Checkout.com Webhook Security

### Research Task: Webhook signature verification

**Decision**: HMAC-SHA256 signature verification

**Rationale**:
- Checkout.com uses standard HMAC-SHA256 for webhook signatures
- Signature in `Cko-Signature` header
- Timestamp included to prevent replay attacks

**Implementation**:
```python
import hmac
import hashlib

def verify_checkout_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Webhook Events to Handle**:
- `payment_captured` - Subscription activated
- `payment_declined` - Payment failed
- `subscription_cancelled` - User cancelled
- `subscription_renewed` - Monthly renewal

---

## 8. SSE Streaming Implementation

### Research Task: Server-Sent Events in FastAPI

**Decision**: FastAPI StreamingResponse with async generators

**Rationale**:
- Native support in FastAPI via StreamingResponse
- Simple text-based protocol, wide browser support
- Automatic reconnection handling in EventSource API
- Better than WebSockets for unidirectional server-to-client streaming

**Implementation**:
```python
from fastapi.responses import StreamingResponse

async def ai_chat_stream(message: str):
    async def generate():
        async for chunk in openai_stream(message):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

## 9. Rate Limiting Strategy

### Research Task: Rate limiting implementation options

**Decision**: In-memory sliding window with slowapi

**Rationale**:
- `slowapi` provides Redis-optional rate limiting for FastAPI
- In-memory storage sufficient for single-instance Railway deployment
- Per-user limits use JWT sub claim
- Per-IP limits for unauthenticated endpoints (auth)

**Implementation**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_user_id(request: Request) -> str:
    # Extract from JWT if authenticated
    if hasattr(request.state, "user"):
        return str(request.state.user.id)
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_id)

@app.get("/api/v1/tasks")
@limiter.limit("100/minute")
async def list_tasks(request: Request):
    ...
```

---

## 10. RRULE Parsing

### Research Task: Recurrence rule parsing library

**Decision**: python-dateutil rrule module

**Rationale**:
- Standard RFC 5545 RRULE format
- Well-tested library, part of python-dateutil
- Handles complex recurrence patterns
- Easy to calculate next occurrence

**Implementation**:
```python
from dateutil.rrule import rrulestr
from datetime import datetime, timezone

def calculate_next_due(rrule_string: str, after: datetime) -> datetime:
    rule = rrulestr(rrule_string, dtstart=after)
    return rule.after(after, inc=False)

# Example
rrule = "FREQ=WEEKLY;BYDAY=MO,WE,FR"
next_date = calculate_next_due(rrule, datetime.now(timezone.utc))
```

---

## 11. Credit FIFO Consumption

### Research Task: Credit consumption order implementation

**Decision**: Database-level FIFO with transaction isolation

**Rationale**:
- Credits must be consumed in strict order: daily → subscription → purchased
- Expiration must be respected (daily credits expire at UTC midnight)
- Transaction isolation prevents race conditions
- Single SQL query can handle consumption

**Implementation**:
```sql
-- Consume credits in FIFO order
WITH available AS (
    SELECT id, credit_type, amount - COALESCE(consumed, 0) as remaining
    FROM ai_credits
    WHERE user_id = $1
      AND (expires_at IS NULL OR expires_at > NOW())
      AND amount > COALESCE(consumed, 0)
    ORDER BY
        CASE credit_type
            WHEN 'daily' THEN 1
            WHEN 'subscription' THEN 2
            WHEN 'purchased' THEN 3
        END,
        created_at
    FOR UPDATE
),
to_consume AS (
    SELECT id, LEAST(remaining, $2 - SUM(LEAST(remaining, $2)) OVER (ORDER BY ...)) as consume_amount
    FROM available
    WHERE ...
)
UPDATE ai_credits SET consumed = consumed + to_consume.consume_amount
FROM to_consume WHERE ai_credits.id = to_consume.id;
```

---

## 12. Idempotency Key Implementation

### Research Task: Idempotency key storage and lookup

**Decision**: PostgreSQL table with unique constraint

**Rationale**:
- 24-hour key validity requires persistent storage
- Unique constraint prevents race conditions
- Store request hash and response for replay
- Cleanup old keys via background job

**Schema**:
```sql
CREATE TABLE idempotency_keys (
    key UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    request_path VARCHAR(255) NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    response_status INTEGER,
    response_body JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_idempotency_cleanup ON idempotency_keys (expires_at)
WHERE response_status IS NOT NULL;
```

---

## Summary

All technical unknowns have been resolved:

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Google OAuth | Direct ID token verification | Stateless, cacheable, no extra API calls |
| JWT | RS256 with 15min/7day expiry | Security + UX balance |
| Database | Neon pooler, asyncpg | Built-in pooling, async support |
| Job Queue | PostgreSQL SKIP LOCKED | No extra infrastructure |
| OpenAI | Agents SDK (openai-agents) | Agent-based architecture, tool definitions, built-in streaming |
| Deepgram | NOVA2 batch API | Best accuracy, simple integration |
| Checkout | HMAC-SHA256 verification | Standard webhook security |
| Rate Limiting | slowapi in-memory | Simple, sufficient for scale |
| RRULE | python-dateutil | RFC 5545 standard |
| Credits | FIFO via SQL | Atomic, race-free consumption |
| Idempotency | PostgreSQL table | 24h persistence, cleanup |

---

**Research Status**: Complete
**Next Step**: Proceed to Phase 1 artifacts (quickstart.md, contracts/)
