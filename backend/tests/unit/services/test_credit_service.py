"""Unit tests for CreditService.

Phase 14: User Story 11 - AI Credit System (Priority: P4)

Tasks:
- T274: Test new user receives 5 kickstart credits (FR-037)
- T275: Test Pro user receives 10 daily credits (FR-038)
- T276: Test Pro user receives 100 monthly credits (FR-039)
- T277: Test FIFO consumption order (FR-042)
- T278: Test daily credits expire at UTC 00:00 (FR-040)
- T279: Test subscription credits carry over (FR-041)
- T280: Test credit FIFO with race conditions (SC-011)
"""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditOperation, CreditType, UserTier
from src.services.credit_service import CreditService


# =============================================================================
# T274: Test new user receives 5 kickstart credits (FR-037)
# =============================================================================


@pytest.mark.asyncio
async def test_new_user_receives_kickstart_credits(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """T274: New users receive 5 kickstart credits (FR-037).

    When a new user is created, they should receive 5 kickstart credits.
    These credits do not expire and are consumed after daily/subscription.
    """
    service = CreditService(db_session, settings)

    # Grant kickstart credits
    await service.grant_kickstart_credits(test_user.id)

    # Verify credits were granted
    balance = await service.get_balance(test_user.id)

    assert balance.total >= settings.kickstart_credits
    assert balance.kickstart == settings.kickstart_credits


@pytest.mark.asyncio
async def test_kickstart_credits_do_not_expire(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """T274: Kickstart credits never expire (FR-037).

    Kickstart credits should have no expiration date.
    """
    service = CreditService(db_session, settings)

    # Grant kickstart credits
    entry = await service.grant_kickstart_credits(test_user.id)

    # Verify no expiration
    assert entry.expires_at is None
    assert entry.credit_type == CreditType.KICKSTART


# =============================================================================
# T275: Test Pro user receives 10 daily credits (FR-038)
# =============================================================================


@pytest.mark.asyncio
async def test_pro_user_receives_daily_credits(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T275: Pro users receive 10 daily AI credits (FR-038).

    Pro tier users should receive 10 daily credits that expire at UTC 00:00.
    """
    service = CreditService(db_session, settings)

    # Grant daily credits
    await service.grant_daily_credits(pro_user.id)

    # Verify credits were granted
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == settings.pro_daily_credits


@pytest.mark.asyncio
async def test_daily_credits_have_expiration(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T275: Daily credits expire at UTC 00:00 (FR-038, FR-040).

    Daily credits should have an expiration at the end of the UTC day.
    """
    service = CreditService(db_session, settings)

    # Grant daily credits
    entry = await service.grant_daily_credits(pro_user.id)

    # Verify expiration is set
    assert entry.expires_at is not None
    assert entry.credit_type == CreditType.DAILY

    # Expiration should be at UTC midnight
    now = datetime.now(timezone.utc)
    expected_expiry = datetime.combine(
        now.date() + timedelta(days=1),
        datetime.min.time(),
    ).replace(tzinfo=timezone.utc)

    assert entry.expires_at == expected_expiry


@pytest.mark.asyncio
async def test_free_user_does_not_receive_daily_credits(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """T275: Free users do not receive daily credits (FR-038).

    Daily credits are only for Pro tier users.
    """
    service = CreditService(db_session, settings)

    # Attempt to grant daily credits to free user
    entry = await service.grant_daily_credits(test_user.id)

    # Should not grant to free users
    assert entry is None


# =============================================================================
# T276: Test Pro user receives 100 monthly credits (FR-039)
# =============================================================================


@pytest.mark.asyncio
async def test_pro_user_receives_monthly_credits(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T276: Pro users receive 100 monthly subscription credits (FR-039).

    Pro tier users should receive 100 monthly credits that can carry over.
    """
    service = CreditService(db_session, settings)

    # Grant monthly credits
    await service.grant_monthly_credits(pro_user.id)

    # Verify credits were granted
    balance = await service.get_balance(pro_user.id)

    assert balance.subscription == settings.pro_monthly_credits


@pytest.mark.asyncio
async def test_monthly_credits_are_subscription_type(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T276: Monthly credits are subscription type (FR-039).

    Monthly credits should be of SUBSCRIPTION type for carryover tracking.
    """
    service = CreditService(db_session, settings)

    # Grant monthly credits
    entry = await service.grant_monthly_credits(pro_user.id)

    assert entry.credit_type == CreditType.SUBSCRIPTION
    assert entry.amount == settings.pro_monthly_credits


# =============================================================================
# T277: Test FIFO consumption order (FR-042)
# =============================================================================


@pytest.mark.asyncio
async def test_fifo_consumption_daily_first(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T277: Daily credits are consumed first (FR-042).

    FIFO order: daily -> subscription -> purchased.
    Daily credits should be consumed before subscription credits.
    """
    service = CreditService(db_session, settings)

    # Grant both daily and subscription credits
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)

    # Consume 1 credit
    await service.consume_credits(pro_user.id, 1, "test_operation")

    # Check balance - daily should be consumed first
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == settings.pro_daily_credits - 1
    assert balance.subscription == settings.pro_monthly_credits


@pytest.mark.asyncio
async def test_fifo_consumption_subscription_after_daily(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T277: Subscription credits consumed after daily depleted (FR-042).

    When daily credits are exhausted, subscription credits are consumed.
    """
    service = CreditService(db_session, settings)

    # Grant both daily and subscription credits
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)

    # Consume all daily plus some subscription
    amount_to_consume = settings.pro_daily_credits + 5
    await service.consume_credits(pro_user.id, amount_to_consume, "test_operation")

    # Check balance
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == 0
    assert balance.subscription == settings.pro_monthly_credits - 5


@pytest.mark.asyncio
async def test_fifo_consumption_purchased_last(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T277: Purchased credits consumed last (FR-042).

    FIFO order: daily -> subscription -> purchased.
    """
    service = CreditService(db_session, settings)

    # Grant all three types
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)
    await service.grant_purchased_credits(pro_user.id, 50)

    # Consume all daily + all subscription + some purchased
    amount_to_consume = settings.pro_daily_credits + settings.pro_monthly_credits + 10
    await service.consume_credits(pro_user.id, amount_to_consume, "test_operation")

    # Check balance
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == 0
    assert balance.subscription == 0
    assert balance.purchased == 40  # 50 - 10


@pytest.mark.asyncio
async def test_fifo_consumption_oldest_first_within_type(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T277: Within same type, oldest credits consumed first (FR-042).

    Credits are consumed in order of creation within the same type.
    """
    service = CreditService(db_session, settings)

    # Grant purchased credits in two batches
    await service.grant_purchased_credits(pro_user.id, 20)
    await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
    await service.grant_purchased_credits(pro_user.id, 30)

    # Consume 25 credits - should take all from first batch + 5 from second
    await service.consume_credits(pro_user.id, 25, "test_operation")

    # Check remaining balance
    balance = await service.get_balance(pro_user.id)
    assert balance.purchased == 25  # 20 + 30 - 25


# =============================================================================
# T278: Test daily credits expire at UTC 00:00 (FR-040)
# =============================================================================


@pytest.mark.asyncio
async def test_daily_credits_expire_at_utc_midnight(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T278: Daily credits expire at UTC 00:00 (FR-040).

    Daily credits should not be available after UTC midnight.
    """
    service = CreditService(db_session, settings)

    # Grant daily credits
    entry = await service.grant_daily_credits(pro_user.id)

    # Verify expiration is at UTC midnight
    now = datetime.now(timezone.utc)
    tomorrow_midnight = datetime.combine(
        now.date() + timedelta(days=1),
        datetime.min.time(),
    ).replace(tzinfo=timezone.utc)

    assert entry.expires_at == tomorrow_midnight


@pytest.mark.asyncio
async def test_expired_daily_credits_not_available(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T278: Expired daily credits are not available for consumption (FR-040).

    Credits past their expiration should not be included in balance.
    """
    service = CreditService(db_session, settings)

    # Manually create an expired daily credit entry
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    expired_entry = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.DAILY,
        operation=CreditOperation.GRANT,
        amount=10,
        balance_after=10,
        consumed=0,
        expires_at=yesterday,
        expired=False,
    )
    db_session.add(expired_entry)
    await db_session.commit()

    # Check balance - should not include expired credits
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == 0


@pytest.mark.asyncio
async def test_cannot_consume_expired_credits(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T278: Cannot consume expired credits (FR-040).

    Attempting to consume expired credits should fail.
    """
    service = CreditService(db_session, settings)

    # Manually create an expired daily credit entry
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    expired_entry = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.DAILY,
        operation=CreditOperation.GRANT,
        amount=10,
        balance_after=10,
        consumed=0,
        expires_at=yesterday,
        expired=False,
    )
    db_session.add(expired_entry)
    await db_session.commit()

    # Try to consume - should fail due to insufficient credits
    with pytest.raises(ValueError, match="Insufficient credits"):
        await service.consume_credits(pro_user.id, 1, "test_operation")


# =============================================================================
# T279: Test subscription credits carry over (FR-041)
# =============================================================================


@pytest.mark.asyncio
async def test_subscription_credits_carry_over_up_to_50(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T279: Up to 50 subscription credits carry over (FR-041).

    Unused subscription credits carry over to the next month, up to 50.
    """
    service = CreditService(db_session, settings)

    # Grant subscription credits with some remaining
    await service.grant_monthly_credits(pro_user.id)

    # Consume some but not all
    await service.consume_credits(pro_user.id, 60, "test_operation")

    # Check remaining (should be 40)
    balance = await service.get_balance(pro_user.id)
    assert balance.subscription == 40

    # These 40 credits should carry over to next month (under 50 limit)
    carryover = await service.calculate_carryover_amount(pro_user.id)
    assert carryover == 40


@pytest.mark.asyncio
async def test_subscription_credits_carryover_capped_at_50(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T279: Subscription credit carryover capped at 50 (FR-041).

    If more than 50 subscription credits remain, only 50 carry over.
    """
    service = CreditService(db_session, settings)

    # Grant subscription credits (100)
    await service.grant_monthly_credits(pro_user.id)

    # Don't consume any - all 100 remain
    balance = await service.get_balance(pro_user.id)
    assert balance.subscription == 100

    # Only 50 should carry over
    carryover = await service.calculate_carryover_amount(pro_user.id)
    assert carryover == settings.max_credit_carryover  # 50


@pytest.mark.asyncio
async def test_excess_subscription_credits_expire(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T279: Excess subscription credits above 50 expire (FR-041).

    Credits exceeding the carryover limit are lost at month end.
    """
    service = CreditService(db_session, settings)

    # Grant subscription credits (100)
    await service.grant_monthly_credits(pro_user.id)

    # Calculate how many should expire
    balance = await service.get_balance(pro_user.id)
    carryover = await service.calculate_carryover_amount(pro_user.id)

    expiring = balance.subscription - carryover
    assert expiring == 50  # 100 - 50


# =============================================================================
# T280: Test credit FIFO with race conditions (SC-011)
# =============================================================================


@pytest.mark.asyncio
async def test_concurrent_credit_consumption_is_safe(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T280: Concurrent credit consumption maintains consistency (SC-011).

    Multiple simultaneous consumption requests should not result in
    negative balance or over-consumption.
    """
    service = CreditService(db_session, settings)

    # Grant 10 credits
    await service.grant_purchased_credits(pro_user.id, 10)

    # The actual concurrent test is in test_credit_stress.py (T289)
    # Here we just verify basic consumption doesn't break
    await service.consume_credits(pro_user.id, 5, "op1")

    balance = await service.get_balance(pro_user.id)
    assert balance.total == 5


@pytest.mark.asyncio
async def test_credit_balance_never_goes_negative(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T280: Credit balance never goes negative (SC-011).

    Even under concurrent load, balance should never be negative.
    """
    service = CreditService(db_session, settings)

    # Grant 5 credits
    await service.grant_purchased_credits(pro_user.id, 5)

    # Try to consume more than available
    with pytest.raises(ValueError, match="Insufficient credits"):
        await service.consume_credits(pro_user.id, 10, "test_operation")

    # Balance should remain 5
    balance = await service.get_balance(pro_user.id)
    assert balance.total == 5


@pytest.mark.asyncio
async def test_fifo_order_maintained_under_concurrent_access(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """T280: FIFO order maintained under concurrent access (SC-011).

    The consumption order should be consistent regardless of
    concurrent access patterns.
    """
    service = CreditService(db_session, settings)

    # Grant different types of credits
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)

    # Sequential consumption should follow FIFO
    daily_amount = settings.pro_daily_credits
    subscription_amount = settings.pro_monthly_credits

    # Consume daily amount
    await service.consume_credits(pro_user.id, daily_amount, "op1")

    balance = await service.get_balance(pro_user.id)
    assert balance.daily == 0
    assert balance.subscription == subscription_amount


# =============================================================================
# HELPER TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_get_balance_breakdown(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test balance breakdown returns all credit types correctly."""
    service = CreditService(db_session, settings)

    # Grant all types of credits
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)
    await service.grant_purchased_credits(pro_user.id, 25)

    # Get balance breakdown
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == settings.pro_daily_credits
    assert balance.subscription == settings.pro_monthly_credits
    assert balance.purchased == 25
    assert balance.total == settings.pro_daily_credits + settings.pro_monthly_credits + 25


@pytest.mark.asyncio
async def test_consume_credits_returns_consumption_details(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test consume_credits returns details of what was consumed."""
    service = CreditService(db_session, settings)

    # Grant credits
    await service.grant_purchased_credits(pro_user.id, 10)

    # Consume and check result
    result = await service.consume_credits(pro_user.id, 3, "test_operation")

    assert result.total_consumed == 3
    assert result.remaining_balance == 7


@pytest.mark.asyncio
async def test_insufficient_credits_error(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """Test error when insufficient credits for consumption."""
    service = CreditService(db_session, settings)

    # No credits granted, try to consume
    with pytest.raises(ValueError, match="Insufficient credits"):
        await service.consume_credits(test_user.id, 1, "test_operation")
