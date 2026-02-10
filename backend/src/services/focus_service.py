"""Focus service for focus mode tracking.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)

T309: FocusService.start_session
T310: FocusService.end_session with duration calculation
T311: Focus completion check (delegated to AchievementService.is_focus_completion)
"""

import logging
from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.focus import FocusSession
from src.models.task import TaskInstance
from src.models.user import User


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class FocusServiceError(Exception):
    """Base exception for focus service errors."""

    pass


class FocusSessionActiveError(FocusServiceError):
    """Raised when trying to start a session that already exists for the task."""

    pass


class FocusSessionNotFoundError(FocusServiceError):
    """Raised when no active session exists for the task."""

    pass


class FocusTaskNotFoundError(FocusServiceError):
    """Raised when the task is not found or user doesn't own it."""

    pass


# =============================================================================
# FOCUS SERVICE
# =============================================================================


class FocusService:
    """Service for focus mode session management.

    Handles:
    - Starting focus sessions on tasks
    - Ending sessions and accumulating focus_time_seconds
    - Focus completion detection (FR-045)
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    async def start_session(
        self, user: User, task_id: UUID
    ) -> FocusSession:
        """Start a focus session for a task.

        T309: FocusService.start_session

        Args:
            user: The session owner
            task_id: The task to focus on

        Returns:
            The created FocusSession

        Raises:
            FocusTaskNotFoundError: If task not found or user doesn't own it
            FocusSessionActiveError: If an active session already exists for this task
        """
        # Verify task exists and user owns it
        task = await self._get_user_task(user, task_id)

        # Check for existing active session on this task
        active = await self._get_active_session(user.id, task_id)
        if active is not None:
            raise FocusSessionActiveError(
                f"Active focus session already exists for task {task_id}"
            )

        now = datetime.now(UTC)
        focus_session = FocusSession(
            id=uuid4(),
            user_id=user.id,
            task_id=task_id,
            started_at=now,
            ended_at=None,
            duration_seconds=None,
        )

        self.session.add(focus_session)
        await self.session.flush()
        await self.session.refresh(focus_session)

        logger.info(
            f"Focus session started: user={user.id}, task={task_id}, "
            f"session={focus_session.id}"
        )

        return focus_session

    async def end_session(
        self, user: User, task_id: UUID
    ) -> FocusSession:
        """End an active focus session and accumulate time.

        T310: FocusService.end_session with duration calculation

        Args:
            user: The session owner
            task_id: The task to end focus for

        Returns:
            The ended FocusSession with duration

        Raises:
            FocusSessionNotFoundError: If no active session exists
        """
        # Find active session
        active = await self._get_active_session(user.id, task_id)
        if active is None:
            raise FocusSessionNotFoundError(
                f"No active focus session found for task {task_id}"
            )

        now = datetime.now(UTC)
        duration = int((now - active.started_at).total_seconds())

        # Ensure non-negative duration
        duration = max(0, duration)

        active.ended_at = now
        active.duration_seconds = duration

        self.session.add(active)

        # Accumulate focus time on the task
        task = await self._get_user_task(user, task_id)
        task.focus_time_seconds = (task.focus_time_seconds or 0) + duration
        self.session.add(task)

        await self.session.flush()
        await self.session.refresh(active)

        logger.info(
            f"Focus session ended: user={user.id}, task={task_id}, "
            f"duration={duration}s, total_focus={task.focus_time_seconds}s"
        )

        return active

    def is_focus_completion(self, task: TaskInstance) -> bool:
        """Check if a completed task qualifies as a focus completion.

        T311: Focus completion check (FR-045)

        A task is a focus completion if:
        - It has an estimated duration
        - User spent >=50% of the estimated time in focus mode

        Args:
            task: The completed task

        Returns:
            True if task qualifies as focus completion
        """
        if task.estimated_duration is None:
            return False

        if task.focus_time_seconds is None or task.focus_time_seconds == 0:
            return False

        # Convert estimated duration (minutes) to seconds
        estimated_seconds = task.estimated_duration * 60

        # Calculate percentage
        focus_percentage = task.focus_time_seconds / estimated_seconds

        return focus_percentage >= 0.5

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    async def _get_user_task(self, user: User, task_id: UUID) -> TaskInstance:
        """Get a task owned by the user.

        Args:
            user: The requesting user
            task_id: The task ID

        Returns:
            The TaskInstance

        Raises:
            FocusTaskNotFoundError: If task not found or user doesn't own it
        """
        query = select(TaskInstance).where(
            TaskInstance.id == task_id,
            TaskInstance.user_id == user.id,
            TaskInstance.hidden == False,
        )
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise FocusTaskNotFoundError(f"Task {task_id} not found")

        return task

    async def _get_active_session(
        self, user_id: UUID, task_id: UUID
    ) -> FocusSession | None:
        """Get the active focus session for a user's task.

        Args:
            user_id: The user ID
            task_id: The task ID

        Returns:
            The active FocusSession, or None if no active session
        """
        query = select(FocusSession).where(
            FocusSession.user_id == user_id,
            FocusSession.task_id == task_id,
            FocusSession.ended_at == None,  # noqa: E711
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_focus_service(session: AsyncSession, settings: Settings) -> FocusService:
    """Get a FocusService instance."""
    return FocusService(session, settings)
