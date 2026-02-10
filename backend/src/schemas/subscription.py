"""Subscription schemas for Pro tier management.

T053: Subscription schemas per api-specification.md Section 10
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.enums import SubscriptionStatus, UserTier


class SubscriptionFeatures(BaseModel):
    """Features available with the subscription."""

    max_subtasks: int = Field(description="Max subtasks per task")
    max_description_length: int = Field(description="Max task description length")
    voice_notes: bool = Field(description="Voice notes enabled")
    monthly_credits: int = Field(description="Monthly AI credits")


class SubscriptionResponse(BaseModel):
    """Subscription status response.

    Per api-specification.md Section 10.1.
    """

    tier: UserTier = Field(description="Current tier")
    status: SubscriptionStatus | None = Field(
        default=None,
        description="Subscription status (null for free tier)",
    )
    current_period_end: datetime | None = Field(
        default=None,
        description="End of current billing period",
    )
    cancel_at_period_end: bool = Field(
        default=False,
        description="Whether subscription cancels at period end",
    )
    features: SubscriptionFeatures = Field(
        description="Available features for tier",
    )


class CheckoutSessionResponse(BaseModel):
    """Response for checkout session creation.

    Per api-specification.md Section 10.2.
    """

    checkout_url: str = Field(description="URL to redirect user for payment")
    session_id: str = Field(description="Checkout session ID")


class CancelSubscriptionResponse(BaseModel):
    """Response for subscription cancellation.

    Per api-specification.md Section 10.3.
    """

    status: SubscriptionStatus = Field(description="New subscription status")
    access_until: datetime = Field(description="When Pro access expires")


class WebhookPayload(BaseModel):
    """Generic webhook payload from Checkout.com."""

    event_type: str = Field(description="Webhook event type")
    data: dict = Field(description="Event-specific data")


class PurchaseCreditsRequest(BaseModel):
    """Request to purchase additional credits.

    Per FR-051.
    """

    amount: int = Field(
        ge=1,
        le=500,
        description="Number of credits to purchase (max 500/month)",
    )


class PurchaseCreditsResponse(BaseModel):
    """Response for credit purchase."""

    credits_added: int = Field(description="Credits added")
    total_credits: int = Field(description="New total credit balance")
    monthly_purchased: int = Field(description="Credits purchased this month")
    monthly_remaining: int = Field(description="Credits that can still be purchased")
