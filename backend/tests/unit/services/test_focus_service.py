"""Unit tests for FocusService.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)

T307: Test focus time accumulates in task.focus_time_seconds
T308: Test focus completion counted when 50%+ of estimate
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import UserTier
from src.services.focus_service import (
    FocusService,
    FocusServiceError,
    FocusSessionActiveError,
    FocusSessionNotFoundError,
    get_focus_service,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def free_user(db_session: AsyncSession) -> User:
    """Create a free tier test user."""
    user = User(
        id=uuid4(),
        google_id=f"google-focus-{uuid4()}",
        email=f"focus-{uuid4()}@example.com",
        name="Focus User",
        tier=UserTier.FREE,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def task_with_estimate(
    db_session: AsyncSession, free_user: User
) -> TaskInstance:
    """Create a task with a 30-minute estimated duration."""
    task = TaskInstance(
        id=uuid4(),
        user_id=free_user.id,
        title="Focus Test Task",
        description="A task for focus testing",
        estimated_duration=30,  # 30 minutes
        focus_time_seconds=0,
        completed=False,
        hidden=False,
        archived=False,
        version=1,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def task_no_estimate(
    db_session: AsyncSession, free_user: User
) -> TaskInstance:
    """Create a task without an estimated duration."""
    task = TaskInstance(
        id=uuid4(),
        user_id=free_user.id,
        title="No Estimate Task",
        description="A task without time estimate",
        estimated_duration=None,
        focus_time_seconds=0,
        completed=False,
        hidden=False,
        archived=False,
        version=1,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest.fixture
def focus_service(db_session: AsyncSession, settings: Settings) -> FocusService:
    """Create a FocusService instance."""
    return get_focus_service(db_session, settings)


# =============================================================================
# T307: FOCUS TIME ACCUMULATION TESTS
# =============================================================================


class TestFocusTimeAccumulation:
    """T307: Test focus time accumulates in task.focus_time_seconds."""

    @pytest.mark.asyncio
    async def test_start_session_records_start_time(
        self,
        focus_service: FocusService,
        free_user: User,
        task_with_estimate: TaskInstance,
    ):
        """Starting a focus session should record the start time."""
        session = await focus_service.start_session(
            user=free_user, task_id=task_with_estimate.id
        )

        assert session.task_id == task_with_estimate.id
        assert session.user_id == free_user.id
        assert session.started_at is not None
        assert session.ended_at is None

    @pytest.mark.asyncio
    async def test_end_session_accumulates_focus_time(
        self,
        focus_service: FocusService,
        free_user: User,
        task_with_estimate: TaskInstance,
        db_session: AsyncSession,
    ):
        """Ending a focus session should add duration to task.focus_time_seconds."""
        # Start session
        session = await focus_service.start_session(
            user=free_user, task_id=task_with_estimate.id
        )

        # Manually backdate started_at to simulate 10 minutes of focus
        session.started_at = datetime.now(UTC) - timedelta(minutes=10)
        db_session.add(session)
        await db_session.flush()

        # End session
        result = await focus_service.end_session(
            user=free_user, task_id=task_with_estimate.id
        )

        # Focus time should be approximately 600 seconds (10 minutes)
        await db_session.refresh(task_with_estimate)
        assert task_with_estimate.focus_time_seconds >= 590  # Allow small timing variance
        assert task_with_estimate.focus_time_seconds <= 620
        assert result.ended_at is not None

    @pytest.mark.asyncio
    async def test_multiple_sessions_accumulate(
        self,
        focus_service: FocusService,
        free_user: User,
        task_with_estimate: TaskInstance,
        db_session: AsyncSession,
    ):
        """Multiple focus sessions should accumulate total time."""
        # First session: 5 minutes
        session1 = await focus_service.start_session(
            user=free_user, task_id=task_with_estimate.id
        )
        session1.started_at = datetime.now(UTC) - timedelta(minutes=5)
        db_session.add(session1)
        await db_session.flush()
        await focus_service.end_session(user=free_user, task_id=task_with_estimate.id)

        # Second session: 10 minutes
        session2 = await focus_service.start_session(
            user=free_user, task_id=task_with_estimate.id
        )
        session2.started_at = datetime.now(UTC) - timedelta(minutes=10)
        db_session.add(session2)
        await db_session.flush()
        await focus_service.end_session(user=free_user, task_id=task_with_estimate.id)

        # Total should be ~15 minutes = 900 seconds
        await db_session.refresh(task_with_estimate)
        assert task_with_estimate.focus_time_seconds >= 880
        assert task_with_estimate.focus_time_seconds <= 920

    @pytest.mark.asyncio
    async def test_cannot_start_duplicate_session(
        self,
        focus_service: FocusService,
        free_user: User,
        task_with_estimate: TaskInstance,
    ):
        """Cannot start a new session if one is already active for the task."""
        await focus_service.start_session(
            user=free_user, task_id=task_with_estimate.id
        )

        with pytest.raises(FocusSessionActiveError):
            await focus_service.start_session(
                user=free_user, task_id=task_with_estimate.id
            )

    @pytest.mark.asyncio
    async def test_end_session_without_start_raises_error(
        self,
        focus_service: FocusService,
        free_user: User,
        task_with_estimate: TaskInstance,
    ):
        """Ending a session that doesn't exist should raise an error."""
        with pytest.raises(FocusSessionNotFoundError):
            await focus_service.end_session(
                user=free_user, task_id=task_with_estimate.id
            )


