"""Unit tests for AchievementService.

Phase 15: User Story 9 - Achievement System (FR-043 to FR-046)

T290: Test: Streak calculation uses UTC calendar days (FR-043)
T291: Test: Streak increments on consecutive day completion
T292: Test: Streak resets after missed day
T293: Test: Achievement unlock is permanent (FR-044)
T294: Test: Perks never revoked even when streak breaks (FR-044)
T295: Test: Focus completion tracked (50%+ focus time) (FR-045)
T296: Test: Effective limits computed from base + perks (FR-046)
T297: Test: Streak edge cases (UTC boundary, DST) (SC-007)
"""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.models.achievement import UserAchievementState, ACHIEVEMENT_SEED_DATA
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import UserTier, PerkType, CompletedBy


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    return settings


@pytest.fixture
def free_user():
    """Create a free tier user."""
    return User(
        id=uuid4(),
        google_id="test_google_id_free",
        email="free@test.com",
        name="Free User",
        tier=UserTier.FREE,
    )


@pytest.fixture
def pro_user():
    """Create a pro tier user."""
    return User(
        id=uuid4(),
        google_id="test_google_id_pro",
        email="pro@test.com",
        name="Pro User",
        tier=UserTier.PRO,
    )


@pytest.fixture
def achievement_state(free_user):
    """Create a fresh achievement state for a user."""
    return UserAchievementState(
        id=uuid4(),
        user_id=free_user.id,
        lifetime_tasks_completed=0,
        current_streak=0,
        longest_streak=0,
        last_completion_date=None,
        focus_completions=0,
        notes_converted=0,
        unlocked_achievements=[],
    )


# =============================================================================
# T290: STREAK CALCULATION USES UTC CALENDAR DAYS (FR-043)
# =============================================================================


class TestStreakUTCCalculation:
    """Test streak calculation uses UTC calendar days."""

    @pytest.mark.asyncio
    async def test_streak_uses_utc_dates_not_local_time(
        self, mock_session, mock_settings, free_user, achievement_state
    ):
        """Streak calculation should use UTC dates, not local time.

        FR-043: System MUST calculate streaks based on UTC calendar days.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete task at 11:30 PM UTC on Day 1
        day1_utc = datetime(2026, 1, 15, 23, 30, 0, tzinfo=timezone.utc)

        with patch('src.services.achievement_service.datetime') as mock_dt:
            mock_dt.now.return_value = day1_utc
            mock_dt.utcnow.return_value = day1_utc.replace(tzinfo=None)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Set initial state
            achievement_state.current_streak = 0
            achievement_state.last_completion_date = None

            # Update streak
            result = await service.update_streak(achievement_state, day1_utc)

        # Should start streak at 1
        assert result.current_streak == 1
        assert result.last_completion_date == date(2026, 1, 15)

    @pytest.mark.asyncio
    async def test_streak_continues_on_next_utc_day(
        self, mock_session, mock_settings, free_user, achievement_state
    ):
        """Streak should continue when completing on the next UTC calendar day."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Set up: already has streak from yesterday (UTC)
        achievement_state.current_streak = 3
        achievement_state.last_completion_date = date(2026, 1, 15)

        # Complete task at 12:30 AM UTC on Day 2 (next UTC day)
        day2_utc = datetime(2026, 1, 16, 0, 30, 0, tzinfo=timezone.utc)

        result = await service.update_streak(achievement_state, day2_utc)

        # Streak should increment
        assert result.current_streak == 4
        assert result.last_completion_date == date(2026, 1, 16)


# =============================================================================
# T291: STREAK INCREMENTS ON CONSECUTIVE DAY COMPLETION
# =============================================================================


