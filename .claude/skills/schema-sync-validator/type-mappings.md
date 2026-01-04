# Type Mappings: Pydantic ↔ Zod

## Core Type Mapping Table

| Pydantic/SQLModel | Zod Equivalent | Notes |
|:------------------|:---------------|:------|
| `str` | `z.string()` | |
| `int` | `z.number().int()` | |
| `float` | `z.number()` | |
| `bool` | `z.boolean()` | |
| `datetime` | `z.string().datetime()` or `z.date()` | ISO 8601 string |
| `UUID` | `z.string().uuid()` | String representation |
| `Optional[T]` | `z.optional()` or `.nullable()` | |
| `List[T]` | `z.array(T)` | |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` | |
| `EmailStr` | `z.string().email()` | |
| `constr(min_length=X, max_length=Y)` | `z.string().min(X).max(Y)` | |
| `conint(ge=X, le=Y)` | `z.number().min(X).max(Y)` | |

## Validation Rule Equivalents

### String Constraints

**Backend (Pydantic):**
```python
from pydantic import Field

# Min/Max length
title: str = Field(min_length=1, max_length=200)

# Regex pattern
slug: str = Field(regex=r'^[a-z0-9-]+$')
```

**Frontend (Zod):**
```typescript
// Min/Max length
title: z.string().min(1).max(200)

// Regex pattern
slug: z.string().regex(/^[a-z0-9-]+$/)
```

### Number Constraints

**Backend (Pydantic):**
```python
# Range constraints
age: int = Field(ge=0, le=150)  # Greater or equal, less or equal
rating: float = Field(gt=0, lt=5)  # Greater than, less than
```

**Frontend (Zod):**
```typescript
// Range constraints
age: z.number().int().min(0).max(150)
rating: z.number().gt(0).lt(5)
```

### Optional Fields

**Backend (Pydantic):**
```python
from typing import Optional

description: Optional[str] = None
# OR
description: Optional[str] = Field(default=None)
```

**Frontend (Zod):**
```typescript
description: z.string().optional()
// OR
description: z.string().nullable()
```

### Default Values

**Backend (Pydantic):**
```python
priority: str = Field(default="medium")
created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Frontend (Zod):**
```typescript
priority: z.string().default("medium")
createdAt: z.string().datetime().default(new Date().toISOString())
```

### Enums

**Backend (Pydantic):**
```python
from typing import Literal

priority: Literal["low", "medium", "high"] = Field(default="medium")
```

**Frontend (Zod):**
```typescript
priority: z.enum(["low", "medium", "high"]).default("medium")
```

### Arrays/Lists

**Backend (Pydantic):**
```python
from typing import List

tags: List[str] = Field(default_factory=list)
scores: List[int] = Field(min_items=1, max_items=10)
```

**Frontend (Zod):**
```typescript
tags: z.array(z.string()).default([])
scores: z.array(z.number().int()).min(1).max(10)
```

### Email Validation

**Backend (Pydantic):**
```python
from pydantic import EmailStr

email: EmailStr
```

**Frontend (Zod):**
```typescript
email: z.string().email()
```

### URL Validation

**Backend (Pydantic):**
```python
from pydantic import HttpUrl

website: HttpUrl
```

**Frontend (Zod):**
```typescript
website: z.string().url()
```

### UUID Handling

**Backend (Pydantic):**
```python
from uuid import UUID

id: UUID = Field(default_factory=uuid4, primary_key=True)
```

**Frontend (Zod):**
```typescript
id: z.string().uuid()
```

### Datetime Handling

**Backend (Pydantic):**
```python
from datetime import datetime

created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Frontend (Zod):**
```typescript
// As ISO 8601 string
createdAt: z.string().datetime()

// Example validation
// "2025-01-04T12:00:00Z" ✓
// "2025-01-04" ✗ (not datetime)
```

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

## Field Name Conversion

### Naming Convention

**Backend:** `snake_case` (Python PEP 8)
**Frontend:** `camelCase` (JavaScript/TypeScript)

### Example Conversions

| Python (Backend) | TypeScript (Frontend) |
|:-----------------|:----------------------|
| `created_at` | `createdAt` |
| `is_completed` | `isCompleted` |
| `user_id` | `userId` |
| `task_priority` | `taskPriority` |
| `updated_at` | `updatedAt` |

### Automatic Conversion

FastAPI handles snake_case ↔ camelCase conversion with alias:

```python
from pydantic import BaseModel, Field

class Task(BaseModel):
    created_at: datetime = Field(alias="createdAt")
```

## Alignment Checklist

When verifying schema alignment:

- [ ] Field names match (accounting for snake_case/camelCase)
- [ ] Types are correctly mapped
- [ ] String constraints match (min/max length)
- [ ] Number constraints match (min/max values)
- [ ] Optional fields marked on both sides
- [ ] Default values are identical
- [ ] Enum values are identical (order doesn't matter)
- [ ] Regex patterns match exactly
- [ ] Email/URL validators present on both sides
- [ ] Nested objects structured identically
- [ ] Array/list types match
- [ ] Datetime handled as ISO 8601 strings
