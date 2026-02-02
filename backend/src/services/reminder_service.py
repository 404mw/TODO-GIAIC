"""Reminder service for task reminder management.

Phase 8: User Story 8 - Reminder System (Priority: P3)
Implements FR-025 to FR-028.

T183: ReminderService.create_reminder with scheduled_at calculation
T184: ReminderService.update_reminder with recalculation (FR-026)
T185: ReminderService.delete_reminder
T186: Reminder recalculation on task due date change (FR-026)
T187: Skip past reminders flag for recovered tasks (FR-027)
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import ReminderType
from src.schemas.reminder import ReminderCreate, ReminderUpdate


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class ReminderServiceError(Exception):
    """Base exception for reminder service errors."""

    pass


class ReminderNotFoundError(ReminderServiceError):
    """Raised when reminder is not found or user doesn't have access."""

    pass


class ReminderLimitExceededError(ReminderServiceError):
    """Raised when user has reached reminder limit for a task (409)."""

    pass


class TaskNoDueDateError(ReminderServiceError):
    """Raised when creating relative reminder for task without due date (400)."""

    pass


class TaskNotFoundError(ReminderServiceError):
    """Raised when task is not found."""

    pass


# =============================================================================
# CONSTANTS
# =============================================================================

MAX_REMINDERS_PER_TASK = 5


# =============================================================================
# REMINDER SERVICE
# =============================================================================


