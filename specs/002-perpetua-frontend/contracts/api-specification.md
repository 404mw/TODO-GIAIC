# API Specification - Perpetua Flow

**Version**: 1.0.0
**Base URL**: `/api` (relative, frontend and backend on same domain)
**Protocol**: REST over HTTP/HTTPS
**Format**: JSON
**Authentication**: Bearer token (out of scope for frontend-only phase)

---

## Table of Contents

1. [General Conventions](#general-conventions)
2. [Error Responses](#error-responses)
3. [Task Endpoints](#task-endpoints)
4. [Sub-task Endpoints](#sub-task-endpoints)
5. [Note Endpoints](#note-endpoints)
6. [User Profile Endpoints](#user-profile-endpoints)
7. [Achievement Endpoints](#achievement-endpoints)
8. [Workflow Endpoints](#workflow-endpoints)
9. [Activity Log Endpoints](#activity-log-endpoints)
10. [AI Endpoints (Future)](#ai-endpoints-future)

---

## General Conventions

### Request Headers
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>  # Future: when backend integrated
```

### Response Headers
```
Content-Type: application/json
X-Request-ID: <uuid>  # For tracing
```

### Timestamps
All timestamps are ISO 8601 format with UTC timezone:
```
2026-01-07T10:30:00.000Z
```

### Pagination (Future)
Not implemented in initial MSW phase. When backend supports large datasets:
```
GET /api/tasks?page=1&limit=50
Response: { data: [...], meta: { total: 150, page: 1, limit: 50 } }
```

### Filtering (Future)
Not implemented initially. Example syntax:
```
GET /api/tasks?priority=high&completed=false
```

---

## Error Responses

All errors return HTTP status codes with JSON body:

### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "title",
        "issue": "String must contain at least 1 character(s)"
      }
    ]
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "resourceId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 409 Conflict
```json
{
  "error": {
    "code": "LIMIT_EXCEEDED",
    "message": "Maximum 50 tasks per user",
    "limit": 50,
    "current": 50
  }
}
```

### 429 Too Many Requests (AI endpoints only, future)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "AI rate limit exceeded",
    "retryAfter": 900
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "requestId": "req_abc123"
  }
}
```

---

## Task Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/tasks`

**Query Parameters**:
- `includeHidden` (optional): `boolean` - Include hidden tasks (default: `false`)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Finish report",
      "description": "Q4 metrics analysis",
      "tags": ["work", "urgent"],
      "priority": "high",
      "estimatedDuration": 120,
      "reminders": [],
      "recurring": null,
      "hidden": false,
      "completed": false,
      "completedAt": null,
      "createdAt": "2026-01-07T10:00:00.000Z",
      "updatedAt": "2026-01-07T10:00:00.000Z",
      "parentTaskId": null
    }
  ]
}
```

**Errors**:
- `500`: Internal server error

---

### 2. Get Task by ID

**Endpoint**: `GET /api/tasks/:id`

**Path Parameters**:
- `id`: Task UUID

**Response** (200 OK):
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Finish report",
    "description": "Q4 metrics analysis",
    "tags": ["work", "urgent"],
    "priority": "high",
    "estimatedDuration": 120,
    "reminders": [],
    "recurring": null,
    "hidden": false,
    "completed": false,
    "completedAt": null,
    "createdAt": "2026-01-07T10:00:00.000Z",
    "updatedAt": "2026-01-07T10:00:00.000Z",
    "parentTaskId": null
  },
  "subtasks": [
    {
      "id": "sub_123",
      "title": "Gather data",
      "completed": false,
      "completedAt": null,
      "createdAt": "2026-01-07T10:05:00.000Z",
      "updatedAt": "2026-01-07T10:05:00.000Z",
      "parentTaskId": "123e4567-e89b-12d3-a456-426614174000"
    }
  ]
}
```

**Errors**:
- `404`: Task not found

---

### 3. Create Task

**Endpoint**: `POST /api/tasks`

**Request Body**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Finish report",
  "description": "Q4 metrics analysis",
  "tags": ["work", "urgent"],
  "priority": "high",
  "estimatedDuration": 120,
  "reminders": [],
  "recurring": null
}
```

**Required Fields**: `id`, `title`, `priority`

**Response** (201 Created):
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Finish report",
    "description": "Q4 metrics analysis",
    "tags": ["work", "urgent"],
    "priority": "high",
    "estimatedDuration": 120,
    "reminders": [],
    "recurring": null,
    "hidden": false,
    "completed": false,
    "completedAt": null,
    "createdAt": "2026-01-07T10:00:00.000Z",
    "updatedAt": "2026-01-07T10:00:00.000Z",
    "parentTaskId": null
  }
}
```

**Errors**:
- `400`: Validation error (missing required fields, invalid data)
- `409`: Limit exceeded (50 tasks per user)

---

### 4. Update Task

**Endpoint**: `PATCH /api/tasks/:id`

**Path Parameters**:
- `id`: Task UUID

**Request Body** (partial update):
```json
{
  "title": "Finish quarterly report",
  "completed": true
}
```

**Response** (200 OK):
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Finish quarterly report",
    "description": "Q4 metrics analysis",
    "tags": ["work", "urgent"],
    "priority": "high",
    "estimatedDuration": 120,
    "reminders": [],
    "recurring": null,
    "hidden": false,
    "completed": true,
    "completedAt": "2026-01-07T11:30:00.000Z",
    "createdAt": "2026-01-07T10:00:00.000Z",
    "updatedAt": "2026-01-07T11:30:00.000Z",
    "parentTaskId": null
  }
}
```

**Special Behavior**:
- Setting `completed: true` auto-sets `completedAt` to current timestamp
- Setting `completed: false` sets `completedAt: null`
- `updatedAt` always updated to current timestamp

**Errors**:
- `400`: Validation error
- `404`: Task not found

---

### 5. Delete Task (Soft Delete)

**Endpoint**: `DELETE /api/tasks/:id`

**Path Parameters**:
- `id`: Task UUID

**Response** (204 No Content)

**Errors**:
- `404`: Task not found

**Note**: Deletes task and all associated sub-tasks (cascade).

---

## Sub-task Endpoints

### 1. List Sub-tasks for Task

**Endpoint**: `GET /api/tasks/:taskId/subtasks`

**Path Parameters**:
- `taskId`: Parent task UUID

**Response** (200 OK):
```json
{
  "subtasks": [
    {
      "id": "sub_123",
      "title": "Gather data",
      "completed": false,
      "completedAt": null,
      "createdAt": "2026-01-07T10:05:00.000Z",
      "updatedAt": "2026-01-07T10:05:00.000Z",
      "parentTaskId": "123e4567-e89b-12d3-a456-426614174000"
    }
  ]
}
```

**Errors**:
- `404`: Parent task not found

---

### 2. Create Sub-task

**Endpoint**: `POST /api/tasks/:taskId/subtasks`

**Path Parameters**:
- `taskId`: Parent task UUID

**Request Body**:
```json
{
  "id": "sub_123",
  "title": "Gather data"
}
```

**Required Fields**: `id`, `title`

**Response** (201 Created):
```json
{
  "subtask": {
    "id": "sub_123",
    "title": "Gather data",
    "completed": false,
    "completedAt": null,
    "createdAt": "2026-01-07T10:05:00.000Z",
    "updatedAt": "2026-01-07T10:05:00.000Z",
    "parentTaskId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Errors**:
- `400`: Validation error
- `404`: Parent task not found
- `409`: Limit exceeded (10 sub-tasks per task)

---

### 3. Update Sub-task

**Endpoint**: `PATCH /api/subtasks/:id`

**Path Parameters**:
- `id`: Sub-task UUID

**Request Body**:
```json
{
  "completed": true
}
```

**Response** (200 OK):
```json
{
  "subtask": {
    "id": "sub_123",
    "title": "Gather data",
    "completed": true,
    "completedAt": "2026-01-07T11:00:00.000Z",
    "createdAt": "2026-01-07T10:05:00.000Z",
    "updatedAt": "2026-01-07T11:00:00.000Z",
    "parentTaskId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Special Behavior**:
- Triggers parent task progress recalculation
- Setting `completed: true` auto-sets `completedAt`

**Errors**:
- `400`: Validation error
- `404`: Sub-task not found

---

### 4. Delete Sub-task

**Endpoint**: `DELETE /api/subtasks/:id`

**Path Parameters**:
- `id`: Sub-task UUID

**Response** (204 No Content)

**Errors**:
- `404`: Sub-task not found

---

## Note Endpoints

### 1. List Notes

**Endpoint**: `GET /api/notes`

**Query Parameters**:
- `includeArchived` (optional): `boolean` - Include archived notes (default: `false`)

**Response** (200 OK):
```json
{
  "notes": [
    {
      "id": "note_123",
      "content": "Buy groceries tomorrow morning",
      "archived": false,
      "voiceMetadata": null,
      "createdAt": "2026-01-07T09:00:00.000Z",
      "updatedAt": "2026-01-07T09:00:00.000Z"
    }
  ]
}
```

---

### 2. Create Note

**Endpoint**: `POST /api/notes`

**Request Body**:
```json
{
  "id": "note_123",
  "content": "Buy groceries tomorrow morning",
  "voiceMetadata": {
    "duration": 5,
    "transcriptionService": "Web Speech API",
    "language": "en",
    "confidence": 0.95
  }
}
```

**Required Fields**: `id`, `content`

**Response** (201 Created):
```json
{
  "note": {
    "id": "note_123",
    "content": "Buy groceries tomorrow morning",
    "archived": false,
    "voiceMetadata": {
      "duration": 5,
      "transcriptionService": "Web Speech API",
      "language": "en",
      "confidence": 0.95
    },
    "createdAt": "2026-01-07T09:00:00.000Z",
    "updatedAt": "2026-01-07T09:00:00.000Z"
  }
}
```

**Errors**:
- `400`: Validation error (content exceeds 1000 chars, voice duration > 60s)

---

### 3. Update Note

**Endpoint**: `PATCH /api/notes/:id`

**Request Body**:
```json
{
  "content": "Buy groceries and milk tomorrow morning",
  "archived": true
}
```

**Response** (200 OK): Full note object

**Errors**:
- `400`: Validation error
- `404`: Note not found

---

### 4. Delete Note

**Endpoint**: `DELETE /api/notes/:id`

**Response** (204 No Content)

**Errors**:
- `404`: Note not found

---

## User Profile Endpoints

### 1. Get Current User Profile

**Endpoint**: `GET /api/user/profile`

**Response** (200 OK):
```json
{
  "user": {
    "id": "user_123",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "preferences": {
      "sidebarOpen": true,
      "themeTweaks": {
        "accentColor": "#3B82F6",
        "glassIntensity": 0.15,
        "animationSpeed": 1.0
      }
    },
    "firstLogin": false,
    "tutorialCompleted": true,
    "createdAt": "2026-01-01T00:00:00.000Z",
    "updatedAt": "2026-01-07T10:00:00.000Z"
  }
}
```

---

### 2. Update User Preferences

**Endpoint**: `PATCH /api/user/preferences`

**Request Body**:
```json
{
  "preferences": {
    "sidebarOpen": false,
    "themeTweaks": {
      "accentColor": "#10B981"
    }
  }
}
```

**Response** (200 OK): Full user profile object

**Errors**:
- `400`: Validation error (invalid hex color, out-of-range values)

---

### 3. Mark Tutorial Complete

**Endpoint**: `POST /api/user/tutorial-complete`

**Request Body**: (empty)

**Response** (200 OK):
```json
{
  "user": {
    "id": "user_123",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "preferences": { ... },
    "firstLogin": false,
    "tutorialCompleted": true,
    "createdAt": "2026-01-01T00:00:00.000Z",
    "updatedAt": "2026-01-07T10:30:00.000Z"
  }
}
```

**Special Behavior**:
- Sets `firstLogin: false` and `tutorialCompleted: true`
- Creates tutorial task "Master Perpetua" if not exists

---

## Achievement Endpoints

### 1. Get Current User Achievements

**Endpoint**: `GET /api/achievements`

**Response** (200 OK):
```json
{
  "achievement": {
    "id": "ach_123",
    "userId": "user_123",
    "highPrioritySlays": 15,
    "consistencyStreak": {
      "currentStreak": 7,
      "longestStreak": 14,
      "lastCompletionDate": "2026-01-07",
      "graceDayUsed": false
    },
    "completionRatio": 78.5,
    "milestones": [
      {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Completed tasks for 7 consecutive days",
        "unlockedAt": "2026-01-07T10:00:00.000Z"
      }
    ],
    "updatedAt": "2026-01-07T11:00:00.000Z"
  }
}
```

**Note**: Achievements are auto-calculated on task completion, not directly writable.

---

## Workflow Endpoints

### 1. List Workflows

**Endpoint**: `GET /api/workflows`

**Response** (200 OK):
```json
{
  "workflows": [
    {
      "id": "wf_123",
      "name": "Morning Routine",
      "description": "Daily morning tasks",
      "taskIds": ["task_1", "task_2", "task_3"],
      "createdAt": "2026-01-05T08:00:00.000Z",
      "updatedAt": "2026-01-07T09:00:00.000Z"
    }
  ]
}
```

---

### 2. Create Workflow

**Endpoint**: `POST /api/workflows`

**Request Body**:
```json
{
  "id": "wf_123",
  "name": "Morning Routine",
  "description": "Daily morning tasks",
  "taskIds": ["task_1", "task_2"]
}
```

**Required Fields**: `id`, `name`, `taskIds`

**Response** (201 Created): Full workflow object

**Errors**:
- `400`: Validation error (invalid task IDs)

---

### 3. Update Workflow

**Endpoint**: `PATCH /api/workflows/:id`

**Request Body**:
```json
{
  "taskIds": ["task_1", "task_3", "task_2"]
}
```

**Response** (200 OK): Full workflow object

**Errors**:
- `400`: Validation error
- `404`: Workflow not found

---

### 4. Delete Workflow

**Endpoint**: `DELETE /api/workflows/:id`

**Response** (204 No Content)

**Note**: Does not delete tasks, only the workflow container.

---

## Activity Log Endpoints

### 1. List Activity Log Events

**Endpoint**: `GET /api/activity`

**Query Parameters**:
- `limit` (optional): Max events to return (default: 100, max: 100)

**Response** (200 OK):
```json
{
  "events": [
    {
      "id": "evt_123",
      "taskId": "task_123",
      "eventType": "task_completed",
      "actor": "user",
      "timestamp": "2026-01-07T11:00:00.000Z",
      "metadata": {
        "taskTitle": "Finish report",
        "completedSubtasks": 3
      }
    }
  ]
}
```

**Note**: Events are **immutable** and **append-only**. No POST/PATCH/DELETE endpoints.

**Rolling Window**: Last 100 events per user automatically maintained by backend.

---

## AI Endpoints (Future)

**Status**: Disabled until backend integration. All endpoints return `503 Service Unavailable` in MSW.

### 1. Generate Sub-tasks (Magic Sub-tasks)

**Endpoint**: `POST /api/ai/generate-subtasks`

**Request Body**:
```json
{
  "taskId": "task_123",
  "taskContext": {
    "title": "Plan company retreat",
    "description": "3-day offsite for 50 people in mountain location"
  }
}
```

**Response** (200 OK, streaming):
```
Content-Type: text/event-stream

data: {"subtask": {"title": "Research mountain venues"}}

data: {"subtask": {"title": "Create budget breakdown"}}

data: {"subtask": {"title": "Survey team for dates"}}

data: [DONE]
```

**Errors**:
- `429`: Rate limit exceeded (10 requests/min, 1000 requests/day)
- `503`: AI service unavailable

---

### 2. Parse Note to Task (Convert Note)

**Endpoint**: `POST /api/ai/parse-note`

**Request Body**:
```json
{
  "noteId": "note_123",
  "noteContent": "Finish project proposal by Friday, high priority"
}
```

**Response** (200 OK):
```json
{
  "parsedTask": {
    "title": "Finish project proposal",
    "description": "Finish project proposal by Friday, high priority",
    "priority": "high",
    "tags": ["project"],
    "reminders": [
      {
        "time": "2026-01-10T09:00:00.000Z"
      }
    ]
  }
}
```

**Note**: User must review and confirm before task creation (FR-021).

**Errors**:
- `400`: Note content too short (< 5 words)
- `429`: Rate limit exceeded

---

## Rate Limits (AI Endpoints Only, Future)

**Limits** (configurable via `.env`):
- Magic Sub-tasks: 10 requests/minute, 1000 requests/day
- Parse Note: 20 requests/minute, 2000 requests/day

**Headers** (in responses):
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1704711600
```

**Retry Strategy**:
- On 429: Wait for `Retry-After` seconds (from response header) or default 15 minutes
- Auto-retry after cooldown period

---

## MSW Implementation Notes

1. **Latency Simulation**: All endpoints have 100-500ms random delay
2. **Error Injection**: 10% random failure rate for edge case testing (disabled in E2E tests)
3. **In-Memory State**: MSW maintains state in-memory (resets on page reload)
4. **Optimistic Updates**: Frontend TanStack Query handles optimistic updates, MSW always returns server truth

**MSW Handler Files**:
- `mocks/handlers/tasks.ts` - Task and Sub-task endpoints
- `mocks/handlers/notes.ts` - Note endpoints
- `mocks/handlers/user.ts` - User profile and achievements
- `mocks/handlers/workflows.ts` - Workflow endpoints
- `mocks/handlers/activity.ts` - Activity log endpoints (read-only)
- `mocks/handlers/ai.ts` - AI endpoints (503 stubs)

---

## Contract Testing

**Test Coverage**:
- ✅ Request validation (Zod schema enforcement)
- ✅ Response shape matches data model
- ✅ Error responses match specification
- ✅ Limit enforcement (50 tasks, 10 sub-tasks, etc.)
- ✅ Relationship validation (orphaned sub-tasks, invalid task IDs)
- ✅ State transitions (completed → completedAt, achievement updates)

**Test Location**: `tests/integration/api-contracts.test.ts`

---

## Future Backend Alignment

When migrating from MSW to real backend:

1. **Endpoint Compatibility**: Real API must match these contracts exactly
2. **Zod → Pydantic**: Backend schemas mirror Zod schemas (type-safe alignment)
3. **Error Codes**: Backend uses same error code strings (`VALIDATION_ERROR`, etc.)
4. **Authentication**: Add `Authorization: Bearer <token>` header handling
5. **Deployment**: Replace MSW browser.ts with real API base URL

**Migration Checklist**:
- [ ] Backend implements all endpoints in this spec
- [ ] Contract tests pass against real backend
- [ ] Remove MSW browser.ts initialization
- [ ] Update `NEXT_PUBLIC_API_BASE_URL` in `.env`
- [ ] Enable AI endpoints (`NEXT_PUBLIC_AI_ENABLED=true`)
