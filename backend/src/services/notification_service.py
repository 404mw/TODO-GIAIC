"""Notification service for in-app and push notifications.

Phase 8: User Story 8 - Reminder System (FR-028)

T196: Implement push notification delivery method (FR-028)
"""

import json
import logging
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.notification import Notification, PushSubscription
from src.models.user import User
from src.schemas.enums import NotificationMethod, NotificationType


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class NotificationServiceError(Exception):
    """Base exception for notification service errors."""

    pass


class NotificationNotFoundError(NotificationServiceError):
    """Raised when notification is not found."""

    pass


class PushNotificationError(NotificationServiceError):
    """Raised when push notification delivery fails."""

    pass


# =============================================================================
# NOTIFICATION SERVICE
# =============================================================================


class NotificationService:
    """Service for notification operations.

    Handles:
    - Creating in-app notifications
    - Delivering push notifications via WebPush
    - Managing notification read status
    - Managing push subscriptions
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # IN-APP NOTIFICATIONS
    # =========================================================================

    async def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        action_url: str | None = None,
    ) -> Notification:
        """Create an in-app notification.

        Args:
            user_id: The notification recipient
            notification_type: Type of notification
            title: Notification title (max 100 chars)
            body: Notification body (max 500 chars)
            action_url: Optional deep link URL

        Returns:
            The created Notification
        """
        # Truncate if needed
        title = title[:100] if len(title) > 100 else title
        body = body[:500] if len(body) > 500 else body

        notification = Notification(
            id=uuid4(),
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            action_url=action_url,
            read=False,
            read_at=None,
        )

        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)

        logger.info(
            f"Created notification {notification.id} for user {user_id}: {title}"
        )

        return notification

    async def get_notification(
        self,
        user: User,
        notification_id: UUID,
    ) -> Notification:
        """Get a notification by ID with ownership check.

        Args:
            user: The requesting user
            notification_id: The notification ID

        Returns:
            The Notification

        Raises:
            NotificationNotFoundError: If not found or user doesn't own it
        """
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )

        result = await self.session.execute(query)
        notification = result.scalar_one_or_none()

        if notification is None:
            raise NotificationNotFoundError(f"Notification {notification_id} not found")

        return notification

    async def list_notifications(
        self,
        user: User,
        unread_only: bool = False,
        limit: int = 50,
    ) -> tuple[Sequence[Notification], int]:
        """List user's notifications.

        Args:
            user: The requesting user
            unread_only: Filter to unread notifications only
            limit: Maximum notifications to return

        Returns:
            Tuple of (notifications, unread_count)
        """
        query = select(Notification).where(Notification.user_id == user.id)

        if unread_only:
            query = query.where(Notification.read == False)

        # Get unread count
        unread_query = select(func.count()).where(
            Notification.user_id == user.id,
            Notification.read == False,
        )
        result = await self.session.execute(unread_query)
        unread_count = result.scalar() or 0

        # Get notifications
        query = (
            query.order_by(Notification.created_at.desc())
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        notifications = result.scalars().all()

        return notifications, unread_count

    async def mark_notification_read(
        self,
        user: User,
        notification_id: UUID,
    ) -> Notification:
        """Mark a notification as read.

        Args:
            user: The requesting user
            notification_id: The notification ID

        Returns:
            The updated Notification
        """
        notification = await self.get_notification(user, notification_id)

        notification.read = True
        notification.read_at = datetime.now(UTC)

        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)

        return notification

    async def mark_all_notifications_read(
        self,
        user: User,
    ) -> int:
        """Mark all notifications as read.

        Args:
            user: The requesting user

        Returns:
            Number of notifications marked read
        """
        from sqlalchemy import update

        now = datetime.now(UTC)

        result = await self.session.execute(
            update(Notification)
            .where(
                Notification.user_id == user.id,
                Notification.read == False,
            )
            .values(read=True, read_at=now)
        )

        await self.session.flush()

        return result.rowcount

    # =========================================================================
    # PUSH NOTIFICATIONS (T196)
    # =========================================================================

    async def send_push_notification(
        self,
        user_id: UUID,
        title: str,
        body: str,
        action_url: str | None = None,
        tag: str | None = None,
    ) -> int:
        """Send push notification to all user's subscribed devices.

        T196: Implement push notification delivery method (FR-028)

        Uses Web Push Protocol to send notifications to subscribed devices.

        Args:
            user_id: The notification recipient
            title: Notification title
            body: Notification body
            action_url: Optional action URL when notification is clicked
            tag: Optional tag for notification grouping

        Returns:
            Number of successful deliveries
        """
        # Get active subscriptions for user
        query = select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.active == True,
        )

        result = await self.session.execute(query)
        subscriptions = result.scalars().all()

        if not subscriptions:
            logger.debug(f"No push subscriptions for user {user_id}")
            return 0

        # Prepare push notification payload
        payload = {
            "title": title,
            "body": body,
            "icon": "/icons/notification-icon.png",
            "badge": "/icons/badge-icon.png",
            "tag": tag or "perpetua-notification",
            "data": {
                "url": action_url,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        successful = 0
        failed_subscriptions = []

        for subscription in subscriptions:
            try:
                await self._send_webpush(
                    subscription=subscription,
                    payload=payload,
                )
                successful += 1

                # Update last used timestamp
                subscription.last_used_at = datetime.now(UTC)
                self.session.add(subscription)

            except PushNotificationError as e:
                logger.warning(
                    f"Push notification failed for subscription "
                    f"{subscription.id}: {e}"
                )
                failed_subscriptions.append(subscription)

        # Deactivate failed subscriptions (likely expired)
        for sub in failed_subscriptions:
            sub.active = False
            self.session.add(sub)

        await self.session.flush()

        logger.info(
            f"Sent push notification to {successful}/{len(subscriptions)} "
            f"devices for user {user_id}"
        )

        return successful

    async def _send_webpush(
        self,
        subscription: PushSubscription,
        payload: dict,
    ) -> None:
        """Send WebPush notification to a single subscription.

        Args:
            subscription: The push subscription
            payload: Notification payload

        Raises:
            PushNotificationError: If delivery fails
        """
        try:
            # Import pywebpush for sending
            # This is a soft dependency - if not installed, push won't work
            from pywebpush import webpush, WebPushException
        except ImportError:
            logger.warning("pywebpush not installed, skipping push notification")
            return

        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh_key,
                "auth": subscription.auth_key,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.settings.vapid_private_key,
                vapid_claims={
                    "sub": f"mailto:{self.settings.vapid_contact_email}",
                },
                ttl=3600,  # 1 hour TTL
            )
        except WebPushException as e:
            logger.error(f"WebPush error: {e}")
            raise PushNotificationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected push error: {e}")
            raise PushNotificationError(str(e))

    # =========================================================================
    # PUSH SUBSCRIPTION MANAGEMENT
    # =========================================================================

    async def register_push_subscription(
        self,
        user: User,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
    ) -> PushSubscription:
        """Register a new push subscription for a user.

        Args:
            user: The subscribing user
            endpoint: Push service endpoint URL
            p256dh_key: Client public key (base64)
            auth_key: Authentication secret (base64)

        Returns:
            The created PushSubscription
        """
        # Check if subscription already exists
        existing_query = select(PushSubscription).where(
            PushSubscription.endpoint == endpoint,
        )
        result = await self.session.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing subscription
            existing.user_id = user.id
            existing.p256dh_key = p256dh_key
            existing.auth_key = auth_key
            existing.active = True
            self.session.add(existing)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        # Create new subscription
        subscription = PushSubscription(
            id=uuid4(),
            user_id=user.id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
            active=True,
        )

        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)

        logger.info(f"Registered push subscription {subscription.id} for user {user.id}")

        return subscription

    async def unregister_push_subscription(
        self,
        user: User,
        endpoint: str,
    ) -> bool:
        """Unregister a push subscription.

        Args:
            user: The user
            endpoint: Push service endpoint URL

        Returns:
            True if subscription was found and deactivated
        """
        query = select(PushSubscription).where(
            PushSubscription.user_id == user.id,
            PushSubscription.endpoint == endpoint,
        )

        result = await self.session.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.active = False
            self.session.add(subscription)
            await self.session.flush()
            return True

        return False


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_notification_service(
    session: AsyncSession, settings: Settings
) -> NotificationService:
    """Get a NotificationService instance."""
    return NotificationService(session, settings)
