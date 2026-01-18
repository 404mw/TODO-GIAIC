# API Contracts

This document defines the expected API endpoints, request/response formats, and contracts that the backend should implement.

## Base URL

```
Production: https://api.perpetuaflow.app/v1
Development: http://localhost:3000/api (MSW mocked)
```

## Authentication

All dashboard API endpoints require authentication.

**Expected Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## API Endpoints

### Tasks

#### GET /api/tasks

Fetch all tasks for the authenticated user.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hidden` | boolean | No | Filter by hidden status |
| `archived` | boolean | No | Filter by archived status |
| `completed` | boolean | No | Filter by completion status |
| `priority` | string | No | Filter by priority (high, medium, low) |
| `dueDate` | string | No | Filter by due date (ISO 8601) |
| `tags` | string[] | No | Filter by tags (comma-separated) |
| `search` | string | No | Search in title/description |
| `sortBy` | string | No | Sort field (dueDate, priority, createdAt, title) |
| `sortOrder` | string | No | Sort direction (asc, desc) |
| `limit` | number | No | Pagination limit (default: 50) |
| `offset` | number | No | Pagination offset (default: 0) |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Complete project documentation",
      "description": "Write comprehensive docs for the API",
      "priority": "high",
      "completed": false,
      "hidden": false,
      "archived": false,
      "dueDate": "2024-01-20T10:00:00Z",
      "tags": ["documentation", "urgent"],
      "estimatedDuration": 120,
      "recurrence": {
        "rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
        "description": "Every Monday, Wednesday, and Friday",
        "nextScheduled": "2024-01-22T10:00:00Z"
      },
      "subtasksCount": 3,
      "completedSubtasksCount": 1,
      "remindersCount": 2,
      "createdAt": "2024-01-15T09:00:00Z",
      "updatedAt": "2024-01-15T09:00:00Z"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 50,
    "offset": 0,
    "hasMore": false
  }
}
```

---

#### GET /api/tasks/:id

Fetch a single task by ID.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string (uuid) | Yes | Task ID |

**Response:**
```json
{
  "id": "uuid",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "priority": "high",
  "completed": false,
  "hidden": false,
  "archived": false,
  "dueDate": "2024-01-20T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "estimatedDuration": 120,
  "recurrence": {
    "rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
    "description": "Every Monday, Wednesday, and Friday",
    "nextScheduled": "2024-01-22T10:00:00Z"
  },
  "subtasks": [
    {
      "id": "uuid",
      "title": "Write introduction",
      "completed": true,
      "estimatedDuration": 30,
      "order": 0
    }
  ],
  "reminders": [
    {
      "id": "uuid",
      "type": "before",
      "offset": 3600,
      "method": "notification"
    }
  ],
  "createdAt": "2024-01-15T09:00:00Z",
  "updatedAt": "2024-01-15T09:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Task does not exist
- `403 Forbidden` - Task belongs to another user

---

#### POST /api/tasks

Create a new task.

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "priority": "high",
  "dueDate": "2024-01-20T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "estimatedDuration": 120,
  "recurrence": {
    "rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR"
  },
  "subtasks": [
    {
      "title": "Write introduction",
      "estimatedDuration": 30
    }
  ],
  "reminders": [
    {
      "type": "before",
      "offset": 3600,
      "method": "notification"
    }
  ]
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `title` | Required, 1-200 characters |
| `description` | Optional, max 1000 characters |
| `priority` | Optional, enum: high, medium, low (default: medium) |
| `dueDate` | Optional, ISO 8601 datetime |
| `tags` | Optional, max 20 tags, each max 30 characters |
| `estimatedDuration` | Optional, positive integer (minutes) |
| `recurrence.rule` | Optional, valid RRULE string |
| `subtasks` | Optional, max 10 items |
| `reminders` | Optional, max 5 items |

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "title": "Complete project documentation",
  // ... full task object
}
```

**Error Responses:**
- `400 Bad Request` - Validation error (with details)
- `429 Too Many Requests` - Rate limited or task limit reached

---

#### PATCH /api/tasks/:id

Update an existing task.

**Request Body:** (partial update)
```json
{
  "title": "Updated title",
  "completed": true
}
```

**Special Behaviors:**

1. **Completing a recurring task:**
   - Sets `completed: true` on current instance
   - Generates next instance based on recurrence rule
   - Response includes `nextInstance` object

2. **Soft delete (hiding):**
   - Set `hidden: true` to soft delete
   - Hidden tasks excluded from default queries

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "title": "Updated title",
  "completed": true,
  // ... full updated task object
  "nextInstance": {
    "id": "new-uuid",
    "dueDate": "2024-01-22T10:00:00Z"
  }
}
```

---

#### DELETE /api/tasks/:id

Permanently delete a task.

**Response:** `204 No Content`

**Note:** Consider soft delete (`PATCH` with `hidden: true`) for most use cases.

---

### Subtasks

#### GET /api/tasks/:taskId/subtasks

Fetch all subtasks for a task.

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "taskId": "parent-task-uuid",
      "title": "Write introduction",
      "completed": false,
      "estimatedDuration": 30,
      "order": 0,
      "createdAt": "2024-01-15T09:00:00Z",
      "updatedAt": "2024-01-15T09:00:00Z"
    }
  ]
}
```

---

#### POST /api/tasks/:taskId/subtasks

