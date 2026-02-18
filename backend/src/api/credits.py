"""Credit API endpoints.

Phase 14: User Story 11 - AI Credit System (FR-037 to FR-042)

Credit balance and transaction history endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.schemas.common import DataResponse, PaginationMeta
from src.schemas.credit import (
    CreditBalanceResponse,
    CreditHistoryEntry,
    CreditHistoryResponse,
)
from src.services.credit_service import CreditService, get_credit_service

router = APIRouter(prefix="/credits", tags=["credits"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_service(
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> CreditService:
    """Get CreditService instance."""
    return get_credit_service(db, settings)


CreditServiceDep = Annotated[CreditService, Depends(get_service)]


# =============================================================================
# CREDIT ENDPOINTS
# =============================================================================


@router.get(
    "/balance",
    response_model=DataResponse[CreditBalanceResponse],
    summary="Get credit balance",
    description="Get credit balance breakdown by type (FR-042).",
)
async def get_balance(
    user: CurrentUser,
    service: CreditServiceDep,
) -> DataResponse[CreditBalanceResponse]:
    """Get user's credit balance breakdown.

    Returns breakdown of available credits by type:
    - Daily credits (expire at UTC midnight)
    - Subscription credits (carry over up to 50)
    - Purchased credits (never expire)
    - Kickstart credits (one-time new user credits)
    """
    balance = await service.get_balance(user.id)

    return DataResponse(
        data=CreditBalanceResponse(
            daily=balance.daily,
            subscription=balance.subscription,
            purchased=balance.purchased,
            kickstart=balance.kickstart,
            total=balance.total,
        )
    )


@router.get(
    "/history",
    response_model=CreditHistoryResponse,
    summary="Get credit transaction history",
    description="Get paginated credit transaction history.",
)
async def get_history(
    user: CurrentUser,
    service: CreditServiceDep,
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
) -> CreditHistoryResponse:
    """Get user's credit transaction history.

    Returns paginated list of credit transactions ordered by most recent first.
    """
    entries, total = await service.get_history(user.id, limit=limit, offset=offset)

    return CreditHistoryResponse(
        data=[CreditHistoryEntry.from_orm(entry) for entry in entries],
        pagination=PaginationMeta(
            offset=offset,
            limit=limit,
            total=total,
            has_more=(offset + limit) < total,
        ),
    )
