"""AI Credit Ledger model for credit management.

T038: AICreditLedger model per data-model.md Entity 9 (FR-042)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, Enum as SQLAEnum
from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import CreditOperation, CreditType

if TYPE_CHECKING:
    from src.models.user import User


class AICreditLedger(BaseModel, table=True):
    """AI Credit Ledger database model.

    Transaction history for credit consumption with FIFO tracking.

    Per data-model.md Entity 9.

    Credit Consumption Order (FIFO):
    1. Daily free credits (expire at UTC 00:00)
    2. Subscription credits (carry over up to 50)
    3. Purchased credits (never expire)

    Credit Costs:
    - AI Chat message: 1 credit
    - Subtask generation: 1 credit (flat)
    - Note-to-task conversion: 1 credit
    - Voice transcription: 5 credits/minute
    """

    __tablename__ = "ai_credit_ledger"

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Credit owner",
    )

    # Credit details
    credit_type: CreditType = Field(
        sa_column=Column(
            SQLAEnum(CreditType, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
        description="Credit source type",
    )
    amount: int = Field(
        nullable=False,
        description="Positive = credit, negative = debit",
    )
    balance_after: int = Field(
        ge=0,
        nullable=False,
        description="Running balance after this transaction",
    )
    operation: CreditOperation = Field(
        sa_column=Column(
            SQLAEnum(CreditOperation, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
        description="Transaction type",
    )
    operation_ref: str | None = Field(
        default=None,
        description="Reference (e.g., task ID, chat ID)",
    )

    # Consumption tracking
    consumed: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Amount consumed from this credit entry",
    )

    # Expiration (for daily credits)
    expires_at: datetime | None = Field(
        default=None,
        index=True,
        description="Expiration time (UTC) for daily credits",
    )
    expired: bool = Field(
        default=False,
        nullable=False,
        description="Whether this credit entry has expired",
    )

    # Reference to source (for expiration entries)
    source_id: UUID | None = Field(
        default=None,
        description="Source credit entry ID (for expiration records)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="credit_entries")

    @property
    def is_expired(self) -> bool:
        """Check if credit has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
