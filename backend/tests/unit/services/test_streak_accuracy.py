"""
Unit Tests: Streak Calculation Accuracy
T394: Create streak calculation test suite (SC-007)

Tests streak calculation accuracy including:
- UTC boundary handling
- Timezone considerations
- DST transitions
- Edge cases
"""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.models.achievement import UserAchievementState
from src.models.user import User
from src.schemas.enums import UserTier


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock()


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=uuid4(),
        google_id="streak_accuracy_user",
        email="streak@test.com",
        name="Streak Test User",
        tier=UserTier.FREE,
    )


@pytest.fixture
def achievement_state(test_user):
    """Create a fresh achievement state."""
    return UserAchievementState(
        id=uuid4(),
        user_id=test_user.id,
        lifetime_tasks_completed=0,
        current_streak=0,
        longest_streak=0,
        last_completion_date=None,
        focus_completions=0,
        notes_converted=0,
        unlocked_achievements=[],
    )


# =============================================================================
# T394: SC-007 – Streak Accuracy
# =============================================================================


class TestUTCBoundaryStreak:
    """Test streak calculation at UTC day boundaries."""

    @pytest.mark.asyncio
    async def test_completion_at_2359_utc(
        self, mock_session, mock_settings, achievement_state
    ):
        """Completion at 23:59 UTC counts for the current day."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        time = datetime(2026, 1, 15, 23, 59, 59, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, time)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 15)

    @pytest.mark.asyncio
    async def test_completion_at_0000_utc(
        self, mock_session, mock_settings, achievement_state
    ):
        """Completion at 00:00 UTC counts for the new day."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        time = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, time)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 16)

    @pytest.mark.asyncio
    async def test_consecutive_across_utc_midnight(
        self, mock_session, mock_settings, achievement_state
    ):
        """Completions at 23:59 and 00:01 are consecutive days."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        t1 = datetime(2026, 1, 15, 23, 59, 59, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)
        assert achievement_state.current_streak == 1

        t2 = datetime(2026, 1, 16, 0, 0, 1, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)
        assert achievement_state.current_streak == 2

    @pytest.mark.asyncio
    async def test_same_day_no_double_count(
        self, mock_session, mock_settings, achievement_state
    ):
        """Multiple completions on the same UTC day don't increment streak."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        t1 = datetime(2026, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)
        assert achievement_state.current_streak == 1

        t2 = datetime(2026, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)
        assert achievement_state.current_streak == 1  # No increment


class TestDSTTransitions:
    """Test streak handling across DST transitions.

    Note: Streaks use UTC calendar days, so DST in local timezones
    should not affect streak calculation.
    """

    @pytest.mark.asyncio
    async def test_streak_through_spring_forward(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak maintained through spring forward (US: Mar 9, 2025).

        All times are UTC so DST transition is transparent.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # March 8 (before spring forward)
        t1 = datetime(2025, 3, 8, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)
        assert achievement_state.current_streak == 1

        # March 9 (spring forward day)
        t2 = datetime(2025, 3, 9, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)
        assert achievement_state.current_streak == 2

        # March 10 (after spring forward)
        t3 = datetime(2025, 3, 10, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t3)
        assert achievement_state.current_streak == 3

    @pytest.mark.asyncio
    async def test_streak_through_fall_back(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak maintained through fall back (US: Nov 2, 2025).

        All times are UTC so DST transition is transparent.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Nov 1 (before fall back)
        t1 = datetime(2025, 11, 1, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)

        # Nov 2 (fall back day)
        t2 = datetime(2025, 11, 2, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)

        # Nov 3 (after fall back)
        t3 = datetime(2025, 11, 3, 22, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t3)

        assert achievement_state.current_streak == 3


class TestStreakResetBehavior:
    """Test streak reset edge cases."""

    @pytest.mark.asyncio
    async def test_streak_resets_after_one_missed_day(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak resets when exactly one day is missed."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Day 1
        t1 = datetime(2026, 1, 10, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)
        assert achievement_state.current_streak == 1

        # Day 2
        t2 = datetime(2026, 1, 11, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)
        assert achievement_state.current_streak == 2

        # Day 4 (skipped Day 3)
        t3 = datetime(2026, 1, 13, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t3)
        assert achievement_state.current_streak == 1  # Reset

    @pytest.mark.asyncio
    async def test_longest_streak_preserved_on_reset(
        self, mock_session, mock_settings, achievement_state
    ):
        """Longest streak is preserved when current streak resets."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Build 5-day streak
        base = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        for day in range(5):
            await service.update_streak(
                achievement_state, base + timedelta(days=day)
            )

        assert achievement_state.current_streak == 5
        assert achievement_state.longest_streak == 5

        # Break streak
        await service.update_streak(
            achievement_state, base + timedelta(days=7)
        )

        assert achievement_state.current_streak == 1
        assert achievement_state.longest_streak == 5  # Preserved

    @pytest.mark.asyncio
    async def test_longest_streak_updates_when_exceeded(
        self, mock_session, mock_settings, achievement_state
    ):
        """Longest streak updates when current exceeds it."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        base = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Build 3-day streak, break, then build 5-day streak
        for day in range(3):
            await service.update_streak(
                achievement_state, base + timedelta(days=day)
            )
        assert achievement_state.longest_streak == 3

        # Break
        await service.update_streak(
            achievement_state, base + timedelta(days=5)
        )

        # Build longer streak
        for day in range(6, 11):
            await service.update_streak(
                achievement_state, base + timedelta(days=day)
            )

        # Streak runs from day 5 through day 10 = 6 consecutive days
        assert achievement_state.current_streak == 6
        assert achievement_state.longest_streak == 6  # Updated


class TestMonthBoundary:
    """Test streak at month boundaries."""

    @pytest.mark.asyncio
    async def test_streak_across_month_boundary(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak continues across month boundaries."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Jan 31
        t1 = datetime(2026, 1, 31, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)

        # Feb 1
        t2 = datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)

        assert achievement_state.current_streak == 2

    @pytest.mark.asyncio
    async def test_streak_across_year_boundary(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak continues across year boundaries."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Dec 31
        t1 = datetime(2025, 12, 31, 23, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)

        # Jan 1
        t2 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)

        assert achievement_state.current_streak == 2

    @pytest.mark.asyncio
    async def test_streak_feb_28_to_mar_1_non_leap(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak across Feb 28 → Mar 1 in non-leap year."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Feb 28 (non-leap year 2025)
        t1 = datetime(2025, 2, 28, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)

        # Mar 1 (next day in non-leap year)
        t2 = datetime(2025, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)

        assert achievement_state.current_streak == 2

    @pytest.mark.asyncio
    async def test_streak_feb_29_leap_year(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak through Feb 29 in leap year."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Feb 28 (leap year 2024)
        t1 = datetime(2024, 2, 28, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t1)

        # Feb 29
        t2 = datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t2)

        # Mar 1
        t3 = datetime(2024, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, t3)

        assert achievement_state.current_streak == 3
