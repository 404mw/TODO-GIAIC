"""Unit tests for Subscription Service.

Phase 17: User Story 10 - Pro Subscription Management (Priority: P4)

Tasks:
- T316: Test payment_captured activates Pro tier (FR-047)
- T317: Test 3 payment failures trigger grace period (FR-049)
- T318: Test grace period expiration downgrades to free (FR-050)
- T319: Test credit purchase limit 500/month enforced (FR-051)
- T320: Test webhook idempotent processing
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.subscription import Subscription
from src.models.user import User
from src.schemas.enums import SubscriptionStatus, UserTier


# =============================================================================
# HELPERS
# =============================================================================


async def _create_subscription(
    db_session: AsyncSession,
    user: User,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    checkout_subscription_id: str | None = None,
    **kwargs,
) -> Subscription:
    """Helper to create a subscription for a user."""
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        id=uuid4(),
        user_id=user.id,
        checkout_subscription_id=checkout_subscription_id or f"sub_{uuid4().hex[:16]}",
        status=status,
        current_period_start=now - timedelta(days=15),
        current_period_end=now + timedelta(days=15),
        **kwargs,
    )
    db_session.add(subscription)
    await db_session.flush()
    return subscription


# =============================================================================
# T316: PAYMENT CAPTURED ACTIVATES PRO TIER (FR-047)
# =============================================================================


class TestPaymentCaptured:
    """Test payment_captured webhook activates Pro tier."""

    @pytest.mark.asyncio
    async def test_payment_captured_activates_pro(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Payment captured should upgrade user to Pro tier and create subscription."""
        from src.services.subscription_service import SubscriptionService

        service = SubscriptionService(db_session, settings)

        result = await service.handle_payment_captured(
            user_id=test_user.id,
            checkout_subscription_id="sub_test_123",
            period_start=datetime.now(timezone.utc),
            period_end=datetime.now(timezone.utc) + timedelta(days=30),
        )

        assert result is not None
        assert result.status == SubscriptionStatus.ACTIVE

        # Verify user tier upgraded
        await db_session.refresh(test_user)
        assert test_user.tier == UserTier.PRO

    @pytest.mark.asyncio
    async def test_payment_captured_existing_subscription_renews(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Payment captured on existing subscription should renew it."""
        from src.services.subscription_service import SubscriptionService

        subscription = await _create_subscription(
            db_session, pro_user, status=SubscriptionStatus.ACTIVE
        )

        service = SubscriptionService(db_session, settings)
        new_period_start = datetime.now(timezone.utc)
        new_period_end = new_period_start + timedelta(days=30)

        result = await service.handle_payment_captured(
            user_id=pro_user.id,
            checkout_subscription_id=subscription.checkout_subscription_id,
            period_start=new_period_start,
            period_end=new_period_end,
        )

        assert result.status == SubscriptionStatus.ACTIVE
        assert result.failed_payment_count == 0
        assert result.retry_count == 0

    @pytest.mark.asyncio
    async def test_payment_captured_reactivates_grace(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Payment captured during grace period should reactivate subscription."""
        from src.services.subscription_service import SubscriptionService

        subscription = await _create_subscription(
            db_session,
            pro_user,
            status=SubscriptionStatus.GRACE,
            grace_period_end=datetime.now(timezone.utc) + timedelta(days=3),
            retry_count=3,
            failed_payment_count=3,
        )

        service = SubscriptionService(db_session, settings)

        result = await service.handle_payment_captured(
            user_id=pro_user.id,
            checkout_subscription_id=subscription.checkout_subscription_id,
            period_start=datetime.now(timezone.utc),
            period_end=datetime.now(timezone.utc) + timedelta(days=30),
        )

        assert result.status == SubscriptionStatus.ACTIVE
        assert result.grace_period_end is None
        assert result.retry_count == 0
        assert result.failed_payment_count == 0


# =============================================================================
# T317: 3 PAYMENT FAILURES TRIGGER GRACE PERIOD (FR-049)
# =============================================================================


class TestPaymentFailures:
    """Test payment failure handling and grace period trigger."""

    @pytest.mark.asyncio
    async def test_first_failure_sets_past_due(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """First payment failure should set status to past_due."""
        from src.services.subscription_service import SubscriptionService

        subscription = await _create_subscription(
            db_session, pro_user, status=SubscriptionStatus.ACTIVE
        )

        service = SubscriptionService(db_session, settings)
        result = await service.handle_payment_declined(
            checkout_subscription_id=subscription.checkout_subscription_id
        )

        assert result.status == SubscriptionStatus.PAST_DUE
        assert result.retry_count == 1

    @pytest.mark.asyncio
    async def test_second_failure_keeps_past_due(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Second payment failure should keep status as past_due."""
        from src.services.subscription_service import SubscriptionService

        subscription = await _create_subscription(
            db_session, pro_user, status=SubscriptionStatus.PAST_DUE,
            retry_count=1, failed_payment_count=1,
        )

        service = SubscriptionService(db_session, settings)
        result = await service.handle_payment_declined(
            checkout_subscription_id=subscription.checkout_subscription_id
        )

        assert result.status == SubscriptionStatus.PAST_DUE
        assert result.retry_count == 2

    @pytest.mark.asyncio
    async def test_third_failure_triggers_grace_period(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Third payment failure should trigger grace period (FR-049)."""
        from src.services.subscription_service import SubscriptionService

        subscription = await _create_subscription(
            db_session, pro_user, status=SubscriptionStatus.PAST_DUE,
            retry_count=2, failed_payment_count=2,
        )

        service = SubscriptionService(db_session, settings)
        result = await service.handle_payment_declined(
            checkout_subscription_id=subscription.checkout_subscription_id
        )

        assert result.status == SubscriptionStatus.GRACE
        assert result.grace_period_end is not None
        # Grace period should be ~7 days from now
        expected_grace_end = datetime.now(timezone.utc) + timedelta(days=7)
        assert abs((result.grace_period_end - expected_grace_end).total_seconds()) < 60


# =============================================================================
# T318: GRACE PERIOD EXPIRATION DOWNGRADES TO FREE (FR-050)
# =============================================================================


class TestGracePeriodExpiration:
    """Test grace period expiration and tier downgrade."""

    @pytest.mark.asyncio
    async def test_grace_expiration_downgrades_to_free(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Grace period expiration should downgrade user to free tier (FR-050)."""
        from src.services.subscription_service import SubscriptionService

        await _create_subscription(
            db_session,
            pro_user,
            status=SubscriptionStatus.GRACE,
            grace_period_end=datetime.now(timezone.utc) - timedelta(hours=1),
            retry_count=3,
            failed_payment_count=3,
        )

        service = SubscriptionService(db_session, settings)
        expired_count = await service.process_expired_grace_periods()

        assert expired_count == 1

        # Verify user downgraded
        await db_session.refresh(pro_user)
        assert pro_user.tier == UserTier.FREE

    @pytest.mark.asyncio
    async def test_active_grace_not_expired(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Active grace period should not trigger downgrade."""
        from src.services.subscription_service import SubscriptionService

        await _create_subscription(
            db_session,
            pro_user,
            status=SubscriptionStatus.GRACE,
            grace_period_end=datetime.now(timezone.utc) + timedelta(days=5),
            retry_count=3,
            failed_payment_count=3,
        )

        service = SubscriptionService(db_session, settings)
        expired_count = await service.process_expired_grace_periods()

        assert expired_count == 0

        # User should still be Pro
        await db_session.refresh(pro_user)
        assert pro_user.tier == UserTier.PRO


# =============================================================================
# T319: CREDIT PURCHASE LIMIT 500/MONTH ENFORCED (FR-051)
# =============================================================================


class TestCreditPurchaseLimit:
    """Test credit purchase monthly limit enforcement."""

    @pytest.mark.asyncio
    async def test_purchase_credits_within_limit(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Should allow credit purchase within 500/month limit (FR-051)."""
        from src.services.subscription_service import SubscriptionService

        await _create_subscription(db_session, pro_user)

        service = SubscriptionService(db_session, settings)
        result = await service.purchase_credits(
            user_id=pro_user.id,
            amount=100,
        )

        assert result["credits_added"] == 100
        assert result["monthly_purchased"] == 100
        assert result["monthly_remaining"] == 400

    @pytest.mark.asyncio
    async def test_purchase_credits_exceeds_limit(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Should reject credit purchase exceeding 500/month limit (FR-051)."""
        from src.services.subscription_service import SubscriptionService

        await _create_subscription(db_session, pro_user)

        service = SubscriptionService(db_session, settings)

        # First purchase: 400
        await service.purchase_credits(user_id=pro_user.id, amount=400)

        # Second purchase: 200 (would exceed 500 limit)
        with pytest.raises(ValueError, match="(?i)monthly.*limit"):
            await service.purchase_credits(user_id=pro_user.id, amount=200)

    @pytest.mark.asyncio
    async def test_purchase_credits_requires_pro(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Free tier users cannot purchase credits."""
        from src.services.subscription_service import SubscriptionService

        service = SubscriptionService(db_session, settings)

        with pytest.raises(ValueError, match="Pro"):
            await service.purchase_credits(user_id=test_user.id, amount=10)


# =============================================================================
# T320: WEBHOOK IDEMPOTENT PROCESSING
# =============================================================================


class TestWebhookIdempotency:
    """Test webhook event idempotent processing."""

    @pytest.mark.asyncio
    async def test_duplicate_payment_captured_idempotent(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Processing same payment_captured event twice should be idempotent."""
        from src.services.subscription_service import SubscriptionService

        service = SubscriptionService(db_session, settings)
        event_id = f"evt_{uuid4().hex[:16]}"
        now = datetime.now(timezone.utc)

        # First processing
        result1 = await service.process_webhook(
            event_id=event_id,
            event_type="payment_captured",
            data={
                "subscription_id": "sub_test_idem",
                "user_id": str(pro_user.id),
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )
        assert result1["processed"] is True

        # Second processing (duplicate)
        result2 = await service.process_webhook(
            event_id=event_id,
            event_type="payment_captured",
            data={
                "subscription_id": "sub_test_idem",
                "user_id": str(pro_user.id),
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )
        assert result2["processed"] is False
        assert result2.get("reason") == "duplicate"

    @pytest.mark.asyncio
    async def test_different_events_not_idempotent(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Different event IDs should both be processed."""
        from src.services.subscription_service import SubscriptionService

        service = SubscriptionService(db_session, settings)
        now = datetime.now(timezone.utc)

        sub_id = f"sub_test_diff_{uuid4().hex[:8]}"

        result1 = await service.process_webhook(
            event_id=f"evt_{uuid4().hex[:16]}",
            event_type="payment_captured",
            data={
                "subscription_id": sub_id,
                "user_id": str(pro_user.id),
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )

        result2 = await service.process_webhook(
            event_id=f"evt_{uuid4().hex[:16]}",
            event_type="payment_captured",
            data={
                "subscription_id": sub_id,
                "user_id": str(pro_user.id),
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )

        assert result1["processed"] is True
        assert result2["processed"] is True
