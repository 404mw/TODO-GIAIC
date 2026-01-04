# Type Mappings: Pydantic ↔ Zod

## Core Type Mappings

| Pydantic (Python) | Zod (TypeScript) | Notes |
|-------------------|------------------|-------|
| `str` | `z.string()` | Basic string |
| `int` | `z.number().int()` | Integer |
| `float` | `z.number()` | Floating point |
| `bool` | `z.boolean()` | Boolean |
| `UUID` | `z.string().uuid()` | UUID as string |
| `datetime` | `z.string().datetime()` | ISO 8601 string |
| `date` | `z.string().date()` | Date string |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` | Enum values |
| `Optional[T]` | `.optional()` | Optional field |
| `List[T]` | `z.array(T)` | Array/List |
| `Dict[str, T]` | `z.record(T)` | Object/Dictionary |

## Field Modifiers

### Optional Fields

**Backend (Pydantic):**
```python
from typing import Optional

class Task(SQLModel):
    description: Optional[str] = None
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  description: z.string().optional(),
});
```

### Default Values

**Backend (Pydantic):**
```python
class Task(SQLModel):
    priority: str = Field(default="medium")
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  priority: z.string().default("medium"),
});
```

### String Validation

**Backend (Pydantic):**
```python
class Task(SQLModel):
    title: str = Field(min_length=1, max_length=200)
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  title: z.string().min(1).max(200),
});
```

### Number Validation

**Backend (Pydantic):**
```python
class Task(SQLModel):
    priority_level: int = Field(ge=1, le=5)  # 1 to 5
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  priorityLevel: z.number().int().min(1).max(5),
});
```

### Array/List Validation

**Backend (Pydantic):**
```python
from typing import List

class Task(SQLModel):
    tags: List[str] = Field(default_factory=list)
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  tags: z.array(z.string()).default([]),
});
```

## Naming Convention Conversion

### Field Names

**Backend (Python):** `snake_case`
**Frontend (TypeScript):** `camelCase`

**Example:**

Backend:
```python
class Task(SQLModel):
    created_at: datetime
    is_completed: bool
    task_priority: str
```

Frontend:
```typescript
const TaskSchema = z.object({
  createdAt: z.string().datetime(),
  isCompleted: z.boolean(),
  taskPriority: z.string(),
});
```

### Automatic Conversion

When serializing/deserializing, FastAPI handles snake_case ↔ camelCase conversion automatically if configured:

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

# Add response model with alias_generator
class Task(SQLModel):
    created_at: datetime

    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(x.split('_'))
        )
```

## Complex Type Examples

### Nested Objects

**Backend (Pydantic):**
```python
class Address(SQLModel):
    street: str
    city: str

class User(SQLModel):
    name: str
    address: Address
```

**Frontend (Zod):**
```typescript
const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
});

const UserSchema = z.object({
  name: z.string(),
  address: AddressSchema,
});
```

### Union Types

**Backend (Pydantic):**
```python
from typing import Union

class Task(SQLModel):
    value: Union[str, int]
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  value: z.union([z.string(), z.number()]),
});
```

### Discriminated Unions

**Backend (Pydantic):**
```python
from typing import Literal, Union
from pydantic import Field

class EmailNotification(SQLModel):
    type: Literal["email"] = "email"
    email: str

class SMSNotification(SQLModel):
    type: Literal["sms"] = "sms"
    phone: str

Notification = Union[EmailNotification, SMSNotification]
```

**Frontend (Zod):**
```typescript
const EmailNotificationSchema = z.object({
  type: z.literal("email"),
  email: z.string().email(),
});

const SMSNotificationSchema = z.object({
  type: z.literal("sms"),
  phone: z.string(),
});

const NotificationSchema = z.discriminatedUnion("type", [
  EmailNotificationSchema,
  SMSNotificationSchema,
]);
```

## Validation Rules Alignment

### Email Validation

**Backend (Pydantic):**
```python
from pydantic import EmailStr

class User(SQLModel):
    email: EmailStr
```

**Frontend (Zod):**
```typescript
const UserSchema = z.object({
  email: z.string().email(),
});
```

### URL Validation

**Backend (Pydantic):**
```python
from pydantic import HttpUrl

class Link(SQLModel):
    url: HttpUrl
```

**Frontend (Zod):**
```typescript
const LinkSchema = z.object({
  url: z.string().url(),
});
```

### Custom Regex

**Backend (Pydantic):**
```python
import re

class Task(SQLModel):
    slug: str = Field(regex=r'^[a-z0-9-]+$')
```

**Frontend (Zod):**
```typescript
const TaskSchema = z.object({
  slug: z.string().regex(/^[a-z0-9-]+$/),
});
```

## Type Inference

### Backend (Pydantic)

```python
# Models define types directly
class Task(SQLModel):
    title: str

# Type is inferred from model
def process_task(task: Task) -> None:
    print(task.title)  # IDE knows this is str
```

### Frontend (Zod)

```typescript
// Define schema
const TaskSchema = z.object({
  title: z.string(),
});

// Infer type from schema
type Task = z.infer<typeof TaskSchema>;

// Use inferred type
function processTask(task: Task): void {
  console.log(task.title); // IDE knows this is string
}
```

## Alignment Checklist

When generating multi-stack code, verify:

- [ ] Field names converted: `snake_case` → `camelCase`
- [ ] Types mapped correctly (see table above)
- [ ] Optional fields marked on both sides
- [ ] Default values match
- [ ] Validation rules equivalent (min/max, regex, etc.)
- [ ] Enum values identical
- [ ] Nested objects structured the same
- [ ] Array/list types match
- [ ] Date/datetime handled as ISO 8601 strings