class ReminderService:
    """Service for reminder operations.

    Handles:
    - Reminder CRUD
    - Scheduled time calculation (before/after/absolute)
    - Reminder limit enforcement (max 5 per task)
    - Recalculation when task due date changes
    - Skip past reminders for recovered tasks
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # REMINDER CRUD (T183-T185)
    # =========================================================================

    async def create_reminder(
        self,
        user: User,
        task_id: UUID,
        data: ReminderCreate,
    ) -> Reminder:
        """Create a new reminder with scheduled_at calculation.

        T183: ReminderService.create_reminder with scheduled_at calculation

        Args:
            user: The reminder owner
            task_id: The task to attach the reminder to
            data: Reminder creation data

        Returns:
            The created Reminder

        Raises:
            TaskNotFoundError: If task not found or user doesn't own it
            TaskNoDueDateError: If relative reminder and task has no due date
            ReminderLimitExceededError: If reminder limit (5) reached for task
        """
        # Verify task exists and user owns it
        task = await self._get_task_for_user(user.id, task_id)

        # FR-025: Check reminder limit (max 5 per task)
        reminder_count = await self._get_reminder_count_for_task(task_id)
        if reminder_count >= MAX_REMINDERS_PER_TASK:
            raise ReminderLimitExceededError(
                f"Reminder limit of {MAX_REMINDERS_PER_TASK} reached for this task"
            )

        # Calculate scheduled_at based on reminder type
        scheduled_at = self._calculate_scheduled_at(
            reminder_type=data.type,
            offset_minutes=data.offset_minutes,
            provided_scheduled_at=data.scheduled_at,
            task_due_date=task.due_date,
        )

        # Create the reminder
        reminder = Reminder(
            id=uuid4(),
            task_id=task_id,
            user_id=user.id,
            type=data.type,
            offset_minutes=data.offset_minutes,
            scheduled_at=scheduled_at,
            method=data.method,
            fired=False,
            fired_at=None,
        )

        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)

        return reminder

    async def get_reminder(
        self,
        user: User,
        reminder_id: UUID,
    ) -> Reminder:
        """Get a reminder by ID with ownership check.

        Args:
            user: The requesting user
            reminder_id: The reminder ID to retrieve

        Returns:
            The Reminder

        Raises:
            ReminderNotFoundError: If reminder not found or user doesn't own it
        """
        query = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user.id,
        )

        result = await self.session.execute(query)
        reminder = result.scalar_one_or_none()

        if reminder is None:
            raise ReminderNotFoundError(f"Reminder {reminder_id} not found")

        return reminder

    async def list_reminders_for_task(
        self,
        user: User,
        task_id: UUID,
    ) -> Sequence[Reminder]:
        """List all reminders for a task.

        Args:
            user: The requesting user
            task_id: The task ID

        Returns:
            List of Reminders
        """
        # Verify task ownership
        await self._get_task_for_user(user.id, task_id)

        query = (
            select(Reminder)
            .where(Reminder.task_id == task_id)
            .order_by(Reminder.scheduled_at.asc())
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_reminder(
        self,
        user: User,
        reminder_id: UUID,
        data: ReminderUpdate,
    ) -> Reminder:
        """Update a reminder with scheduled_at recalculation.

        T184: ReminderService.update_reminder with recalculation (FR-026)

        Args:
            user: The requesting user
            reminder_id: The reminder ID to update
            data: Update data

        Returns:
            The updated Reminder

        Raises:
            ReminderNotFoundError: If reminder not found
        """
        reminder = await self.get_reminder(user=user, reminder_id=reminder_id)

        # Update method if provided
        if data.method is not None:
            reminder.method = data.method

        # Update offset_minutes and recalculate scheduled_at
        if data.offset_minutes is not None:
            reminder.offset_minutes = data.offset_minutes

            # Need to get task to recalculate
            task = await self._get_task_by_id(reminder.task_id)

            if reminder.type in (ReminderType.BEFORE, ReminderType.AFTER):
                reminder.scheduled_at = self._calculate_scheduled_at(
                    reminder_type=reminder.type,
                    offset_minutes=data.offset_minutes,
                    provided_scheduled_at=None,
                    task_due_date=task.due_date,
                )

        # Update scheduled_at directly for absolute reminders
        if data.scheduled_at is not None and reminder.type == ReminderType.ABSOLUTE:
            reminder.scheduled_at = data.scheduled_at

        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)

        return reminder

    async def delete_reminder(
        self,
        user: User,
        reminder_id: UUID,
    ) -> None:
        """Delete a reminder.

        T185: ReminderService.delete_reminder

        Args:
            user: The requesting user
            reminder_id: The reminder ID to delete

        Raises:
            ReminderNotFoundError: If reminder not found
        """
        reminder = await self.get_reminder(user=user, reminder_id=reminder_id)

        await self.session.delete(reminder)
        await self.session.flush()

    # =========================================================================
    # RECALCULATION (T186)
    # =========================================================================

    async def recalculate_reminders_for_task(
        self,
        task_id: UUID,
        new_due_date: datetime,
    ) -> Sequence[Reminder]:
        """Recalculate relative reminders when task due date changes.

        T186: Reminder recalculation on task due date change (FR-026)

        Only 'before' and 'after' reminders are recalculated.
        'absolute' reminders are NOT affected.

        Args:
            task_id: The task ID
            new_due_date: The new due date

        Returns:
            List of all reminders for the task (recalculated)
        """
        # Get all reminders for the task
        query = select(Reminder).where(Reminder.task_id == task_id)
        result = await self.session.execute(query)
        reminders = result.scalars().all()

        for reminder in reminders:
            # Only recalculate relative reminders
            if reminder.type == ReminderType.BEFORE and reminder.offset_minutes:
                reminder.scheduled_at = new_due_date - timedelta(
                    minutes=reminder.offset_minutes
                )
                self.session.add(reminder)
            elif reminder.type == ReminderType.AFTER and reminder.offset_minutes:
                reminder.scheduled_at = new_due_date + timedelta(
                    minutes=reminder.offset_minutes
                )
                self.session.add(reminder)
            # Absolute reminders are NOT changed

        await self.session.flush()

        # Refresh all reminders
        for reminder in reminders:
            await self.session.refresh(reminder)

        return reminders

    # =========================================================================
    # RECOVERY HANDLING (T187)
    # =========================================================================

    async def skip_past_reminders_for_task(
        self,
        task_id: UUID,
        skip_before: datetime,
    ) -> int:
        """Skip past reminders for a recovered task.

        T187: Skip past reminders flag for recovered tasks (FR-027)

        Marks all unfired reminders with scheduled_at < skip_before as fired
        to prevent them from firing.

        Args:
            task_id: The task ID
            skip_before: Skip reminders scheduled before this time

        Returns:
            Number of reminders skipped
        """
        # Get unfired reminders that are past due
        query = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.fired == False,
            Reminder.scheduled_at < skip_before,
        )

        result = await self.session.execute(query)
        reminders = result.scalars().all()

        skipped_count = 0
        for reminder in reminders:
            reminder.fired = True
            reminder.fired_at = datetime.now(UTC)  # Mark when skipped
            self.session.add(reminder)
            skipped_count += 1

        await self.session.flush()

        return skipped_count

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _calculate_scheduled_at(
        self,
        reminder_type: ReminderType,
        offset_minutes: int | None,
        provided_scheduled_at: datetime | None,
        task_due_date: datetime | None,
    ) -> datetime:
        """Calculate scheduled_at based on reminder type.

        Args:
            reminder_type: The type of reminder
            offset_minutes: Minutes offset for relative reminders
            provided_scheduled_at: Provided time for absolute reminders
            task_due_date: Task's due date for relative reminders

        Returns:
            Calculated scheduled_at datetime

        Raises:
            TaskNoDueDateError: If relative reminder and task has no due date
        """
        if reminder_type == ReminderType.ABSOLUTE:
            if provided_scheduled_at is None:
                raise ValueError("scheduled_at required for absolute reminder")
            # Strip tzinfo for DB storage consistency (naive UTC)
            if provided_scheduled_at.tzinfo is not None:
                return provided_scheduled_at.replace(tzinfo=None)
            return provided_scheduled_at

        # For relative reminders (before/after), we need due_date
        if task_due_date is None:
            raise TaskNoDueDateError(
                "Cannot create relative reminder for task without due date"
            )

        if offset_minutes is None:
            raise ValueError("offset_minutes required for relative reminder")

        if reminder_type == ReminderType.BEFORE:
            return task_due_date - timedelta(minutes=offset_minutes)
        else:  # AFTER
            return task_due_date + timedelta(minutes=offset_minutes)

    async def _get_task_for_user(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> TaskInstance:
        """Get task ensuring user owns it.

        Args:
            user_id: The user ID
            task_id: The task ID

        Returns:
            The TaskInstance

        Raises:
            TaskNotFoundError: If task not found or user doesn't own it
        """
        query = select(TaskInstance).where(
            TaskInstance.id == task_id,
            TaskInstance.user_id == user_id,
            TaskInstance.hidden == False,
        )

        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        return task

    async def _get_task_by_id(self, task_id: UUID) -> TaskInstance:
        """Get task by ID without ownership check (for internal use).

        Args:
            task_id: The task ID

        Returns:
            The TaskInstance

        Raises:
            TaskNotFoundError: If task not found
        """
        query = select(TaskInstance).where(TaskInstance.id == task_id)

        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        return task

    async def _get_reminder_count_for_task(self, task_id: UUID) -> int:
        """Get count of reminders for a task."""
        query = select(func.count()).where(Reminder.task_id == task_id)
        result = await self.session.execute(query)
        return result.scalar() or 0


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_reminder_service(session: AsyncSession, settings: Settings) -> ReminderService:
    """Get a ReminderService instance."""
    return ReminderService(session, settings)
