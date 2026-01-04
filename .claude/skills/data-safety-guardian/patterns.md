# Implementation Patterns

## Soft Delete Pattern

### Backend Model
```python
# app/models/task.py
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    deleted_at: Optional[datetime] = Field(default=None)
    # When deleted_at is set, task is "deleted"
    # Queries filter out deleted tasks by default
```

### Backend Delete Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Soft delete a task (mark as deleted, don't remove from DB).
    Can be restored using PATCH /api/tasks/{task_id}/restore
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    if task.deleted_at is not None:
        raise HTTPException(400, "Task already deleted")

    # Soft delete
    task.deleted_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return {"message": "Task deleted", "can_undo": True}
```

### Backend Restore Endpoint
```python
@router.patch("/{task_id}/restore", status_code=status.HTTP_200_OK)
async def restore_task(
    task_id: UUID,
    session: Session = Depends(get_session)
):
    """Restore a soft-deleted task (undo deletion)"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    if task.deleted_at is None:
        raise HTTPException(400, "Task is not deleted")

    # Restore
    task.deleted_at = None
    session.add(task)
    session.commit()

    return {"message": "Task restored"}
```

### Frontend Delete with Undo
```typescript
async function handleDeleteTask(task: Task) {
  // Step 1: Confirm
  const confirmed = await showConfirmDialog({
    title: "Delete Task",
    message: `Delete "${task.title}"? This can be undone.`,
    confirmText: "Delete",
  });

  if (!confirmed) return;

  // Step 2: Delete (soft delete)
  await deleteTask(task.id);

  // Step 3: Show undo
  showUndoPopup({
    message: `Deleted "${task.title}"`,
    onUndo: () => restoreTask(task.id),
    timeout: 10000, // 10 seconds
  });
}
```

## Undo Implementation Pattern

### Undo Log Model
```python
# app/models/undo_log.py
class UndoLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="task.id")
    operation: str  # "update", "delete", "bulk_delete"
    previous_state: str  # JSON of previous values
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    batch_id: Optional[UUID] = None  # For bulk operations
    undone_at: Optional[datetime] = None
```

### Capture Before Mutation
```python
def capture_undo(task: Task, operation: str) -> UndoLog:
    return UndoLog(
        task_id=task.id,
        operation=operation,
        previous_state=task.json(),
    )
```

### Restore from Undo Log
```python
def execute_undo(undo_log_id: UUID):
    log = session.get(UndoLog, undo_log_id)
    if log.undone_at is not None:
        raise ValueError("Already undone")

    task = session.get(Task, log.task_id)
    previous = json.loads(log.previous_state)

    # Restore previous state
    for key, value in previous.items():
        setattr(task, key, value)

    log.undone_at = datetime.utcnow()
    session.commit()
```

### Update with Undo
```python
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task. All fields optional."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    # Capture previous state (for undo)
    previous_state = task.dict()

    # Update
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    # Log update for undo
    log_update(task_id, previous_state, task.dict())

    return task
```

### Frontend Undo
```typescript
async function handleUpdateTask(id: string, updates: TaskUpdate) {
  const previousState = await getTask(id); // Capture current state

  await updateTask(id, updates);

  showUndoPopup({
    message: "Task updated",
    onUndo: () => updateTask(id, previousState), // Restore previous state
    timeout: 10000,
  });
}
```

## Bulk Operations Pattern

### Rate Limiting
```python
MAX_BULK_DELETE = 100

@router.post("/bulk-delete")
async def bulk_delete_tasks(
    task_ids: list[UUID],
    session: Session = Depends(get_session)
):
    if len(task_ids) > MAX_BULK_DELETE:
        raise HTTPException(
            400,
            f"Bulk delete limited to {MAX_BULK_DELETE} tasks. "
            f"You requested {len(task_ids)}."
        )

    # ... perform soft delete
```

### Batch Undo
```python
# Link all deletes with batch ID
batch_id = uuid4()

for task_id in task_ids:
    task = session.get(Task, task_id)
    task.deleted_at = datetime.utcnow()
    task.deletion_batch_id = batch_id  # Link to batch

session.commit()

# Undo endpoint restores entire batch
@router.post("/restore-batch/{batch_id}")
async def restore_batch(batch_id: UUID):
    tasks = session.exec(
        select(Task).where(Task.deletion_batch_id == batch_id)
    ).all()

    for task in tasks:
        task.deleted_at = None
        task.deletion_batch_id = None

    session.commit()
```

### Frontend Preview
```typescript
async function bulkDeleteCompleted() {
  // Step 1: Get list of tasks to delete
  const completedTasks = await listTasks({ completed: true });

  // Step 2: Show preview
  const confirmed = await showBulkDeleteDialog({
    title: "Delete All Completed Tasks",
    message: `You are about to delete ${completedTasks.length} completed tasks:`,
    items: completedTasks.map(t => t.title),
    confirmText: `Delete ${completedTasks.length} Tasks`,
  });

  if (!confirmed) return;

  // Step 3: Execute
  const batchId = await bulkDelete(completedTasks.map(t => t.id));

  // Step 4: Undo
  showUndoPopup({
    message: `Deleted ${completedTasks.length} tasks`,
    onUndo: () => restoreBulk(batchId),
  });
}
```

## Backup Strategy Requirements

### Minimum Requirements (Section III.2)

**Frequency:** Daily (minimum)
**Retention:** 30 days (minimum)
**Testing:** Monthly restore test
**Storage:** Off-site or managed service

### Example: Neon DB + S3
```yaml
# Backup Configuration
provider: Neon DB (managed PostgreSQL)
automated_backups:
  frequency: Daily at 2 AM UTC
  retention: 30 days
  location: Neon's infrastructure

additional_backups:
  frequency: Weekly on Sunday
  retention: 90 days
  location: S3 bucket (offsite)
  format: pg_dump

restore_testing:
  frequency: Monthly
  last_test: 2026-01-01
  result: Success
```

## Dummy Data for Testing

### Fixtures
```python
# tests/fixtures/dummy_data.py

DUMMY_TASKS = [
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": False,
        "priority": "medium",
    },
    {
        "title": "Finish report",
        "description": "Q4 financial report",
        "completed": True,
        "priority": "high",
    },
    # ... more dummy tasks
]

def create_dummy_tasks(session: Session) -> list[Task]:
    """Create fake tasks for testing"""
    tasks = []
    for data in DUMMY_TASKS:
        task = Task(**data)
        session.add(task)
        tasks.append(task)
    session.commit()
    return tasks
```

### Test Database Setup
```python
# tests/conftest.py
import pytest
from sqlmodel import create_engine, Session

@pytest.fixture
def test_db():
    """Create isolated test database"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    # OR separate test database
    # engine = create_engine("postgresql://localhost/todo_test")

    # Create tables
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Populate with dummy data
        create_dummy_tasks(session)
        yield session

    # Cleanup after test
    SQLModel.metadata.drop_all(engine)
```

### Using Dummy Data in Tests
```python
# tests/test_task_api.py

def test_get_tasks(test_db: Session):
    """Test GET /api/tasks with dummy data"""
    # Uses dummy data from fixture
    response = client.get("/api/tasks")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0
    assert tasks[0]["title"] == "Buy groceries"  # Dummy data
```