# =============================================================================
# T308: FOCUS COMPLETION THRESHOLD TESTS
# =============================================================================


class TestFocusCompletionThreshold:
    """T308: Test focus completion counted when 50%+ of estimate (FR-045)."""

    @pytest.mark.asyncio
    async def test_focus_completion_at_50_percent(
        self,
        focus_service: FocusService,
        task_with_estimate: TaskInstance,
    ):
        """Task with ≥50% focus time should count as focus completion.

        Task has 30 min estimate = 1800 seconds.
        50% = 900 seconds.
        """
        task_with_estimate.focus_time_seconds = 900  # Exactly 50%
        assert focus_service.is_focus_completion(task_with_estimate) is True

    @pytest.mark.asyncio
    async def test_focus_completion_above_50_percent(
        self,
        focus_service: FocusService,
        task_with_estimate: TaskInstance,
    ):
        """Task with >50% focus time should count as focus completion."""
        task_with_estimate.focus_time_seconds = 1200  # 67%
        assert focus_service.is_focus_completion(task_with_estimate) is True

    @pytest.mark.asyncio
    async def test_focus_completion_below_50_percent(
        self,
        focus_service: FocusService,
        task_with_estimate: TaskInstance,
    ):
        """Task with <50% focus time should NOT count as focus completion."""
        task_with_estimate.focus_time_seconds = 600  # 33%
        assert focus_service.is_focus_completion(task_with_estimate) is False

    @pytest.mark.asyncio
    async def test_focus_completion_no_estimate(
        self,
        focus_service: FocusService,
        task_no_estimate: TaskInstance,
    ):
        """Task without estimated duration cannot be a focus completion."""
        task_no_estimate.focus_time_seconds = 1800
        assert focus_service.is_focus_completion(task_no_estimate) is False

    @pytest.mark.asyncio
    async def test_focus_completion_zero_focus_time(
        self,
        focus_service: FocusService,
        task_with_estimate: TaskInstance,
    ):
        """Task with zero focus time is not a focus completion."""
        task_with_estimate.focus_time_seconds = 0
        assert focus_service.is_focus_completion(task_with_estimate) is False

    @pytest.mark.asyncio
    async def test_focus_completion_100_percent(
        self,
        focus_service: FocusService,
        task_with_estimate: TaskInstance,
    ):
        """Task with 100% focus time is a focus completion."""
        task_with_estimate.focus_time_seconds = 1800  # Full 30 minutes
        assert focus_service.is_focus_completion(task_with_estimate) is True
