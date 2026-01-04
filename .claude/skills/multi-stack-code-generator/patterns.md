# Multi-Stack Code Generation Patterns

## Pattern 1: New Entity (Model + API + Frontend)

### Backend: SQLModel

```python
# app/models/{entity}.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Literal

class {Entity}Base(SQLModel):
    """Base schema for {Entity} (shared fields)"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    # ... other fields

class {Entity}({Entity}Base, table=True):
    """Database model for {Entity}"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class {Entity}Create({Entity}Base):
    """Schema for creating {Entity}"""
    pass  # Inherits fields from Base, excludes id/timestamps

class {Entity}Update(SQLModel):
    """Schema for updating {Entity} (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

class {Entity}Read({Entity}Base):
    """Schema for reading {Entity} (includes id/timestamps)"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
```

### Backend: FastAPI Endpoints

```python
# app/api/{entity}.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from app.models.{entity} import {Entity}, {Entity}Create, {Entity}Update, {Entity}Read
from app.database import get_session

router = APIRouter(prefix="/{entities}", tags=["{entities}"])

@router.post(
    "/",
    response_model={Entity}Read,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new {entity}",
)
async def create_{entity}(
    {entity}: {Entity}Create,
    session: Session = Depends(get_session)
):
    """
    Create a new {entity}.

    - **title**: {Entity} title (1-200 chars, required)
    - **description**: Optional description (max 2000 chars)
    """
    db_{entity} = {Entity}.from_orm({entity})
    session.add(db_{entity})
    session.commit()
    session.refresh(db_{entity})
    return db_{entity}

@router.get(
    "/",
    response_model=List[{Entity}Read],
    summary="List all {entities}",
)
async def list_{entities}(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Retrieve a list of {entities}.

    - **skip**: Number of items to skip (pagination)
    - **limit**: Max items to return (max 100)
    """
    statement = select({Entity}).offset(skip).limit(limit)
    {entities} = session.exec(statement).all()
    return {entities}

@router.get(
    "/{{{entity}_id}}",
    response_model={Entity}Read,
    summary="Get {entity} by ID",
)
async def get_{entity}(
    {entity}_id: UUID,
    session: Session = Depends(get_session)
):
    """Get a specific {entity} by ID."""
    {entity} = session.get({Entity}, {entity}_id)
    if not {entity}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{Entity} with id {{{entity}_id}} not found"
        )
    return {entity}

@router.put(
    "/{{{entity}_id}}",
    response_model={Entity}Read,
    summary="Update {entity}",
)
async def update_{entity}(
    {entity}_id: UUID,
    {entity}_update: {Entity}Update,
    session: Session = Depends(get_session)
):
    """
    Update an existing {entity}.

    Only provided fields will be updated.
    """
    db_{entity} = session.get({Entity}, {entity}_id)
    if not db_{entity}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{Entity} with id {{{entity}_id}} not found"
        )

    # Update only provided fields
    {entity}_data = {entity}_update.dict(exclude_unset=True)
    for key, value in {entity}_data.items():
        setattr(db_{entity}, key, value)

    db_{entity}.updated_at = datetime.utcnow()
    session.add(db_{entity})
    session.commit()
    session.refresh(db_{entity})
    return db_{entity}

@router.delete(
    "/{{{entity}_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete {entity}",
)
async def delete_{entity}(
    {entity}_id: UUID,
    session: Session = Depends(get_session)
):
    """Delete a {entity} by ID."""
    {entity} = session.get({Entity}, {entity}_id)
    if not {entity}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{Entity} with id {{{entity}_id}} not found"
        )

    session.delete({entity})
    session.commit()
    return None
```

### Frontend: Zod Schema

```typescript
// src/schemas/{entity}.ts
import { z } from "zod";

/**
 * Base schema for {Entity} (shared validation)
 */
export const {Entity}BaseSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  description: z.string().max(2000, "Description too long").optional(),
});

/**
 * Schema for creating a {Entity}
 */
export const {Entity}CreateSchema = {Entity}BaseSchema;

/**
 * Schema for updating a {Entity} (all fields optional)
 */
export const {Entity}UpdateSchema = {Entity}BaseSchema.partial();

/**
 * Schema for reading a {Entity} (includes id and timestamps)
 */
export const {Entity}ReadSchema = {Entity}BaseSchema.extend({
  id: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime().nullable(),
});

// TypeScript types inferred from schemas
export type {Entity}Base = z.infer<typeof {Entity}BaseSchema>;
export type {Entity}Create = z.infer<typeof {Entity}CreateSchema>;
export type {Entity}Update = z.infer<typeof {Entity}UpdateSchema>;
export type {Entity}Read = z.infer<typeof {Entity}ReadSchema>;
```

### Frontend: API Client

```typescript
// src/lib/api/{entity}.ts
import { {Entity}Create, {Entity}Update, {Entity}Read, {Entity}ReadSchema } from "@/schemas/{entity}";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Create a new {entity}
 */
export async function create{Entity}(data: {Entity}Create): Promise<{Entity}Read> {
  const response = await fetch(`${API_BASE}/{entities}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create {entity}");
  }

  const json = await response.json();
  return {Entity}ReadSchema.parse(json); // Runtime validation
}

/**
 * List all {entities}
 */
export async function list{Entity}s(
  skip = 0,
  limit = 100
): Promise<{Entity}Read[]> {
  const response = await fetch(
    `${API_BASE}/{entities}?skip=${skip}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch {entities}");
  }

  const json = await response.json();
  return z.array({Entity}ReadSchema).parse(json);
}

/**
 * Get {entity} by ID
 */
export async function get{Entity}(id: string): Promise<{Entity}Read> {
  const response = await fetch(`${API_BASE}/{entities}/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("{Entity} not found");
    }
    throw new Error("Failed to fetch {entity}");
  }

  const json = await response.json();
  return {Entity}ReadSchema.parse(json);
}

/**
 * Update {entity}
 */
export async function update{Entity}(
  id: string,
  data: {Entity}Update
): Promise<{Entity}Read> {
  const response = await fetch(`${API_BASE}/{entities}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update {entity}");
  }

  const json = await response.json();
  return {Entity}ReadSchema.parse(json);
}

/**
 * Delete {entity}
 */
export async function delete{Entity}(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/{entities}/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("{Entity} not found");
    }
    throw new Error("Failed to delete {entity}");
  }
}
```

## Pattern 2: Enum Alignment

When specs define enum values:

### Backend (Python)

```python
# app/constants/priority.py
from typing import Literal

PriorityType = Literal["low", "medium", "high"]

# app/models/task.py
from app.constants.priority import PriorityType

class Task(SQLModel, table=True):
    priority: PriorityType = Field(default="medium")
```

### Frontend (TypeScript)

```typescript
// src/constants/priority.ts
export const PRIORITY_VALUES = ["low", "medium", "high"] as const;
export type Priority = typeof PRIORITY_VALUES[number];

// src/schemas/task.ts
import { PRIORITY_VALUES } from "@/constants/priority";

export const TaskSchema = z.object({
  priority: z.enum(PRIORITY_VALUES).default("medium"),
});
```

## Pattern 3: Date/Timestamp Handling

### Backend (Python)

```python
from datetime import datetime

class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Frontend (TypeScript)

```typescript
// Schema accepts ISO 8601 string
export const TaskSchema = z.object({
  createdAt: z.string().datetime(), // ISO 8601: "2025-01-04T12:00:00Z"
});

// Convert to Date object when needed
const task = await getTask(id);
const date = new Date(task.createdAt);
```
