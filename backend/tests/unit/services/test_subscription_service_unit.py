"""Mock-based unit tests for SubscriptionService.

Covers code paths not exercised by the integration tests in test_subscription_service.py:
- process_webhook dispatching for all event types
- handle_subscription_cancelled
- cancel_subscription (user-initiated)
- get_subscription
- get_subscription_service factory
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.schemas.enums import SubscriptionStatus, UserTier


def _make_subscription(**overrides):
    s = MagicMock()
    s.id = uuid4()
    s.user_id = uuid4()
    s.checkout_subscription_id = f"sub_{uuid4().hex[:16]}"
    s.status = SubscriptionStatus.ACTIVE
    s.current_period_start = datetime.now(timezone.utc) - timedelta(days=15)
    s.current_period_end = datetime.now(timezone.utc) + timedelta(days=15)
    s.last_payment_at = datetime.now(timezone.utc)
    s.failed_payment_count = 0
    s.retry_count = 0
    s.grace_period_end = None
    s.grace_warning_sent = False
    s.cancelled_at = None
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def _make_service():
    from src.services.subscription_service import SubscriptionService

    session = AsyncMock()
    settings = MagicMock()
    service = SubscriptionService(session, settings)
    return service, session, settings


class TestProcessWebhookDispatching:
    """Tests for process_webhook event type dispatching."""

    @pytest.mark.asyncio
    async def test_payment_declined_dispatches(self):
        service, session, _ = _make_service()
        sub = _make_subscription(retry_count=0, failed_payment_count=0)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        result = await service.process_webhook(
            event_id="evt_decline_1",
            event_type="payment_declined",
            data={"subscription_id": sub.checkout_subscription_id},
        )

        assert result["processed"] is True
        assert sub.retry_count == 1

    @pytest.mark.asyncio
    async def test_subscription_cancelled_dispatches(self):
        service, session, _ = _make_service()
        sub = _make_subscription()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        result = await service.process_webhook(
            event_id="evt_cancel_1",
            event_type="subscription_cancelled",
            data={"subscription_id": sub.checkout_subscription_id},
        )

        assert result["processed"] is True
        assert sub.status == SubscriptionStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_subscription_renewed_dispatches(self):
        service, session, _ = _make_service()
        sub = _make_subscription()
        now = datetime.now(timezone.utc)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock
        session.get.return_value = None

        result = await service.process_webhook(
            event_id="evt_renew_1",
            event_type="subscription_renewed",
            data={
                "subscription_id": sub.checkout_subscription_id,
                "user_id": str(sub.user_id),
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )

        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_unknown_event_type(self):
        service, _, _ = _make_service()

        result = await service.process_webhook(
            event_id="evt_unknown_1",
            event_type="unknown_event",
            data={},
        )

        assert result["processed"] is False
        assert result["reason"] == "unknown_event_type"

    @pytest.mark.asyncio
    async def test_exception_propagates(self):
        service, session, _ = _make_service()
        session.execute.side_effect = RuntimeError("DB down")

        with pytest.raises(RuntimeError, match="DB down"):
            await service.process_webhook(
                event_id="evt_err_1",
                event_type="payment_declined",
                data={"subscription_id": "sub_err"},
            )


class TestHandleSubscriptionCancelled:
    @pytest.mark.asyncio
    async def test_success(self):
        service, session, _ = _make_service()
        sub = _make_subscription()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        result = await service.handle_subscription_cancelled(
            checkout_subscription_id=sub.checkout_subscription_id,
        )

        assert result.status == SubscriptionStatus.CANCELLED
        assert result.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_not_found(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="Subscription not found"):
            await service.handle_subscription_cancelled(
                checkout_subscription_id="sub_nonexistent",
            )


class TestCancelSubscription:
    @pytest.mark.asyncio
    async def test_success(self):
        service, session, _ = _make_service()
        sub = _make_subscription(status=SubscriptionStatus.ACTIVE)

        # get_subscription query
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        result = await service.cancel_subscription(user_id=sub.user_id)

        assert result.status == SubscriptionStatus.CANCELLED
        assert result.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_no_subscription(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="No subscription found"):
            await service.cancel_subscription(user_id=uuid4())

    @pytest.mark.asyncio
    async def test_already_cancelled(self):
        service, session, _ = _make_service()
        sub = _make_subscription(status=SubscriptionStatus.CANCELLED)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="already cancelled"):
            await service.cancel_subscription(user_id=sub.user_id)

    @pytest.mark.asyncio
    async def test_already_expired(self):
        service, session, _ = _make_service()
        sub = _make_subscription(status=SubscriptionStatus.EXPIRED)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="already cancelled or expired"):
            await service.cancel_subscription(user_id=sub.user_id)


class TestGetSubscription:
    @pytest.mark.asyncio
    async def test_found(self):
        service, session, _ = _make_service()
        sub = _make_subscription()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = sub
        session.execute.return_value = result_mock

        result = await service.get_subscription(user_id=sub.user_id)
        assert result == sub

    @pytest.mark.asyncio
    async def test_not_found(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        result = await service.get_subscription(user_id=uuid4())
        assert result is None


class TestPaymentDeclinedNotFound:
    @pytest.mark.asyncio
    async def test_subscription_not_found_raises(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="Subscription not found"):
            await service.handle_payment_declined(
                checkout_subscription_id="sub_missing",
            )


class TestGetSubscriptionServiceFactory:
    def test_factory_returns_service(self):
        from src.services.subscription_service import (
            SubscriptionService,
            get_subscription_service,
        )

        session = AsyncMock()
        settings = MagicMock()
        result = get_subscription_service(session, settings)
        assert isinstance(result, SubscriptionService)
