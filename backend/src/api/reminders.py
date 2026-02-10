"""Reminder API endpoints.

Phase 8: User Story 8 - Reminder System (FR-025 to FR-028)

T191: POST /api/v1/tasks/:task_id/reminders per api-specification.md Section 6.1
T192: PATCH /api/v1/reminders/:id per api-specification.md Section 6.2
T193: DELETE /api/v1/reminders/:id per api-specification.md Section 6.3
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import DataResponse, ErrorCode
from src.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)
from src.services.reminder_service import (
    ReminderLimitExceededError,
    ReminderNotFoundError,
    ReminderService,
    ReminderServiceError,
    TaskNoDueDateError,
    TaskNotFoundError,
)


router = APIRouter(tags=["reminders"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_reminder_service(
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> ReminderService:
    """Get ReminderService instance."""
    return ReminderService(db, settings)


ReminderServiceDep = Annotated[ReminderService, Depends(get_reminder_service)]


# =============================================================================
# REMINDER ENDPOINTS (under /tasks/:task_id)
# =============================================================================

tasks_router = APIRouter(prefix="/tasks", tags=["reminders"])


@tasks_router.post(
    "/{task_id}/reminders",
    response_model=DataResponse[ReminderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create reminder",
    description="""
Create a new reminder for a task.

**Reminder types (FR-025):**
- `before`: Minutes before the task's due date (requires `offset_minutes`)
- `after`: Minutes after the task's due date (requires `offset_minutes`)
- `absolute`: Specific timestamp (requires `scheduled_at`)

**Limits (FR-025):**
- Maximum 5 reminders per task

**Notification methods (FR-028):**
- `push`: Push notification to device
- `in_app`: In-app notification only

**Scheduled time calculation:**
- For `before` type: `scheduled_at = task.due_date - offset_minutes`
- For `after` type: `scheduled_at = task.due_date + offset_minutes`
- For `absolute` type: Uses the provided `scheduled_at` directly

**Requirements:**
- Relative reminders (`before`/`after`) require the task to have a due date
- Returns 400 if creating relative reminder for task without due date

**Example request (before):**
```json
{
  "type": "before",
  "offset_minutes": 60,
  "method": "push"
}
```

**Example request (absolute):**
```json
{
  "type": "absolute",
  "scheduled_at": "2026-01-25T16:00:00Z",
  "method": "in_app"
}
```
""",
    responses={
        201: {"description": "Reminder created successfully"},
        400: {"description": "Validation error or task has no due date"},
        404: {"description": "Task not found or user doesn't own it"},
        409: {"description": "Reminder limit (5) exceeded for this task"},
    },
)
async def create_reminder(
    task_id: UUID,
    data: ReminderCreate,
    user: CurrentUser,
    service: ReminderServiceDep,
) -> DataResponse[ReminderResponse]:
    """T191: POST /api/v1/tasks/:task_id/reminders per api-specification.md Section 6.1."""
    try:
        reminder = await service.create_reminder(
            user=user,
            task_id=task_id,
            data=data,
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except TaskNoDueDateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.VALIDATION_ERROR,
                "message": str(e),
            },
        )
    except ReminderLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.LIMIT_EXCEEDED,
                "message": str(e),
            },
        )
    except ReminderServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    return DataResponse(
        data=ReminderResponse(
            id=reminder.id,
            task_id=reminder.task_id,
            type=reminder.type,
            offset_minutes=reminder.offset_minutes,
            scheduled_at=reminder.scheduled_at,
            method=reminder.method,
            fired=reminder.fired,
            fired_at=reminder.fired_at,
            created_at=reminder.created_at,
        )
    )


# =============================================================================
# REMINDER ENDPOINTS (direct /reminders/:id)
# =============================================================================


@router.patch(
    "/{reminder_id}",
    response_model=DataResponse[ReminderResponse],
    summary="Update reminder",
    description="""
Update a reminder's timing or notification method.

**Updatable fields:**
- `offset_minutes`: New offset for relative reminders (recalculates `scheduled_at`)
- `scheduled_at`: New time for absolute reminders
- `method`: Notification method (`push` or `in_app`)

**Recalculation (FR-026):**
- Updating `offset_minutes` recalculates `scheduled_at` based on task's due date
- This applies to `before` and `after` reminder types
- `absolute` reminders use `scheduled_at` directly, not `offset_minutes`

**Partial updates:**
- Send only the fields you want to update
- Omitted fields retain their current values

**Example request:**
```json
{
  "offset_minutes": 30
}
```
""",
    responses={
        200: {"description": "Reminder updated successfully"},
        404: {"description": "Reminder not found or user doesn't own it"},
        400: {"description": "Validation error"},
    },
)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    user: CurrentUser,
    service: ReminderServiceDep,
) -> DataResponse[ReminderResponse]:
    """T192: PATCH /api/v1/reminders/:id per api-specification.md Section 6.2."""
    try:
        reminder = await service.update_reminder(
            user=user,
            reminder_id=reminder_id,
            data=data,
        )
    except ReminderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Reminder not found"},
        )
    except ReminderServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    return DataResponse(
        data=ReminderResponse(
            id=reminder.id,
            task_id=reminder.task_id,
            type=reminder.type,
            offset_minutes=reminder.offset_minutes,
            scheduled_at=reminder.scheduled_at,
            method=reminder.method,
            fired=reminder.fired,
            fired_at=reminder.fired_at,
            created_at=reminder.created_at,
        )
    )


@router.delete(
    "/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete reminder",
    description="""
Delete a reminder.

**Behaviors:**
- Reminder is permanently deleted
- If reminder was scheduled for firing, it will be cancelled
- Deleting a reminder frees up a slot for a new reminder (max 5 per task)

**Note:** When a task is deleted, all its reminders are automatically deleted
via cascade.
""",
    responses={
        204: {"description": "Reminder deleted successfully (no content)"},
        404: {"description": "Reminder not found or user doesn't own it"},
    },
)
async def delete_reminder(
    reminder_id: UUID,
    user: CurrentUser,
    service: ReminderServiceDep,
) -> None:
    """T193: DELETE /api/v1/reminders/:id per api-specification.md Section 6.3."""
    try:
        await service.delete_reminder(user=user, reminder_id=reminder_id)
    except ReminderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Reminder not found"},
        )
    except ReminderServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )
