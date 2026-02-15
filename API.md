# Perpetua Flow Backend API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000` (development) | `https://api.perpetua.com` (production)
**API Prefix:** `/api/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Request & Response Formats](#request--response-formats)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Idempotency](#idempotency)
7. [API Endpoints](#api-endpoints)
   - [Health](#health)
   - [Authentication](#authentication-endpoints)
   - [Users](#users)
   - [Tasks](#tasks)
   - [Subtasks](#subtasks)
   - [Templates](#templates)
   - [Notes](#notes)
   - [Reminders](#reminders)
   - [AI](#ai)
   - [Credits](#credits)
   - [Achievements](#achievements)
   - [Focus Mode](#focus-mode)
   - [Subscriptions](#subscriptions)
   - [Recovery](#recovery)
   - [Notifications](#notifications)
   - [Activity Logs](#activity-logs)

---

## Overview

The Perpetua Flow Backend API is a RESTful API built with FastAPI for task management and productivity features. It provides:

- **OAuth 2.0 Authentication** via Google (handled by BetterAuth on frontend)
- **JWT-based authorization** with access and refresh tokens
- **AI-powered features** for chat, subtask generation, and voice transcription
- **Credit system** for AI usage
- **Achievement system** for gamification
- **Comprehensive task management** with subtasks, notes, reminders, and templates

---

## Authentication

### Authentication Flow

The API uses a **two-token system** with JWT access tokens and opaque refresh tokens:

1. **Frontend** handles Google OAuth flow via BetterAuth
2. **Frontend** sends Google ID token to backend `/api/v1/auth/google/callback`
3. **Backend** verifies Google token and issues:
   - **Access token** (JWT, 15 minutes expiry)
   - **Refresh token** (opaque, 7 days expiry)
4. **Frontend** uses access token in `Authorization` header for API requests
5. **Frontend** refreshes tokens before expiry using `/api/v1/auth/refresh`

### Token Types

#### Access Token (JWT)
- **Type:** JSON Web Token (JWT)
- **Lifetime:** 15 minutes
- **Usage:** Include in `Authorization: Bearer <access_token>` header
- **Structure:**
  ```json
  {
    "sub": "user-uuid",
    "email": "user@example.com",
    "tier": "free",
    "exp": 1234567890,
    "jti": "session-uuid"
  }
  ```

#### Refresh Token
- **Type:** Opaque token (random string)
- **Lifetime:** 7 days
- **Usage:** Used only for token refresh endpoint
- **Rotation:** Single-use tokens (new token issued on each refresh)

### Authentication Headers

All authenticated requests must include:

```http
Authorization: Bearer <access_token>
```

For AI endpoints, also include:

```http
Idempotency-Key: <uuid>
```

### Public Endpoints (No Auth Required)

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `POST /api/v1/auth/google/callback` - Google OAuth callback
- `POST /api/v1/auth/refresh` - Refresh tokens
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/.well-known/jwks.json` - JWKS for JWT verification

---

## Request & Response Formats

### Content Type

All requests and responses use `application/json`.

### Request Headers

```http
Content-Type: application/json
Authorization: Bearer <access_token>
Idempotency-Key: <uuid>  # Required for mutations (POST, PUT, PATCH, DELETE)
```

### Response Wrappers

#### Single Item Response

```json
{
  "data": {
    "id": "uuid",
    "field": "value"
  }
}
```

#### Paginated Response

```json
{
  "data": [
    { "id": "uuid", "field": "value" }
  ],
  "pagination": {
    "offset": 0,
    "limit": 25,
    "total": 100,
    "has_more": true
  }
}
```

### Pagination Parameters

```
offset: int (default: 0, min: 0)
limit: int (default: 25, min: 1, max: 100)
```

---

## Error Handling

### Error Response Format