class TestStreakIncrement:
    """Test streak increments on consecutive day completion."""

    @pytest.mark.asyncio
    async def test_streak_increments_on_consecutive_day(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should increment when completing task on consecutive days."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Day 1: Start streak
        achievement_state.current_streak = 0
        achievement_state.last_completion_date = None

        day1 = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day1)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 15)

        # Day 2: Continue streak
        day2 = datetime(2026, 1, 16, 14, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day2)

        assert achievement_state.current_streak == 2
        assert achievement_state.last_completion_date == date(2026, 1, 16)

        # Day 3: Continue streak
        day3 = datetime(2026, 1, 17, 8, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day3)

        assert achievement_state.current_streak == 3
        assert achievement_state.longest_streak == 3

    @pytest.mark.asyncio
    async def test_multiple_completions_same_day_no_double_increment(
        self, mock_session, mock_settings, achievement_state
    ):
        """Multiple task completions on same UTC day should not double increment streak."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        achievement_state.current_streak = 5
        achievement_state.last_completion_date = date(2026, 1, 15)

        # Complete multiple tasks on day 16
        day16_morning = datetime(2026, 1, 16, 8, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day16_morning)

        assert achievement_state.current_streak == 6

        # Complete another task same day
        day16_evening = datetime(2026, 1, 16, 20, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day16_evening)

        # Streak should not double increment
        assert achievement_state.current_streak == 6


# =============================================================================
# T292: STREAK RESETS AFTER MISSED DAY
# =============================================================================


class TestStreakReset:
    """Test streak resets after missed day."""

    @pytest.mark.asyncio
    async def test_streak_resets_after_one_missed_day(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should reset to 1 after missing a day."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Had a 7-day streak, last completed on Jan 15
        achievement_state.current_streak = 7
        achievement_state.longest_streak = 7
        achievement_state.last_completion_date = date(2026, 1, 15)

        # Complete on Jan 17 (skipped Jan 16)
        day17 = datetime(2026, 1, 17, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day17)

        # Streak should reset to 1
        assert achievement_state.current_streak == 1
        # Longest streak should be preserved
        assert achievement_state.longest_streak == 7

    @pytest.mark.asyncio
    async def test_streak_resets_after_multiple_missed_days(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should reset after missing multiple days."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Had a streak, last completed on Jan 10
        achievement_state.current_streak = 10
        achievement_state.longest_streak = 10
        achievement_state.last_completion_date = date(2026, 1, 10)

        # Complete on Jan 20 (missed 9 days!)
        day20 = datetime(2026, 1, 20, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day20)

        # Streak should reset to 1
        assert achievement_state.current_streak == 1
        # Longest streak preserved
        assert achievement_state.longest_streak == 10


# =============================================================================
# T293: ACHIEVEMENT UNLOCK IS PERMANENT (FR-044)
# =============================================================================


class TestAchievementPermanence:
    """Test achievement unlocks are permanent."""

    @pytest.mark.asyncio
    async def test_achievement_unlock_is_permanent(
        self, mock_session, mock_settings, achievement_state
    ):
        """Once unlocked, achievements cannot be revoked.

        FR-044: System MUST unlock achievements permanently.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Set up user with 5 completed tasks
        achievement_state.lifetime_tasks_completed = 5

        # Check and unlock achievements
        unlocked = await service.check_and_unlock(achievement_state)

        # Should unlock tasks_5
        assert "tasks_5" in achievement_state.unlocked_achievements
        assert any(a["id"] == "tasks_5" for a in unlocked)

    @pytest.mark.asyncio
    async def test_achievement_not_double_unlocked(
        self, mock_session, mock_settings, achievement_state
    ):
        """Achievement should not be unlocked twice if already unlocked."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Already has tasks_5 achievement
        achievement_state.lifetime_tasks_completed = 10
        achievement_state.unlocked_achievements = ["tasks_5"]

        # Check and unlock
        unlocked = await service.check_and_unlock(achievement_state)

        # tasks_5 should not be in newly unlocked list
        assert not any(a["id"] == "tasks_5" for a in unlocked)
        # Should still only have one entry
        assert achievement_state.unlocked_achievements.count("tasks_5") == 1


# =============================================================================
# T294: PERKS NEVER REVOKED EVEN WHEN STREAK BREAKS (FR-044)
# =============================================================================


class TestPerkPermanence:
    """Test perks are never revoked."""

    @pytest.mark.asyncio
    async def test_perks_retained_when_streak_breaks(
        self, mock_session, mock_settings, achievement_state
    ):
        """Achievement perks should remain even if the streak that earned them breaks.

        FR-044: Perks are never revoked.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # User had 7-day streak and earned streak_7 achievement
        achievement_state.current_streak = 7
        achievement_state.longest_streak = 7
        achievement_state.unlocked_achievements = ["streak_7"]
        achievement_state.last_completion_date = date(2026, 1, 15)

        # Skip a day and break streak
        day17 = datetime(2026, 1, 17, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, day17)

        # Streak broke
        assert achievement_state.current_streak == 1

        # But achievement and perk still present
        assert "streak_7" in achievement_state.unlocked_achievements

        # Calculate effective limits - perk should still apply
        limits = await service.calculate_effective_limits(
            UserTier.PRO, achievement_state
        )

        # streak_7 grants +2 daily credits
        # PRO base is 10, so effective should be 12
        assert limits.daily_ai_credits == 12


