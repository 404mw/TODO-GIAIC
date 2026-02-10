"""Activity service for activity logging and querying.

Phase 20: Activity Logging & Observability (FR-052 to FR-054)

T359: ActivityService.log_event for all entity types
T361: Ensure source field tracked (user, AI, system) in all log entries
"""

import logging
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.activity import ActivityLog
from src.schemas.enums import ActivitySource, EntityType


logger = logging.getLogger(__name__)


# =============================================================================
# ACTIVITY SERVICE (T359)
# =============================================================================


class ActivityService:
    """Service for activity logging and querying.

    Handles:
    - Direct activity logging for all entity types (FR-052)
    - Source field tracking (user/ai/system) (FR-054)
    - Activity log querying for audit/debugging
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # LOG EVENT (T359, FR-052)
    # =========================================================================

    async def log_event(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
        action: str,
        source: ActivitySource,
        metadata: dict | None = None,
        request_id: UUID | None = None,
    ) -> ActivityLog:
        """Log an activity event for any entity type.

        T359: ActivityService.log_event for all entity types (FR-052)
        T361: Source field tracked (user, AI, system) in all log entries (FR-054)

        Args:
            user_id: User who triggered or is associated with the event
            entity_type: Type of entity (task, subtask, note, reminder, etc.)
            entity_id: ID of the affected entity
            action: Action performed (e.g., 'task_created', 'note_converted')
            source: Who initiated the action (user, ai, system) (FR-054)
            metadata: Additional context about the action
            request_id: Request correlation ID for tracing

        Returns:
            The created ActivityLog entry
        """
        activity = ActivityLog(
            id=uuid4(),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            source=source,
            extra_data=metadata or {},
            request_id=request_id,
            created_at=datetime.now(UTC),
        )

        self.session.add(activity)
        await self.session.flush()

        logger.debug(
            f"Activity logged: {action} on {entity_type.value}/{entity_id} "
            f"by {source.value} (user={user_id})"
        )

        return activity

    # =========================================================================
    # QUERY ACTIVITY (T362 support)
    # =========================================================================

    async def list_activities(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 25,
        entity_type: EntityType | None = None,
        action: str | None = None,
        source: ActivitySource | None = None,
        entity_id: UUID | None = None,
    ) -> tuple[Sequence[ActivityLog], int]:
        """List activity logs with filters and pagination.

        Args:
            user_id: Filter by user
            offset: Pagination offset
            limit: Items per page (max 100)
            entity_type: Filter by entity type
            action: Filter by action
            source: Filter by source (user/ai/system)
            entity_id: Filter by specific entity

        Returns:
            Tuple of (activities, total_count)
        """
        query = select(ActivityLog).where(ActivityLog.user_id == user_id)

        if entity_type is not None:
            query = query.where(ActivityLog.entity_type == entity_type)

        if action is not None:
            query = query.where(ActivityLog.action == action)

        if source is not None:
            query = query.where(ActivityLog.source == source)

        if entity_id is not None:
            query = query.where(ActivityLog.entity_id == entity_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering (newest first)
        query = (
            query.order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return activities, total

    async def get_activity_by_entity(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
        limit: int = 50,
    ) -> Sequence[ActivityLog]:
        """Get activity history for a specific entity.

        Args:
            user_id: User context
            entity_type: Entity type
            entity_id: Entity ID
            limit: Max entries to return

        Returns:
            Activity log entries for the entity
        """
        query = (
            select(ActivityLog)
            .where(
                ActivityLog.user_id == user_id,
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id,
            )
            .order_by(ActivityLog.created_at.desc())
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        return result.scalars().all()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_activity_service(session: AsyncSession, settings: Settings) -> ActivityService:
    """Get an ActivityService instance."""
    return ActivityService(session, settings)
