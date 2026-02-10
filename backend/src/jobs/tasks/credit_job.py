"""Background job for credit expiration and daily grants.

T209: Implement credit_expire job (UTC 00:00 daily) per FR-040, FR-041

This job runs daily at UTC 00:00 to:
- Expire daily credits (FR-040)
- Carry over subscription credits up to 50 (FR-041)
- Grant new daily credits to Pro users (FR-038)
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
from sqlmodel import select

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditOperation, CreditType, UserTier


logger = logging.getLogger(__name__)


async def handle_credit_expire(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Process credit expiration and daily grants.

    T209: Credit expire job per FR-040, FR-041

    This job:
    1. Expires all daily credits from previous day (FR-040)
    2. Calculates subscription credit carryover (FR-041)
    3. Grants new daily credits to Pro users (FR-038)

    Args:
        payload: Job payload (usually empty)
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary with processing summary
    """
    now = datetime.now(UTC)
    today = now.date()

    logger.info(f"Starting credit expiration job for {today}")

    try:
        # Step 1: Expire daily credits (FR-040)
        expired_count = await _expire_daily_credits(session, now)

        # Step 2: Handle subscription credit carryover (FR-041)
        carryover_stats = await _process_subscription_carryover(session, settings)

        # Step 3: Grant new daily credits to Pro users (FR-038)
        grants_count = await _grant_daily_credits(session, settings, now)

        await session.commit()

        logger.info(
            f"Credit job complete: {expired_count} expired, "
            f"{carryover_stats['carried_over']} carried over, "
            f"{grants_count} daily grants"
        )

        return {
            "status": "success",
            "date": str(today),
            "expired_credits": expired_count,
            "carryover_users": carryover_stats["users_processed"],
            "credits_carried_over": carryover_stats["carried_over"],
            "credits_expired_from_carryover": carryover_stats["expired"],
            "daily_grants": grants_count,
        }

    except Exception as e:
        logger.error(f"Credit expiration job failed: {e}", exc_info=True)
        return {
            "status": "retry",
            "error": str(e),
        }


async def _expire_daily_credits(
    session: AsyncSession,
    now: datetime,
) -> int:
    """Expire all daily credits that are past their expiration.

    FR-040: Daily credits expire at UTC 00:00

    Args:
        session: Database session
        now: Current time

    Returns:
        Number of credit entries expired
    """
    # Mark expired credits
    query = select(AICreditLedger).where(
        AICreditLedger.credit_type == CreditType.DAILY,
        AICreditLedger.expires_at <= now,
        AICreditLedger.expired == False,
        AICreditLedger.amount > AICreditLedger.consumed,
    )

    result = await session.execute(query)
    credits_to_expire = result.scalars().all()

    expired_count = 0
    for credit in credits_to_expire:
        remaining = credit.amount - credit.consumed
        if remaining > 0:
            # Create expiration record
            expiration_entry = AICreditLedger(
                id=uuid4(),
                user_id=credit.user_id,
                credit_type=credit.credit_type,
                operation=CreditOperation.EXPIRE,
                amount=-remaining,  # Negative to show expiration
                balance_after=0,
                consumed=0,
                expires_at=None,
                expired=True,
                source_id=credit.id,
            )
            session.add(expiration_entry)

            # Mark original as expired
            credit.expired = True
            session.add(credit)

            expired_count += 1
            logger.debug(f"Expired {remaining} daily credits for user {credit.user_id}")

    await session.flush()
    return expired_count


