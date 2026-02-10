"""Recovery API endpoints.

Phase 18: User Story 13 - Task Deletion and Recovery (FR-062 to FR-064)

T344: GET /api/v1/tombstones
T345: POST /api/v1/tasks/recover/:tombstone_id per api-specification.md Section 3.7
"""

from datetime import datetime, timedelta, UTC
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import DataResponse, ErrorCode, PaginatedResponse, PaginationMeta
from src.schemas.enums import TombstoneEntityType
from src.schemas.task import TaskDetailResponse
from src.services.recovery_service import (
    RecoveryService,
    RecoveryServiceError,
    TaskIDCollisionError,
    TombstoneNotFoundError,
)


# =============================================================================
# SCHEMAS
# =============================================================================


class TombstoneResponse(BaseModel):
    """Response schema for a deletion tombstone."""

    id: UUID = Field(description="Tombstone ID")
    entity_type: TombstoneEntityType = Field(description="Deleted entity type")
    entity_id: UUID = Field(description="Original entity ID")
    entity_data: dict = Field(description="Serialized entity state")
    deleted_at: datetime = Field(description="Deletion timestamp (UTC)")
    recoverable_until: datetime = Field(description="Recovery expiration time")

    class Config:
        from_attributes = True


# =============================================================================
# ROUTERS
# =============================================================================

# Tombstone listing endpoint
router = APIRouter(prefix="/tombstones", tags=["recovery"])

# Task recovery endpoint (mounted under /tasks)
tasks_router = APIRouter(prefix="/tasks", tags=["recovery"])


# Recovery window: 7 days
RECOVERY_WINDOW_DAYS = 7


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_recovery_service(db: DBSession) -> RecoveryService:
    """Get RecoveryService instance."""
    return RecoveryService(db)


RecoveryServiceDep = Annotated[RecoveryService, Depends(get_recovery_service)]


# =============================================================================
# T344: GET /api/v1/tombstones
# =============================================================================


@router.get(
    "",
    response_model=DataResponse[list[TombstoneResponse]],
    summary="List tombstones",
    description="List all recoverable deleted tasks for the current user (FR-062).",
)
async def list_tombstones(
    user: CurrentUser,
    service: RecoveryServiceDep,
) -> DataResponse[list[TombstoneResponse]]:
    """T344: GET /api/v1/tombstones."""
    tombstones = await service.list_tombstones(user=user)

    responses = []
    now = datetime.now(UTC)
    for t in tombstones:
        # Ensure deleted_at is timezone-aware (SQLite strips timezone info)
        deleted_at = t.deleted_at.replace(tzinfo=UTC) if t.deleted_at.tzinfo is None else t.deleted_at
        recoverable_until = deleted_at + timedelta(days=RECOVERY_WINDOW_DAYS)
        # Only include tombstones that are still within the recovery window
        if recoverable_until > now:
            responses.append(
                TombstoneResponse(
                    id=t.id,
                    entity_type=t.entity_type,
                    entity_id=t.entity_id,
                    entity_data=t.entity_data,
                    deleted_at=t.deleted_at,
                    recoverable_until=recoverable_until,
                )
            )

    return DataResponse(data=responses)


# =============================================================================
# T345: POST /api/v1/tasks/recover/:tombstone_id
# =============================================================================


@tasks_router.post(
    "/recover/{tombstone_id}",
    response_model=DataResponse[TaskDetailResponse],
    summary="Recover deleted task",
    description="Recover a deleted task from its tombstone (FR-063). "
    "Restores original ID, timestamps, and subtasks. "
    "Recovered tasks do NOT trigger achievements or affect streaks (FR-064).",
    responses={
        404: {"description": "Tombstone not found or expired"},
        409: {"description": "Original task ID collision"},
    },
)
async def recover_task(
    tombstone_id: UUID,
    user: CurrentUser,
    service: RecoveryServiceDep,
) -> DataResponse[TaskDetailResponse]:
    """T345: POST /api/v1/tasks/recover/:tombstone_id."""
    # Check recovery window
    try:
        tombstone = await service.get_tombstone(user=user, tombstone_id=tombstone_id)
    except TombstoneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Tombstone not found"},
        )

    # Verify still within recovery window (ensure timezone-aware for SQLite)
    deleted_at = tombstone.deleted_at.replace(tzinfo=UTC) if tombstone.deleted_at.tzinfo is None else tombstone.deleted_at
    recoverable_until = deleted_at + timedelta(days=RECOVERY_WINDOW_DAYS)
    if datetime.now(UTC) > recoverable_until:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Tombstone recovery window expired"},
        )

    try:
        recovered_task = await service.recover_task(
            user=user, tombstone_id=tombstone_id
        )
    except TombstoneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Tombstone not found"},
        )
    except TaskIDCollisionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.CONFLICT,
                "message": "Original task ID already exists",
            },
        )

    # Build response
    task_response = TaskDetailResponse(
        id=recovered_task.id,
        title=recovered_task.title,
        description=recovered_task.description or "",
        priority=recovered_task.priority,
        due_date=recovered_task.due_date,
        estimated_duration=recovered_task.estimated_duration,
        focus_time_seconds=recovered_task.focus_time_seconds,
        completed=recovered_task.completed,
        completed_at=recovered_task.completed_at,
        completed_by=recovered_task.completed_by,
        hidden=recovered_task.hidden,
        archived=recovered_task.archived,
        template_id=recovered_task.template_id if hasattr(recovered_task, "template_id") else None,
        version=recovered_task.version,
        created_at=recovered_task.created_at,
        updated_at=recovered_task.updated_at,
        subtasks=[],
        reminders=[],
    )

    return DataResponse(data=task_response)