Create a new subtask.

**Request Body:**
```json
{
  "title": "Write conclusion",
  "estimatedDuration": 20
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `title` | Required, 1-100 characters |
| `estimatedDuration` | Optional, positive integer (minutes) |

**Response:** `201 Created`

**Error Responses:**
- `400 Bad Request` - Validation error
- `400 Bad Request` - Maximum subtasks (10) reached

---

#### PATCH /api/subtasks/:id

Update a subtask.

**Request Body:**
```json
{
  "completed": true
}
```

**Response:** `200 OK`

---

#### DELETE /api/subtasks/:id

Delete a subtask.

**Response:** `204 No Content`

---

### Notes

#### GET /api/notes

Fetch all notes.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Search in content |
| `sortBy` | string | No | Sort field (createdAt, updatedAt) |
| `limit` | number | No | Pagination limit |
| `offset` | number | No | Pagination offset |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "content": "Remember to review the API documentation",
      "voiceRecordingUrl": null,
      "createdAt": "2024-01-15T09:00:00Z",
      "updatedAt": "2024-01-15T09:00:00Z"
    }
  ],
  "pagination": {
    "total": 10,
    "limit": 50,
    "offset": 0
  }
}
```

---

#### POST /api/notes

Create a new note.

**Request Body:**
```json
{
  "content": "Remember to review the API documentation",
  "voiceRecordingUrl": null
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `content` | Required, 1-1000 characters |
| `voiceRecordingUrl` | Optional, valid URL |

**Response:** `201 Created`

---

#### PATCH /api/notes/:id

Update a note.

**Response:** `200 OK`

---

#### DELETE /api/notes/:id

Delete a note.

**Response:** `204 No Content`

---

### Reminders

#### GET /api/tasks/:taskId/reminders

Fetch reminders for a task.

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "taskId": "task-uuid",
      "type": "before",
      "offset": 3600,
      "method": "notification",
      "sent": false,
      "scheduledFor": "2024-01-20T09:00:00Z",
      "createdAt": "2024-01-15T09:00:00Z"
    }
  ]
}
```

---

#### POST /api/tasks/:taskId/reminders

Create a reminder.

**Request Body:**
```json
{
  "type": "before",
  "offset": 3600,
  "method": "notification"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | "before" or "after" due date |
| `offset` | number | Seconds before/after due date |
| `method` | enum | "notification", "email", "sms" |

**Response:** `201 Created`

---

### Achievements

#### GET /api/achievements

Fetch user achievements and streaks.

**Response:**
```json
{
  "currentStreak": 7,
  "longestStreak": 14,
  "totalTasksCompleted": 142,
  "tasksCompletedToday": 5,
  "tasksCompletedThisWeek": 23,
  "milestones": [
    {
      "id": "first-task",
      "title": "First Task",
      "description": "Complete your first task",
      "unlockedAt": "2024-01-01T10:00:00Z",
      "icon": "trophy"
    },
    {
      "id": "week-streak",
      "title": "Week Warrior",
      "description": "Maintain a 7-day streak",
      "unlockedAt": "2024-01-15T10:00:00Z",
      "icon": "fire"
    }
  ],
  "recentActivity": [
    {
      "type": "task_completed",
      "taskId": "uuid",
      "taskTitle": "Complete documentation",
      "timestamp": "2024-01-15T14:00:00Z"
    }
  ]
}
```

---

### User

#### GET /api/user

Get current user profile.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "https://...",
  "preferences": {
    "theme": "system",
    "defaultPriority": "medium",
    "notificationsEnabled": true,
    "focusDefaultDuration": 25
  },
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

#### PATCH /api/user

Update user profile.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "preferences": {
    "theme": "dark"
  }
}
```

**Response:** `200 OK`

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "title",
        "message": "Title is required"
      }
    ]
  }
}
```

**Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

**Limits:**
- 100 requests per minute per user
- 10 task creations per minute
- 1000 requests per hour per user

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705320000
```

---

## Webhooks (Future)

**Events:**
- `task.created`
- `task.updated`
- `task.completed`
- `task.deleted`
- `reminder.triggered`
- `streak.updated`

**Payload:**
```json
{
  "event": "task.completed",
  "timestamp": "2024-01-15T14:00:00Z",
  "data": {
    "task": { /* task object */ }
  }
}
```

---

## Backend Implementation Notes

### Required Features

1. **Authentication & Authorization**
   - JWT-based auth with refresh tokens
   - User isolation for all resources

2. **Database Schema**
   - Users, Tasks, Subtasks, Notes, Reminders tables
   - Proper foreign keys and indexes

3. **Recurrence Handling**
   - Parse and validate RRULE strings
   - Generate next instance on completion
   - Handle edge cases (holidays, weekends)

4. **Reminder System**
   - Background job scheduler
   - Push notification service integration
   - Email service integration

5. **Streak Calculation**
   - Daily streak logic (timezone-aware)
   - Activity logging for history

### Suggested Technology Stack

| Component | Recommendation |
|-----------|----------------|
| Runtime | Node.js / Python / Go |
| Framework | Express / FastAPI / Gin |
| Database | PostgreSQL |
| Cache | Redis |
| Queue | Bull (Node) / Celery (Python) |
| Auth | JWT with refresh tokens |
| Validation | Zod (Node) / Pydantic (Python) |
