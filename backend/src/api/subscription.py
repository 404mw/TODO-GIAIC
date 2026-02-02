"""Subscription API endpoints.

Phase 17: User Story 10 - Pro Subscription Management (Priority: P4)

Tasks:
- T328: GET /api/v1/subscription per api-specification.md Section 9.1
- T329: POST /api/v1/subscription/checkout per api-specification.md Section 9.2
- T330: POST /api/v1/subscription/cancel per api-specification.md Section 9.3
- T331: POST /api/v1/webhooks/checkout per api-specification.md Section 9.4
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import get_current_user, get_db_session
from src.integrations.checkout_client import get_checkout_client
from src.models.user import User
from src.schemas.enums import SubscriptionStatus, UserTier
from src.schemas.subscription import (
    CancelSubscriptionResponse,
    CheckoutSessionResponse,
    PurchaseCreditsRequest,
    PurchaseCreditsResponse,
    SubscriptionFeatures,
    SubscriptionResponse,
    WebhookPayload,
)
from src.services.subscription_service import get_subscription_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["subscription"])


# =============================================================================
# T328: GET /api/v1/subscription (Section 9.1)
# =============================================================================


@router.get(
    "/subscription",
    response_model=dict,
    summary="Get subscription status",
    description="""
    Retrieve the authenticated user's subscription status, tier, and features.

    Per api-specification.md Section 9.1.
    """,
)
async def get_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Get user's subscription status.

    T328: GET /api/v1/subscription

    Returns:
        Subscription status with tier and features
    """
    service = get_subscription_service(session, settings)
    subscription = await service.get_subscription(current_user.id)

    # Determine features based on tier
    is_pro = current_user.tier == UserTier.PRO
    features = SubscriptionFeatures(
        max_subtasks=settings.pro_max_subtasks if is_pro else settings.free_max_subtasks,
        max_description_length=settings.pro_desc_max_length if is_pro else settings.free_desc_max_length,
        voice_notes=is_pro,
        monthly_credits=settings.pro_monthly_credits if is_pro else 0,
    )

    response = SubscriptionResponse(
        tier=current_user.tier,
        status=SubscriptionStatus(subscription.status) if subscription else None,
        current_period_end=subscription.current_period_end if subscription else None,
        cancel_at_period_end=(
            subscription.status == SubscriptionStatus.CANCELLED
            if subscription
            else False
        ),
        features=features,
    )

    return {"data": response.model_dump(mode="json")}


# =============================================================================
# T329: POST /api/v1/subscription/checkout (Section 9.2)
# =============================================================================


@router.post(
    "/subscription/checkout",
    response_model=dict,
    summary="Create checkout session",
    description="""
    Create a Checkout.com payment session for Pro subscription.
    Returns a URL to redirect the user to for payment.

    Per api-specification.md Section 9.2.
    """,
)
async def create_checkout_session(
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Create checkout session for subscription.

    T329: POST /api/v1/subscription/checkout

    Returns:
        CheckoutSessionResponse with checkout_url and session_id
    """
    if current_user.tier == UserTier.PRO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has Pro subscription",
        )

    checkout_client = get_checkout_client(settings)
    result = await checkout_client.create_checkout_session(
        user_id=str(current_user.id),
        email=current_user.email,
    )

    response = CheckoutSessionResponse(
        checkout_url=result["checkout_url"],
        session_id=result["session_id"],
    )

    return {"data": response.model_dump()}


# =============================================================================
# T330: POST /api/v1/subscription/cancel (Section 9.3)
# =============================================================================


@router.post(
    "/subscription/cancel",
    response_model=dict,
    summary="Cancel subscription",
    description="""
    Cancel the authenticated user's Pro subscription.
    Access continues until the end of the current billing period.

    Per api-specification.md Section 9.3.
    """,
)
async def cancel_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Cancel user's subscription.

    T330: POST /api/v1/subscription/cancel

    Returns:
        CancelSubscriptionResponse with status and access_until
    """
    service = get_subscription_service(session, settings)

    try:
        subscription = await service.cancel_subscription(current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    response = CancelSubscriptionResponse(
        status=SubscriptionStatus(subscription.status),
        access_until=subscription.current_period_end,
    )

    return {"data": response.model_dump(mode="json")}


# =============================================================================
# T331: POST /api/v1/webhooks/checkout (Section 9.4)
# =============================================================================


@router.post(
    "/webhooks/checkout",
    summary="Checkout.com webhook handler",
    description="""
    Process Checkout.com webhook events.
    Verifies HMAC-SHA256 signature before processing.

    Per api-specification.md Section 9.4.
    """,
    status_code=status.HTTP_200_OK,
)
async def handle_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Handle Checkout.com webhook.

    T331: POST /api/v1/webhooks/checkout

    Verifies webhook signature and processes subscription events.

    Returns:
        Processing result
    """
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("Cko-Signature", "")

    # Verify webhook signature (FR-048)
    checkout_client = get_checkout_client(settings)
    if not checkout_client.verify_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    # Parse payload
    import json
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event_id = payload.get("id", "")
    event_type = payload.get("event_type", payload.get("type", ""))
    data = payload.get("data", {})

    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing event_type in webhook payload",
        )

    # Process webhook event (idempotent - T320)
    service = get_subscription_service(session, settings)
    result = await service.process_webhook(
        event_id=event_id,
        event_type=event_type,
        data=data,
    )

    await session.commit()

    logger.info(f"Webhook processed: event_id={event_id}, type={event_type}, result={result}")

    return {"status": "ok", **result}


# =============================================================================
# CREDIT PURCHASE ENDPOINT (FR-051)
# =============================================================================


@router.post(
    "/subscription/purchase-credits",
    response_model=dict,
    summary="Purchase additional AI credits",
    description="""
    Purchase additional AI credits (Pro tier only).
    Maximum 500 credits per month.

    Per FR-051.
    """,
)
async def purchase_credits(
    request_body: PurchaseCreditsRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Purchase additional AI credits.

    Returns:
        PurchaseCreditsResponse with purchase result
    """
    service = get_subscription_service(session, settings)

    try:
        result = await service.purchase_credits(
            user_id=current_user.id,
            amount=request_body.amount,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    await session.commit()

    response = PurchaseCreditsResponse(**result)
    return {"data": response.model_dump()}
