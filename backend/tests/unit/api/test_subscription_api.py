"""Unit tests for Subscription API endpoints.

Tests subscription management, checkout, webhook, and credit purchase endpoints.
"""

import json
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from src.api.subscription import (
    get_subscription,
    create_checkout_session,
    cancel_subscription,
    handle_webhook,
    purchase_credits,
)
from src.schemas.enums import SubscriptionStatus, UserTier


@pytest.fixture
def mock_free_user():
    user = MagicMock()
    user.id = uuid4()
    user.email = "free@test.com"
    user.tier = UserTier.FREE
    user.is_pro = False
    return user


@pytest.fixture
def mock_pro_user():
    user = MagicMock()
    user.id = uuid4()
    user.email = "pro@test.com"
    user.tier = UserTier.PRO
    user.is_pro = True
    return user


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    s = MagicMock()
    s.free_max_subtasks = 5
    s.pro_max_subtasks = 10
    s.free_desc_max_length = 1000
    s.pro_desc_max_length = 2000
    s.pro_monthly_credits = 50
    s.checkout_webhook_secret = "test-secret"
    return s


class MockRequest:
    """Mock Starlette Request for webhook tests."""

    def __init__(self, body_content=b"{}", headers=None):
        self._body = body_content
        self.headers = headers or {}

    async def body(self):
        return self._body


# =============================================================================
# GET SUBSCRIPTION
# =============================================================================


class TestGetSubscription:
    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_free_user_no_subscription(
        self, mock_get_service, mock_free_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_subscription.return_value = None

        result = await get_subscription(
            current_user=mock_free_user, session=mock_session, settings=mock_settings,
        )

        assert "data" in result
        mock_service.get_subscription.assert_awaited_once_with(mock_free_user.id)

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_pro_user_with_subscription(
        self, mock_get_service, mock_pro_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        sub = MagicMock()
        sub.status = SubscriptionStatus.ACTIVE
        sub.current_period_end = datetime.now(UTC)
        mock_service.get_subscription.return_value = sub

        result = await get_subscription(
            current_user=mock_pro_user, session=mock_session, settings=mock_settings,
        )

        assert "data" in result

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_cancelled_subscription(
        self, mock_get_service, mock_pro_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        sub = MagicMock()
        sub.status = SubscriptionStatus.CANCELLED
        sub.current_period_end = datetime.now(UTC)
        mock_service.get_subscription.return_value = sub

        result = await get_subscription(
            current_user=mock_pro_user, session=mock_session, settings=mock_settings,
        )

        assert "data" in result


# =============================================================================
# CREATE CHECKOUT SESSION
# =============================================================================


class TestCreateCheckoutSession:
    @pytest.mark.asyncio
    @patch("src.api.subscription.get_checkout_client")
    async def test_success(self, mock_get_checkout, mock_free_user, mock_settings):
        mock_client = AsyncMock()
        mock_get_checkout.return_value = mock_client
        mock_client.create_checkout_session.return_value = {
            "checkout_url": "https://pay.example.com/session123",
            "session_id": "session123",
        }

        result = await create_checkout_session(
            current_user=mock_free_user, settings=mock_settings,
        )

        assert "data" in result

    @pytest.mark.asyncio
    async def test_already_pro(self, mock_pro_user, mock_settings):
        with pytest.raises(HTTPException) as exc_info:
            await create_checkout_session(
                current_user=mock_pro_user, settings=mock_settings,
            )

        assert exc_info.value.status_code == 409


# =============================================================================
# CANCEL SUBSCRIPTION
# =============================================================================


class TestCancelSubscription:
    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_success(
        self, mock_get_service, mock_pro_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        sub = MagicMock()
        sub.status = SubscriptionStatus.CANCELLED
        sub.current_period_end = datetime.now(UTC)
        mock_service.cancel_subscription.return_value = sub

        result = await cancel_subscription(
            current_user=mock_pro_user, session=mock_session, settings=mock_settings,
        )

        assert "data" in result

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_error(
        self, mock_get_service, mock_free_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.cancel_subscription.side_effect = ValueError("No subscription found")

        with pytest.raises(HTTPException) as exc_info:
            await cancel_subscription(
                current_user=mock_free_user, session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# HANDLE WEBHOOK
# =============================================================================


class TestHandleWebhook:
    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    @patch("src.api.subscription.get_checkout_client")
    async def test_success(
        self, mock_get_checkout, mock_get_service, mock_session, mock_settings,
    ):
        payload = {
            "id": "evt_123",
            "event_type": "payment_captured",
            "data": {"user_id": str(uuid4()), "subscription_id": "sub_1"},
        }
        request = MockRequest(
            body_content=json.dumps(payload).encode(),
            headers={"Cko-Signature": "valid-sig"},
        )

        mock_client = MagicMock()
        mock_client.verify_signature.return_value = True
        mock_get_checkout.return_value = mock_client

        mock_service = AsyncMock()
        mock_service.process_webhook.return_value = {"processed": True}
        mock_get_service.return_value = mock_service

        result = await handle_webhook(
            request=request, session=mock_session, settings=mock_settings,
        )

        assert result["status"] == "ok"
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_checkout_client")
    async def test_invalid_signature(self, mock_get_checkout, mock_session, mock_settings):
        request = MockRequest(
            body_content=b'{"event_type": "test"}',
            headers={"Cko-Signature": "bad-sig"},
        )

        mock_client = MagicMock()
        mock_client.verify_signature.return_value = False
        mock_get_checkout.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await handle_webhook(
                request=request, session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_checkout_client")
    async def test_invalid_json(self, mock_get_checkout, mock_session, mock_settings):
        request = MockRequest(
            body_content=b"not-json-{{{",
            headers={"Cko-Signature": "sig"},
        )

        mock_client = MagicMock()
        mock_client.verify_signature.return_value = True
        mock_get_checkout.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await handle_webhook(
                request=request, session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_checkout_client")
    async def test_missing_event_type(self, mock_get_checkout, mock_session, mock_settings):
        payload = {"id": "evt_456", "data": {}}
        request = MockRequest(
            body_content=json.dumps(payload).encode(),
            headers={"Cko-Signature": "sig"},
        )

        mock_client = MagicMock()
        mock_client.verify_signature.return_value = True
        mock_get_checkout.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await handle_webhook(
                request=request, session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# PURCHASE CREDITS
# =============================================================================


class TestPurchaseCredits:
    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_success(
        self, mock_get_service, mock_pro_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.purchase_credits.return_value = {
            "credits_added": 50,
            "total_credits": 100,
            "monthly_purchased": 50,
            "monthly_remaining": 450,
        }

        body = MagicMock()
        body.amount = 50

        result = await purchase_credits(
            request_body=body, current_user=mock_pro_user,
            session=mock_session, settings=mock_settings,
        )

        assert "data" in result
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.api.subscription.get_subscription_service")
    async def test_limit_exceeded(
        self, mock_get_service, mock_pro_user, mock_session, mock_settings,
    ):
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.purchase_credits.side_effect = ValueError("Monthly limit exceeded")

        body = MagicMock()
        body.amount = 600

        with pytest.raises(HTTPException) as exc_info:
            await purchase_credits(
                request_body=body, current_user=mock_pro_user,
                session=mock_session, settings=mock_settings,
            )

        assert exc_info.value.status_code == 400
