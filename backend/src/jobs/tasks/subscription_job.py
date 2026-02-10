"""Background job for subscription status checking.

T210: Implement subscription_check job (daily) per FR-049, FR-050

This job runs daily to:
- Check subscription statuses
- Handle grace period expiration (FR-049)
- Downgrade expired subscriptions to free tier (FR-050)
"""

import logging
from datetime import datetime, UTC
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.subscription import Subscription
from src.models.user import User
from src.schemas.enums import SubscriptionStatus, UserTier


logger = logging.getLogger(__name__)


async def handle_subscription_check(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Check subscription statuses and handle expirations.

    T210: Subscription check job per FR-049, FR-050

    This job:
    1. Finds subscriptions in grace period that have expired
    2. Downgrades users to free tier when grace period expires
    3. Sends notifications for upcoming expirations

    Args:
        payload: Job payload (usually empty)
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary with processing summary
    """
    now = datetime.now(UTC)
    today = now.date()

    logger.info(f"Starting subscription check job for {today}")

    try:
        # Step 1: Find and process expired grace periods (FR-050)
        expired_count = await _process_expired_grace_periods(session, now)

        # Step 2: Find subscriptions approaching grace period end
        warnings_sent = await _send_expiration_warnings(session, now)

        await session.commit()

        logger.info(
            f"Subscription check complete: {expired_count} expired, "
            f"{warnings_sent} warnings sent"
        )

        return {
            "status": "success",
            "date": str(today),
            "expired_subscriptions": expired_count,
            "warnings_sent": warnings_sent,
        }

    except Exception as e:
        logger.error(f"Subscription check job failed: {e}", exc_info=True)
        return {
            "status": "retry",
            "error": str(e),
        }


async def _process_expired_grace_periods(
    session: AsyncSession,
    now: datetime,
) -> int:
    """Process subscriptions with expired grace periods.

    FR-050: Grace period expiration downgrades to free tier

    Args:
        session: Database session
        now: Current time

    Returns:
        Number of subscriptions expired
    """
    # Find subscriptions in grace period that have expired
    query = select(Subscription).where(
        Subscription.status == SubscriptionStatus.GRACE,
        Subscription.grace_period_end <= now,
    )

    result = await session.execute(query)
    expired_subscriptions = result.scalars().all()

    expired_count = 0
    for subscription in expired_subscriptions:
        # Update subscription status
        subscription.status = SubscriptionStatus.EXPIRED
        session.add(subscription)

        # Downgrade user to free tier
        user_query = select(User).where(User.id == subscription.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user and user.tier == UserTier.PRO:
            user.tier = UserTier.FREE
            session.add(user)

            logger.info(
                f"Downgraded user {user.id} to free tier "
                f"(grace period expired)"
            )

            # Create notification for the user
            await _create_expiration_notification(
                session, user.id, "expired"
            )

        expired_count += 1

    await session.flush()
    return expired_count


async def _send_expiration_warnings(
    session: AsyncSession,
    now: datetime,
) -> int:
    """Send warnings for subscriptions approaching grace period end.

    Args:
        session: Database session
        now: Current time

    Returns:
        Number of warnings sent
    """
    from datetime import timedelta

    # Find subscriptions in grace with 3 days left
    warning_threshold = now + timedelta(days=3)

    query = select(Subscription).where(
        Subscription.status == SubscriptionStatus.GRACE,
        Subscription.grace_period_end > now,
        Subscription.grace_period_end <= warning_threshold,
        Subscription.grace_warning_sent == False,
    )

    result = await session.execute(query)
    subscriptions = result.scalars().all()

    warnings_sent = 0
    for subscription in subscriptions:
        await _create_expiration_notification(
            session, subscription.user_id, "warning"
        )

        subscription.grace_warning_sent = True
        session.add(subscription)
        warnings_sent += 1

        logger.debug(
            f"Sent grace period warning to user {subscription.user_id}"
        )

    await session.flush()
    return warnings_sent


async def _create_expiration_notification(
    session: AsyncSession,
    user_id: UUID,
    notification_type: str,
) -> None:
    """Create a notification for subscription expiration.

    Args:
        session: Database session
        user_id: User ID
        notification_type: 'warning' or 'expired'
    """
    from uuid import uuid4
    from src.models.notification import Notification
    from src.schemas.enums import NotificationType

    if notification_type == "warning":
        title = "Subscription Grace Period Ending"
        body = (
            "Your subscription grace period is ending in 3 days. "
            "Please update your payment method to continue enjoying Pro features."
        )
    else:  # expired
        title = "Subscription Expired"
        body = (
            "Your Pro subscription has expired. "
            "You've been downgraded to the free tier. "
            "Upgrade again to restore Pro features."
        )

    notification = Notification(
        id=uuid4(),
        user_id=user_id,
        type=NotificationType.SUBSCRIPTION,
        title=title,
        body=body,
        action_url="/settings/subscription",
        read=False,
    )

    session.add(notification)
    await session.flush()


# =============================================================================
# SUBSCRIPTION EVENT HANDLERS
# =============================================================================


async def handle_payment_failed(
    session: AsyncSession,
    subscription_id: UUID,
) -> None:
    """Handle a failed payment.

    FR-049: After 3 payment failures, enter grace period

    Args:
        session: Database session
        subscription_id: Subscription ID
    """
    from datetime import timedelta

    query = select(Subscription).where(Subscription.id == subscription_id)
    result = await session.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription is None:
        return

    subscription.retry_count += 1
    subscription.last_retry_at = datetime.now(UTC)

    if subscription.retry_count >= 3:
        # Enter grace period (7 days)
        subscription.status = SubscriptionStatus.GRACE
        subscription.grace_period_end = datetime.now(UTC) + timedelta(days=7)

        logger.info(
            f"Subscription {subscription_id} entered grace period "
            f"after {subscription.retry_count} payment failures"
        )

        # Notify user
        await _create_expiration_notification(
            session, subscription.user_id, "warning"
        )
    else:
        subscription.status = SubscriptionStatus.PAST_DUE

        logger.info(
            f"Subscription {subscription_id} payment failed "
            f"({subscription.retry_count}/3)"
        )

    session.add(subscription)
    await session.flush()


async def handle_payment_success(
    session: AsyncSession,
    subscription_id: UUID,
) -> None:
    """Handle a successful payment.

    Args:
        session: Database session
        subscription_id: Subscription ID
    """
    query = select(Subscription).where(Subscription.id == subscription_id)
    result = await session.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription is None:
        return

    subscription.status = SubscriptionStatus.ACTIVE
    subscription.retry_count = 0
    subscription.grace_period_end = None
    subscription.grace_warning_sent = False
    subscription.last_payment_at = datetime.now(UTC)

    session.add(subscription)
    await session.flush()

    logger.info(f"Subscription {subscription_id} payment successful")