# =============================================================================
# T295: FOCUS COMPLETION TRACKED (50%+ FOCUS TIME) (FR-045)
# =============================================================================


class TestFocusCompletion:
    """Test focus completion tracking."""

    @pytest.mark.asyncio
    async def test_focus_completion_counted_at_50_percent(
        self, mock_session, mock_settings, achievement_state
    ):
        """Task counts as focus completion if 50%+ of estimate spent in focus.

        FR-045: Track focus mode completion (≥50% of estimated duration in focus).
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Task with 30 min (1800 seconds) estimate
        # User spent 15 min (900 seconds) in focus mode = exactly 50%
        task = MagicMock()
        task.estimated_duration = 30  # minutes
        task.focus_time_seconds = 900  # 15 minutes = 50%
        task.completed = True

        is_focus_completion = service.is_focus_completion(task)

        assert is_focus_completion is True

    @pytest.mark.asyncio
    async def test_focus_completion_not_counted_under_50_percent(
        self, mock_session, mock_settings, achievement_state
    ):
        """Task does not count if less than 50% of estimate spent in focus."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Task with 30 min estimate, only 14 min focus = 46.7%
        task = MagicMock()
        task.estimated_duration = 30  # minutes
        task.focus_time_seconds = 840  # 14 minutes = 46.7%
        task.completed = True

        is_focus_completion = service.is_focus_completion(task)

        assert is_focus_completion is False

    @pytest.mark.asyncio
    async def test_focus_completion_requires_estimated_duration(
        self, mock_session, mock_settings, achievement_state
    ):
        """Task without estimated duration cannot count as focus completion."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Task without estimate
        task = MagicMock()
        task.estimated_duration = None
        task.focus_time_seconds = 1800
        task.completed = True

        is_focus_completion = service.is_focus_completion(task)

        assert is_focus_completion is False


# =============================================================================
# T296: EFFECTIVE LIMITS COMPUTED FROM BASE + PERKS (FR-046)
# =============================================================================


class TestEffectiveLimits:
    """Test effective limits computation."""

    @pytest.mark.asyncio
    async def test_effective_limits_base_free_tier(
        self, mock_session, mock_settings
    ):
        """Free tier should have base limits with no perks."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # No achievements
        state = UserAchievementState(
            id=uuid4(),
            user_id=uuid4(),
            unlocked_achievements=[],
        )

        limits = await service.calculate_effective_limits(UserTier.FREE, state)

        assert limits.max_tasks == 50  # Free base
        assert limits.max_notes == 10  # Free base
        assert limits.daily_ai_credits == 0  # Free gets 0 daily

    @pytest.mark.asyncio
    async def test_effective_limits_base_pro_tier(
        self, mock_session, mock_settings
    ):
        """Pro tier should have higher base limits."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # No achievements
        state = UserAchievementState(
            id=uuid4(),
            user_id=uuid4(),
            unlocked_achievements=[],
        )

        limits = await service.calculate_effective_limits(UserTier.PRO, state)

        assert limits.max_tasks == 200  # Pro base
        assert limits.max_notes == 25  # Pro base
        assert limits.daily_ai_credits == 10  # Pro base

    @pytest.mark.asyncio
    async def test_effective_limits_with_task_perks(
        self, mock_session, mock_settings
    ):
        """Task achievements should add to max_tasks."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Has tasks_5 (+15), tasks_25 (+25)
        state = UserAchievementState(
            id=uuid4(),
            user_id=uuid4(),
            unlocked_achievements=["tasks_5", "tasks_25"],
        )

        limits = await service.calculate_effective_limits(UserTier.FREE, state)

        # Free base 50 + 15 + 25 = 90
        assert limits.max_tasks == 90

    @pytest.mark.asyncio
    async def test_effective_limits_with_streak_perks(
        self, mock_session, mock_settings
    ):
        """Streak achievements should add to daily_ai_credits."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Has streak_7 (+2), streak_30 (+5)
        state = UserAchievementState(
            id=uuid4(),
            user_id=uuid4(),
            unlocked_achievements=["streak_7", "streak_30"],
        )

        limits = await service.calculate_effective_limits(UserTier.PRO, state)

        # Pro base 10 + 2 + 5 = 17
        assert limits.daily_ai_credits == 17

    @pytest.mark.asyncio
    async def test_effective_limits_with_note_perks(
        self, mock_session, mock_settings
    ):
        """Focus and note achievements should add to max_notes."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Has focus_10 (+5), notes_10 (+5)
        state = UserAchievementState(
            id=uuid4(),
            user_id=uuid4(),
            unlocked_achievements=["focus_10", "notes_10"],
        )

        limits = await service.calculate_effective_limits(UserTier.FREE, state)

        # Free base 10 + 5 + 5 = 20
        assert limits.max_notes == 20


