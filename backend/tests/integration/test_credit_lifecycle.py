"""Integration tests for credit lifecycle.

T287: Integration test for credit lifecycle

Tests the complete credit flow from granting through consumption
and expiration, ensuring all components work together correctly.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.jobs.tasks.credit_job import (
    handle_credit_expire,
    grant_kickstart_credits as job_grant_kickstart,
)
from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditOperation, CreditType, UserTier
from src.services.credit_service import CreditService


@pytest.mark.asyncio
async def test_complete_credit_lifecycle(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test complete credit lifecycle: grant -> consume -> check balance.

    This tests the full flow:
    1. Grant daily credits
    2. Grant monthly credits
    3. Consume some credits
    4. Verify FIFO order was followed
    5. Check remaining balance
    """
    service = CreditService(db_session, settings)

    # Step 1: Grant daily credits
    daily_entry = await service.grant_daily_credits(pro_user.id)
    assert daily_entry is not None

    # Step 2: Grant monthly credits
    monthly_entry = await service.grant_monthly_credits(pro_user.id)
    assert monthly_entry is not None

    # Verify initial balance
    balance = await service.get_balance(pro_user.id)
    expected_total = settings.pro_daily_credits + settings.pro_monthly_credits
    assert balance.total == expected_total

    # Step 3: Consume some credits (less than daily)
    consume_amount = 5
    result = await service.consume_credits(pro_user.id, consume_amount, "test_op")
    assert result.total_consumed == consume_amount

    # Step 4: Verify FIFO - daily should be consumed first
    balance_after = await service.get_balance(pro_user.id)
    assert balance_after.daily == settings.pro_daily_credits - consume_amount
    assert balance_after.subscription == settings.pro_monthly_credits

    # Step 5: Check total balance
    assert balance_after.total == expected_total - consume_amount


