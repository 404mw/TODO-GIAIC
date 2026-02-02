"""
Integration Tests: Webhook Processing Performance
T395: Webhook processing < 30 seconds (SC-008)

Tests that webhook events are processed within acceptable time.
"""
import time
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from src.config import Settings
from src.models.subscription import Subscription
from src.models.user import User
from src.schemas.enums import SubscriptionStatus, UserTier
from src.services.subscription_service import SubscriptionService


# =============================================================================
# T395: SC-008 – Webhook Processing Time
# =============================================================================


class TestWebhookProcessingPerformance:
    """
    SC-008: Webhook Processing
    Target: Webhook processing < 30 seconds
    """

    @pytest.mark.asyncio
    async def test_payment_captured_under_30_seconds(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """payment_captured webhook processes within 30 seconds (SC-008)."""
        service = SubscriptionService(db_session, settings)

        now = datetime.now(timezone.utc)

        start = time.perf_counter()

        result = await service.process_webhook(
            event_id=f"evt_{uuid4().hex[:16]}",
            event_type="payment_captured",
            data={
                "user_id": str(test_user.id),
                "subscription_id": f"sub_{uuid4().hex[:16]}",
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )

        elapsed = time.perf_counter() - start

        assert result["processed"] is True
        assert elapsed < 30.0, (
            f"payment_captured took {elapsed:.3f}s, exceeds 30s (SC-008)"
        )

    @pytest.mark.asyncio
    async def test_payment_declined_under_30_seconds(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """payment_declined webhook processes within 30 seconds (SC-008)."""
        service = SubscriptionService(db_session, settings)

        now = datetime.now(timezone.utc)
        sub_id = f"sub_{uuid4().hex[:16]}"

        # First create a subscription
        await service.process_webhook(
            event_id=f"evt_{uuid4().hex[:16]}",
            event_type="payment_captured",
            data={
                "user_id": str(test_user.id),
                "subscription_id": sub_id,
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )
        await db_session.commit()

        # Now test payment_declined
        start = time.perf_counter()

        result = await service.process_webhook(
            event_id=f"evt_{uuid4().hex[:16]}",
            event_type="payment_declined",
            data={"subscription_id": sub_id},
        )

        elapsed = time.perf_counter() - start

        assert result["processed"] is True
        assert elapsed < 30.0, (
            f"payment_declined took {elapsed:.3f}s, exceeds 30s (SC-008)"
        )

    @pytest.mark.asyncio
    async def test_webhook_batch_processing_performance(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Multiple webhook events process efficiently (SC-008)."""
        service = SubscriptionService(db_session, settings)

        now = datetime.now(timezone.utc)
        times: List[float] = []

        for i in range(10):
            sub_id = f"sub_batch_{i}_{uuid4().hex[:8]}"

            start = time.perf_counter()

            await service.process_webhook(
                event_id=f"evt_batch_{i}_{uuid4().hex[:8]}",
                event_type="payment_captured",
                data={
                    "user_id": str(test_user.id),
                    "subscription_id": sub_id,
                    "period_start": now.isoformat(),
                    "period_end": (now + timedelta(days=30)).isoformat(),
                },
            )

            elapsed = time.perf_counter() - start
            times.append(elapsed)

            await db_session.commit()

        avg = sum(times) / len(times)
        max_time = max(times)

        assert max_time < 30.0, (
            f"Worst webhook took {max_time:.3f}s, exceeds 30s (SC-008)"
        )
        # Average should be well under threshold
        assert avg < 5.0, (
            f"Average webhook {avg:.3f}s is too high"
        )

    @pytest.mark.asyncio
    async def test_duplicate_webhook_idempotent_fast(
        self, db_session: AsyncSession, test_user: User, settings: Settings
    ):
        """Duplicate webhook events are handled quickly (idempotency)."""
        service = SubscriptionService(db_session, settings)

        now = datetime.now(timezone.utc)
        event_id = f"evt_dup_{uuid4().hex[:16]}"

        # First processing
        await service.process_webhook(
            event_id=event_id,
            event_type="payment_captured",
            data={
                "user_id": str(test_user.id),
                "subscription_id": f"sub_{uuid4().hex[:16]}",
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )
        await db_session.commit()

        # Duplicate processing should be fast
        start = time.perf_counter()

        result = await service.process_webhook(
            event_id=event_id,
            event_type="payment_captured",
            data={
                "user_id": str(test_user.id),
                "subscription_id": f"sub_{uuid4().hex[:16]}",
                "period_start": now.isoformat(),
                "period_end": (now + timedelta(days=30)).isoformat(),
            },
        )

        elapsed = time.perf_counter() - start

        assert result["processed"] is False
        assert result["reason"] == "duplicate"
        # Duplicate detection should be very fast
        assert elapsed < 1.0, (
            f"Duplicate detection took {elapsed:.3f}s, should be < 1s"
        )
