"""Unit tests for NotificationService.

Phase 19: Notifications (FR-055 to FR-057)

T349: Test: Notification created for reminders
T350: Test: Notification read status tracking
T358c: Test: Expired/invalid push tokens handled gracefully (FR-028b)
"""

import json
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.notification import Notification, PushSubscription
from src.models.user import User
from src.schemas.enums import NotificationType, UserTier
from src.services.notification_service import (
    NotificationNotFoundError,
    NotificationService,
    PushNotificationError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def notification_service(db_session: AsyncSession, settings: Settings):
    """Create NotificationService instance."""
    return NotificationService(db_session, settings)


# =============================================================================
# T349: Notification created for reminders
# =============================================================================


class TestCreateNotification:
    """T349: Test notification creation for reminders (FR-055)."""

    @pytest.mark.asyncio
    async def test_create_reminder_notification(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Notification is created with correct type and content for reminders."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title="Task Reminder",
            body="Complete quarterly report is due in 1 hour",
            action_url="/tasks/some-task-id",
        )

        assert notification.id is not None
        assert notification.user_id == test_user.id
        assert notification.type == NotificationType.REMINDER
        assert notification.title == "Task Reminder"
        assert notification.body == "Complete quarterly report is due in 1 hour"
        assert notification.action_url == "/tasks/some-task-id"
        assert notification.read is False
        assert notification.read_at is None
        assert notification.created_at is not None

    @pytest.mark.asyncio
    async def test_create_achievement_notification(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Notification is created for achievement unlocks."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ACHIEVEMENT,
            title="Achievement Unlocked!",
            body="You completed 5 tasks! +15 max tasks",
        )

        assert notification.type == NotificationType.ACHIEVEMENT
        assert notification.read is False

    @pytest.mark.asyncio
    async def test_create_notification_truncates_long_title(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Title is truncated to 100 chars if too long."""
        long_title = "x" * 150
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title=long_title,
            body="Test body",
        )

        assert len(notification.title) == 100

    @pytest.mark.asyncio
    async def test_create_notification_truncates_long_body(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Body is truncated to 500 chars if too long."""
        long_body = "y" * 600
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title="Test",
            body=long_body,
        )

        assert len(notification.body) == 500

    @pytest.mark.asyncio
    async def test_create_notification_without_action_url(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Notification can be created without an action URL."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.SYSTEM,
            title="System Update",
            body="New features available",
        )

        assert notification.action_url is None


# =============================================================================
# T350: Notification read status tracking (FR-057)
# =============================================================================


class TestNotificationReadStatus:
    """T350: Test notification read status tracking (FR-057)."""

    @pytest.mark.asyncio
    async def test_notification_starts_unread(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Newly created notification is unread."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title="Test",
            body="Test body",
        )

        assert notification.read is False
        assert notification.read_at is None

    @pytest.mark.asyncio
    async def test_mark_notification_read(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Marking notification as read sets read flag and timestamp."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title="Test",
            body="Test body",
        )

        updated = await notification_service.mark_notification_read(
            user=test_user,
            notification_id=notification.id,
        )

        assert updated.read is True
        assert updated.read_at is not None
        assert isinstance(updated.read_at, datetime)

    @pytest.mark.asyncio
    async def test_mark_all_notifications_read(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Mark all read updates all unread notifications."""
        # Create multiple notifications
        for i in range(3):
            await notification_service.create_notification(
                user_id=test_user.id,
                notification_type=NotificationType.REMINDER,
                title=f"Test {i}",
                body=f"Body {i}",
            )

        count = await notification_service.mark_all_notifications_read(user=test_user)

        assert count == 3

    @pytest.mark.asyncio
    async def test_list_notifications_with_unread_filter(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """List notifications with unread_only filter returns only unread."""
        # Create 3 notifications
        notifications = []
        for i in range(3):
            n = await notification_service.create_notification(
                user_id=test_user.id,
                notification_type=NotificationType.REMINDER,
                title=f"Test {i}",
                body=f"Body {i}",
            )
            notifications.append(n)

        # Mark one as read
        await notification_service.mark_notification_read(
            user=test_user,
            notification_id=notifications[0].id,
        )

        # List unread only
        result, unread_count = await notification_service.list_notifications(
            user=test_user,
            unread_only=True,
        )

        assert len(result) == 2
        assert unread_count == 2

    @pytest.mark.asyncio
    async def test_list_notifications_returns_unread_count(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """List notifications returns total unread count regardless of filter."""
        for i in range(5):
            await notification_service.create_notification(
                user_id=test_user.id,
                notification_type=NotificationType.REMINDER,
                title=f"Test {i}",
                body=f"Body {i}",
            )

        result, unread_count = await notification_service.list_notifications(
            user=test_user,
        )

        assert len(result) == 5
        assert unread_count == 5

    @pytest.mark.asyncio
    async def test_notification_not_found_raises_error(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Getting non-existent notification raises NotificationNotFoundError."""
        with pytest.raises(NotificationNotFoundError):
            await notification_service.get_notification(
                user=test_user,
                notification_id=uuid4(),
            )

    @pytest.mark.asyncio
    async def test_notification_ownership_check(
        self,
        notification_service: NotificationService,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Cannot access another user's notification."""
        notification = await notification_service.create_notification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            title="Test",
            body="Test body",
        )

        # Create another user
        other_user = User(
            id=uuid4(),
            google_id=f"google-other-{uuid4()}",
            email="other@example.com",
            name="Other User",
            tier=UserTier.FREE,
        )
        db_session.add(other_user)
        await db_session.commit()

        with pytest.raises(NotificationNotFoundError):
            await notification_service.get_notification(
                user=other_user,
                notification_id=notification.id,
            )


# =============================================================================
# T358c: Expired/invalid push tokens handled gracefully (FR-028b)
# =============================================================================


class TestPushNotificationTokenHandling:
    """T358c: Test expired/invalid push tokens handled gracefully (FR-028b)."""

    @pytest.mark.asyncio
    async def test_expired_push_subscription_deactivated(
        self,
        notification_service: NotificationService,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Expired/failed push subscriptions are deactivated after failure."""
        # Create a push subscription
        subscription = PushSubscription(
            id=uuid4(),
            user_id=test_user.id,
            endpoint="https://push.example.com/expired-endpoint",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            active=True,
        )
        db_session.add(subscription)
        await db_session.flush()

        # Mock _send_webpush to raise PushNotificationError (simulating expired token)
        with patch.object(
            notification_service,
            "_send_webpush",
            side_effect=PushNotificationError("410 Gone - Subscription expired"),
        ):
            successful = await notification_service.send_push_notification(
                user_id=test_user.id,
                title="Test",
                body="Test body",
            )

        assert successful == 0

        # Verify subscription was deactivated
        await db_session.refresh(subscription)
        assert subscription.active is False

    @pytest.mark.asyncio
    async def test_invalid_push_subscription_deactivated(
        self,
        notification_service: NotificationService,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Invalid push subscription (bad endpoint) is deactivated."""
        subscription = PushSubscription(
            id=uuid4(),
            user_id=test_user.id,
            endpoint="https://push.example.com/invalid",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            active=True,
        )
        db_session.add(subscription)
        await db_session.flush()

        with patch.object(
            notification_service,
            "_send_webpush",
            side_effect=PushNotificationError("404 Not Found"),
        ):
            successful = await notification_service.send_push_notification(
                user_id=test_user.id,
                title="Test",
                body="Test body",
            )

        assert successful == 0

        await db_session.refresh(subscription)
        assert subscription.active is False

    @pytest.mark.asyncio
    async def test_mixed_valid_and_invalid_subscriptions(
        self,
        notification_service: NotificationService,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Valid subscriptions succeed while invalid ones are deactivated."""
        # Create two subscriptions
        valid_sub = PushSubscription(
            id=uuid4(),
            user_id=test_user.id,
            endpoint="https://push.example.com/valid",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            active=True,
        )
        invalid_sub = PushSubscription(
            id=uuid4(),
            user_id=test_user.id,
            endpoint="https://push.example.com/expired",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            active=True,
        )
        db_session.add(valid_sub)
        db_session.add(invalid_sub)
        await db_session.flush()

        call_count = 0

        async def mock_send(subscription, payload):
            nonlocal call_count
            call_count += 1
            if subscription.endpoint == "https://push.example.com/expired":
                raise PushNotificationError("410 Gone")
            # Valid subscription succeeds (no exception)

        with patch.object(
            notification_service,
            "_send_webpush",
            side_effect=mock_send,
        ):
            successful = await notification_service.send_push_notification(
                user_id=test_user.id,
                title="Test",
                body="Test body",
            )

        assert successful == 1  # Only valid sub succeeded

        # Invalid sub deactivated, valid sub still active
        await db_session.refresh(valid_sub)
        await db_session.refresh(invalid_sub)
        assert valid_sub.active is True
        assert invalid_sub.active is False

    @pytest.mark.asyncio
    async def test_no_subscriptions_returns_zero(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Sending push with no subscriptions returns 0 without error."""
        successful = await notification_service.send_push_notification(
            user_id=test_user.id,
            title="Test",
            body="Test body",
        )

        assert successful == 0

    @pytest.mark.asyncio
    async def test_push_subscription_registration(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Push subscription can be registered and retrieved."""
        subscription = await notification_service.register_push_subscription(
            user=test_user,
            endpoint="https://push.example.com/new-endpoint",
            p256dh_key="new-p256dh-key",
            auth_key="new-auth-key",
        )

        assert subscription.id is not None
        assert subscription.user_id == test_user.id
        assert subscription.endpoint == "https://push.example.com/new-endpoint"
        assert subscription.active is True

    @pytest.mark.asyncio
    async def test_duplicate_endpoint_updates_existing(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Re-registering the same endpoint updates the existing subscription."""
        endpoint = "https://push.example.com/same-endpoint"

        sub1 = await notification_service.register_push_subscription(
            user=test_user,
            endpoint=endpoint,
            p256dh_key="key1",
            auth_key="auth1",
        )

        sub2 = await notification_service.register_push_subscription(
            user=test_user,
            endpoint=endpoint,
            p256dh_key="key2",
            auth_key="auth2",
        )

        # Same subscription updated
        assert sub2.id == sub1.id
        assert sub2.p256dh_key == "key2"
        assert sub2.auth_key == "auth2"

    @pytest.mark.asyncio
    async def test_unregister_push_subscription(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Unregistering a push subscription deactivates it."""
        endpoint = "https://push.example.com/to-remove"

        await notification_service.register_push_subscription(
            user=test_user,
            endpoint=endpoint,
            p256dh_key="key",
            auth_key="auth",
        )

        result = await notification_service.unregister_push_subscription(
            user=test_user,
            endpoint=endpoint,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_returns_false(
        self,
        notification_service: NotificationService,
        test_user: User,
    ):
        """Unregistering a non-existent subscription returns False."""
        result = await notification_service.unregister_push_subscription(
            user=test_user,
            endpoint="https://push.example.com/does-not-exist",
        )

        assert result is False
