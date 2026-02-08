"""Unit tests for subscription check job.

T210: subscription_check job (daily) per FR-049, FR-050
"""

from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.jobs.tasks.subscription_job import (
    handle_subscription_check,
    handle_payment_failed,
    handle_payment_success,
    _process_expired_grace_periods,
    _send_expiration_warnings,
    _create_expiration_notification,
)
from src.schemas.enums import SubscriptionStatus, UserTier


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    return MagicMock()


# =============================================================================
# handle_subscription_check TESTS
# =============================================================================


class TestHandleSubscriptionCheck:
    """Test the main subscription check handler."""

    @pytest.mark.asyncio
    async def test_success_with_no_expirations(self, mock_session, mock_settings):
        """Should return success when nothing to process."""
        # Mock _process_expired_grace_periods and _send_expiration_warnings
        expired_result = MagicMock()
        expired_result.scalars.return_value.all.return_value = []

        warning_result = MagicMock()
        warning_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[expired_result, warning_result]
        )

        result = await handle_subscription_check({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["expired_subscriptions"] == 0
        assert result["warnings_sent"] == 0

    @pytest.mark.asyncio
    async def test_handles_error(self, mock_session, mock_settings):
        """Should return retry status on error."""
        mock_session.execute = AsyncMock(side_effect=Exception("DB error"))

        result = await handle_subscription_check({}, mock_session, mock_settings)

        assert result["status"] == "retry"
        assert "DB error" in result["error"]


# =============================================================================
# handle_payment_failed TESTS
# =============================================================================


class TestHandlePaymentFailed:
    """Test payment failure handler."""

    @pytest.mark.asyncio
    async def test_increments_retry_count(self, mock_session):
        """Should increment retry count."""
        subscription = MagicMock()
        subscription.retry_count = 0
        subscription.status = SubscriptionStatus.ACTIVE

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = subscription
        mock_session.execute.return_value = result_mock

        await handle_payment_failed(mock_session, uuid4())

        assert subscription.retry_count == 1
        assert subscription.status == SubscriptionStatus.PAST_DUE

    @pytest.mark.asyncio
    async def test_enters_grace_period_after_3_failures(self, mock_session):
        """Should enter grace period after 3 payment failures (FR-049)."""
        subscription = MagicMock()
        subscription.retry_count = 2  # Will be incremented to 3
        subscription.user_id = uuid4()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = subscription
        mock_session.execute.return_value = result_mock

        with patch(
            "src.jobs.tasks.subscription_job._create_expiration_notification",
            new_callable=AsyncMock,
        ):
            await handle_payment_failed(mock_session, uuid4())

        assert subscription.retry_count == 3
        assert subscription.status == SubscriptionStatus.GRACE
        assert subscription.grace_period_end is not None

    @pytest.mark.asyncio
    async def test_handles_missing_subscription(self, mock_session):
        """Should handle missing subscription gracefully."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        # Should not raise
        await handle_payment_failed(mock_session, uuid4())


# =============================================================================
# handle_payment_success TESTS
# =============================================================================


class TestHandlePaymentSuccess:
    """Test payment success handler."""

    @pytest.mark.asyncio
    async def test_resets_subscription_status(self, mock_session):
        """Should reset subscription to active status."""
        subscription = MagicMock()
        subscription.status = SubscriptionStatus.GRACE
        subscription.retry_count = 3

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = subscription
        mock_session.execute.return_value = result_mock

        await handle_payment_success(mock_session, uuid4())

        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.retry_count == 0
        assert subscription.grace_period_end is None
        assert subscription.grace_warning_sent is False

    @pytest.mark.asyncio
    async def test_handles_missing_subscription(self, mock_session):
        """Should handle missing subscription gracefully."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        # Should not raise
        await handle_payment_success(mock_session, uuid4())


# =============================================================================
# _create_expiration_notification TESTS
# =============================================================================


class TestCreateExpirationNotification:
    """Test notification creation for subscription events."""

    @pytest.mark.asyncio
    async def test_creates_warning_notification(self, mock_session):
        """Should create warning notification."""
        await _create_expiration_notification(mock_session, uuid4(), "warning")

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_creates_expired_notification(self, mock_session):
        """Should create expired notification."""
        await _create_expiration_notification(mock_session, uuid4(), "expired")

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