# =============================================================================
# T297: STREAK EDGE CASES (UTC BOUNDARY, DST) (SC-007)
# =============================================================================


class TestStreakEdgeCases:
    """Test streak edge cases at UTC boundaries."""

    @pytest.mark.asyncio
    async def test_streak_utc_boundary_11_59_pm_to_12_01_am(
        self, mock_session, mock_settings, achievement_state
    ):
        """Completing task at 11:59 PM UTC, then 12:01 AM UTC should continue streak."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete at 11:59 PM UTC on Jan 15
        time1 = datetime(2026, 1, 15, 23, 59, 0, tzinfo=timezone.utc)
        achievement_state.current_streak = 0
        achievement_state.last_completion_date = None

        await service.update_streak(achievement_state, time1)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 15)

        # Complete at 12:01 AM UTC on Jan 16 (2 minutes later, but new day)
        time2 = datetime(2026, 1, 16, 0, 1, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, time2)

        # Should be consecutive days
        assert achievement_state.current_streak == 2
        assert achievement_state.last_completion_date == date(2026, 1, 16)

    @pytest.mark.asyncio
    async def test_streak_handles_timezone_naive_as_utc(
        self, mock_session, mock_settings, achievement_state
    ):
        """Timezone-naive datetimes should be treated as UTC."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Naive datetime (should be treated as UTC)
        time1 = datetime(2026, 1, 15, 10, 0, 0)  # No tzinfo
        achievement_state.current_streak = 0
        achievement_state.last_completion_date = None

        await service.update_streak(achievement_state, time1)

        assert achievement_state.current_streak == 1
        assert achievement_state.last_completion_date == date(2026, 1, 15)

    @pytest.mark.asyncio
    async def test_streak_no_false_breaks_on_month_boundary(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should not falsely break on month boundaries.

        SC-007: Streak calculations accurate to UTC day boundary with no false breaks.
        """
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete on Jan 31
        achievement_state.current_streak = 10
        achievement_state.last_completion_date = date(2026, 1, 31)

        # Complete on Feb 1
        feb1 = datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, feb1)

        # Should continue streak
        assert achievement_state.current_streak == 11
        assert achievement_state.last_completion_date == date(2026, 2, 1)

    @pytest.mark.asyncio
    async def test_streak_no_false_breaks_on_year_boundary(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should not falsely break on year boundaries."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # Complete on Dec 31, 2025
        achievement_state.current_streak = 30
        achievement_state.last_completion_date = date(2025, 12, 31)

        # Complete on Jan 1, 2026
        jan1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, jan1)

        # Should continue streak
        assert achievement_state.current_streak == 31
        assert achievement_state.last_completion_date == date(2026, 1, 1)

    @pytest.mark.asyncio
    async def test_streak_handles_leap_year(
        self, mock_session, mock_settings, achievement_state
    ):
        """Streak should handle leap year correctly (Feb 28 -> Feb 29 -> Mar 1)."""
        from src.services.achievement_service import AchievementService

        service = AchievementService(mock_session, mock_settings)

        # 2024 is a leap year
        # Complete on Feb 28
        achievement_state.current_streak = 5
        achievement_state.last_completion_date = date(2024, 2, 28)

        # Complete on Feb 29 (leap day)
        feb29 = datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, feb29)

        assert achievement_state.current_streak == 6
        assert achievement_state.last_completion_date == date(2024, 2, 29)

        # Complete on Mar 1
        mar1 = datetime(2024, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        await service.update_streak(achievement_state, mar1)

        assert achievement_state.current_streak == 7
        assert achievement_state.last_completion_date == date(2024, 3, 1)
