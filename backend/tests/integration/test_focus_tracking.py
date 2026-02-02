"""Integration tests for focus mode tracking.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)

T314: Integration test for focus tracking lifecycle.
Tests the full flow: start session -> end session -> verify accumulation -> achievement check.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import UserTier
from src.services.achievement_service import AchievementService, get_achievement_service
from src.services.focus_service import (
    FocusService,
    FocusSessionActiveError,
    FocusSessionNotFoundError,
    get_focus_service,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def focus_user(db_session: AsyncSession) -> User:
    """Create a test user for focus integration tests."""
    user = User(
        id=uuid4(),
        google_id=f"google-focus-int-{uuid4()}",
        email=f"focus-int-{uuid4()}@example.com",
        name="Focus Integration User",
        tier=UserTier.FREE,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def estimated_task(
    db_session: AsyncSession, focus_user: User
) -> TaskInstance:
    """Create a task with 20-minute estimated duration."""
    task = TaskInstance(
        id=uuid4(),
        user_id=focus_user.id,
        title="Integration Focus Task",
        description="Task for integration testing",
        estimated_duration=20,  # 20 minutes
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


@pytest.fixture
def achievement_service(
    db_session: AsyncSession, settings: Settings
) -> AchievementService:
    """Create an AchievementService instance."""
    return get_achievement_service(db_session, settings)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestFocusTrackingLifecycle:
    """Integration test for focus tracking end-to-end flow."""

    @pytest.mark.asyncio
    async def test_full_focus_session_lifecycle(
        self,
        focus_service: FocusService,
        focus_user: User,
        estimated_task: TaskInstance,
        db_session: AsyncSession,
    ):
        """Full lifecycle: start -> accumulate -> end -> verify total."""
        # 1. Start focus session
        session = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        assert session.is_active
        assert session.started_at is not None

        # 2. Simulate 12 minutes of focus by backdating
        session.started_at = datetime.now(UTC) - timedelta(minutes=12)
        db_session.add(session)
        await db_session.flush()

        # 3. End session
        ended_session = await focus_service.end_session(
            user=focus_user, task_id=estimated_task.id
        )
        assert not ended_session.is_active
        assert ended_session.duration_seconds is not None
        assert ended_session.duration_seconds >= 700  # ~12 min

        # 4. Verify focus time accumulated on task
        await db_session.refresh(estimated_task)
        assert estimated_task.focus_time_seconds >= 700

    @pytest.mark.asyncio
    async def test_focus_completion_threshold_in_context(
        self,
        focus_service: FocusService,
        achievement_service: AchievementService,
        focus_user: User,
        estimated_task: TaskInstance,
        db_session: AsyncSession,
    ):
        """Focus completion counted when >=50% of estimate achieved.

        Task has 20 min estimate = 1200 seconds.
        50% threshold = 600 seconds (10 minutes).
        """
        # Start and simulate 11 minutes of focus (above threshold)
        session = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        session.started_at = datetime.now(UTC) - timedelta(minutes=11)
        db_session.add(session)
        await db_session.flush()

        await focus_service.end_session(
            user=focus_user, task_id=estimated_task.id
        )

        # Verify task qualifies as focus completion
        await db_session.refresh(estimated_task)
        assert focus_service.is_focus_completion(estimated_task) is True

        # Verify achievement service also agrees
        assert achievement_service.is_focus_completion(estimated_task) is True

    @pytest.mark.asyncio
    async def test_below_threshold_not_counted(
        self,
        focus_service: FocusService,
        focus_user: User,
        estimated_task: TaskInstance,
        db_session: AsyncSession,
    ):
        """Focus time below 50% should NOT count as focus completion."""
        # Start and simulate 5 minutes of focus (below threshold)
        session = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        session.started_at = datetime.now(UTC) - timedelta(minutes=5)
        db_session.add(session)
        await db_session.flush()

        await focus_service.end_session(
            user=focus_user, task_id=estimated_task.id
        )

        await db_session.refresh(estimated_task)
        assert focus_service.is_focus_completion(estimated_task) is False

    @pytest.mark.asyncio
    async def test_multiple_sessions_accumulate_to_threshold(
        self,
        focus_service: FocusService,
        focus_user: User,
        estimated_task: TaskInstance,
        db_session: AsyncSession,
    ):
        """Multiple shorter sessions can accumulate past 50% threshold."""
        # Session 1: 4 minutes
        s1 = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        s1.started_at = datetime.now(UTC) - timedelta(minutes=4)
        db_session.add(s1)
        await db_session.flush()
        await focus_service.end_session(user=focus_user, task_id=estimated_task.id)

        # Session 2: 4 minutes
        s2 = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        s2.started_at = datetime.now(UTC) - timedelta(minutes=4)
        db_session.add(s2)
        await db_session.flush()
        await focus_service.end_session(user=focus_user, task_id=estimated_task.id)

        # Session 3: 4 minutes
        s3 = await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )
        s3.started_at = datetime.now(UTC) - timedelta(minutes=4)
        db_session.add(s3)
        await db_session.flush()
        await focus_service.end_session(user=focus_user, task_id=estimated_task.id)

        # Total: ~12 minutes = 720s, threshold is 600s (50% of 1200s)
        await db_session.refresh(estimated_task)
        assert estimated_task.focus_time_seconds >= 700
        assert focus_service.is_focus_completion(estimated_task) is True

    @pytest.mark.asyncio
    async def test_concurrent_session_prevented(
        self,
        focus_service: FocusService,
        focus_user: User,
        estimated_task: TaskInstance,
    ):
        """Cannot have two active sessions on the same task."""
        await focus_service.start_session(
            user=focus_user, task_id=estimated_task.id
        )

        with pytest.raises(FocusSessionActiveError):
            await focus_service.start_session(
                user=focus_user, task_id=estimated_task.id
            )

    @pytest.mark.asyncio
    async def test_end_without_start_fails(
        self,
        focus_service: FocusService,
        focus_user: User,
        estimated_task: TaskInstance,
    ):
        """Ending a non-existent session raises error."""
        with pytest.raises(FocusSessionNotFoundError):
            await focus_service.end_session(
                user=focus_user, task_id=estimated_task.id
            )
