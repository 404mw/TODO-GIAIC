"""AI Credit Service for credit management with FIFO consumption.

Phase 14: User Story 11 - AI Credit System (Priority: P4)

Tasks:
- T281: CreditService.grant_kickstart_credits (FR-037)
- T282: CreditService.grant_daily_credits (FR-038, FR-040)
- T283: CreditService.grant_monthly_credits (FR-039)
- T284: CreditService.consume_credits with FIFO SQL (FR-042)
- T285: CreditService.get_balance breakdown

Credit Consumption Order (FIFO per FR-042):
1. Daily free credits (expire at UTC 00:00)
2. Subscription credits (carry over up to 50)
3. Purchased credits (never expire)
4. Kickstart credits (never expire)

Credit Types:
- Kickstart: 5 credits for new users (FR-037)
- Daily: 10 credits for Pro users, expire at UTC midnight (FR-038, FR-040)
- Subscription: 100 monthly credits for Pro users (FR-039)
- Purchased: Never expire, consumed last
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.user import User
from src.schemas.enums import CreditOperation, CreditType, UserTier

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CreditBalance:
    """Credit balance breakdown by type."""

    daily: int = 0
    subscription: int = 0
    purchased: int = 0
    kickstart: int = 0

    @property
    def total(self) -> int:
        """Total available credits."""
        return self.daily + self.subscription + self.purchased + self.kickstart


@dataclass
class ConsumptionResult:
    """Result of credit consumption."""

    total_consumed: int
    remaining_balance: int
    entries_updated: int = 0


# =============================================================================
# CREDIT SERVICE
# =============================================================================


class CreditService:
    """Service for managing AI credits with FIFO consumption.

    Implements credit granting, consumption, and balance tracking
    per FR-037 through FR-042.
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Initialize credit service.

        Args:
            session: Database session
            settings: Application settings
        """
        self._session = session
        self._settings = settings

    # =========================================================================
    # GRANT METHODS
    # =========================================================================

    async def grant_kickstart_credits(self, user_id: UUID) -> AICreditLedger:
        """Grant kickstart credits to a new user.

        T281: FR-037 - New users receive 5 kickstart credits.

        Kickstart credits:
        - Granted once on user creation
        - Never expire
        - Consumed after daily/subscription/purchased

        Args:
            user_id: User ID to grant credits to

        Returns:
            Created credit entry
        """
        amount = self._settings.kickstart_credits

        # Check if user already has kickstart credits
        existing = await self._session.execute(
            select(AICreditLedger).where(
                AICreditLedger.user_id == user_id,
                AICreditLedger.credit_type == CreditType.KICKSTART,
                AICreditLedger.operation == CreditOperation.GRANT,
            ).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            logger.warning(f"User {user_id} already has kickstart credits")
            # Return existing entry info via balance
            balance = await self.get_balance(user_id)
            # Create a dummy entry for return (won't be saved)
            return AICreditLedger(
                id=uuid4(),
                user_id=user_id,
                credit_type=CreditType.KICKSTART,
                operation=CreditOperation.GRANT,
                amount=balance.kickstart,
                balance_after=balance.total,
                consumed=0,
                expires_at=None,
                expired=False,
            )

        # Calculate current balance for balance_after
        current_balance = await self.get_balance(user_id)

        entry = AICreditLedger(
            id=uuid4(),
            user_id=user_id,
            credit_type=CreditType.KICKSTART,
            operation=CreditOperation.GRANT,
            amount=amount,
            balance_after=current_balance.total + amount,
            consumed=0,
            expires_at=None,  # Kickstart credits never expire
            expired=False,
        )

        self._session.add(entry)
        await self._session.flush()

        logger.info(f"Granted {amount} kickstart credits to user {user_id}")
        return entry

    async def grant_daily_credits(self, user_id: UUID) -> AICreditLedger | None:
        """Grant daily credits to a Pro user.

        T282: FR-038, FR-040 - Pro users receive 10 daily credits that
        expire at UTC 00:00.

        Daily credits:
        - Only for Pro tier users
        - Expire at UTC midnight
        - Consumed first in FIFO order

        Args:
            user_id: User ID to grant credits to

        Returns:
            Created credit entry, or None if not a Pro user
        """
        # Check user tier
        user = await self._session.get(User, user_id)
        if user is None or user.tier != UserTier.PRO:
            logger.debug(f"User {user_id} is not Pro tier, no daily credits granted")
            return None

        amount = self._settings.pro_daily_credits

        # Check if already granted today
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

        existing = await self._session.execute(
            select(AICreditLedger).where(
                AICreditLedger.user_id == user_id,
                AICreditLedger.credit_type == CreditType.DAILY,
                AICreditLedger.operation == CreditOperation.GRANT,
                AICreditLedger.created_at >= today_start,
            ).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            logger.debug(f"User {user_id} already received daily credits today")
            return None

        # Calculate expiration (UTC midnight)
        expires_at = datetime.combine(
            today + timedelta(days=1),
            datetime.min.time(),
        ).replace(tzinfo=timezone.utc)

        # Calculate current balance
        current_balance = await self.get_balance(user_id)

        entry = AICreditLedger(
            id=uuid4(),
            user_id=user_id,
            credit_type=CreditType.DAILY,
            operation=CreditOperation.GRANT,
            amount=amount,
            balance_after=current_balance.total + amount,
            consumed=0,
            expires_at=expires_at,
            expired=False,
        )

        self._session.add(entry)
        await self._session.flush()

        logger.info(f"Granted {amount} daily credits to user {user_id}, expires {expires_at}")
        return entry

    async def grant_monthly_credits(self, user_id: UUID) -> AICreditLedger | None:
        """Grant monthly subscription credits to a Pro user.

        T283: FR-039 - Pro users receive 100 monthly subscription credits.

        Subscription credits:
        - Only for Pro tier users
        - Up to 50 can carry over to next month (FR-041)
        - Consumed after daily credits

        Args:
            user_id: User ID to grant credits to

        Returns:
            Created credit entry, or None if not a Pro user
        """
        # Check user tier
        user = await self._session.get(User, user_id)
        if user is None or user.tier != UserTier.PRO:
            logger.debug(f"User {user_id} is not Pro tier, no monthly credits granted")
            return None

        amount = self._settings.pro_monthly_credits

        # Calculate current balance
        current_balance = await self.get_balance(user_id)

        entry = AICreditLedger(
            id=uuid4(),
            user_id=user_id,
            credit_type=CreditType.SUBSCRIPTION,
            operation=CreditOperation.GRANT,
            amount=amount,
            balance_after=current_balance.total + amount,
            consumed=0,
            expires_at=None,  # Subscription credits don't have hard expiration
            expired=False,
        )

        self._session.add(entry)
        await self._session.flush()

        logger.info(f"Granted {amount} monthly subscription credits to user {user_id}")
        return entry

    async def grant_purchased_credits(
        self,
        user_id: UUID,
        amount: int,
        order_ref: str | None = None,
    ) -> AICreditLedger:
        """Grant purchased credits to a user.

        Purchased credits:
        - Never expire
        - Consumed after daily and subscription credits
        - Before kickstart credits

        Args:
            user_id: User ID to grant credits to
            amount: Number of credits to grant
            order_ref: Optional payment order reference

        Returns:
            Created credit entry
        """
        # Calculate current balance
        current_balance = await self.get_balance(user_id)

        entry = AICreditLedger(
            id=uuid4(),
            user_id=user_id,
            credit_type=CreditType.PURCHASED,
            operation=CreditOperation.GRANT,
            amount=amount,
            balance_after=current_balance.total + amount,
            consumed=0,
            expires_at=None,  # Purchased credits never expire
            expired=False,
            operation_ref=order_ref,
        )

        self._session.add(entry)
        await self._session.flush()

        logger.info(f"Granted {amount} purchased credits to user {user_id}")
        return entry

    # =========================================================================
    # CONSUMPTION
    # =========================================================================

    async def consume_credits(
        self,
        user_id: UUID,
        amount: int,
        operation_ref: str,
    ) -> ConsumptionResult:
        """Consume credits in FIFO order.

        T284: FR-042 - FIFO consumption order:
        1. Daily (expire soonest)
        2. Subscription (carry over limited)
        3. Purchased (never expire)
        4. Kickstart (never expire)

        Uses database-level FOR UPDATE to prevent race conditions (SC-011).

        Args:
            user_id: User ID to consume credits from
            amount: Number of credits to consume
            operation_ref: Reference for the operation (e.g., task ID)

        Returns:
            ConsumptionResult with details

        Raises:
            ValueError: If insufficient credits available
        """
        # Get current balance first
        balance = await self.get_balance(user_id)

        if balance.total < amount:
            raise ValueError(
                f"Insufficient credits: requested {amount}, available {balance.total}"
            )

        now = datetime.now(timezone.utc)

        # Query available credit entries in FIFO order with FOR UPDATE
        # Order: daily (1) -> subscription (2) -> purchased (3) -> kickstart (4)
        query = (
            select(AICreditLedger)
            .where(
                AICreditLedger.user_id == user_id,
                AICreditLedger.operation == CreditOperation.GRANT,
                AICreditLedger.expired == False,
                AICreditLedger.amount > AICreditLedger.consumed,
                # Exclude expired entries
                (AICreditLedger.expires_at.is_(None)) | (AICreditLedger.expires_at > now),
            )
            .order_by(
                # FIFO priority: daily(1) -> subscription(2) -> purchased(3) -> kickstart(4)
                case(
                    (AICreditLedger.credit_type == CreditType.DAILY, 1),
                    (AICreditLedger.credit_type == CreditType.SUBSCRIPTION, 2),
                    (AICreditLedger.credit_type == CreditType.PURCHASED, 3),
                    (AICreditLedger.credit_type == CreditType.KICKSTART, 4),
                    else_=5,
                ),
                # Within same type, oldest first
                AICreditLedger.created_at.asc(),
            )
            .with_for_update()
        )

        result = await self._session.execute(query)
        entries = result.scalars().all()

        remaining_to_consume = amount
        entries_updated = 0

        for entry in entries:
            if remaining_to_consume <= 0:
                break

            available = entry.amount - entry.consumed
            consume_from_entry = min(available, remaining_to_consume)

            entry.consumed += consume_from_entry
            remaining_to_consume -= consume_from_entry
            entries_updated += 1

            self._session.add(entry)
            logger.debug(
                f"Consumed {consume_from_entry} from entry {entry.id} "
                f"(type={entry.credit_type}, remaining={entry.amount - entry.consumed})"
            )

        if remaining_to_consume > 0:
            # This shouldn't happen if balance check was correct
            raise ValueError(
                f"Failed to consume all credits: {remaining_to_consume} remaining"
            )

        # Flush updated entries before recalculating balance
        await self._session.flush()

        # Create consumption record
        new_balance = await self.get_balance(user_id)
        consumption_entry = AICreditLedger(
            id=uuid4(),
            user_id=user_id,
            credit_type=CreditType.DAILY,  # Type is informational for consumption
            operation=CreditOperation.CONSUME,
            amount=-amount,  # Negative for consumption
            balance_after=new_balance.total,
            consumed=0,
            expires_at=None,
            expired=False,
            operation_ref=operation_ref,
        )
        self._session.add(consumption_entry)

        await self._session.flush()

        logger.info(
            f"Consumed {amount} credits from user {user_id}, "
            f"new balance: {new_balance.total}"
        )

        return ConsumptionResult(
            total_consumed=amount,
            remaining_balance=new_balance.total,
            entries_updated=entries_updated,
        )

    # =========================================================================
    # BALANCE QUERIES
    # =========================================================================

    async def get_balance(self, user_id: UUID) -> CreditBalance:
        """Get credit balance breakdown by type.

        T285: Returns breakdown of available credits by type.

        Args:
            user_id: User ID to check balance for

        Returns:
            CreditBalance with breakdown by type
        """
        now = datetime.now(timezone.utc)

        # Query available credits grouped by type
        query = (
            select(
                AICreditLedger.credit_type,
                func.sum(AICreditLedger.amount - AICreditLedger.consumed).label("available"),
            )
            .where(
                AICreditLedger.user_id == user_id,
                AICreditLedger.operation == CreditOperation.GRANT,
                AICreditLedger.expired == False,
                AICreditLedger.amount > AICreditLedger.consumed,
                # Exclude expired entries
                (AICreditLedger.expires_at.is_(None)) | (AICreditLedger.expires_at > now),
            )
            .group_by(AICreditLedger.credit_type)
        )

        result = await self._session.execute(query)
        rows = result.all()

        balance = CreditBalance()
        for row in rows:
            credit_type, available = row
            available = int(available) if available else 0

            if credit_type == CreditType.DAILY:
                balance.daily = available
            elif credit_type == CreditType.SUBSCRIPTION:
                balance.subscription = available
            elif credit_type == CreditType.PURCHASED:
                balance.purchased = available
            elif credit_type == CreditType.KICKSTART:
                balance.kickstart = available

        return balance

    async def calculate_carryover_amount(self, user_id: UUID) -> int:
        """Calculate subscription credit carryover amount.

        T285: FR-041 - Up to 50 subscription credits can carry over.

        Args:
            user_id: User ID to calculate carryover for

        Returns:
            Number of credits that will carry over (max 50)
        """
        balance = await self.get_balance(user_id)
        max_carryover = self._settings.max_credit_carryover

        return min(balance.subscription, max_carryover)

    async def has_sufficient_credits(self, user_id: UUID, required: int) -> bool:
        """Check if user has sufficient credits.

        Args:
            user_id: User ID to check
            required: Number of credits required

        Returns:
            True if sufficient credits available
        """
        balance = await self.get_balance(user_id)
        return balance.total >= required


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_credit_service(
    session: AsyncSession,
    settings: Settings,
) -> CreditService:
    """Factory function to create CreditService.

    Args:
        session: Database session
        settings: Application settings

    Returns:
        Configured CreditService instance
    """
    return CreditService(session, settings)
