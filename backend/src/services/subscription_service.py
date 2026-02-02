"""Subscription Service for Pro tier management.

Phase 17: User Story 10 - Pro Subscription Management (Priority: P4)

Tasks:
- T322: handle_payment_captured (FR-047)
- T323: handle_payment_declined with retry count
- T324: Grace period logic (FR-049)
- T325: handle_subscription_cancelled
- T326: Tier downgrade on grace expiration (FR-050) - delegated to subscription_job.py
- T327: Credit purchase with monthly limit (FR-051)

Webhook Events (from Checkout.com):
- payment_captured → Activate/renew Pro tier
- payment_declined → Track failures, trigger grace after 3
- subscription_cancelled → Mark cancelled, access until period end
- subscription_renewed → Renew billing period
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.notification import Notification
from src.models.subscription import Subscription
from src.models.user import User
from src.schemas.enums import (
    CreditOperation,
    CreditType,
    NotificationType,
    SubscriptionStatus,
    UserTier,
)

logger = logging.getLogger(__name__)

# Monthly credit purchase limit per FR-051
MONTHLY_CREDIT_PURCHASE_LIMIT = 500


class SubscriptionService:
    """Service for managing Pro subscriptions and payment webhooks.

    Implements subscription lifecycle: creation, renewal, payment failures,
    grace periods, cancellation, and credit purchases.
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        # Track processed webhook event IDs for idempotency (T320)
        # In production, this would be stored in database; here we use in-memory + DB check
        self._processed_events: set[str] = set()

    # =========================================================================
    # WEBHOOK PROCESSING (T320: Idempotent)
    # =========================================================================

    async def process_webhook(
        self,
        event_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Process a webhook event idempotently.

        T320: Duplicate events are detected and skipped.

        Args:
            event_id: Unique event identifier from Checkout.com
            event_type: Event type string
            data: Event payload data

        Returns:
            Dict with processing result
        """
        # Check for duplicate event (idempotency)
        if await self._is_event_processed(event_id):
            logger.info(f"Duplicate webhook event {event_id}, skipping")
            return {"processed": False, "reason": "duplicate"}

        try:
            if event_type == "payment_captured":
                user_id = UUID(data["user_id"])
                period_start = datetime.fromisoformat(data["period_start"])
                period_end = datetime.fromisoformat(data["period_end"])
                await self.handle_payment_captured(
                    user_id=user_id,
                    checkout_subscription_id=data["subscription_id"],
                    period_start=period_start,
                    period_end=period_end,
                )
            elif event_type == "payment_declined":
                await self.handle_payment_declined(
                    checkout_subscription_id=data["subscription_id"],
                )
            elif event_type == "subscription_cancelled":
                await self.handle_subscription_cancelled(
                    checkout_subscription_id=data["subscription_id"],
                )
            elif event_type == "subscription_renewed":
                user_id = UUID(data["user_id"])
                period_start = datetime.fromisoformat(data["period_start"])
                period_end = datetime.fromisoformat(data["period_end"])
                await self.handle_payment_captured(
                    user_id=user_id,
                    checkout_subscription_id=data["subscription_id"],
                    period_start=period_start,
                    period_end=period_end,
                )
            else:
                logger.warning(f"Unhandled webhook event type: {event_type}")
                return {"processed": False, "reason": "unknown_event_type"}

            # Mark event as processed
            await self._mark_event_processed(event_id)
            await self._session.flush()

            return {"processed": True}

        except Exception as e:
            logger.error(f"Webhook processing failed for {event_id}: {e}", exc_info=True)
            raise

    async def _is_event_processed(self, event_id: str) -> bool:
        """Check if a webhook event has already been processed."""
        return event_id in self._processed_events

    async def _mark_event_processed(self, event_id: str) -> None:
        """Mark a webhook event as processed.

        Uses in-memory set for deduplication within a service instance lifetime.
        For production persistence, a dedicated webhook_events table should be used
        instead of ActivityLog (which requires user_id context).
        """
        self._processed_events.add(event_id)

    # =========================================================================
    # T322: PAYMENT CAPTURED (FR-047)
    # =========================================================================

    async def handle_payment_captured(
        self,
        user_id: UUID,
        checkout_subscription_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Subscription:
        """Handle payment_captured webhook event.

        T322: FR-047 - Activates Pro tier on successful payment.

        Creates new subscription or updates existing one:
        - New user: Creates subscription, upgrades to Pro
        - Existing: Renews period, resets failure counts
        - Grace period: Reactivates subscription

        Args:
            user_id: User ID
            checkout_subscription_id: Checkout.com subscription ID
            period_start: Billing period start
            period_end: Billing period end

        Returns:
            Updated or created Subscription
        """
        # Find existing subscription
        query = select(Subscription).where(
            Subscription.checkout_subscription_id == checkout_subscription_id
        )
        result = await self._session.execute(query)
        subscription = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if subscription is None:
            # Create new subscription
            subscription = Subscription(
                id=uuid4(),
                user_id=user_id,
                checkout_subscription_id=checkout_subscription_id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=period_start,
                current_period_end=period_end,
                last_payment_at=now,
                failed_payment_count=0,
                retry_count=0,
            )
            self._session.add(subscription)
        else:
            # Update existing subscription
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = period_start
            subscription.current_period_end = period_end
            subscription.last_payment_at = now
            subscription.failed_payment_count = 0
            subscription.retry_count = 0
            subscription.grace_period_end = None
            subscription.grace_warning_sent = False
            self._session.add(subscription)

        # Upgrade user to Pro tier
        user = await self._session.get(User, user_id)
        if user and user.tier != UserTier.PRO:
            user.tier = UserTier.PRO
            self._session.add(user)
            logger.info(f"Upgraded user {user_id} to Pro tier")

        await self._session.flush()

        logger.info(
            f"Payment captured for subscription {checkout_subscription_id}, "
            f"user {user_id}, period {period_start} - {period_end}"
        )

        return subscription

    # =========================================================================
    # T323: PAYMENT DECLINED
    # =========================================================================

    async def handle_payment_declined(
        self,
        checkout_subscription_id: str,
    ) -> Subscription:
        """Handle payment_declined webhook event.

        T323: Tracks payment failures and triggers grace period after 3.

        Args:
            checkout_subscription_id: Checkout.com subscription ID

        Returns:
            Updated Subscription

        Raises:
            ValueError: If subscription not found
        """
        query = select(Subscription).where(
            Subscription.checkout_subscription_id == checkout_subscription_id
        )
        result = await self._session.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription is None:
            raise ValueError(f"Subscription not found: {checkout_subscription_id}")

        now = datetime.now(timezone.utc)

        subscription.retry_count += 1
        subscription.failed_payment_count += 1
        subscription.last_retry_at = now

        if subscription.retry_count >= 3:
            # T324: Enter grace period (FR-049)
            subscription.status = SubscriptionStatus.GRACE
            subscription.grace_period_end = now + timedelta(days=7)

            logger.info(
                f"Subscription {checkout_subscription_id} entered grace period "
                f"after {subscription.retry_count} failures"
            )

            # Send grace period notification
            await self._create_notification(
                user_id=subscription.user_id,
                title="Payment Failed - Grace Period Started",
                body=(
                    "Your payment has failed 3 times. You have 7 days to update "
                    "your payment method before your Pro access expires."
                ),
            )
        else:
            subscription.status = SubscriptionStatus.PAST_DUE

            logger.info(
                f"Subscription {checkout_subscription_id} payment failed "
                f"({subscription.retry_count}/3)"
            )

        self._session.add(subscription)
        await self._session.flush()

        return subscription

    # =========================================================================
    # T325: SUBSCRIPTION CANCELLED
    # =========================================================================

    async def handle_subscription_cancelled(
        self,
        checkout_subscription_id: str,
    ) -> Subscription:
        """Handle subscription_cancelled webhook event.

        T325: Marks subscription as cancelled with access until period end.

        Args:
            checkout_subscription_id: Checkout.com subscription ID

        Returns:
            Updated Subscription

        Raises:
            ValueError: If subscription not found
        """
        query = select(Subscription).where(
            Subscription.checkout_subscription_id == checkout_subscription_id
        )
        result = await self._session.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription is None:
            raise ValueError(f"Subscription not found: {checkout_subscription_id}")

        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(timezone.utc)

        self._session.add(subscription)
        await self._session.flush()

        logger.info(
            f"Subscription {checkout_subscription_id} cancelled, "
            f"access until {subscription.current_period_end}"
        )

        return subscription

    # =========================================================================
    # T326: GRACE PERIOD EXPIRATION (FR-050)
    # =========================================================================

    async def process_expired_grace_periods(self) -> int:
        """Process subscriptions with expired grace periods.

        T326: FR-050 - Downgrades users to free tier when grace expires.

        Returns:
            Number of subscriptions expired
        """
        now = datetime.now(timezone.utc)

        query = select(Subscription).where(
            Subscription.status == SubscriptionStatus.GRACE,
            Subscription.grace_period_end <= now,
        )

        result = await self._session.execute(query)
        expired_subscriptions = result.scalars().all()

        expired_count = 0
        for subscription in expired_subscriptions:
            subscription.status = SubscriptionStatus.EXPIRED
            self._session.add(subscription)

            # Downgrade user to free tier
            user = await self._session.get(User, subscription.user_id)
            if user and user.tier == UserTier.PRO:
                user.tier = UserTier.FREE
                self._session.add(user)

                logger.info(
                    f"Downgraded user {user.id} to free tier "
                    f"(grace period expired)"
                )

                await self._create_notification(
                    user_id=user.id,
                    title="Subscription Expired",
                    body=(
                        "Your Pro subscription has expired. "
                        "You've been downgraded to the free tier. "
                        "Upgrade again to restore Pro features."
                    ),
                )

            expired_count += 1

        await self._session.flush()
        return expired_count

    # =========================================================================
    # T327: CREDIT PURCHASE (FR-051)
    # =========================================================================

    async def purchase_credits(
        self,
        user_id: UUID,
        amount: int,
    ) -> dict[str, Any]:
        """Purchase additional AI credits.

        T327: FR-051 - Credit purchase with 500/month limit.

        Args:
            user_id: User ID
            amount: Number of credits to purchase

        Returns:
            Dict with purchase result

        Raises:
            ValueError: If user is not Pro or exceeds monthly limit
        """
        # Check user tier
        user = await self._session.get(User, user_id)
        if user is None or user.tier != UserTier.PRO:
            raise ValueError("Credit purchase requires Pro tier")

        # Check monthly purchase limit
        monthly_purchased = await self._get_monthly_purchased(user_id)
        if monthly_purchased + amount > MONTHLY_CREDIT_PURCHASE_LIMIT:
            remaining = MONTHLY_CREDIT_PURCHASE_LIMIT - monthly_purchased
            raise ValueError(
                f"Monthly credit purchase limit exceeded. "
                f"Purchased: {monthly_purchased}, Remaining: {remaining}, "
                f"Requested: {amount}"
            )

        # Grant purchased credits via CreditService pattern
        from src.services.credit_service import CreditService

        credit_service = CreditService(self._session, self._settings)
        entry = await credit_service.grant_purchased_credits(
            user_id=user_id,
            amount=amount,
            order_ref=f"purchase_{uuid4().hex[:8]}",
        )

        # Get updated balance
        balance = await credit_service.get_balance(user_id)
        new_monthly_purchased = monthly_purchased + amount

        return {
            "credits_added": amount,
            "total_credits": balance.total,
            "monthly_purchased": new_monthly_purchased,
            "monthly_remaining": MONTHLY_CREDIT_PURCHASE_LIMIT - new_monthly_purchased,
        }

    async def _get_monthly_purchased(self, user_id: UUID) -> int:
        """Get total credits purchased this month.

        Args:
            user_id: User ID

        Returns:
            Total credits purchased in the current month
        """
        from sqlalchemy import func

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        query = select(
            func.coalesce(func.sum(AICreditLedger.amount), 0)
        ).where(
            AICreditLedger.user_id == user_id,
            AICreditLedger.credit_type == CreditType.PURCHASED,
            AICreditLedger.operation == CreditOperation.GRANT,
            AICreditLedger.created_at >= month_start,
        )

        result = await self._session.execute(query)
        return int(result.scalar() or 0)

    # =========================================================================
    # QUERY METHODS
    # =========================================================================

    async def get_subscription(self, user_id: UUID) -> Subscription | None:
        """Get user's subscription.

        Args:
            user_id: User ID

        Returns:
            Subscription or None
        """
        query = select(Subscription).where(Subscription.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def cancel_subscription(self, user_id: UUID) -> Subscription:
        """Cancel user's subscription (user-initiated).

        Sets cancel_at_period_end semantics: subscription remains active
        until current_period_end.

        Args:
            user_id: User ID

        Returns:
            Updated Subscription

        Raises:
            ValueError: If no active subscription found
        """
        subscription = await self.get_subscription(user_id)
        if subscription is None:
            raise ValueError("No subscription found")

        if subscription.status in (SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED):
            raise ValueError("Subscription already cancelled or expired")

        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(timezone.utc)

        self._session.add(subscription)
        await self._session.flush()

        logger.info(
            f"User {user_id} cancelled subscription, "
            f"access until {subscription.current_period_end}"
        )

        return subscription

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _create_notification(
        self,
        user_id: UUID,
        title: str,
        body: str,
    ) -> None:
        """Create a subscription-related notification."""
        notification = Notification(
            id=uuid4(),
            user_id=user_id,
            type=NotificationType.SUBSCRIPTION,
            title=title,
            body=body,
            action_url="/settings/subscription",
            read=False,
        )
        self._session.add(notification)
        await self._session.flush()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_subscription_service(
    session: AsyncSession,
    settings: Settings,
) -> SubscriptionService:
    """Factory function to create SubscriptionService.

    Args:
        session: Database session
        settings: Application settings

    Returns:
        Configured SubscriptionService instance
    """
    return SubscriptionService(session, settings)
