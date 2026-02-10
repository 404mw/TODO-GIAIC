"""Recovery service for tombstone-based task recovery.

Phase 18: User Story 13 - Task Deletion and Recovery (FR-062 to FR-064)

T340: RecoveryService.create_tombstone with FIFO limit (FR-062)
T341: RecoveryService.recover_task (FR-063)
T342: Skip flags for achievements/streaks on recovery (FR-064)
T343: RecoveryService.list_tombstones
"""

import logging
import time
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.subtask import Subtask
from src.models.task import TaskInstance
from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.middleware.metrics import record_recovery_latency, record_recovery_operation
from src.schemas.enums import (
    CompletedBy,
    SubtaskSource,
    TaskPriority,
    TombstoneEntityType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class RecoveryServiceError(Exception):
    """Base exception for recovery service errors."""
    pass


class TombstoneNotFoundError(RecoveryServiceError):
    """Raised when tombstone is not found or user doesn't have access."""
    pass


class TaskIDCollisionError(RecoveryServiceError):
    """Raised when the original task ID already exists in the database (409)."""
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

MAX_TOMBSTONES_PER_USER = 3


# =============================================================================
# RECOVERY SERVICE
# =============================================================================


class RecoveryService:
    """Service for tombstone-based task recovery.

    Handles:
    - Listing user tombstones
    - Recovering deleted tasks from tombstones
    - Enforcing FIFO tombstone limits
    - Skip flags for achievement/streak processing

    FR-062: Max 3 tombstones per user (FIFO)
    FR-063: Recovery restores original ID and timestamps
    FR-064: Recovered tasks do NOT trigger achievements or streaks
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # T342: Skip flags for downstream handlers (FR-064)
        self.skip_achievement_processing: bool = False
        self.skip_streak_processing: bool = False
        self.last_recovery_was_flagged: bool = False

    # -------------------------------------------------------------------------
    # T343: List tombstones
    # -------------------------------------------------------------------------

    async def list_tombstones(
        self,
        user: User,
    ) -> Sequence[DeletionTombstone]:
        """List all tombstones for a user, newest first.

        T343: RecoveryService.list_tombstones

        Args:
            user: The requesting user

        Returns:
            List of tombstones ordered by deletion time (newest first)
        """
        stmt = (
            select(DeletionTombstone)
            .where(DeletionTombstone.user_id == user.id)
            .order_by(DeletionTombstone.deleted_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # -------------------------------------------------------------------------
    # Get single tombstone
    # -------------------------------------------------------------------------

    async def get_tombstone(
        self,
        user: User,
        tombstone_id: UUID,
    ) -> DeletionTombstone:
        """Get a specific tombstone by ID with ownership check.

        Args:
            user: The requesting user
            tombstone_id: The tombstone ID to retrieve

        Returns:
            The tombstone

        Raises:
            TombstoneNotFoundError: If tombstone not found or belongs to another user
        """
        stmt = select(DeletionTombstone).where(
            DeletionTombstone.id == tombstone_id,
            DeletionTombstone.user_id == user.id,
        )
        result = await self.session.execute(stmt)
        tombstone = result.scalar_one_or_none()

        if tombstone is None:
            raise TombstoneNotFoundError(
                f"Tombstone {tombstone_id} not found or access denied"
            )

        return tombstone

    # -------------------------------------------------------------------------
    # T341: Recover task from tombstone (FR-063)
    # -------------------------------------------------------------------------

    async def recover_task(
        self,
        user: User,
        tombstone_id: UUID,
    ) -> TaskInstance:
        """Recover a deleted task from its tombstone.

        T341: RecoveryService.recover_task (FR-063)

        Restores the task with its original ID, timestamps, and subtasks.
        Sets skip flags so downstream handlers do NOT trigger achievements
        or streak updates (FR-064).

        Args:
            user: The requesting user
            tombstone_id: The tombstone to recover from

        Returns:
            The recovered TaskInstance

        Raises:
            TombstoneNotFoundError: If tombstone not found or access denied
            TaskIDCollisionError: If original task ID already exists
        """
        start_time = time.monotonic()

        tombstone = await self.get_tombstone(user=user, tombstone_id=tombstone_id)

        if tombstone.entity_type != TombstoneEntityType.TASK:
            record_recovery_operation("recover", "invalid_type")
            raise RecoveryServiceError(
                f"Tombstone {tombstone_id} is not a task tombstone"
            )

        entity_data = tombstone.entity_data
        original_id = UUID(entity_data["id"])

        # Check for ID collision (FR-063)
        existing = await self.session.get(TaskInstance, original_id)
        if existing is not None:
            record_recovery_operation("recover", "collision")
            raise TaskIDCollisionError(
                f"Task with ID {original_id} already exists"
            )

        # Restore task with original data
        task = TaskInstance(
            id=original_id,
            user_id=user.id,
            title=entity_data["title"],
            description=entity_data.get("description", ""),
            priority=TaskPriority(entity_data["priority"]),
            due_date=(
                datetime.fromisoformat(entity_data["due_date"])
                if entity_data.get("due_date")
                else None
            ),
            estimated_duration=entity_data.get("estimated_duration"),
            focus_time_seconds=entity_data.get("focus_time_seconds", 0),
            completed=entity_data.get("completed", False),
            completed_at=(
                datetime.fromisoformat(entity_data["completed_at"])
                if entity_data.get("completed_at")
                else None
            ),
            completed_by=(
                CompletedBy(entity_data["completed_by"])
                if entity_data.get("completed_by")
                else None
            ),
            # Restore original created_at (FR-063)
            created_at=datetime.fromisoformat(entity_data["created_at"]),
            # Reset version to 1 on recovery
            version=1,
            hidden=False,
            archived=False,
        )

        self.session.add(task)
        await self.session.flush()

        # Restore subtasks
        for sub_data in entity_data.get("subtasks", []):
            subtask = Subtask(
                id=UUID(sub_data["id"]),
                task_id=original_id,
                title=sub_data["title"],
                completed=sub_data.get("completed", False),
                order_index=sub_data.get("order_index", 0),
                source=SubtaskSource(sub_data.get("source", "user")),
            )
            self.session.add(subtask)

        # Delete the tombstone after successful recovery
        await self.session.delete(tombstone)
        await self.session.flush()

        # T342: Set skip flags for downstream handlers (FR-064)
        self.skip_achievement_processing = True
        self.skip_streak_processing = True
        self.last_recovery_was_flagged = True

        # T347: Record recovery metrics (SC-010)
        duration = time.monotonic() - start_time
        record_recovery_operation("recover", "success")
        record_recovery_latency(duration)

        logger.info(
            "Task recovered from tombstone",
            extra={
                "user_id": str(user.id),
                "task_id": str(original_id),
                "tombstone_id": str(tombstone_id),
                "subtasks_restored": len(entity_data.get("subtasks", [])),
                "duration_seconds": round(duration, 3),
            },
        )

        await self.session.refresh(task)
        return task
