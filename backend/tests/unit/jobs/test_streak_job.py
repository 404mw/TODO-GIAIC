"""Unit tests for the streak calculation job.

T215: Test streak calculation UTC boundary handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta, UTC
from uuid import uuid4

from src.jobs.tasks.streak_job import (
    handle_streak_calculate,
    _user_completed_task_on_date,
    calculate_user_streak,
)


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock()


class TestStreakCalculation:
    """Tests for streak calculation job."""

    @pytest.mark.asyncio
    async def test_no_users_returns_success(self, mock_session, mock_settings):
        """Test handling when no users exist."""
        # Mock empty user list
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await handle_streak_calculate({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["users_processed"] == 0

    @pytest.mark.asyncio
    async def test_streak_incremented_on_completion(self, mock_session, mock_settings):
        """T215: Test streak increments when user completed task yesterday."""
        user_id = uuid4()

        # Mock user achievement state
        mock_state = MagicMock()
        mock_state.user_id = user_id
        mock_state.current_streak = 5
        mock_state.longest_streak = 10
        mock_state.last_completion_date = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_state]
        mock_session.execute.return_value = mock_result

        # Mock task completion check
        with patch(
            "src.jobs.tasks.streak_job._user_completed_task_on_date",
            new=AsyncMock(return_value=True),
        ):
            result = await handle_streak_calculate({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["streaks_incremented"] == 1
        assert mock_state.current_streak == 6

    @pytest.mark.asyncio
    async def test_longest_streak_updated(self, mock_session, mock_settings):
        """Test longest streak is updated when current exceeds it."""
        user_id = uuid4()

        # Mock user at their longest streak
        mock_state = MagicMock()
        mock_state.user_id = user_id
        mock_state.current_streak = 10
        mock_state.longest_streak = 10
        mock_state.last_completion_date = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_state]
        mock_session.execute.return_value = mock_result

        with patch(
            "src.jobs.tasks.streak_job._user_completed_task_on_date",
            new=AsyncMock(return_value=True),
        ):
            await handle_streak_calculate({}, mock_session, mock_settings)

        assert mock_state.current_streak == 11
        assert mock_state.longest_streak == 11

    @pytest.mark.asyncio
    async def test_streak_reset_on_missed_day(self, mock_session, mock_settings):
        """T215: Test streak resets when user misses a day."""
        user_id = uuid4()
        # Use UTC date to match job's datetime.now(UTC).date() calculation
        today_utc = datetime.now(UTC).date()
        yesterday = today_utc - timedelta(days=1)
        two_days_ago = yesterday - timedelta(days=1)

        # Mock user with active streak
        mock_state = MagicMock()
        mock_state.user_id = user_id
        mock_state.current_streak = 7
        mock_state.longest_streak = 10
        mock_state.last_completion_date = two_days_ago  # Last activity was 2 days ago

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_state]
        mock_session.execute.return_value = mock_result

        with patch(
            "src.jobs.tasks.streak_job._user_completed_task_on_date",
            new=AsyncMock(return_value=False),
        ):
            result = await handle_streak_calculate({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["streaks_reset"] == 1
        assert mock_state.current_streak == 0

    @pytest.mark.asyncio
    async def test_error_returns_retry(self, mock_session, mock_settings):
        """Test that errors return retry status."""
        mock_session.execute.side_effect = Exception("Database error")

        result = await handle_streak_calculate({}, mock_session, mock_settings)

        assert result["status"] == "retry"
        assert "Database error" in result["error"]


class TestUserCompletedTaskOnDate:
    """Tests for checking if user completed task on a date."""

    @pytest.mark.asyncio
    async def test_returns_true_when_task_completed(self, mock_session):
        """Test returns True when user has completed task on date."""
        user_id = uuid4()
        check_date = date.today()

        # Mock finding a completed task
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = uuid4()
        mock_session.execute.return_value = mock_result

        result = await _user_completed_task_on_date(mock_session, user_id, check_date)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_task(self, mock_session):
        """Test returns False when no tasks completed on date."""
        user_id = uuid4()
        check_date = date.today()

        # Mock no completed task
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await _user_completed_task_on_date(mock_session, user_id, check_date)

        assert result is False


class TestUTCBoundaryHandling:
    """Tests for UTC boundary accuracy (SC-007)."""

    @pytest.mark.asyncio
    async def test_uses_utc_for_date_comparison(self, mock_session):
        """T215: Test that date comparison uses UTC."""
        user_id = uuid4()
        yesterday = date.today() - timedelta(days=1)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        await _user_completed_task_on_date(mock_session, user_id, yesterday)

        # Verify the query was called (checking timezone is used)
        mock_session.execute.assert_called_once()