All errors return a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "field_name",
        "message": "Field-specific error"
      }
    ],
    "request_id": "req-uuid"
  }
}
```

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request body, validation error |
| 401 | Unauthorized | Missing or invalid access token |
| 402 | Payment Required | Insufficient credits |
| 403 | Forbidden | Tier upgrade required |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Version conflict, limit exceeded |
| 429 | Too Many Requests | Rate limit exceeded |
| 503 | Service Unavailable | AI service unavailable |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Authentication required |
| `TOKEN_EXPIRED` | 401 | Access token expired (refresh needed) |
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token invalid or revoked |
| `FORBIDDEN` | 403 | Access denied |
| `TIER_REQUIRED` | 403 | Pro tier required for this feature |
| `NOT_FOUND` | 404 | Resource not found |
| `TASK_NOT_FOUND` | 404 | Task not found |
| `INSUFFICIENT_CREDITS` | 402 | Not enough AI credits |
| `CONFLICT` | 409 | Version conflict (optimistic locking) |
| `LIMIT_EXCEEDED` | 409 | Task limit exceeded for tier |
| `ARCHIVED` | 409 | Cannot modify archived task |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `AI_TASK_LIMIT_REACHED` | 429 | Too many AI requests per session |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI service temporarily unavailable |
| `TRANSCRIPTION_SERVICE_UNAVAILABLE` | 503 | Voice transcription unavailable |

### Error Handling Example (TypeScript)

```typescript
try {
  const response = await fetch('/api/v1/tasks', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();

    // Handle specific error codes
    switch (error.error.code) {
      case 'TOKEN_EXPIRED':
        // Refresh token and retry
        await refreshTokens();
        return retryRequest();

      case 'INSUFFICIENT_CREDITS':
        // Show upgrade modal
        showUpgradeModal();
        break;

      case 'RATE_LIMIT_EXCEEDED':
        // Show rate limit message
        const retryAfter = response.headers.get('X-RateLimit-Reset');
        showRateLimitMessage(retryAfter);
        break;

      default:
        // Show generic error
        showError(error.error.message);
    }
  }

  const data = await response.json();
  return data;

} catch (err) {
  console.error('Network error:', err);
  showNetworkError();
}
```

---

## Rate Limiting

### Rate Limit Categories

| Category | Limit | Scope | Endpoints |
|----------|-------|-------|-----------|
| **Auth** | 10/min | Per IP | `/auth/*` |
| **AI** | 20/min | Per User | `/ai/*` |
| **General** | 100/min | Per User | All others |

### Rate Limit Headers

Response headers indicate rate limit status:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200  # Unix timestamp
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "request_id": "req-uuid"
  }
}
```

### Handling Rate Limits (TypeScript)

```typescript
const response = await fetch(url, options);

if (response.status === 429) {
  const resetTime = parseInt(response.headers.get('X-RateLimit-Reset') || '0');
  const waitTime = resetTime - Math.floor(Date.now() / 1000);

  // Wait and retry
  await delay(waitTime * 1000);
  return retryRequest();
}
```

---

## Idempotency

### Idempotency-Key Header

For **mutation operations** (POST, PUT, PATCH, DELETE), include an idempotency key to prevent duplicate operations:

```http
Idempotency-Key: <uuid>
```

### Requirements

- **Required for:** All AI endpoints (strictly enforced)
- **Recommended for:** Task creation, updates, deletions
- **Format:** UUID v4
- **Uniqueness:** Must be unique per operation
- **Retention:** Keys are stored for 24 hours

### Idempotency Behavior

1. **First request:** Operation executes normally, response cached
2. **Duplicate request (same key):** Cached response returned immediately
3. **Response headers:**
   ```http
   X-Idempotent-Replayed: true  # Indicates cached response
   ```

### Example (TypeScript)

```typescript
import { v4 as uuidv4 } from 'uuid';

async function createTask(data: TaskCreate) {
  const idempotencyKey = uuidv4();

  const response = await fetch('/api/v1/tasks', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
    },
    body: JSON.stringify(data),
  });

  // Check if response was replayed from cache
  const wasReplayed = response.headers.get('X-Idempotent-Replayed') === 'true';

  return await response.json();
}
```

---

## API Endpoints

---

## Health

### Liveness Probe

Check if the service is running.

```http
GET /health/live
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Readiness Probe

Check if the service is ready to handle requests.

```http
GET /health/ready
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "checks": {
    "database": {
      "status": "ok"
    },
    "configuration": {
      "status": "ok"
    }
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "error",
  "checks": {
    "database": {
      "status": "error",
      "message": "Connection timeout"
    },
    "configuration": {
      "status": "ok"
    }
  }
}
```

---

## Authentication Endpoints

### Google OAuth Callback

Exchange Google ID token for backend JWT tokens.

```http
POST /api/v1/auth/google/callback
```

**Rate Limit:** 10 requests/minute per IP

**Request:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "rt_abc123def456...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "tier": "free",
    "created_at": "2026-01-15T10:30:00.000Z"
  }
}
```

**Errors:**
- `401 UNAUTHORIZED` - Invalid Google token
- `429 RATE_LIMIT_EXCEEDED` - Too many requests

---

### Refresh Tokens

Exchange refresh token for new access and refresh tokens.

```http
POST /api/v1/auth/refresh
```

**Rate Limit:** 10 requests/minute per IP

**Request:**
```json
{
  "refresh_token": "rt_abc123def456..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "rt_newtoken789...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors:**
- `401 INVALID_REFRESH_TOKEN` - Invalid or expired refresh token
- `429 RATE_LIMIT_EXCEEDED` - Too many requests

**Note:** Refresh tokens are single-use. The old token is revoked when a new one is issued.

---

### Logout

Revoke refresh token and end session.

```http
POST /api/v1/auth/logout
```

**Rate Limit:** 10 requests/minute per IP

**Request:**
```json
{
  "refresh_token": "rt_abc123def456..."
}
```

**Response:** `204 No Content`

**Note:** Idempotent. Always returns 204 even if token was already revoked.

---

### JWKS Endpoint

Get public keys for JWT verification.

```http
GET /api/v1/.well-known/jwks.json
```

**Response:**
```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "kid": "key-id-1",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

---

## Users

### Get Current User Profile

Get authenticated user's profile information.

```http
GET /api/v1/users/me
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid",
    "google_id": "google-user-id",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "timezone": "America/New_York",
    "tier": "free",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### Update Current User Profile

Update authenticated user's profile.

```http
PATCH /api/v1/users/me
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Request:**
```json
{
  "name": "Jane Doe",
  "timezone": "America/Los_Angeles"
}
```

**Validation:**
- `name`: 1-100 characters
- `timezone`: Valid IANA timezone (e.g., "America/New_York")

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid",
    "google_id": "google-user-id",
    "email": "user@example.com",
    "name": "Jane Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "timezone": "America/Los_Angeles",
    "tier": "free",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:20:00Z"
  }
}
```

**Errors:**
- `400 VALIDATION_ERROR` - Invalid timezone or name too long

---

## Tasks

### List Tasks

Get paginated list of tasks with optional filters.

```http
GET /api/v1/tasks
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Query Parameters:**
```
offset: int = 0                     # Pagination offset
limit: int = 25                     # Items per page (max 100)
completed: bool | null = null       # Filter by completion status
priority: "low" | "medium" | "high" | null = null
hidden: bool = false                # Include hidden tasks
due_before: datetime | null = null  # Tasks due before this date
due_after: datetime | null = null   # Tasks due after this date
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Complete project proposal",
      "description": "Draft and submit Q1 project proposal",
      "priority": "high",
      "due_date": "2026-02-15T17:00:00.000Z",
      "estimated_duration": 120,
      "focus_time_seconds": 3600,
      "completed": false,
      "completed_at": null,
      "completed_by": null,
      "hidden": false,
      "archived": false,
      "template_id": null,
      "subtask_count": 3,
      "subtask_completed_count": 1,
      "version": 1,
      "created_at": "2026-02-01T10:00:00.000Z",
      "updated_at": "2026-02-10T14:30:00.000Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 25,
    "total": 42,
    "has_more": true
  }
}
```

---

### Get Task by ID

Get detailed task information including subtasks and reminders.

```http
GET /api/v1/tasks/{task_id}
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Complete project proposal",
    "description": "Draft and submit Q1 project proposal",
    "priority": "high",
    "due_date": "2026-02-15T17:00:00.000Z",
    "estimated_duration": 120,
    "focus_time_seconds": 3600,
    "completed": false,
    "completed_at": null,
    "completed_by": null,
    "hidden": false,
    "archived": false,
    "template_id": null,
    "version": 1,
    "created_at": "2026-02-01T10:00:00.000Z",
    "updated_at": "2026-02-10T14:30:00.000Z",
    "subtasks": [
      {
        "id": "uuid",
        "title": "Research similar proposals",
        "completed": true,
        "completed_at": "2026-02-05T12:00:00.000Z",
        "order_index": 0,
        "source": "manual"
      },
      {
        "id": "uuid",
        "title": "Draft outline",
        "completed": false,
        "completed_at": null,
        "order_index": 1,
        "source": "ai"
      }
    ],
    "reminders": [
      {
        "id": "uuid",
        "type": "absolute",
        "offset_minutes": null,
        "scheduled_at": "2026-02-15T09:00:00.000Z",
        "method": "push",
        "fired": false
      }
    ]
  }
}
```

**Errors:**
- `404 NOT_FOUND` - Task not found

---

### Create Task

Create a new task with idempotency support.

```http
POST /api/v1/tasks
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user
**Idempotency:** Recommended

**Request:**
```json
{
  "title": "Write documentation",
  "description": "Create API documentation for frontend team",
  "priority": "medium",
  "due_date": "2026-02-20T17:00:00.000Z",
  "estimated_duration": 180
}
```

**Validation:**
- `title`: Required, 1-500 characters
- `description`: Optional, max 5000 characters
- `priority`: "low" | "medium" | "high"
- `due_date`: Optional, max 30 days from creation
- `estimated_duration`: Optional, minutes (positive integer)

**Response (201 Created):**
```json
{
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Write documentation",
    "description": "Create API documentation for frontend team",
    "priority": "medium",
    "due_date": "2026-02-20T17:00:00.000Z",
    "estimated_duration": 180,
    "focus_time_seconds": 0,
    "completed": false,
    "completed_at": null,
    "completed_by": null,
    "hidden": false,
    "archived": false,
    "template_id": null,
    "subtask_count": 0,
    "subtask_completed_count": 0,
    "version": 1,
    "created_at": "2026-02-11T10:00:00.000Z",
    "updated_at": "2026-02-11T10:00:00.000Z"
  }
}
```

**Errors:**
- `400 VALIDATION_ERROR` - Due date exceeds 30 days
- `409 LIMIT_EXCEEDED` - Task limit exceeded for tier (Free: 50, Pro: unlimited)

---

### Update Task

Update task with optimistic locking (version check).

```http
PUT /api/v1/tasks/{task_id}
PATCH /api/v1/tasks/{task_id}
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user
**Idempotency:** Recommended

**Request:**
```json
{
  "title": "Write comprehensive documentation",
  "priority": "high",
  "version": 1
}
```

**Validation:**
- `version`: Required for optimistic locking
- Other fields: Same as create task

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Write comprehensive documentation",
    "priority": "high",
    "version": 2,
    ...
  }
}
```

**Errors:**
- `404 NOT_FOUND` - Task not found
- `409 CONFLICT` - Version conflict (task was modified by another request)
- `409 ARCHIVED` - Cannot modify archived task

---

### Force Complete Task

Complete task and all incomplete subtasks, with achievement tracking.

```http
POST /api/v1/tasks/{task_id}/force-complete
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Request:**
```json
{
  "version": 1
}
```

**Response (200 OK):**
```json
{
  "data": {
    "task": {
      "id": "uuid",
      "completed": true,
      "completed_at": "2026-02-11T15:30:00.000Z",
      "completed_by": "manual",
      "version": 2,
      ...
    },
    "unlocked_achievements": [
      {
        "id": "uuid",
        "name": "First Steps",
        "perk_type": "storage",
        "perk_value": 10
      }
    ],
    "streak": 5
  }
}
```

**Errors:**
- `404 NOT_FOUND` - Task not found
- `409 CONFLICT` - Version conflict
- `409 ARCHIVED` - Cannot complete archived task

---

### Delete Task

Hard delete task and create recovery tombstone.

```http
DELETE /api/v1/tasks/{task_id}
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Response (200 OK):**
```json
{
  "data": {
    "tombstone_id": "uuid",
    "recoverable_until": "2026-02-18T10:00:00.000Z"
  }
}
```

**Errors:**
- `404 NOT_FOUND` - Task not found

**Note:** Tasks are recoverable for 7 days after deletion via the Recovery API.

---

## AI

### AI Chat

Send message to AI assistant with context awareness.

```http
POST /api/v1/ai/chat
```

**Auth:** Required
**Rate Limit:** 20 requests/minute per user
**Idempotency:** **Required**
**Cost:** 1 credit per message

**Request:**
```json
{
  "message": "What tasks should I focus on today?",
  "context": {
    "include_tasks": true,
    "task_limit": 10
  }
}
```

**Headers:**
```http
Authorization: Bearer <access_token>
Idempotency-Key: <uuid>
X-Task-Id: <uuid>  # Optional: for task-specific context
```

**Response (200 OK):**
```json
{
  "data": {
    "response": "Based on your tasks, I recommend focusing on the high-priority items first...",
    "suggested_actions": [
      {
        "type": "complete_task",
        "task_id": "uuid",
        "description": "Mark 'Research similar proposals' as complete",
        "data": {}
      }
    ],
    "credits_used": 1,
    "credits_remaining": 14,
    "ai_request_warning": false
  }
}
```

**Errors:**
- `400 VALIDATION_ERROR` - Missing Idempotency-Key header
- `402 INSUFFICIENT_CREDITS` - No credits available
- `429 AI_TASK_LIMIT_REACHED` - Too many AI requests per session
- `503 AI_SERVICE_UNAVAILABLE` - AI service temporarily unavailable

---

### AI Chat (Streaming)

Stream AI chat response via Server-Sent Events.

```http
POST /api/v1/ai/chat/stream
```

**Auth:** Required
**Rate Limit:** 20 requests/minute per user
**Idempotency:** **Required**
**Cost:** 1 credit per message

**Request:** Same as `/ai/chat`

**Response (200 OK):**
```
Content-Type: text/event-stream

data: {"text": "Based on your tasks..."}
data: {"text": " I recommend focusing..."}
data: [DONE]
```

---

### Generate Subtasks (AI)

AI generates subtask suggestions for a task.

```http
POST /api/v1/ai/generate-subtasks
```

**Auth:** Required
**Rate Limit:** 20 requests/minute per user
**Idempotency:** **Required**
**Cost:** 1 credit per generation

**Request:**
```json
{
  "task_id": "uuid"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "suggested_subtasks": [
      { "title": "Research market trends" },
      { "title": "Draft project timeline" },
      { "title": "Assign team resources" }
    ],
    "credits_used": 1,
    "credits_remaining": 9
  }
}
```

**Tier Limits:**
- **Free tier:** Max 4 subtasks suggested
- **Pro tier:** Max 10 subtasks suggested

**Errors:**
- `400 VALIDATION_ERROR` - Missing Idempotency-Key
- `402 INSUFFICIENT_CREDITS` - No credits available
- `404 TASK_NOT_FOUND` - Task not found
- `503 AI_SERVICE_UNAVAILABLE` - AI service unavailable

---

### Transcribe Voice (Pro Only)

Transcribe voice audio using Deepgram NOVA2.

```http
POST /api/v1/ai/transcribe
```

**Auth:** Required
**Rate Limit:** 20 requests/minute per user
**Idempotency:** **Required**
**Tier:** Pro subscription required
**Cost:** 5 credits per minute (rounded up)

**Request:**
```json
{
  "audio_url": "https://storage.example.com/audio/recording.webm",
  "duration_seconds": 45
}
```

**Validation:**
- `duration_seconds`: Max 300 seconds (5 minutes)

**Response (200 OK):**
```json
{
  "data": {
    "transcription": "This is the transcribed text from your voice recording.",
    "language": "en",
    "confidence": 0.95,
    "credits_used": 5,
    "credits_remaining": 45
  }
}
```

**Credit Calculation:**
- 45 seconds → 1 minute → 5 credits
- 90 seconds → 2 minutes → 10 credits
- 300 seconds → 5 minutes → 25 credits

**Errors:**
- `400 AUDIO_DURATION_EXCEEDED` - Audio exceeds 300 seconds
- `402 INSUFFICIENT_CREDITS` - Not enough credits
- `403 PRO_TIER_REQUIRED` - Pro subscription required
- `503 TRANSCRIPTION_SERVICE_UNAVAILABLE` - Service unavailable

---

### Confirm AI Action

Execute AI-suggested action after user confirmation.

```http
POST /api/v1/ai/confirm-action
```

**Auth:** Required
**Rate Limit:** 20 requests/minute per user
**Idempotency:** **Required**

**Request:**
```json
{
  "action_type": "create_subtasks",
  "action_data": {
    "task_id": "uuid",
    "subtasks": [
      { "title": "Research market trends" },
      { "title": "Draft timeline" }
    ]
  }
}
```

**Supported Actions:**
- `complete_task` - Mark task as complete
- `create_subtasks` - Create subtasks for a task
- `update_task` - Update task fields

**Response (200 OK):**
```json
{
  "data": {
    "subtasks": [
      { "id": "uuid", "title": "Research market trends" },
      { "id": "uuid", "title": "Draft timeline" }
    ]
  }
}
```

---

### Get AI Credits

Get credit balance breakdown.

```http
GET /api/v1/ai/credits
```

**Auth:** Required

**Response (200 OK):**
```json
{
  "data": {
    "balance": {
      "daily_free": 8,
      "subscription": 45,
      "purchased": 20,
      "total": 73
    },
    "daily_reset_at": "2026-01-20T00:00:00.000Z",
    "tier": "pro"
  }
}
```

---

## Credits

### Get Credit Balance

Get detailed credit balance breakdown.

```http
GET /api/v1/credits/balance
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Response (200 OK):**
```json
{
  "data": {
    "daily": 10,
    "subscription": 50,
    "purchased": 25,
    "kickstart": 5,
    "total": 90
  }
}
```

**Credit Types:**
- **Daily:** Free daily credits (expire at UTC midnight)
- **Subscription:** Pro tier monthly credits (carry over up to 50)
- **Purchased:** One-time purchased credits (never expire)
- **Kickstart:** New user bonus credits (one-time)

---

### Get Credit History

Get paginated credit transaction history.

```http
GET /api/v1/credits/history
```

**Auth:** Required
**Rate Limit:** 100 requests/minute per user

**Query Parameters:**
```
offset: int = 0
limit: int = 50  # Max 100
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "type": "deduct",
      "category": "ai",
      "amount": 1,
      "balance_after": 89,
      "description": "AI chat message",
      "created_at": "2026-02-11T10:30:00.000Z"
    },
    {
      "id": "uuid",
      "user_id": "uuid",
      "type": "grant",
      "category": "subscription",
      "amount": 50,
      "balance_after": 90,
      "description": "Monthly subscription credits",
      "created_at": "2026-02-01T00:00:00.000Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total": 142,
    "has_more": true
  }
}
```

---

## Additional Endpoints

### Subtasks

- `GET /api/v1/subtasks` - List all subtasks
- `POST /api/v1/tasks/{task_id}/subtasks` - Create subtask
- `PATCH /api/v1/subtasks/{subtask_id}` - Update subtask
- `DELETE /api/v1/subtasks/{subtask_id}` - Delete subtask

### Templates

- `GET /api/v1/templates` - List task templates
- `POST /api/v1/templates` - Create template
- `POST /api/v1/templates/{template_id}/instantiate` - Create task from template

### Notes

- `GET /api/v1/tasks/{task_id}/notes` - List task notes
- `POST /api/v1/tasks/{task_id}/notes` - Create note
- `PATCH /api/v1/notes/{note_id}` - Update note
- `DELETE /api/v1/notes/{note_id}` - Delete note

### Reminders

- `GET /api/v1/reminders` - List reminders
- `POST /api/v1/tasks/{task_id}/reminders` - Create reminder
- `DELETE /api/v1/reminders/{reminder_id}` - Delete reminder

### Achievements

- `GET /api/v1/achievements` - Get user's achievement data (stats, unlocked, progress, limits)
- `GET /api/v1/achievements/me` - Alias for `/achievements` (same response)
- `GET /api/v1/achievements/stats` - Get only user stats (lifetime tasks, streak, etc.)
- `GET /api/v1/achievements/limits` - Get only effective limits based on tier and perks

### Focus Mode

- `POST /api/v1/focus/start` - Start focus session
- `POST /api/v1/focus/stop` - Stop focus session
- `GET /api/v1/focus/active` - Get active focus session

### Subscriptions

- `GET /api/v1/subscription` - Get subscription status
- `POST /api/v1/subscription/upgrade` - Upgrade to Pro

### Recovery

- `GET /api/v1/recovery/tombstones` - List recoverable items
- `POST /api/v1/recovery/tombstones/{tombstone_id}/recover` - Recover deleted item

### Notifications

- `GET /api/v1/notifications` - List notifications
- `PATCH /api/v1/notifications/{notification_id}/read` - Mark as read

### Activity Logs

- `GET /api/v1/activity` - Get activity log

---

## TypeScript Integration Examples

### API Client Setup

```typescript
// api-client.ts
import { v4 as uuidv4 } from 'uuid';

interface ApiClientConfig {
  baseUrl: string;
  accessToken: string;
  refreshToken: string;
  onTokenRefresh: (tokens: { accessToken: string; refreshToken: string }) => void;
}

class ApiClient {
  private config: ApiClientConfig;

  constructor(config: ApiClientConfig) {
    this.config = config;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requiresIdempotency = false
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.config.accessToken}`,
      ...options.headers,
    };

    // Add idempotency key for mutations
    if (requiresIdempotency && !headers['Idempotency-Key']) {
      headers['Idempotency-Key'] = uuidv4();
    }

    let response = await fetch(`${this.config.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle token expiration
    if (response.status === 401) {
      const error = await response.json();
      if (error.error.code === 'TOKEN_EXPIRED') {
        await this.refreshTokens();
        // Retry with new token
        headers['Authorization'] = `Bearer ${this.config.accessToken}`;
        response = await fetch(`${this.config.baseUrl}${endpoint}`, {
          ...options,
          headers,
        });
      }
    }

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.error);
    }

    return response.json();
  }

  private async refreshTokens(): Promise<void> {
    const response = await fetch(`${this.config.baseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.config.refreshToken }),
    });

    if (!response.ok) {
      // Refresh failed - redirect to login
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    const data = await response.json();
    this.config.accessToken = data.access_token;
    this.config.refreshToken = data.refresh_token;
    this.config.onTokenRefresh({
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
    });
  }
}

class ApiError extends Error {
  code: string;
  details?: any;

  constructor(error: { code: string; message: string; details?: any }) {
    super(error.message);
    this.code = error.code;
    this.details = error.details;
  }
}
```

### Task Management Example

```typescript
// tasks.ts
import { ApiClient } from './api-client';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  completed: boolean;
  version: number;
}

interface TaskCreate {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  estimated_duration?: number;
}

export class TasksService {
  constructor(private client: ApiClient) {}

  async listTasks(filters?: {
    completed?: boolean;
    priority?: 'low' | 'medium' | 'high';
    offset?: number;
    limit?: number;
  }) {
    const params = new URLSearchParams();
    if (filters?.completed !== undefined) params.set('completed', String(filters.completed));
    if (filters?.priority) params.set('priority', filters.priority);
    if (filters?.offset) params.set('offset', String(filters.offset));
    if (filters?.limit) params.set('limit', String(filters.limit));

    return this.client.request<{ data: Task[]; pagination: any }>(
      `/api/v1/tasks?${params}`,
      { method: 'GET' }
    );
  }

  async createTask(data: TaskCreate) {
    return this.client.request<{ data: Task }>(
      '/api/v1/tasks',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      true // Requires idempotency
    );
  }

  async updateTask(taskId: string, data: Partial<TaskCreate> & { version: number }) {
    return this.client.request<{ data: Task }>(
      `/api/v1/tasks/${taskId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      },
      true // Requires idempotency
    );
  }

  async forceComplete(taskId: string, version: number) {
    return this.client.request<{ data: any }>(
      `/api/v1/tasks/${taskId}/force-complete`,
      {
        method: 'POST',
        body: JSON.stringify({ version }),
      }
    );
  }
}
```

### AI Service Example

```typescript
// ai.ts
import { ApiClient } from './api-client';

export class AIService {
  constructor(private client: ApiClient) {}

  async chat(message: string, context?: { include_tasks?: boolean; task_limit?: number }) {
    return this.client.request<{
      data: {
        response: string;
        suggested_actions: any[];
        credits_used: number;
        credits_remaining: number;
      };
    }>(
      '/api/v1/ai/chat',
      {
        method: 'POST',
        body: JSON.stringify({ message, context }),
      },
      true // Idempotency required
    );
  }

  async generateSubtasks(taskId: string) {
    return this.client.request<{
      data: {
        suggested_subtasks: Array<{ title: string }>;
        credits_used: number;
        credits_remaining: number;
      };
    }>(
      '/api/v1/ai/generate-subtasks',
      {
        method: 'POST',
        body: JSON.stringify({ task_id: taskId }),
      },
      true // Idempotency required
    );
  }

  async transcribeVoice(audioUrl: string, durationSeconds: number) {
    return this.client.request<{
      data: {
        transcription: string;
        language: string;
        confidence: number;
        credits_used: number;
        credits_remaining: number;
      };
    }>(
      '/api/v1/ai/transcribe',
      {
        method: 'POST',
        body: JSON.stringify({
          audio_url: audioUrl,
          duration_seconds: durationSeconds,
        }),
      },
      true // Idempotency required
    );
  }
}
```

---

## Development & Testing

### OpenAPI Documentation

Interactive API documentation is available in development mode:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Testing with cURL

```bash
# Login with Google
curl -X POST http://localhost:8000/api/v1/auth/google/callback \
  -H "Content-Type: application/json" \
  -d '{"id_token": "google-id-token"}'

# List tasks
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer access-token"

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer access-token" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "title": "New task",
    "priority": "high",
    "due_date": "2026-02-20T17:00:00.000Z"
  }'
```

---

## Best Practices

### 1. Token Management
- Store access/refresh tokens securely (HttpOnly cookies or secure storage)
- Refresh tokens proactively before expiry (e.g., when < 5 min remaining)
- Handle token refresh transparently in API client
- Redirect to login on refresh failure

### 2. Error Handling
- Always check `response.ok` before parsing JSON
- Handle specific error codes (TOKEN_EXPIRED, INSUFFICIENT_CREDITS, etc.)
- Show user-friendly error messages
- Log errors with request IDs for debugging

### 3. Rate Limiting
- Implement exponential backoff for rate limit errors
- Show rate limit warnings to users
- Use rate limit headers to track remaining quota

### 4. Idempotency
- Always use idempotency keys for mutations
- Generate unique UUID v4 for each operation
- Store and reuse keys for retries (don't generate new keys on retry)

### 5. Optimistic Locking
- Always include `version` field when updating tasks
- Handle CONFLICT errors by refetching latest data
- Show version conflict warnings to users

### 6. Pagination
- Use consistent offset/limit parameters
- Check `has_more` field to determine if more data exists
- Implement infinite scroll or "Load More" buttons

---

## Support

For questions or issues with the API:
- **GitHub Issues:** https://github.com/your-org/perpetua-flow/issues
- **Email:** support@perpetua.com
- **Documentation:** https://docs.perpetua.com

---

**Last Updated:** 2026-02-11
**API Version:** 1.0.0
