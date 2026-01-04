# Schema Sync Validator Examples

## Example 1: Catching String Length Mismatch

### User Request
"Update max title length to 300 characters"

### Response

```
🚫 SCHEMA MISALIGNMENT DETECTED

Constitution Section VII.2: "Any mismatch between schemas is a defect"

Frontend Schema: src/schemas/task.ts
Backend Schema: app/models/task.py

Current State:
❌ Field: title
   Frontend: z.string().min(1).max(200)
   Backend:  constr(min_length=1, max_length=200)
   Status: Currently aligned at 200

Proposed Change Creates Risk:
If we update only one side to 300, misalignment will occur.

Required: Synchronized update to BOTH schemas

## Proposed Synchronized Update

Backend (app/models/task.py):
```python
class Task(SQLModel, table=True):
    # Change from max_length=200 to max_length=300
    title: str = Field(min_length=1, max_length=300)
```

Frontend (src/schemas/task.ts):
```typescript
const TaskSchema = z.object({
  // Change from .max(200) to .max(300)
  title: z.string().min(1).max(300),
});
```

Migration Notes:
- Database migration required (ALTER TABLE tasks)
- Existing tasks <200 chars unaffected
- Client-side validation updated simultaneously

Approve this synchronized update?
```

## Example 2: Detecting Missing Field

### User Request
"Add priority field to backend Task model"

### Response

```
⚠️ INCOMPLETE SCHEMA UPDATE DETECTED

Request: Add priority to backend only
Issue: This creates immediate schema misalignment

Constitutional Requirement:
"Schema consistency is mandatory" (Section VII.1)
"Any mismatch between schemas is a defect" (Section VII.2)

You MUST update both schemas simultaneously:

## Required Synchronized Update

Backend (app/models/task.py):
```python
from typing import Literal

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    priority: Literal["low", "medium", "high"] = Field(default="medium")  # NEW
    completed: bool = Field(default=False)
```

Frontend (src/schemas/task.ts):
```typescript
const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  priority: z.enum(["low", "medium", "high"]).default("medium"),  // NEW
  completed: z.boolean(),
});

type Task = z.infer<typeof TaskSchema>;
```

API Contract Impact:
- POST /api/tasks: accepts optional priority (defaults to "medium")
- PUT /api/tasks/:id: accepts optional priority
- GET /api/tasks: returns priority in response

Database Migration (Alembic):
```python
# Add column with default value
op.add_column('tasks', sa.Column('priority', sa.String(), nullable=False, server_default='medium'))
```

Shall I proceed with synchronized update?
```

## Example 3: Enum Value Mismatch

### Scenario
Backend uses `"med"` but frontend uses `"medium"`

### Response

```
🚫 SCHEMA MISALIGNMENT DETECTED

Frontend Schema: src/schemas/task.ts
Backend Schema: app/models/task.py

Mismatches Found:

❌ Field: priority
   Frontend: z.enum(["low", "medium", "high"])
   Backend:  Literal["low", "med", "high"]
   Issue: Enum value mismatch ("medium" vs "med")

This is a CRITICAL defect:
- Backend accepts "med"
- Frontend validates "medium"
- API calls will fail with 422 Unprocessable Entity

Required Action:
Decide authoritative values, then align both schemas.

Recommendation: Use full word "medium" (more readable)

Proposed Fix:
Backend: Change Literal["low", "med", "high"] → Literal["low", "medium", "high"]
Frontend: Keep z.enum(["low", "medium", "high"])

⚠️ Data Migration Required:
UPDATE tasks SET priority = 'medium' WHERE priority = 'med';

Approve this fix?
```

## Example 4: Complete Synchronized Update

### User Request
"Add 'description' field to Task"

### Response

```
📋 SYNCHRONIZED SCHEMA UPDATE PROPOSAL

Entity: Task

## Backend Schema Update

File: app/models/task.py

```python
# Current
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    completed: bool = Field(default=False)

# Proposed
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)  # NEW
    completed: bool = Field(default=False)
```

## Frontend Schema Update

File: src/schemas/task.ts

```typescript
// Current
const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  completed: z.boolean(),
});

// Proposed
const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),  // NEW
  completed: z.boolean(),
});
```

Alignment Verified:
✓ Field names match (description)
✓ Types compatible (Optional[str] → z.string().optional())
✓ Validation rules identical (max 2000 chars)
✓ Optional/required status matches (both optional)

Database Migration:
```python
# Alembic migration
op.add_column('tasks', sa.Column('description', sa.String(length=2000), nullable=True))
```

Approve synchronized update?
```

## Example 5: Datetime Field Alignment

### Scenario
Ensuring datetime fields are properly synced

### Response

```
✅ SCHEMA ALIGNMENT VERIFIED

Frontend Schema: src/schemas/task.ts
Backend Schema: app/models/task.py

Verified Fields:
✓ id: UUID → string.uuid() - Aligned
✓ title: string (1-200 chars) - Aligned
✓ completed: boolean - Aligned
✓ created_at: datetime → string.datetime() (ISO 8601) - Aligned
✓ updated_at: Optional[datetime] → string.datetime().nullable() - Aligned

All validation rules match.
Schemas are in sync.

Backend:
```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: Optional[datetime] = None
```

Frontend:
```typescript
createdAt: z.string().datetime(),  // ISO 8601 format
updatedAt: z.string().datetime().nullable(),
```

API Contract:
- Backend serializes datetime as ISO 8601 string
- Frontend validates string format
- Conversion: `new Date(task.createdAt)` when needed

Proceeding with implementation...
```

## Example 6: Nested Object Alignment

### Scenario
Adding address to User model

### Response

```
📋 SYNCHRONIZED SCHEMA UPDATE PROPOSAL

Entity: User (with nested Address)

## Backend Schema Update

File: app/models/user.py

```python
class Address(SQLModel):
    street: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(regex=r'^\d{5}(-\d{4})?$')

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=200)
    address: Address  # NEW nested object
```

## Frontend Schema Update

File: src/schemas/user.ts

```typescript
const AddressSchema = z.object({
  street: z.string().min(1).max(200),
  city: z.string().min(1).max(100),
  state: z.string().min(2).max(2),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/),
});

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  address: AddressSchema,  // NEW nested object
});

type Address = z.infer<typeof AddressSchema>;
type User = z.infer<typeof UserSchema>;
```

Alignment Verified:
✓ Nested object structure matches
✓ All Address fields aligned:
  - street: string(1-200)
  - city: string(1-100)
  - state: string(2-2)
  - zipCode/zip_code: regex pattern matches
✓ Field name conversion: zip_code → zipCode

Approve synchronized update?
```
