"""Credit schemas for request/response validation.

Credit system per FR-037 through FR-042.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.common import PaginationMeta
from src.schemas.enums import CreditOperation, CreditType


class CreditBalanceResponse(BaseModel):
    """Credit balance breakdown by type.

    Per FR-042: FIFO consumption order.
    """

    daily: int = Field(ge=0, description="Daily free credits (expire at UTC midnight)")
    subscription: int = Field(ge=0, description="Monthly Pro credits (carry over up to 50)")
    purchased: int = Field(ge=0, description="Purchased credits (never expire)")
    kickstart: int = Field(ge=0, description="One-time new user credits")
    total: int = Field(ge=0, description="Total available credits")


class CreditHistoryEntry(BaseModel):
    """Single credit transaction entry."""

    id: UUID = Field(description="Transaction ID")
    credit_type: CreditType = Field(description="Credit source type")
    amount: int = Field(description="Positive = credit, negative = debit")
    balance_after: int = Field(ge=0, description="Running balance after transaction")
    operation: CreditOperation = Field(description="Transaction type (grant/consume/expire)")
    operation_ref: str | None = Field(
        default=None,
        description="Reference (e.g., task ID, chat ID)",
    )
    consumed: int = Field(ge=0, description="Amount consumed from this entry")
    expires_at: datetime | None = Field(
        default=None,
        description="Expiration time (UTC) for daily credits",
    )
    expired: bool = Field(description="Whether this entry has expired")
    created_at: datetime = Field(description="Transaction timestamp")

    class Config:
        from_attributes = True


class CreditHistoryResponse(BaseModel):
    """Paginated credit transaction history."""

    data: list[CreditHistoryEntry] = Field(description="Credit transactions")
    pagination: PaginationMeta = Field(description="Pagination metadata")
