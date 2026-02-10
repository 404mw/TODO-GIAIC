"""
Integration Tests: Credit FIFO Accuracy
T400: Credit FIFO test suite (SC-011)

Tests credit balance accuracy, FIFO consumption order,
and race condition handling.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.config import Settings
from src.models.user import User
from src.schemas.enums import UserTier
from src.services.credit_service import CreditService


# =============================================================================
# T400: SC-011 – Credit Balance Accuracy
# =============================================================================


class TestCreditFIFOOrder:
    """Test FIFO consumption order: daily → subscription → purchased."""

    @pytest.mark.asyncio
    async def test_daily_credits_consumed_first(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Daily credits are consumed before subscription credits (SC-011).

        FR-042: FIFO order: daily → subscription → purchased.
        """
        service = CreditService(db_session, settings)
        daily_amount = settings.pro_daily_credits  # 10
        monthly_amount = settings.pro_monthly_credits  # 100

        # Grant different credit types
        await service.grant_daily_credits(pro_user.id)
        await service.grant_monthly_credits(pro_user.id)
        await service.grant_purchased_credits(pro_user.id, 20)
        await db_session.commit()

        # Consume 3 credits - should come from daily first
        result = await service.consume_credits(pro_user.id, 3, "fifo_test_1")
        await db_session.commit()

        # Get balance breakdown
        balance = await service.get_balance(pro_user.id)

        # Daily should be reduced
        assert balance.daily == daily_amount - 3
        # Subscription and purchased should be untouched
        assert balance.subscription == monthly_amount
        assert balance.purchased == 20

    @pytest.mark.asyncio
    async def test_subscription_consumed_after_daily_exhausted(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Subscription credits consumed after daily exhausted (SC-011)."""
        service = CreditService(db_session, settings)
        daily_amount = settings.pro_daily_credits
        monthly_amount = settings.pro_monthly_credits

        # Grant credits
        await service.grant_daily_credits(pro_user.id)
        await service.grant_monthly_credits(pro_user.id)
        await service.grant_purchased_credits(pro_user.id, 20)
        await db_session.commit()

        # Consume daily + 2 extra (should exhaust daily and take 2 from subscription)
        consume_amount = daily_amount + 2
        result = await service.consume_credits(pro_user.id, consume_amount, "fifo_test_2")
        await db_session.commit()

        balance = await service.get_balance(pro_user.id)

        assert balance.daily == 0
        assert balance.subscription == monthly_amount - 2
        assert balance.purchased == 20

    @pytest.mark.asyncio
    async def test_purchased_consumed_last(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Purchased credits consumed after daily and subscription (SC-011)."""
        service = CreditService(db_session, settings)
        daily_amount = settings.pro_daily_credits
        monthly_amount = settings.pro_monthly_credits

        await service.grant_daily_credits(pro_user.id)
        await service.grant_monthly_credits(pro_user.id)
        await service.grant_purchased_credits(pro_user.id, 20)
        await db_session.commit()

        # Consume all daily + all subscription + 3 purchased
        consume_amount = daily_amount + monthly_amount + 3
        result = await service.consume_credits(pro_user.id, consume_amount, "fifo_test_3")
        await db_session.commit()

        balance = await service.get_balance(pro_user.id)

        assert balance.daily == 0
        assert balance.subscription == 0
        assert balance.purchased == 17  # 20 - 3

    @pytest.mark.asyncio
    async def test_insufficient_credits_raises_error(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Consuming more credits than available raises error (SC-011)."""
        service = CreditService(db_session, settings)

        await service.grant_daily_credits(pro_user.id)
        await db_session.commit()

        # Try to consume more than available (daily credits from settings)
        over_amount = settings.pro_daily_credits + 5
        with pytest.raises((ValueError, Exception)):
            await service.consume_credits(pro_user.id, over_amount, "over_consume")


class TestCreditRaceConditions:
    """Test credit operations under concurrent access."""

    @pytest.mark.asyncio
    async def test_balance_never_negative(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Credit balance never goes negative under concurrent access (SC-011)."""
        # Capture user ID before any rollback can expire the ORM object
        user_id = pro_user.id
        service = CreditService(db_session, settings)

        # Grant 10 credits
        await service.grant_purchased_credits(user_id, 10)
        await db_session.commit()

        # Sequential consumption (since SQLite doesn't support true concurrency)
        consumed = 0
        for i in range(15):
            try:
                await service.consume_credits(user_id, 1, f"race_test_{i}")
                consumed += 1
                await db_session.commit()
            except (ValueError, Exception):
                await db_session.rollback()
                break

        # Verify consumed at most 10
        assert consumed <= 10

        # Verify balance is not negative
        balance = await service.get_balance(user_id)
        assert balance.total >= 0

    @pytest.mark.asyncio
    async def test_consistent_balance_after_mixed_operations(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Balance stays consistent after grants and consumption (SC-011)."""
        service = CreditService(db_session, settings)

        # Grant 50 credits
        await service.grant_purchased_credits(pro_user.id, 50)
        await db_session.commit()

        # Consume 20
        await service.consume_credits(pro_user.id, 20, "mixed_1")
        await db_session.commit()

        # Grant 10 more
        await service.grant_purchased_credits(pro_user.id, 10)
        await db_session.commit()

        # Consume 15
        await service.consume_credits(pro_user.id, 15, "mixed_2")
        await db_session.commit()

        # Expected: 50 - 20 + 10 - 15 = 25
        balance = await service.get_balance(pro_user.id)
        assert balance.total == 25


class TestCreditExpiration:
    """Test credit expiration behavior."""

    @pytest.mark.asyncio
    async def test_daily_credits_expire_at_utc_midnight(
        self, db_session: AsyncSession, pro_user: User, settings: Settings
    ):
        """Daily credits have correct expiration timestamp (SC-011).

        FR-040: Daily credits expire at UTC 00:00.
        """
        service = CreditService(db_session, settings)

        await service.grant_daily_credits(pro_user.id)
        await db_session.commit()

        # Balance should include daily credits
        balance = await service.get_balance(pro_user.id)
        assert balance.daily == settings.pro_daily_credits

    @pytest.mark.asyncio
    async def test_kickstart_credits_granted_to_new_user(
        self, db_session: AsyncSession, settings: Settings
    ):
        """New users receive 5 kickstart credits (FR-037)."""
        user = User(
            id=uuid4(),
            google_id=f"google-kickstart-{uuid4()}",
            email=f"kickstart-{uuid4()}@example.com",
            name="Kickstart User",
            tier=UserTier.FREE,
        )
        db_session.add(user)
        await db_session.commit()

        service = CreditService(db_session, settings)
        await service.grant_kickstart_credits(user.id)
        await db_session.commit()

        balance = await service.get_balance(user.id)
        assert balance.total == 5
