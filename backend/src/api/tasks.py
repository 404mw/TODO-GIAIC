"""Task API endpoints.

Phase 4: User Story 2 - Task Creation and Management (FR-007 to FR-014)

T119-T124: Task CRUD endpoints per api-specification.md Section 4.
"""

from datetime import datetime, timedelta, UTC
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import (
    DataResponse,
    DeleteResponse,
    ErrorCode,
    PaginatedResponse,
    PaginationMeta,
)
from src.schemas.enums import TaskPriority
from src.schemas.task import (
    ForceCompleteRequest,
    TaskCompletionResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskListFilters,
    TaskResponse,
    TaskUpdate,
    UnlockedAchievementCompact,
)
from src.services.task_service import (
    TaskService,
    TaskArchivedError,
    TaskDueDateExceededError,
    TaskLimitExceededError,
    TaskNotFoundError,
    TaskServiceError,
    TaskVersionConflictError,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


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
# TASK ENDPOINTS
# =============================================================================


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    summary="List tasks",
    description="Get paginated list of tasks with optional filters (FR-060).",
)
async def list_tasks(
    user: CurrentUser,
    service: TaskServiceDep,
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=25, ge=1, le=100, description="Items per page"),
    completed: bool | None = Query(default=None, description="Filter by completion"),
    priority: TaskPriority | None = Query(default=None, description="Filter by priority"),
    hidden: bool = Query(default=False, description="Include hidden tasks"),
    due_before: datetime | None = Query(default=None, description="Tasks due before"),
    due_after: datetime | None = Query(default=None, description="Tasks due after"),
) -> PaginatedResponse[TaskResponse]:
    """T119: GET /api/v1/tasks with pagination and filters."""
    tasks, total = await service.list_tasks(
        user=user,
        offset=offset,
        limit=limit,
        completed=completed,
        priority=priority,
        hidden=hidden,
        due_before=due_before,
        due_after=due_after,
    )

    # Convert to response models with subtask counts
    task_responses = []
    for task in tasks:
        # Get subtask counts (lazy load if needed)
        subtasks = task.subtasks if task.subtasks else []
        subtask_count = len(subtasks)
        subtask_completed_count = sum(1 for s in subtasks if s.completed)

        task_responses.append(
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description or "",
                priority=task.priority,
                due_date=task.due_date,
                estimated_duration=task.estimated_duration,
                focus_time_seconds=task.focus_time_seconds or 0,
                completed=task.completed,
                completed_at=task.completed_at,
                completed_by=task.completed_by,
                hidden=task.hidden,
                archived=task.archived,
                template_id=task.template_id,
                subtask_count=subtask_count,
                subtask_completed_count=subtask_completed_count,
                version=task.version,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        )

    return PaginatedResponse(
        data=task_responses,
        pagination=PaginationMeta(
            offset=offset,
            limit=limit,
            total=total,
            has_more=(offset + limit) < total,
        ),
    )


@router.get(
    "/{task_id}",
    response_model=DataResponse[TaskDetailResponse],
    summary="Get task by ID",
    description="Get task details with subtasks and reminders.",
)
async def get_task(
    task_id: UUID,
    user: CurrentUser,
    service: TaskServiceDep,
) -> DataResponse[TaskDetailResponse]:
    """T120: GET /api/v1/tasks/:id with subtasks and reminders."""
    try:
        task = await service.get_task(
            user=user,
            task_id=task_id,
            include_subtasks=True,
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )

    # Build subtask response objects
    subtasks = [
        {
            "id": s.id,
            "title": s.title,
            "completed": s.completed,
            "completed_at": s.completed_at,
            "order_index": s.order_index,
            "source": s.source.value,
        }
        for s in sorted(task.subtasks, key=lambda s: s.order_index)
    ]

    # Build reminder response objects (reminders relationship may not be loaded yet)
    reminders = []
    if hasattr(task, "reminders") and task.reminders:
        reminders = [
            {
                "id": r.id,
                "type": r.type.value,
                "offset_minutes": r.offset_minutes,
                "scheduled_at": r.scheduled_at,
                "method": r.method.value if r.method else "push",
                "fired": r.fired,
            }
            for r in task.reminders
        ]

    response = TaskDetailResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description or "",
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        focus_time_seconds=task.focus_time_seconds or 0,
        completed=task.completed,
        completed_at=task.completed_at,
        completed_by=task.completed_by,
        hidden=task.hidden,
        archived=task.archived,
        template_id=task.template_id,
        version=task.version,
        created_at=task.created_at,
        updated_at=task.updated_at,
        subtasks=subtasks,
        reminders=reminders,
    )

    return DataResponse(data=response)


@router.post(
    "",
    response_model=DataResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task with idempotency support (FR-059).",
)
async def create_task(
    data: TaskCreate,
    user: CurrentUser,
    service: TaskServiceDep,
    idempotency_key: Annotated[
        str | None, Header(alias="Idempotency-Key", description="Idempotency key")
    ] = None,
) -> DataResponse[TaskResponse]:
    """T121: POST /api/v1/tasks with idempotency."""
    # TODO: Implement idempotency check with IdempotencyKey model

    try:
        task = await service.create_task(user=user, data=data)
    except TaskDueDateExceededError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Due date cannot exceed 30 days from creation",
            },
        )
    except TaskLimitExceededError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.LIMIT_EXCEEDED,
                "message": "Task limit exceeded for your tier",
            },
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    response = TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description or "",
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        focus_time_seconds=task.focus_time_seconds or 0,
        completed=task.completed,
        completed_at=task.completed_at,
        completed_by=task.completed_by,
        hidden=task.hidden,
        archived=task.archived,
        template_id=task.template_id,
        subtask_count=0,
        subtask_completed_count=0,
        version=task.version,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

    return DataResponse(data=response)


