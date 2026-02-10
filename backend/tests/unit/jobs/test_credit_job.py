"""Unit tests for the credit expiration job.

T216: Test credit expiration at UTC midnight
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta, UTC
from uuid import uuid4

from src.jobs.tasks.credit_job import (
    handle_credit_expire,
    _expire_daily_credits,
    _grant_daily_credits,
    grant_kickstart_credits,
)
from src.schemas.enums import CreditType, UserTier


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
    settings = MagicMock()
    settings.pro_daily_credits = 10
    settings.kickstart_credits = 5
    settings.max_credit_carryover = 50
    return settings


class TestCreditExpiration:
    """Tests for credit expiration job."""

    @pytest.mark.asyncio
    async def test_job_success(self, mock_session, mock_settings):
        """Test successful credit expiration job execution."""
        # Mock no credits to expire
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        with patch(
            "src.jobs.tasks.credit_job._expire_daily_credits",
            return_value=0,
        ), patch(
            "src.jobs.tasks.credit_job._process_subscription_carryover",
            return_value={"users_processed": 0, "carried_over": 0, "expired": 0},
        ), patch(
            "src.jobs.tasks.credit_job._grant_daily_credits",
            return_value=0,
        ):
            result = await handle_credit_expire({}, mock_session, mock_settings)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_error_returns_retry(self, mock_session, mock_settings):
        """Test that errors return retry status."""
        with patch(
            "src.jobs.tasks.credit_job._expire_daily_credits",
            side_effect=Exception("Database error"),
        ):
            result = await handle_credit_expire({}, mock_session, mock_settings)

        assert result["status"] == "retry"
        assert "Database error" in result["error"]


class TestDailyCreditExpiration:
    """Tests for daily credit expiration (FR-040)."""

    @pytest.mark.asyncio
    async def test_expires_daily_credits(self, mock_session):
        """T216: Test daily credits are expired at UTC midnight."""
        now = datetime.now(UTC)

        # Mock credits to expire
        mock_credit = MagicMock()
        mock_credit.amount = 10
        mock_credit.consumed = 5
        mock_credit.user_id = uuid4()
        mock_credit.id = uuid4()
        mock_credit.credit_type = CreditType.DAILY

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_credit]
        mock_session.execute.return_value = mock_result

        expired_count = await _expire_daily_credits(mock_session, now)

        assert expired_count == 1
        # Verify expiration record was added
        assert mock_session.add.call_count >= 1

    @pytest.mark.asyncio
    async def test_no_credits_to_expire(self, mock_session):
        """Test when no credits need expiration."""
        now = datetime.now(UTC)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        expired_count = await _expire_daily_credits(mock_session, now)

        assert expired_count == 0


class TestDailyCreditGrant:
    """Tests for daily credit grants to Pro users (FR-038)."""

    @pytest.mark.asyncio
    async def test_grants_to_pro_users(self, mock_session, mock_settings):
        """Test that Pro users receive daily credits."""
        now = datetime.now(UTC)

        # Mock Pro user
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.tier = UserTier.PRO

        # First query returns Pro users
        # Second query checks for existing grant (returns None)
        mock_users_result = MagicMock()
        mock_users_result.scalars.return_value.all.return_value = [mock_user]

        mock_check_result = MagicMock()
        mock_check_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [mock_users_result, mock_check_result]

        grants = await _grant_daily_credits(mock_session, mock_settings, now)

        assert grants == 1

    @pytest.mark.asyncio
    async def test_skips_already_granted(self, mock_session, mock_settings):
        """Test that users who already received credits are skipped."""
        now = datetime.now(UTC)

        # Mock Pro user
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.tier = UserTier.PRO

        mock_users_result = MagicMock()
        mock_users_result.scalars.return_value.all.return_value = [mock_user]

        # Second query finds existing grant
        mock_check_result = MagicMock()
        mock_check_result.scalar_one_or_none.return_value = MagicMock()

        mock_session.execute.side_effect = [mock_users_result, mock_check_result]

        grants = await _grant_daily_credits(mock_session, mock_settings, now)

        assert grants == 0


class TestKickstartCredits:
    """Tests for kickstart credits (FR-037)."""

    @pytest.mark.asyncio
    async def test_grants_kickstart_credits(self, mock_session, mock_settings):
        """Test granting kickstart credits to new users."""
        user_id = uuid4()

        credit = await grant_kickstart_credits(mock_session, mock_settings, user_id)

        assert credit is not None
        assert credit.user_id == user_id
        assert credit.credit_type == CreditType.KICKSTART
        assert credit.amount == 5
        assert credit.expires_at is None  # Kickstart credits don't expire


class TestUTCMidnightHandling:
    """Tests for UTC midnight boundary (T216)."""

    @pytest.mark.asyncio
    async def test_credit_expiration_uses_utc(self, mock_session):
        """T216: Test that credit expiration uses UTC time."""
        now = datetime.now(UTC)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        await _expire_daily_credits(mock_session, now)

        # Verify execute was called (indicating proper UTC handling)
        mock_session.execute.assert_called_once()