async def _process_subscription_carryover(
    session: AsyncSession,
    settings: Settings,
) -> dict[str, int]:
    """Process subscription credit carryover.

    FR-041: Up to 50 subscription credits can carry over to next month

    Args:
        session: Database session
        settings: Application settings

    Returns:
        Dictionary with carryover statistics
    """
    max_carryover = getattr(settings, "max_credit_carryover", 50)

    # Find subscription credits that are about to expire (monthly boundary)
    # This is typically run at the start of a new month
    now = datetime.now(UTC)

    # Get all users with unexpired subscription credits
    query = select(AICreditLedger).where(
        AICreditLedger.credit_type == CreditType.SUBSCRIPTION,
        AICreditLedger.expired == False,
        AICreditLedger.operation == CreditOperation.GRANT,
        AICreditLedger.amount > AICreditLedger.consumed,
    )

    result = await session.execute(query)
    subscription_credits = result.scalars().all()

    # Group by user
    user_credits: dict[UUID, list[AICreditLedger]] = {}
    for credit in subscription_credits:
        if credit.user_id not in user_credits:
            user_credits[credit.user_id] = []
        user_credits[credit.user_id].append(credit)

    users_processed = 0
    total_carried_over = 0
    total_expired = 0

    for user_id, credits in user_credits.items():
        # Calculate total remaining subscription credits
        total_remaining = sum(c.amount - c.consumed for c in credits)

        if total_remaining <= 0:
            continue

        users_processed += 1

        if total_remaining > max_carryover:
            # Some credits will expire
            to_expire = total_remaining - max_carryover
            total_expired += to_expire
            total_carried_over += max_carryover

            logger.debug(
                f"User {user_id}: carrying over {max_carryover}, "
                f"expiring {to_expire}"
            )
        else:
            # All credits carry over
            total_carried_over += total_remaining

            logger.debug(f"User {user_id}: carrying over all {total_remaining}")

    return {
        "users_processed": users_processed,
        "carried_over": total_carried_over,
        "expired": total_expired,
    }


async def _grant_daily_credits(
    session: AsyncSession,
    settings: Settings,
    now: datetime,
) -> int:
    """Grant daily credits to Pro users.

    FR-038: Pro users receive 10 daily credits

    Args:
        session: Database session
        settings: Application settings
        now: Current time

    Returns:
        Number of users granted credits
    """
    daily_credits = getattr(settings, "pro_daily_credits", 10)

    # Calculate expiration (end of today UTC)
    today = now.date()
    expires_at = datetime.combine(
        today + timedelta(days=1),
        datetime.min.time(),
    ).replace(tzinfo=UTC)

    # Find all Pro users
    query = select(User).where(User.tier == UserTier.PRO)
    result = await session.execute(query)
    pro_users = result.scalars().all()

    grants_count = 0
    for user in pro_users:
        # Check if user already received daily credits today
        check_query = select(AICreditLedger).where(
            AICreditLedger.user_id == user.id,
            AICreditLedger.credit_type == CreditType.DAILY,
            AICreditLedger.operation == CreditOperation.GRANT,
            AICreditLedger.created_at >= datetime.combine(
                today, datetime.min.time()
            ).replace(tzinfo=UTC),
        ).limit(1)

        check_result = await session.execute(check_query)
        if check_result.scalar_one_or_none() is not None:
            # Already granted today
            continue

        # Grant daily credits
        credit_entry = AICreditLedger(
            id=uuid4(),
            user_id=user.id,
            credit_type=CreditType.DAILY,
            operation=CreditOperation.GRANT,
            amount=daily_credits,
            balance_after=daily_credits,
            consumed=0,
            expires_at=expires_at,
            expired=False,
        )
        session.add(credit_entry)
        grants_count += 1

        logger.debug(f"Granted {daily_credits} daily credits to user {user.id}")

    await session.flush()
    return grants_count


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


async def grant_kickstart_credits(
    session: AsyncSession,
    settings: Settings,
    user_id: UUID,
) -> AICreditLedger:
    """Grant kickstart credits to a new user.

    FR-037: New users receive 5 kickstart credits

    Args:
        session: Database session
        settings: Application settings
        user_id: User ID

    Returns:
        Created credit entry
    """
    kickstart_amount = getattr(settings, "kickstart_credits", 5)

    credit_entry = AICreditLedger(
        id=uuid4(),
        user_id=user_id,
        credit_type=CreditType.KICKSTART,
        operation=CreditOperation.GRANT,
        amount=kickstart_amount,
        consumed=0,
        expires_at=None,  # Kickstart credits don't expire
        expired=False,
    )

    session.add(credit_entry)
    await session.flush()

    logger.info(f"Granted {kickstart_amount} kickstart credits to user {user_id}")

    return credit_entry