@router.put(
    "/{task_id}",
    response_model=DataResponse[TaskResponse],
    summary="Update task",
    description="Update task with PUT/PATCH semantics and optimistic locking (FR-058, FR-014).",
)
@router.patch(
    "/{task_id}",
    response_model=DataResponse[TaskResponse],
    summary="Update task",
    description="Update task with PUT/PATCH semantics and optimistic locking (FR-058, FR-014).",
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    user: CurrentUser,
    service: TaskServiceDep,
    idempotency_key: Annotated[
        str | None, Header(alias="Idempotency-Key", description="Idempotency key")
    ] = None,
) -> DataResponse[TaskResponse]:
    """T122: PATCH /api/v1/tasks/:id with PATCH semantics."""
    try:
        task = await service.update_task(user=user, task_id=task_id, data=data)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except TaskVersionConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.CONFLICT,
                "message": "Version conflict. Refresh and retry.",
            },
        )
    except TaskArchivedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.ARCHIVED,
                "message": "Cannot modify archived task",
            },
        )
    except TaskServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.VALIDATION_ERROR, "message": str(e)},
        )

    # Get subtask counts
    task_with_subtasks = await service.get_task(
        user=user, task_id=task_id, include_subtasks=True
    )
    subtasks = task_with_subtasks.subtasks if task_with_subtasks.subtasks else []

    response = TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description or "",
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        focus_time_seconds=task.focus_time_seconds or 0,
        completed=task.completed,
        completed_at=task.completed_at,
        completed_by=task.completed_by,
        hidden=task.hidden,
        archived=task.archived,
        template_id=task.template_id,
        subtask_count=len(subtasks),
        subtask_completed_count=sum(1 for s in subtasks if s.completed),
        version=task.version,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

    return DataResponse(data=response)


@router.post(
    "/{task_id}/force-complete",
    response_model=DataResponse[TaskCompletionResponse],
    summary="Force complete task",
    description="""
    Complete task and all incomplete subtasks (FR-010).

    T305b: Returns unlocked achievements if any were earned by this completion.
    Per plan.md Achievement Notification Delivery.
    """,
)
async def force_complete_task(
    task_id: UUID,
    data: ForceCompleteRequest,
    user: CurrentUser,
    service: TaskServiceDep,
    settings: Settings = Depends(get_settings),
) -> DataResponse[TaskCompletionResponse]:
    """T123: POST /api/v1/tasks/:id/force-complete with achievement tracking."""
    from src.services.achievement_service import get_achievement_service

    try:
        task = await service.force_complete_task(user=user, task_id=task_id, data=data)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except TaskVersionConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.CONFLICT,
                "message": "Version conflict. Refresh and retry.",
            },
        )
    except TaskArchivedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.ARCHIVED,
                "message": "Cannot complete archived task",
            },
        )

    # Get subtask counts
    task_with_subtasks = await service.get_task(
        user=user, task_id=task_id, include_subtasks=True
    )
    subtasks = task_with_subtasks.subtasks if task_with_subtasks.subtasks else []

    # T305b: Process achievements using the same session as the task service
    achievement_service = get_achievement_service(service.session, settings)
    state = await achievement_service.get_or_create_achievement_state(user.id)

    # Update streak and stats
    await achievement_service.update_streak(state, task.completed_at)
    await achievement_service.increment_lifetime_tasks(state)

    # Check focus completion
    if achievement_service.is_focus_completion(task):
        await achievement_service.increment_focus_completions(state)

    # Check and unlock achievements
    newly_unlocked = await achievement_service.check_and_unlock(state)

    # Build unlocked achievements compact list
    unlocked_achievements = [
        UnlockedAchievementCompact(
            id=a["id"],
            name=a["name"],
            perk_type=a["perk"]["type"].value if a.get("perk") else None,
            perk_value=a["perk"]["value"] if a.get("perk") else None,
        )
        for a in newly_unlocked
    ]

    # Build task detail response
    subtask_responses = [
        {
            "id": s.id,
            "title": s.title,
            "completed": s.completed,
            "completed_at": s.completed_at,
            "order_index": s.order_index,
            "source": s.source.value,
        }
        for s in sorted(subtasks, key=lambda s: s.order_index)
    ]

    task_detail = TaskDetailResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description or "",
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        focus_time_seconds=task.focus_time_seconds or 0,
        completed=task.completed,
        completed_at=task.completed_at,
        completed_by=task.completed_by,
        hidden=task.hidden,
        archived=task.archived,
        template_id=task.template_id,
        version=task.version,
        created_at=task.created_at,
        updated_at=task.updated_at,
        subtasks=subtask_responses,
        reminders=[],
    )

    response = TaskCompletionResponse(
        task=task_detail,
        unlocked_achievements=unlocked_achievements,
        streak=state.current_streak,
    )

    return DataResponse(data=response)


@router.delete(
    "/{task_id}",
    response_model=DataResponse[DeleteResponse],
    summary="Delete task",
    description="Hard delete task and create tombstone for recovery (FR-012).",
)
async def delete_task(
    task_id: UUID,
    user: CurrentUser,
    service: TaskServiceDep,
) -> DataResponse[DeleteResponse]:
    """T124: DELETE /api/v1/tasks/:id."""
    try:
        tombstone = await service.hard_delete_task(user=user, task_id=task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )

    # Tombstones are recoverable for 7 days
    recoverable_until = tombstone.deleted_at + timedelta(days=7)

    return DataResponse(
        data=DeleteResponse(
            tombstone_id=tombstone.id,
            recoverable_until=recoverable_until,
        )
    )
