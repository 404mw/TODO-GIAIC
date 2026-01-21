# API Specification - Perpetua Flow Backend

**Version**: 1.0.0
**Base URL**: `/api/v1`
**Protocol**: REST over HTTPS
**Format**: JSON
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [General Conventions](#general-conventions)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Endpoints](#user-endpoints)
4. [Task Endpoints](#task-endpoints)
5. [Subtask Endpoints](#subtask-endpoints)
6. [Note Endpoints](#note-endpoints)
7. [Reminder Endpoints](#reminder-endpoints)
8. [AI Endpoints](#ai-endpoints)
9. [Achievement Endpoints](#achievement-endpoints)
10. [Subscription Endpoints](#subscription-endpoints)
11. [Notification Endpoints](#notification-endpoints)
12. [WebSocket Endpoints](#websocket-endpoints)
13. [Error Handling](#error-handling)
14. [Rate Limiting](#rate-limiting)

---

## General Conventions

### Request Headers

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access_token>
Idempotency-Key: <uuid>  # Required for POST/PATCH
X-Request-ID: <uuid>     # Optional, for tracing
```

### Response Headers

```
Content-Type: application/json
X-Request-ID: <uuid>
X-RateLimit-Limit: <number>
X-RateLimit-Remaining: <number>
X-RateLimit-Reset: <unix_timestamp>
```

### Timestamps

All timestamps are ISO 8601 format with UTC timezone:
```
2026-01-19T10:30:00.000Z
```

### Pagination

Offset-based pagination with default 25, max 100 items:
```
GET /api/v1/tasks?offset=0&limit=25

Response:
{
  "data": [...],
  "pagination": {
    "offset": 0,
    "limit": 25,
    "total": 150,
    "has_more": true
  }
}
```

### PATCH Semantics

- Omitted fields remain unchanged
- `null` explicitly clears a field (where allowed)
- `version` field required for optimistic locking

---

## Authentication Endpoints

### 1. Exchange Google ID Token for Tokens

**Endpoint**: `POST /api/v1/auth/google/callback`

**Description**: Verify Google ID token (from frontend BetterAuth) and issue backend JWT tokens.

**Request Body**:
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "Jane Doe",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "tier": "free",
    "created_at": "2026-01-19T10:00:00.000Z"
  }
}
```

**Errors**:
- `400`: Invalid authorization code
- `401`: OAuth authentication failed

---

### 2. Refresh Access Token

**Endpoint**: `POST /api/v1/auth/refresh`

**Request Body**:
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "bmV3IHJlZnJlc2ggdG9rZW4...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors**:
- `401`: Invalid or expired refresh token

**Note**: Refresh tokens rotate on use (7-day expiry).

---

### 3. Logout

**Endpoint**: `POST /api/v1/auth/logout`

**Request Body**:
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response** (204 No Content)

---

## User Endpoints

### 1. Get Current User Profile

**Endpoint**: `GET /api/v1/users/me`

**Description**: Get the authenticated user's profile information.

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "Jane Doe",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "tier": "pro",
    "timezone": "America/New_York",
    "created_at": "2026-01-19T10:00:00.000Z",
    "updated_at": "2026-01-19T14:30:00.000Z"
  }
}
```

---

### 2. Update Current User Profile

**Endpoint**: `PATCH /api/v1/users/me`

**Description**: Update the authenticated user's profile (FR-070).

**Headers**:
```
Idempotency-Key: <uuid>
```

**Request Body**:
```json
{
  "name": "Jane Smith",
  "timezone": "Europe/London"
}
```

**Updatable Fields**:
- `name` (string, max 100 chars)
- `timezone` (string, valid IANA timezone)

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "Jane Smith",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "tier": "pro",
    "timezone": "Europe/London",
    "created_at": "2026-01-19T10:00:00.000Z",
    "updated_at": "2026-01-19T15:00:00.000Z"
  }
}
```

**Errors**:
- `400`: Invalid timezone or name too long

---

## Task Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/v1/tasks`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | 0 | Pagination offset |
| `limit` | integer | 25 | Items per page (max 100) |
| `completed` | boolean | - | Filter by completion status |
| `priority` | string | - | Filter by priority (low, medium, high) |
| `hidden` | boolean | false | Include hidden tasks |
| `due_before` | ISO timestamp | - | Tasks due before date |
| `due_after` | ISO timestamp | - | Tasks due after date |

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete quarterly report",
      "description": "Q4 financial analysis",
      "priority": "high",
      "due_date": "2026-01-25T17:00:00.000Z",
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
      "version": 2,
      "created_at": "2026-01-19T10:00:00.000Z",
      "updated_at": "2026-01-19T14:30:00.000Z"
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

### 2. Get Task by ID

**Endpoint**: `GET /api/v1/tasks/:id`

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete quarterly report",
    "description": "Q4 financial analysis",
    "priority": "high",
    "due_date": "2026-01-25T17:00:00.000Z",
    "estimated_duration": 120,
    "focus_time_seconds": 3600,
    "completed": false,
    "completed_at": null,
    "completed_by": null,
    "hidden": false,
    "archived": false,
    "template_id": null,
    "version": 2,
    "created_at": "2026-01-19T10:00:00.000Z",
    "updated_at": "2026-01-19T14:30:00.000Z",
    "subtasks": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "Gather data",
        "completed": true,
        "completed_at": "2026-01-19T12:00:00.000Z",
        "order_index": 0,
        "source": "user"
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440002",
        "title": "Create visualizations",
        "completed": false,
        "completed_at": null,
        "order_index": 1,
        "source": "ai"
      }
    ],
    "reminders": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440001",
        "type": "before",
        "offset_minutes": -60,
        "scheduled_at": "2026-01-25T16:00:00.000Z",
        "method": "push",
        "fired": false
      }
    ]
  }
}
```

**Errors**:
- `404`: Task not found

---

### 3. Create Task

**Endpoint**: `POST /api/v1/tasks`

**Headers**:
```
Idempotency-Key: <uuid>
```

**Request Body**:
```json
{
  "title": "Complete quarterly report",
  "description": "Q4 financial analysis",
  "priority": "high",
  "due_date": "2026-01-25T17:00:00.000Z",
  "estimated_duration": 120
}
```

**Required Fields**: `title`

**Response** (201 Created):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete quarterly report",
    "description": "Q4 financial analysis",
    "priority": "high",
    "due_date": "2026-01-25T17:00:00.000Z",
    "estimated_duration": 120,
    "focus_time_seconds": 0,
    "completed": false,
    "completed_at": null,
    "completed_by": null,
    "hidden": false,
    "archived": false,
    "template_id": null,
    "version": 1,
    "created_at": "2026-01-19T10:00:00.000Z",
    "updated_at": "2026-01-19T10:00:00.000Z"
  }
}
```

**Errors**:
- `400`: Validation error
- `409`: Task limit exceeded

---

### 4. Update Task

**Endpoint**: `PATCH /api/v1/tasks/:id`

**Headers**:
```
Idempotency-Key: <uuid>
```

**Request Body**:
```json
{
  "title": "Complete Q4 report",
  "completed": true,
  "version": 2
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete Q4 report",
    "completed": true,
    "completed_at": "2026-01-19T15:00:00.000Z",
    "completed_by": "manual",
    "version": 3,
    ...
  }
}
```

**Special Behaviors**:
- Setting `completed: true` → sets `completed_at` and `completed_by: manual`
- All subtasks completed → auto-completes task with `completed_by: auto`

**Errors**:
- `400`: Validation error
- `404`: Task not found
- `409`: Version conflict (stale update) or archived task

---

### 5. Force Complete Task

**Endpoint**: `POST /api/v1/tasks/:id/force-complete`

**Description**: Complete task and all incomplete subtasks.

**Request Body**:
```json
{
  "version": 2
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "completed": true,
    "completed_at": "2026-01-19T15:00:00.000Z",
    "completed_by": "force",
    "version": 3,
    ...
  }
}
```

---

### 6. Delete Task

**Endpoint**: `DELETE /api/v1/tasks/:id`

**Response** (200 OK):
```json
{
  "data": {
    "tombstone_id": "880e8400-e29b-41d4-a716-446655440001",
    "recoverable_until": "2026-01-26T15:00:00.000Z"
  }
}
```

**Note**: Creates tombstone for recovery. Cascades to subtasks and reminders.

---

### 7. Recover Deleted Task

**Endpoint**: `POST /api/v1/tasks/recover/:tombstone_id`

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Recovered task",
    ...
  }
}
```

**Errors**:
- `404`: Tombstone not found or expired
- `409`: Original task ID collision

---

## Subtask Endpoints

### 1. Create Subtask

**Endpoint**: `POST /api/v1/tasks/:task_id/subtasks`

**Request Body**:
```json
{
  "title": "Research competitors"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Research competitors",
    "completed": false,
    "completed_at": null,
    "order_index": 2,
    "source": "user",
    "created_at": "2026-01-19T15:00:00.000Z",
    "updated_at": "2026-01-19T15:00:00.000Z"
  }
}
```

**Errors**:
- `404`: Parent task not found
- `409`: Subtask limit exceeded (4 free / 10 pro)

---

### 2. Update Subtask

**Endpoint**: `PATCH /api/v1/subtasks/:id`

**Request Body**:
```json
{
  "completed": true
}
```

**Response** (200 OK): Updated subtask object

**Note**: May trigger parent task auto-completion if all subtasks now complete.

---

### 3. Reorder Subtasks

**Endpoint**: `PUT /api/v1/tasks/:task_id/subtasks/reorder`

**Request Body**:
```json
{
  "subtask_ids": [
    "660e8400-e29b-41d4-a716-446655440002",
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440003"
  ]
}
```

**Response** (200 OK):
```json
{
  "data": [
    { "id": "...", "order_index": 0 },
    { "id": "...", "order_index": 1 },
    { "id": "...", "order_index": 2 }
  ]
}
```

---

### 4. Delete Subtask

**Endpoint**: `DELETE /api/v1/subtasks/:id`

**Response** (204 No Content)

---

## Note Endpoints

### 1. List Notes

**Endpoint**: `GET /api/v1/notes`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `archived` | boolean | false | Include archived notes |
| `offset` | integer | 0 | Pagination offset |
| `limit` | integer | 25 | Items per page |

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440001",
      "content": "Remember to call supplier about delivery",
      "archived": false,
      "voice_url": null,
      "voice_duration_seconds": null,
      "transcription_status": null,
      "created_at": "2026-01-19T09:00:00.000Z",
      "updated_at": "2026-01-19T09:00:00.000Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 2. Create Note

**Endpoint**: `POST /api/v1/notes`

**Request Body** (text note):
```json
{
  "content": "Follow up with client on proposal"
}
```

**Request Body** (voice note - Pro only):
```json
{
  "content": "Transcribed content here...",
  "voice_url": "https://storage.example.com/voice/abc123.webm",
  "voice_duration_seconds": 45
}
```

**Response** (201 Created): Note object

**Errors**:
- `400`: Content exceeds 2000 chars
- `403`: Voice notes require Pro tier
- `409`: Note limit exceeded

---

### 3. Convert Note to Task

**Endpoint**: `POST /api/v1/notes/:id/convert`

**Description**: Uses AI to suggest task details. Costs 1 AI credit.

**Response** (200 OK):
```json
{
  "data": {
    "suggested_task": {
      "title": "Call supplier about delivery",
      "description": "Follow up on delayed shipment",
      "priority": "medium",
      "due_date": null
    },
    "credits_remaining": 14
  }
}
```

**Note**: Returns suggestion only. User must confirm to create task.

---

## Reminder Endpoints

### 1. Create Reminder

**Endpoint**: `POST /api/v1/tasks/:task_id/reminders`

**Request Body**:
```json
{
  "type": "before",
  "offset_minutes": 60,
  "method": "push"
}
```

**Reminder Types**:
- `before`: Minutes before due date (positive offset)
- `after`: Minutes after due date (positive offset)
- `absolute`: Specific timestamp (use `scheduled_at` instead of `offset_minutes`)

**Response** (201 Created): Reminder object

**Errors**:
- `400`: Task has no due date (for relative reminders)
- `409`: Reminder limit exceeded (5 per task)

---

### 2. Update Reminder

**Endpoint**: `PATCH /api/v1/reminders/:id`

**Request Body**:
```json
{
  "offset_minutes": 30
}
```

**Response** (200 OK): Updated reminder

---

### 3. Delete Reminder

**Endpoint**: `DELETE /api/v1/reminders/:id`

**Response** (204 No Content)

---

## AI Endpoints

### 1. AI Chat

**Endpoint**: `POST /api/v1/ai/chat`

**Description**: Send message to AI assistant. Costs 1 credit per message.

**Request Body**:
```json
{
  "message": "What tasks should I focus on today?",
  "context": {
    "include_tasks": true,
    "task_limit": 10
  }
}
```

**Response** (200 OK):
```json
{
  "data": {
    "response": "Based on your tasks, I recommend focusing on...",
    "suggested_actions": [
      {
        "type": "complete_task",
        "task_id": "550e8400-...",
        "description": "Complete the quarterly report"
      }
    ],
    "credits_used": 1,
    "credits_remaining": 13
  }
}
```

**Errors**:
- `402`: Insufficient credits
- `429`: AI rate limit exceeded (20 req/min)
- `503`: AI service unavailable

---

### 2. Generate Subtasks

**Endpoint**: `POST /api/v1/ai/generate-subtasks`

**Description**: AI generates subtasks for a task. Costs 1 credit (flat rate).

**Request Body**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "suggested_subtasks": [
      { "title": "Gather Q4 financial data" },
      { "title": "Create revenue charts" },
      { "title": "Write executive summary" },
      { "title": "Review with finance team" }
    ],
    "credits_used": 1,
    "credits_remaining": 12
  }
}
```

**Note**: Returns suggestions only. Max subtasks based on user tier limit.

---

### 3. Confirm AI Action

**Endpoint**: `POST /api/v1/ai/confirm-action`

**Description**: Execute an AI-suggested action.

**Request Body**:
```json
{
  "action_type": "create_subtasks",
  "action_data": {
    "task_id": "550e8400-...",
    "subtasks": [
      { "title": "Gather Q4 financial data" },
      { "title": "Create revenue charts" }
    ]
  }
}
```

**Response** (200 OK): Created/modified resources

---

### 4. Transcribe Voice

**Endpoint**: `POST /api/v1/ai/transcribe`

**Description**: Transcribe voice recording. Costs 5 credits per minute. Pro only.

**Request Body**:
```json
{
  "audio_url": "https://storage.example.com/voice/abc123.webm",
  "duration_seconds": 45
}
```

**Response** (200 OK):
```json
{
  "data": {
    "transcription": "Remember to call the supplier about the delayed delivery...",
    "language": "en",
    "confidence": 0.95,
    "credits_used": 5,
    "credits_remaining": 95
  }
}
```

---

### 5. Get Credit Balance

**Endpoint**: `GET /api/v1/ai/credits`

**Response** (200 OK):
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

## Achievement Endpoints

### 1. Get User Achievements

**Endpoint**: `GET /api/v1/achievements`

**Response** (200 OK):
```json
{
  "data": {
    "stats": {
      "lifetime_tasks_completed": 127,
      "current_streak": 14,
      "longest_streak": 30,
      "focus_completions": 45,
      "notes_converted": 12
    },
    "unlocked": [
      {
        "id": "tasks_25",
        "name": "Task Master",
        "description": "Complete 25 tasks",
        "unlocked_at": "2026-01-15T10:00:00.000Z",
        "perk": { "type": "max_tasks", "value": 25 }
      },
      {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "unlocked_at": "2026-01-10T10:00:00.000Z",
        "perk": { "type": "daily_credits", "value": 2 }
      }
    ],
    "progress": [
      {
        "id": "tasks_100",
        "name": "Centurion",
        "current": 127,
        "threshold": 100,
        "unlocked": true
      },
      {
        "id": "streak_30",
        "name": "Monthly Master",
        "current": 14,
        "threshold": 30,
        "unlocked": false
      }
    ],
    "effective_limits": {
      "max_tasks": 140,
      "max_notes": 30,
      "daily_ai_credits": 12
    }
  }
}
```

---

## Subscription Endpoints

### 1. Get Subscription Status

**Endpoint**: `GET /api/v1/subscription`

**Response** (200 OK):
```json
{
  "data": {
    "tier": "pro",
    "status": "active",
    "current_period_end": "2026-02-19T00:00:00.000Z",
    "cancel_at_period_end": false,
    "features": {
      "max_subtasks": 10,
      "max_description_length": 2000,
      "voice_notes": true,
      "monthly_credits": 100
    }
  }
}
```

---

### 2. Create Checkout Session

**Endpoint**: `POST /api/v1/subscription/checkout`

**Response** (200 OK):
```json
{
  "data": {
    "checkout_url": "https://checkout.example.com/session/abc123",
    "session_id": "cs_abc123"
  }
}
```

---

### 3. Cancel Subscription

**Endpoint**: `POST /api/v1/subscription/cancel`

**Response** (200 OK):
```json
{
  "data": {
    "status": "cancelled",
    "access_until": "2026-02-19T00:00:00.000Z"
  }
}
```

---

### 4. Webhook Handler

**Endpoint**: `POST /api/v1/webhooks/checkout`

**Headers**:
```
Checkout-Signature: <signature>
```

**Note**: Verifies webhook signature. Processes subscription events.

---

## Notification Endpoints

### 1. List Notifications

**Endpoint**: `GET /api/v1/notifications`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `unread_only` | boolean | false | Filter unread only |
| `limit` | integer | 50 | Max notifications |

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "aa0e8400-...",
      "type": "reminder",
      "title": "Task Reminder",
      "body": "Complete quarterly report is due in 1 hour",
      "action_url": "/tasks/550e8400-...",
      "read": false,
      "created_at": "2026-01-19T16:00:00.000Z"
    }
  ],
  "unread_count": 5
}
```

---

### 2. Mark Notification Read

**Endpoint**: `PATCH /api/v1/notifications/:id/read`

**Response** (200 OK): Updated notification

---

### 3. Mark All Read

**Endpoint**: `POST /api/v1/notifications/read-all`

**Response** (200 OK):
```json
{
  "data": {
    "marked_count": 5
  }
}
```

---

## WebSocket Endpoints

### 1. Voice Transcription Stream

**Endpoint**: `WS /api/v1/ws/voice/transcribe`

**Description**: Real-time voice-to-text transcription via WebSocket relay to Deepgram NOVA2. Pro tier only.

**Authentication**: JWT token via query parameter or first message:
```
ws://api.perpetua.flow/api/v1/ws/voice/transcribe?token=<jwt>
```
Or first message:
```json
{ "type": "auth", "token": "<jwt>" }
```

**Client → Server Messages**:

1. **Audio chunk** (binary WebM/Opus format)

2. **End stream**:
```json
{ "type": "end_stream" }
```

**Server → Client Messages**:

1. **Connection established**:
```json
{
  "type": "connected",
  "session_id": "sess_abc123",
  "max_duration_seconds": 300
}
```

2. **Transcript (partial)**:
```json
{
  "type": "transcript",
  "text": "remember to call...",
  "is_final": false,
  "confidence": 0.85
}
```

3. **Transcript (final)**:
```json
{
  "type": "transcript",
  "text": "Remember to call the supplier about delivery",
  "is_final": true,
  "confidence": 0.95
}
```

4. **Session complete**:
```json
{
  "type": "complete",
  "full_transcript": "Remember to call the supplier about delivery",
  "duration_seconds": 45,
  "credits_used": 5,
  "credits_remaining": 95
}
```

5. **Error**:
```json
{
  "type": "error",
  "code": "INSUFFICIENT_CREDITS",
  "message": "Not enough AI credits for transcription"
}
```

**Error Codes**:
| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Invalid or missing JWT token |
| `TIER_REQUIRED` | Voice features require Pro tier |
| `INSUFFICIENT_CREDITS` | Not enough credits to start/continue |
| `MAX_DURATION_EXCEEDED` | 300 second limit reached |
| `TRANSCRIPTION_FAILED` | Deepgram service error |

**Constraints**:
- Pro tier required (closes with `TIER_REQUIRED` for free users)
- Credit check before stream starts
- Maximum 300 seconds (5 minutes) per session
- 5 credits charged per minute (rounded up)
- Session auto-closes at max duration with partial transcript

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "title",
        "message": "String must contain at least 1 character"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

### Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request body/params invalid |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 401 | `TOKEN_EXPIRED` | Access token expired (use refresh) |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 403 | `TIER_REQUIRED` | Feature requires Pro tier |
| 404 | `NOT_FOUND` | Resource not found |
| 402 | `INSUFFICIENT_CREDITS` | Not enough AI credits |
| 409 | `CONFLICT` | Version conflict or limit exceeded |
| 409 | `LIMIT_EXCEEDED` | Resource limit reached |
| 409 | `ARCHIVED` | Cannot modify archived resource |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 503 | `AI_SERVICE_UNAVAILABLE` | AI provider error |

---

## Rate Limiting

### Limits by Endpoint Category

| Category | Limit | Window |
|----------|-------|--------|
| General API | 100 requests | 1 minute |
| AI Endpoints | 20 requests | 1 minute |
| Auth Endpoints | 10 requests | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1705674900
```

### 429 Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "retry_after": 45
  }
}
```

---

## Idempotency

All `POST` and `PATCH` requests require an `Idempotency-Key` header (UUID v4).

- Duplicate requests with same key return original response
- Keys are valid for 24 hours
- After 24 hours, same key creates new request

---

## Health Check Endpoints

### Liveness Probe

**Endpoint**: `GET /api/v1/health/live`

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

### Readiness Probe

**Endpoint**: `GET /api/v1/health/ready`

**Response** (200 OK):
```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "ai_service": "ok"
  }
}
```

---

## OpenAPI Specification

Full OpenAPI 3.1 specification available at:
- Development: `GET /api/v1/openapi.json`
- Documentation: `GET /api/v1/docs` (Swagger UI)