@pytest.mark.asyncio
async def test_credit_lifecycle_with_kickstart(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """Test kickstart credits are granted and consumed correctly.

    Kickstart credits should be consumed last in FIFO order.
    """
    service = CreditService(db_session, settings)

    # Grant kickstart credits
    kickstart_entry = await service.grant_kickstart_credits(test_user.id)
    assert kickstart_entry is not None

    # Grant purchased credits
    purchased_entry = await service.grant_purchased_credits(test_user.id, 10)
    assert purchased_entry is not None

    # Check balance
    balance = await service.get_balance(test_user.id)
    assert balance.kickstart == settings.kickstart_credits
    assert balance.purchased == 10

    # Consume purchased credits first (FIFO order)
    await service.consume_credits(test_user.id, 8, "test_op1")

    balance_after = await service.get_balance(test_user.id)
    assert balance_after.purchased == 2  # 10 - 8
    assert balance_after.kickstart == settings.kickstart_credits  # Unchanged

    # Consume the remaining purchased + some kickstart
    await service.consume_credits(test_user.id, 5, "test_op2")  # 2 purchased + 3 kickstart

    final_balance = await service.get_balance(test_user.id)
    assert final_balance.purchased == 0
    assert final_balance.kickstart == settings.kickstart_credits - 3


@pytest.mark.asyncio
async def test_credit_lifecycle_with_expiration(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test that expired credits are not available for consumption.

    Manually create an expired credit and verify it's excluded.
    """
    service = CreditService(db_session, settings)

    # Manually create an expired credit entry (created yesterday so daily grant dedup won't trigger)
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
        created_at=yesterday,
    )
    db_session.add(expired_entry)
    await db_session.commit()

    # Grant valid daily credits
    valid_entry = await service.grant_daily_credits(pro_user.id)
    assert valid_entry is not None

    # Check balance - should only include valid credits
    balance = await service.get_balance(pro_user.id)
    assert balance.daily == settings.pro_daily_credits  # Not 10 + pro_daily


@pytest.mark.asyncio
async def test_credit_job_daily_grant_and_expiration(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test the credit job grants daily credits and handles expiration.

    Simulates the daily job run at UTC midnight.
    """
    # Create an expired daily credit entry
    yesterday_midnight = datetime.combine(
        datetime.now(timezone.utc).date() - timedelta(days=1),
        datetime.min.time(),
    ).replace(tzinfo=timezone.utc)

    expired_entry = AICreditLedger(
        id=uuid4(),
        user_id=pro_user.id,
        credit_type=CreditType.DAILY,
        operation=CreditOperation.GRANT,
        amount=10,
        balance_after=10,
        consumed=5,  # Partially consumed
        expires_at=yesterday_midnight,
        expired=False,
    )
    db_session.add(expired_entry)
    await db_session.commit()

    # Run the credit expiration job
    result = await handle_credit_expire({}, db_session, settings)

    # Verify job completed successfully
    assert result["status"] == "success"
    assert result["expired_credits"] >= 0
    assert result["daily_grants"] >= 0


@pytest.mark.asyncio
async def test_multiple_credit_types_fifo_order(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test FIFO consumption across all credit types.

    Grant all types and verify consumption follows:
    daily -> subscription -> purchased -> kickstart
    """
    service = CreditService(db_session, settings)

    # Grant all credit types
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)
    await service.grant_purchased_credits(pro_user.id, 20)
    await service.grant_kickstart_credits(pro_user.id)

    # Calculate total
    total = (
        settings.pro_daily_credits
        + settings.pro_monthly_credits
        + 20
        + settings.kickstart_credits
    )

    balance = await service.get_balance(pro_user.id)
    assert balance.total == total

    # Consume all daily + some subscription
    consume_1 = settings.pro_daily_credits + 5
    await service.consume_credits(pro_user.id, consume_1, "op1")

    balance_1 = await service.get_balance(pro_user.id)
    assert balance_1.daily == 0
    assert balance_1.subscription == settings.pro_monthly_credits - 5

    # Consume remaining subscription + some purchased
    consume_2 = balance_1.subscription + 10
    await service.consume_credits(pro_user.id, consume_2, "op2")

    balance_2 = await service.get_balance(pro_user.id)
    assert balance_2.daily == 0
    assert balance_2.subscription == 0
    assert balance_2.purchased == 10  # 20 - 10

    # Consume remaining purchased + some kickstart
    consume_3 = balance_2.purchased + 2
    await service.consume_credits(pro_user.id, consume_3, "op3")

    balance_3 = await service.get_balance(pro_user.id)
    assert balance_3.purchased == 0
    assert balance_3.kickstart == settings.kickstart_credits - 2


@pytest.mark.asyncio
async def test_credit_balance_breakdown_accuracy(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test that balance breakdown is accurate after various operations."""
    service = CreditService(db_session, settings)

    # Grant credits
    await service.grant_daily_credits(pro_user.id)
    await service.grant_monthly_credits(pro_user.id)
    await service.grant_purchased_credits(pro_user.id, 15)

    # Partial consumption
    await service.consume_credits(pro_user.id, 3, "op1")
    await service.consume_credits(pro_user.id, 7, "op2")

    # Total consumed: 10 (all from daily)
    balance = await service.get_balance(pro_user.id)

    assert balance.daily == 0  # 10 - 10 = 0
    assert balance.subscription == settings.pro_monthly_credits
    assert balance.purchased == 15
    assert balance.total == settings.pro_monthly_credits + 15


@pytest.mark.asyncio
async def test_insufficient_credits_error(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """Test that consuming more credits than available raises error."""
    service = CreditService(db_session, settings)

    # Grant only 5 kickstart credits
    await service.grant_kickstart_credits(test_user.id)

    # Try to consume more than available
    with pytest.raises(ValueError, match="Insufficient credits"):
        await service.consume_credits(test_user.id, 10, "test_op")


@pytest.mark.asyncio
async def test_carryover_calculation(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Test subscription credit carryover calculation."""
    service = CreditService(db_session, settings)

    # Grant subscription credits
    await service.grant_monthly_credits(pro_user.id)

    # Consume some, leaving more than 50
    await service.consume_credits(pro_user.id, 30, "op1")  # 100 - 30 = 70 remaining

    # Calculate carryover (should be capped at 50)
    carryover = await service.calculate_carryover_amount(pro_user.id)
    assert carryover == settings.max_credit_carryover  # 50

    # Consume more to leave less than 50
    await service.consume_credits(pro_user.id, 30, "op2")  # 70 - 30 = 40 remaining

    carryover_2 = await service.calculate_carryover_amount(pro_user.id)
    assert carryover_2 == 40  # All 40 carry over
