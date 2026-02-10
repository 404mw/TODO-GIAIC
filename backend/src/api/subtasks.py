"""Subtask API endpoints.

Phase 4: User Story 2 - Task Creation and Management (FR-019 to FR-021)

T125-T128: Subtask CRUD endpoints per api-specification.md Section 5.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import DataResponse, ErrorCode
from src.schemas.subtask import (
    SubtaskCreate,
    SubtaskOrderResponse,
    SubtaskReorderRequest,
    SubtaskResponse,
    SubtaskUpdate,
)
from src.services.task_service import (
    SubtaskLimitExceededError,
    SubtaskNotFoundError,
    TaskNotFoundError,
    TaskService,
    TaskServiceError,
)

router = APIRouter(tags=["subtasks"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_task_service(
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> TaskService:
    """Get TaskService instance."""
    return TaskService(db, settings)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


# =============================================================================
# SUBTASK ENDPOINTS (under /tasks/:task_id)
# =============================================================================

tasks_router = APIRouter(prefix="/tasks", tags=["subtasks"])


@tasks_router.post(
    "/{task_id}/subtasks",
    response_model=DataResponse[SubtaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create subtask",
    description="""
Add a new subtask to a task.

**Tier-based limits (FR-019):**
- Free tier: Maximum 4 subtasks per task
- Pro tier: Maximum 10 subtasks per task

**Behaviors:**
- Subtask is appended with the next `order_index`
- Source is set to 'user' by default (AI-generated subtasks use 'ai')
- Returns 409 Conflict if subtask limit is reached

**Auto-completion (FR-009):**
- When all subtasks are completed, the parent task is automatically completed
- The task's `completed_by` field is set to 'auto'
""",
    responses={
        201: {"description": "Subtask created successfully"},
        404: {"description": "Parent task not found or user doesn't own it"},
        409: {"description": "Subtask limit exceeded for user's tier"},
    },
)
async def create_subtask(
    task_id: UUID,
    data: SubtaskCreate,
    user: CurrentUser,
    service: TaskServiceDep,
) -> DataResponse[SubtaskResponse]:
    """T125: POST /api/v1/tasks/:task_id/subtasks - T138: OpenAPI documentation."""
    try:
        subtask = await service.create_subtask(
            user=user,
            task_id=task_id,
            data=data,
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except SubtaskLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.LIMIT_EXCEEDED,
                "message": str(e),
            },
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    return DataResponse(
        data=SubtaskResponse(
            id=subtask.id,
            task_id=subtask.task_id,
            title=subtask.title,
            completed=subtask.completed,
            completed_at=subtask.completed_at,
            order_index=subtask.order_index,
            source=subtask.source,
            created_at=subtask.created_at,
            updated_at=subtask.updated_at,
        )
    )


@tasks_router.put(
    "/{task_id}/subtasks/reorder",
    response_model=DataResponse[list[SubtaskOrderResponse]],
    summary="Reorder subtasks",
    description="""
Reorder subtasks to maintain gapless indices (FR-020).

**Request format:**
Send an array of subtask IDs in the desired order. All subtask IDs for the task
must be included in the array.

**Behaviors:**
- Order indices are reassigned starting from 0
- Indices are always gapless: [0, 1, 2, ...]
- Completion status is preserved during reorder
- Returns 404 if any subtask ID is invalid or doesn't belong to the task

**Example:**
```json
{
  "subtask_ids": [
    "uuid-of-third-subtask",
    "uuid-of-first-subtask",
    "uuid-of-second-subtask"
  ]
}
```

This moves the third subtask to position 0, first to position 1, etc.
""",
    responses={
        200: {"description": "Subtasks reordered successfully"},
        404: {"description": "Task or subtask not found"},
        400: {"description": "Invalid subtask IDs provided"},
    },
)
async def reorder_subtasks(
    task_id: UUID,
    data: SubtaskReorderRequest,
    user: CurrentUser,
    service: TaskServiceDep,
) -> DataResponse[list[SubtaskOrderResponse]]:
    """T127: PUT /api/v1/tasks/:task_id/subtasks/reorder - T138: OpenAPI documentation."""
    try:
        subtasks = await service.reorder_subtasks(
            user=user,
            task_id=task_id,
            subtask_ids=data.subtask_ids,
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except SubtaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": str(e)},
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    return DataResponse(
        data=[
            SubtaskOrderResponse(id=s.id, order_index=s.order_index)
            for s in subtasks
        ]
    )


# =============================================================================
# SUBTASK ENDPOINTS (direct /subtasks/:id)
# =============================================================================


@router.patch(
    "/{subtask_id}",
    response_model=DataResponse[SubtaskResponse],
    summary="Update subtask",
    description="""
Update subtask title and/or completion status.

**Updatable fields:**
- `title`: New title (1-200 characters)
- `completed`: Completion status (true/false)

**Auto-completion trigger (FR-009):**
When setting `completed: true` on a subtask:
1. The subtask's `completed_at` timestamp is set
2. The system checks if ALL subtasks for the parent task are now completed
3. If yes, the parent task is automatically marked as completed with `completed_by: 'auto'`

**Un-completing a subtask:**
When setting `completed: false`:
- The subtask's `completed_at` is cleared to null
- This does NOT un-complete an auto-completed parent task

**Partial updates:**
- Send only the fields you want to update
- Omitted fields retain their current values
""",
    responses={
        200: {"description": "Subtask updated successfully"},
        404: {"description": "Subtask not found or user doesn't own parent task"},
        400: {"description": "Validation error (e.g., title too long)"},
    },
)
async def update_subtask(
    subtask_id: UUID,
    data: SubtaskUpdate,
    user: CurrentUser,
    service: TaskServiceDep,
) -> DataResponse[SubtaskResponse]:
    """T126: PATCH /api/v1/subtasks/:id - T138: OpenAPI documentation."""
    try:
        subtask = await service.update_subtask(
            user=user,
            subtask_id=subtask_id,
            title=data.title,
            completed=data.completed,
        )
    except SubtaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Subtask not found"},
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    return DataResponse(
        data=SubtaskResponse(
            id=subtask.id,
            task_id=subtask.task_id,
            title=subtask.title,
            completed=subtask.completed,
            completed_at=subtask.completed_at,
            order_index=subtask.order_index,
            source=subtask.source,
            created_at=subtask.created_at,
            updated_at=subtask.updated_at,
        )
    )


@router.delete(
    "/{subtask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete subtask",
    description="""
Delete a subtask and automatically reorder remaining subtasks.

**Behaviors:**
- Subtask is permanently deleted (no soft delete for subtasks)
- Remaining subtasks are reordered to maintain gapless indices
- For example: deleting subtask at index 1 from [0, 1, 2] results in [0, 1]

**Auto-completion check:**
- Deleting a subtask does NOT trigger auto-completion
- Even if all remaining subtasks are complete, the task stays incomplete

**Limit effect:**
- Deleting a subtask frees up a slot for a new subtask
- User can immediately create a new subtask after deletion

**Note:** When a task is deleted, all its subtasks are automatically deleted
via cascade (no need to delete subtasks individually before deleting a task).
""",
    responses={
        204: {"description": "Subtask deleted successfully (no content)"},
        404: {"description": "Subtask not found or user doesn't own parent task"},
    },
)
async def delete_subtask(
    subtask_id: UUID,
    user: CurrentUser,
    service: TaskServiceDep,
) -> None:
    """T128: DELETE /api/v1/subtasks/:id - T138: OpenAPI documentation."""
    try:
        await service.delete_subtask(user=user, subtask_id=subtask_id)
    except SubtaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Subtask not found"},
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )
