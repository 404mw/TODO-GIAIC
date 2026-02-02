"""Subscription model for Pro tier management.

T039: Subscription model per data-model.md Entity 10
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import SubscriptionStatus

if TYPE_CHECKING:
    from src.models.user import User


class Subscription(BaseModel, table=True):
    """Subscription database model.

    Payment and plan status for Pro tier management.

    Per data-model.md Entity 10.

    Status Transitions:
    [active] → Payment succeeds monthly
        ↓ (payment fails)
    [past_due] → 1-3 retry attempts
        ↓ (3 failures)
    [grace] → 3-day grace period
        ↓ (grace expires without payment)
    [expired] → Downgrade to free tier

    [active] → User cancels
        ↓
    [cancelled] → Access until period end, then expired
    """

    __tablename__ = "subscriptions"

    # Foreign key (one-to-one with User)
    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        nullable=False,
        index=True,
        description="Subscriber",
    )

    # Checkout.com integration
    checkout_subscription_id: str = Field(
        unique=True,
        nullable=False,
        description="Checkout.com subscription ID",
    )

    # Status
    status: SubscriptionStatus = Field(
        nullable=False,
        description="Current subscription status",
    )

    # Billing period
    current_period_start: datetime = Field(
        nullable=False,
        description="Billing period start (UTC)",
    )
    current_period_end: datetime = Field(
        nullable=False,
        description="Billing period end (UTC)",
    )

    # Grace period (FR-049)
    grace_period_end: datetime | None = Field(
        default=None,
        description="Grace period expiration (UTC)",
    )

    # Payment tracking
    failed_payment_count: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Consecutive payment failures",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Payment retry count (resets on success)",
    )
    last_retry_at: datetime | None = Field(
        default=None,
        description="Last payment retry timestamp (UTC)",
    )
    last_payment_at: datetime | None = Field(
        default=None,
        description="Last successful payment timestamp (UTC)",
    )
    grace_warning_sent: bool = Field(
        default=False,
        nullable=False,
        description="Whether grace period warning was sent",
    )

    # Cancellation
    cancelled_at: datetime | None = Field(
        default=None,
        description="Cancellation timestamp (UTC)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="subscription")

    @property
    def is_active(self) -> bool:
        """Check if subscription provides Pro access."""
        return self.status in (
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.GRACE,
            SubscriptionStatus.CANCELLED,  # Until period end
        )

    @property
    def in_grace_period(self) -> bool:
        """Check if currently in grace period."""
        if self.status != SubscriptionStatus.GRACE:
            return False
        if self.grace_period_end is None:
            return False
        return datetime.utcnow() < self.grace_period_end
