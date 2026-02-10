"""Focus mode API endpoints.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)

T312: POST /api/v1/focus/start
T313: POST /api/v1/focus/end
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import DataResponse, ErrorCode
from src.schemas.focus import (
    FocusEndRequest,
    FocusSessionResponse,
    FocusStartRequest,
)
from src.services.focus_service import (
    FocusService,
    FocusSessionActiveError,
    FocusSessionNotFoundError,
    FocusTaskNotFoundError,
)

router = APIRouter(prefix="/focus", tags=["focus"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_focus_service(
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> FocusService:
    """Get FocusService instance."""
    return FocusService(db, settings)


FocusServiceDep = Annotated[FocusService, Depends(get_focus_service)]


# =============================================================================
# FOCUS ENDPOINTS
# =============================================================================


@router.post(
    "/start",
    response_model=DataResponse[FocusSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start focus session",
    description="Start a focus session for a task. Only one active session per task allowed.",
)
async def start_focus_session(
    data: FocusStartRequest,
    user: CurrentUser,
    service: FocusServiceDep,
) -> DataResponse[FocusSessionResponse]:
    """T312: POST /api/v1/focus/start."""
    try:
        session = await service.start_session(user=user, task_id=data.task_id)
    except FocusTaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    except FocusSessionActiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": ErrorCode.CONFLICT,
                "message": "Active focus session already exists for this task",
            },
        )

    response = FocusSessionResponse(
        id=session.id,
        task_id=session.task_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
    )

    return DataResponse(data=response)


@router.post(
    "/end",
    response_model=DataResponse[FocusSessionResponse],
    summary="End focus session",
    description="End an active focus session. Duration is accumulated to the task's focus_time_seconds.",
)
async def end_focus_session(
    data: FocusEndRequest,
    user: CurrentUser,
    service: FocusServiceDep,
) -> DataResponse[FocusSessionResponse]:
    """T313: POST /api/v1/focus/end."""
    try:
        session = await service.end_session(user=user, task_id=data.task_id)
    except FocusSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": ErrorCode.NOT_FOUND,
                "message": "No active focus session found for this task",
            },
        )
    except FocusTaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )

    response = FocusSessionResponse(
        id=session.id,
        task_id=session.task_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
    )

    return DataResponse(data=response)
