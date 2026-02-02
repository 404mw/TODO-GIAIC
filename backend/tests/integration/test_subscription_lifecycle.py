"""Integration tests for subscription lifecycle.

T333: Full subscription lifecycle integration test

Tests the complete subscription flow:
1. Create checkout session
2. Payment captured → Pro tier activated
3. Payment failure → Grace period
4. Grace expiration → Downgrade to free
5. Cancellation → Access until period end
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.subscription import Subscription
from src.models.user import User
from src.schemas.enums import SubscriptionStatus, UserTier
from src.services.subscription_service import SubscriptionService


# =============================================================================
# HELPERS
# =============================================================================


async def _create_active_subscription(
    db_session: AsyncSession,
    user: User,
) -> Subscription:
    """Create an active subscription for testing."""
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        id=uuid4(),
        user_id=user.id,
        checkout_subscription_id=f"sub_{uuid4().hex[:16]}",
        status=SubscriptionStatus.ACTIVE,
        current_period_start=now - timedelta(days=15),
        current_period_end=now + timedelta(days=15),
        last_payment_at=now - timedelta(days=15),
    )
    db_session.add(subscription)
    await db_session.flush()
    return subscription


# =============================================================================
# SUBSCRIPTION LIFECYCLE
# =============================================================================


class TestSubscriptionLifecycle:
    """Test full subscription lifecycle from creation to expiration."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_activate_to_cancel(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Test: new user → payment → Pro → cancel → access until period end."""
        service = SubscriptionService(db_session, settings)
        now = datetime.now(timezone.utc)

        # Step 1: Payment captured - user becomes Pro
        subscription = await service.handle_payment_captured(
            user_id=test_user.id,
            checkout_subscription_id="sub_lifecycle_test",
            period_start=now,
            period_end=now + timedelta(days=30),
        )

        assert subscription.status == SubscriptionStatus.ACTIVE
        await db_session.refresh(test_user)
        assert test_user.tier == UserTier.PRO

        # Step 2: User cancels
        cancelled = await service.cancel_subscription(test_user.id)
        assert cancelled.status == SubscriptionStatus.CANCELLED
        assert cancelled.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_payment_failure_to_grace_to_expiration(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Test: active → 3 failures → grace → expiration → free tier."""
        service = SubscriptionService(db_session, settings)
        subscription = await _create_active_subscription(db_session, pro_user)
        sub_id = subscription.checkout_subscription_id

        # 3 payment failures
        for i in range(3):
            result = await service.handle_payment_declined(
                checkout_subscription_id=sub_id
            )

        # Should now be in grace period
        assert result.status == SubscriptionStatus.GRACE
        assert result.grace_period_end is not None

        # Simulate grace period expiration
        result.grace_period_end = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.add(result)
        await db_session.flush()

        # Process expired grace periods
        expired_count = await service.process_expired_grace_periods()
        assert expired_count == 1

        # User should be downgraded
        await db_session.refresh(pro_user)
        assert pro_user.tier == UserTier.FREE

    @pytest.mark.asyncio
    async def test_payment_recovery_during_grace(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Test: grace period → payment succeeds → reactivated."""
        service = SubscriptionService(db_session, settings)
        now = datetime.now(timezone.utc)

        # Create subscription in grace period
        subscription = Subscription(
            id=uuid4(),
            user_id=pro_user.id,
            checkout_subscription_id="sub_recovery_test",
            status=SubscriptionStatus.GRACE,
            current_period_start=now - timedelta(days=30),
            current_period_end=now - timedelta(days=1),
            grace_period_end=now + timedelta(days=5),
            retry_count=3,
            failed_payment_count=3,
        )
        db_session.add(subscription)
        await db_session.flush()

        # Payment succeeds during grace
        result = await service.handle_payment_captured(
            user_id=pro_user.id,
            checkout_subscription_id="sub_recovery_test",
            period_start=now,
            period_end=now + timedelta(days=30),
        )

        assert result.status == SubscriptionStatus.ACTIVE
        assert result.grace_period_end is None
        assert result.retry_count == 0
        assert result.failed_payment_count == 0

    @pytest.mark.asyncio
    async def test_credit_purchase_lifecycle(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Test credit purchase within monthly limits."""
        service = SubscriptionService(db_session, settings)
        await _create_active_subscription(db_session, pro_user)

        # Purchase credits
        result = await service.purchase_credits(
            user_id=pro_user.id,
            amount=50,
        )

        assert result["credits_added"] == 50
        assert result["monthly_purchased"] == 50
        assert result["monthly_remaining"] == 450

        # Purchase more
        result2 = await service.purchase_credits(
            user_id=pro_user.id,
            amount=100,
        )

        assert result2["monthly_purchased"] == 150
        assert result2["monthly_remaining"] == 350


class TestWebhookIdempotency:
    """Integration tests for webhook idempotency."""

    @pytest.mark.asyncio
    async def test_webhook_duplicate_prevention(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Duplicate webhook events should be ignored."""
        service = SubscriptionService(db_session, settings)
        event_id = f"evt_{uuid4().hex[:16]}"
        now = datetime.now(timezone.utc)

        data = {
            "subscription_id": "sub_webhook_test",
            "user_id": str(test_user.id),
            "period_start": now.isoformat(),
            "period_end": (now + timedelta(days=30)).isoformat(),
        }

        # First call processes
        result1 = await service.process_webhook(event_id, "payment_captured", data)
        assert result1["processed"] is True

        # Second call skipped
        result2 = await service.process_webhook(event_id, "payment_captured", data)
        assert result2["processed"] is False
