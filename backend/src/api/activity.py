"""Activity log API endpoints.

Phase 20: Activity Logging & Observability (FR-052 to FR-054)

T362: Implement GET /api/v1/activity (user-scoped) for audit/debugging
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.dependencies import (
    CurrentUser,
    DBSession,
    get_settings,
)
from src.schemas.common import PaginatedResponse, PaginationMeta
from src.schemas.enums import ActivitySource, EntityType
from src.services.activity_service import ActivityService


router = APIRouter(prefix="/activity", tags=["activity"])


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class ActivityLogResponse(BaseModel):
    """Activity log entry response."""

    id: UUID = Field(description="Log entry ID")
    user_id: UUID = Field(description="User who performed the action")
    entity_type: EntityType = Field(description="Target entity type")
    entity_id: UUID = Field(description="Target entity ID")
    action: str = Field(description="Action performed")
    source: ActivitySource = Field(description="Who initiated (user/ai/system)")
    metadata: dict = Field(default_factory=dict, description="Action-specific data")
    created_at: datetime = Field(description="When the action occurred (UTC)")


class ActivityListResponse(PaginatedResponse[ActivityLogResponse]):
    """Paginated activity log list response."""

    pass


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_activity_service(
    db: DBSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ActivityService:
    """Get ActivityService instance."""
    return ActivityService(db, settings)


ActivityServiceDep = Annotated[ActivityService, Depends(get_activity_service)]


# =============================================================================
# T362: GET /api/v1/activity
# =============================================================================


@router.get(
    "",
    response_model=ActivityListResponse,
    summary="List activity logs",
    description="Get paginated activity logs for the authenticated user. "
    "Supports filtering by entity type, action, and source.",
)
async def list_activities(
    user: CurrentUser,
    service: ActivityServiceDep,
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=25, ge=1, le=100, description="Items per page"),
    entity_type: EntityType | None = Query(
        default=None, description="Filter by entity type"
    ),
    action: str | None = Query(default=None, description="Filter by action"),
    source: ActivitySource | None = Query(
        default=None, description="Filter by source (user/ai/system)"
    ),
    entity_id: UUID | None = Query(
        default=None, description="Filter by specific entity ID"
    ),
) -> ActivityListResponse:
    """List activity logs for the authenticated user.

    T362: GET /api/v1/activity (user-scoped) for audit/debugging

    Returns paginated activity log entries with optional filtering.
    Only returns activity for the authenticated user (user-scoped).
    """
    activities, total = await service.list_activities(
        user_id=user.id,
        offset=offset,
        limit=limit,
        entity_type=entity_type,
        action=action,
        source=source,
        entity_id=entity_id,
    )

    return ActivityListResponse(
        data=[
            ActivityLogResponse(
                id=a.id,
                user_id=a.user_id,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                action=a.action,
                source=a.source,
                metadata=a.extra_data,
                created_at=a.created_at,
            )
            for a in activities
        ],
        pagination=PaginationMeta(
            offset=offset,
            limit=limit,
            total=total,
            has_more=(offset + limit) < total,
        ),
    )
