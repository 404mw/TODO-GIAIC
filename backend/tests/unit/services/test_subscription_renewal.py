"""Unit tests for subscription credit renewal with carryover.

Task 7.1 / FR-007: Monthly subscription credit renewal with carryover.

Tests:
- User with 30 sub credits → renewal → balance = 80 (50 new + 30 carryover)
- User with 60 sub credits → renewal → balance = 100 (50 new + 50 capped)
- Free-tier user unaffected by subscription renewal job
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditOperation, CreditType
from src.services.credit_service import CreditService


# =============================================================================
# HELPERS
# =============================================================================


async def _grant_subscription_credits(
    session: AsyncSession, user_id, amount: int
) -> AICreditLedger:
    """Directly insert a SUBSCRIPTION GRANT ledger entry."""
    entry = AICreditLedger(
        id=uuid4(),
        user_id=user_id,
        credit_type=CreditType.SUBSCRIPTION,
        operation=CreditOperation.GRANT,
        amount=amount,
        balance_after=amount,
        consumed=0,
        expired=False,
        expires_at=None,
    )
    session.add(entry)
    await session.flush()
    return entry


# =============================================================================
# FR-007: SUBSCRIPTION CREDIT CARRYOVER
# =============================================================================


@pytest.mark.asyncio
async def test_renewal_with_30_sub_credits_gives_80_total(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Task 7.1 / FR-007: user with 30 sub credits → monthly renewal → balance = 80.

    Carryover = min(30, 50) = 30. Fresh = 50. Total = 80.
    """
    service = CreditService(db_session, settings)

    # Grant 30 subscription credits (prior balance)
    await _grant_subscription_credits(db_session, pro_user.id, 30)

    # Verify initial balance
    balance_before = await service.get_balance(pro_user.id)
    assert balance_before.subscription == 30

    # Run monthly renewal
    entry = await service.renew_subscription_credits(pro_user.id)

    # Renewal should succeed for Pro user
    assert entry is not None
    # carryover = min(30, 50) = 30; fresh = 50; total = 80
    assert entry.amount == 80
    assert entry.credit_type == CreditType.SUBSCRIPTION
    assert entry.operation == CreditOperation.GRANT

    # Verify final balance equals new grant only (old entries expired)
    balance_after = await service.get_balance(pro_user.id)
    assert balance_after.subscription == 80


@pytest.mark.asyncio
async def test_renewal_with_60_sub_credits_gives_100_total_capped(
    db_session: AsyncSession,
    pro_user: User,
    settings: Settings,
) -> None:
    """Task 7.1 / FR-007: user with 60 sub credits → monthly renewal → balance = 100.

    Carryover = min(60, 50) = 50 (capped). Fresh = 50. Total = 100.
    """
    service = CreditService(db_session, settings)

    # Grant 60 subscription credits (over carryover cap)
    await _grant_subscription_credits(db_session, pro_user.id, 60)

    # Verify initial balance
    balance_before = await service.get_balance(pro_user.id)
    assert balance_before.subscription == 60

    # Run monthly renewal
    entry = await service.renew_subscription_credits(pro_user.id)

    # Renewal should succeed for Pro user
    assert entry is not None
    # carryover = min(60, 50) = 50 (capped); fresh = 50; total = 100
    assert entry.amount == 100
    assert entry.credit_type == CreditType.SUBSCRIPTION
    assert entry.operation == CreditOperation.GRANT

    # Verify final balance is capped at 100
    balance_after = await service.get_balance(pro_user.id)
    assert balance_after.subscription == 100


@pytest.mark.asyncio
async def test_free_tier_user_unaffected_by_renewal(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
) -> None:
    """Task 7.1 / FR-007: Free-tier user is unaffected by subscription renewal.

    renew_subscription_credits() must return None for non-Pro users and
    leave their credit balance unchanged.
    """
    service = CreditService(db_session, settings)

    # Verify initial balance
    balance_before = await service.get_balance(test_user.id)
    initial_total = balance_before.total

    # Attempt renewal for Free user
    entry = await service.renew_subscription_credits(test_user.id)

    # Must return None (no action taken)
    assert entry is None

    # Balance must remain unchanged
    balance_after = await service.get_balance(test_user.id)
    assert balance_after.total == initial_total
    assert balance_after.subscription == 0
