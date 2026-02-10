"""Unit tests for Notification API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from fastapi import HTTPException

from src.api.notifications import (
    list_notifications,
    mark_notification_read,
    mark_all_read,
    register_push_subscription,
    unregister_push_subscription,
)
from src.services.notification_service import NotificationNotFoundError


def _make_notification(**overrides):
    n = MagicMock()
    n.id = uuid4()
    n.user_id = uuid4()
    n.type = "subscription"
    n.title = "Test Notification"
    n.body = "Test body"
    n.action_url = "/settings"
    n.read = False
    n.created_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(n, k, v)
    return n


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = uuid4()
    return u


@pytest.fixture
def mock_service():
    return AsyncMock()


class TestListNotifications:
    @pytest.mark.asyncio
    @patch("src.api.notifications.NotificationListResponse")
    @patch("src.api.notifications.NotificationResponse")
    async def test_success(self, mock_resp_cls, mock_list_cls, mock_user, mock_service):
        note = _make_notification()
        mock_service.list_notifications.return_value = ([note], 3)
        mock_resp_cls.model_validate.return_value = MagicMock()
        mock_result = MagicMock()
        mock_result.unread_count = 3
        mock_list_cls.return_value = mock_result

        result = await list_notifications(
            user=mock_user, service=mock_service,
            unread_only=False, limit=50,
        )

        assert result.unread_count == 3

    @pytest.mark.asyncio
    @patch("src.api.notifications.NotificationListResponse")
    @patch("src.api.notifications.NotificationResponse")
    async def test_empty(self, mock_resp_cls, mock_list_cls, mock_user, mock_service):
        mock_service.list_notifications.return_value = ([], 0)
        mock_result = MagicMock()
        mock_result.unread_count = 0
        mock_result.data = []
        mock_list_cls.return_value = mock_result

        result = await list_notifications(
            user=mock_user, service=mock_service,
            unread_only=False, limit=50,
        )

        assert result.unread_count == 0
        assert result.data == []

    @pytest.mark.asyncio
    @patch("src.api.notifications.NotificationListResponse")
    @patch("src.api.notifications.NotificationResponse")
    async def test_unread_only(self, mock_resp_cls, mock_list_cls, mock_user, mock_service):
        note = _make_notification(read=False)
        mock_service.list_notifications.return_value = ([note], 1)
        mock_resp_cls.model_validate.return_value = MagicMock()
        mock_list_cls.return_value = MagicMock()

        await list_notifications(
            user=mock_user, service=mock_service,
            unread_only=True, limit=50,
        )

        mock_service.list_notifications.assert_called_once_with(
            user=mock_user, unread_only=True, limit=50,
        )


class TestMarkNotificationRead:
    @pytest.mark.asyncio
    @patch("src.api.notifications.NotificationResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_service):
        note = _make_notification(read=True)
        mock_service.mark_notification_read.return_value = note
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await mark_notification_read(
            notification_id=note.id, user=mock_user, service=mock_service,
        )

        assert result.data is not None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.mark_notification_read.side_effect = NotificationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await mark_notification_read(
                notification_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404


class TestMarkAllRead:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        mock_service.mark_all_notifications_read.return_value = 5

        result = await mark_all_read(user=mock_user, service=mock_service)

        assert result.data.marked_count == 5

    @pytest.mark.asyncio
    async def test_none_to_mark(self, mock_user, mock_service):
        mock_service.mark_all_notifications_read.return_value = 0

        result = await mark_all_read(user=mock_user, service=mock_service)

        assert result.data.marked_count == 0


class TestRegisterPushSubscription:
    @pytest.mark.asyncio
    @patch("src.api.notifications.PushSubscriptionResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_service):
        sub = MagicMock()
        mock_service.register_push_subscription.return_value = sub
        mock_resp_cls.model_validate.return_value = MagicMock()

        request = MagicMock()
        request.endpoint = "https://push.example.com"
        request.p256dh_key = "key1"
        request.auth_key = "key2"

        result = await register_push_subscription(
            request=request, user=mock_user, service=mock_service,
        )

        assert result.data is not None


class TestUnregisterPushSubscription:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        mock_service.unregister_push_subscription.return_value = True

        result = await unregister_push_subscription(
            user=mock_user, service=mock_service,
            endpoint="https://push.example.com",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.unregister_push_subscription.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await unregister_push_subscription(
                user=mock_user, service=mock_service,
                endpoint="https://push.example.com",
            )
        assert exc_info.value.status_code == 404
