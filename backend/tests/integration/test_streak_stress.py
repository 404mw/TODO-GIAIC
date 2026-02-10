"""Streak calculation stress tests.

Phase 15: User Story 9 - Achievement System

T306: Add streak calculation stress test (SC-007)

Tests streak calculation edge cases and performance with large date ranges.
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
    settings = MagicMock()
    return settings


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=uuid4(),
        google_id="stress_test_user",
        email="stress@test.com",
        name="Stress Test User",
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
# T306: STREAK CALCULATION STRESS TEST (SC-007)
# =============================================================================


class TestStreakStress:
    """Stress tests for streak calculation."""

    @pytest.mark.asyncio
    async def test_long_streak_365_days(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test maintaining a year-long streak.

        SC-007: Streak calculation accurate even for very long streaks.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Start date
        start_date = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Complete a task every day for 365 days
        for day in range(365):
            completion_time = start_date + timedelta(days=day)
            await service.update_streak(achievement_state, completion_time)

        # Verify final streak state
        assert achievement_state.current_streak == 365
        assert achievement_state.longest_streak == 365
        assert achievement_state.last_completion_date == date(2025, 12, 31)

    @pytest.mark.asyncio
    async def test_streak_after_long_gap(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test streak reset after a very long gap."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Build up a 30-day streak
        start_date = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        for day in range(30):
            completion_time = start_date + timedelta(days=day)
            await service.update_streak(achievement_state, completion_time)

        assert achievement_state.current_streak == 30
        assert achievement_state.longest_streak == 30

        # Skip 100 days
        long_gap_date = datetime(2025, 5, 11, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, long_gap_date)

        # Streak should reset
        assert achievement_state.current_streak == 1
        # Longest streak should be preserved
        assert achievement_state.longest_streak == 30

    @pytest.mark.asyncio
    async def test_multiple_completions_per_day_stress(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test many completions on the same day don't affect streak incorrectly."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete 100 tasks on Day 1
        day1 = datetime(2026, 1, 15, tzinfo=timezone.utc)
        for hour in range(24):
            for minute in range(4):  # 4 completions per hour
                completion_time = day1.replace(hour=hour, minute=minute * 15)
                await service.update_streak(achievement_state, completion_time)

        # Streak should be exactly 1 (not 96)
        assert achievement_state.current_streak == 1

        # Complete on next day
        day2 = datetime(2026, 1, 16, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day2)

        assert achievement_state.current_streak == 2

    @pytest.mark.asyncio
    async def test_streak_through_all_months(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test streak accurately tracks through different month lengths."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Test through a full year with varying month lengths
        # Jan (31), Feb (28/29), Mar (31), Apr (30), etc.
        start_date = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)  # 2024 is leap year

        # Complete task every day for 366 days (leap year)
        for day in range(366):
            completion_time = start_date + timedelta(days=day)
            await service.update_streak(achievement_state, completion_time)

        assert achievement_state.current_streak == 366
        assert achievement_state.longest_streak == 366
        # Dec 31, 2024
        assert achievement_state.last_completion_date == date(2024, 12, 31)

    @pytest.mark.asyncio
    async def test_streak_recovery_patterns(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test multiple streak build-break-rebuild cycles."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        base_date = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Cycle 1: Build 7-day streak
        for day in range(7):
            await service.update_streak(
                achievement_state, base_date + timedelta(days=day)
            )

        assert achievement_state.current_streak == 7
        assert achievement_state.longest_streak == 7

        # Break (skip day 7, complete on day 9)
        await service.update_streak(
            achievement_state, base_date + timedelta(days=9)
        )

        assert achievement_state.current_streak == 1
        assert achievement_state.longest_streak == 7  # Preserved

        # Cycle 2: Build streak from day 10-19
        # Day 10 is consecutive after day 9, so streak continues from 1
        # streak goes: 2 (day 10), 3 (day 11), ..., 11 (day 19)
        for day in range(10, 20):
            await service.update_streak(
                achievement_state, base_date + timedelta(days=day)
            )

        assert achievement_state.current_streak == 11  # 1 (day 9) + 10 more
        assert achievement_state.longest_streak == 11  # Updated (surpasses 7)

        # Break again
        await service.update_streak(
            achievement_state, base_date + timedelta(days=25)
        )

        assert achievement_state.current_streak == 1
        assert achievement_state.longest_streak == 11  # Still preserved

    @pytest.mark.asyncio
    async def test_timezone_edge_cases_utc_boundary(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test streak handling at exact UTC midnight boundaries."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete at 23:59:59 UTC on Day 1
        time1 = datetime(2026, 1, 15, 23, 59, 59, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, time1)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 15)

        # Complete at 00:00:01 UTC on Day 2
        time2 = datetime(2026, 1, 16, 0, 0, 1, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, time2)

        # Should be consecutive
        assert achievement_state.current_streak == 2
        assert achievement_state.last_completion_date == date(2026, 1, 16)

    @pytest.mark.asyncio
    async def test_streak_calculation_performance(
        self, mock_session, mock_settings, achievement_state
    ):
        """Test streak calculation performance is reasonable.

        This test verifies that streak updates don't degrade with long streaks.
        """
        from src.services.achievement_service import AchievementService
        import time

        service = AchievementService(mock_session, mock_settings)

        base_date = datetime(2020, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Measure time for 1000 streak updates
        start_time = time.time()

        for day in range(1000):
            completion_time = base_date + timedelta(days=day)
            await service.update_streak(achievement_state, completion_time)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in under 1 second (actual should be much faster)
        assert duration < 1.0, f"1000 streak updates took {duration:.2f}s"

        # Verify final state
        assert achievement_state.current_streak == 1000
        assert achievement_state.longest_streak == 1000


class TestEffectiveLimitsStress:
    """Stress tests for effective limits calculation."""

    @pytest.mark.asyncio
    async def test_all_achievements_unlocked(
        self, mock_session, mock_settings, test_user
    ):
        """Test effective limits with all achievements unlocked."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # User with all achievements unlocked
        state = UserAchievementState(
            id=uuid4(),
            user_id=test_user.id,
            unlocked_achievements=[
                "tasks_5",
                "tasks_25",
                "tasks_100",
                "streak_7",
                "streak_30",
                "focus_10",
                "notes_10",
            ],
        )

        # Calculate limits for free tier
        limits_free = await service.calculate_effective_limits(UserTier.FREE, state)

        # Free base: 50 tasks, 10 notes, 0 daily credits
        # Perks: +15+25+50=90 tasks, +5+5=10 notes, +2+5=7 credits
        assert limits_free.max_tasks == 50 + 15 + 25 + 50  # 140
        assert limits_free.max_notes == 10 + 5 + 5  # 20
        assert limits_free.daily_ai_credits == 0 + 2 + 5  # 7

        # Calculate limits for pro tier
        limits_pro = await service.calculate_effective_limits(UserTier.PRO, state)

        # Pro base: 200 tasks, 25 notes, 10 daily credits
        assert limits_pro.max_tasks == 200 + 15 + 25 + 50  # 290
        assert limits_pro.max_notes == 25 + 5 + 5  # 35
        assert limits_pro.daily_ai_credits == 10 + 2 + 5  # 17
