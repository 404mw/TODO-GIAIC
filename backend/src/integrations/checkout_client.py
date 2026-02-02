"""Checkout.com client integration.

T321: Implement CheckoutClient with HMAC signature verification
per research.md Section 7 (FR-048)

Handles:
- Webhook HMAC-SHA256 signature verification
- Checkout session creation for subscription payments
- Payment link API integration
"""

import hashlib
import hmac
import logging
from typing import Any

import httpx

from src.config import Settings

logger = logging.getLogger(__name__)

CHECKOUT_API_BASE = "https://api.checkout.com"


class CheckoutClient:
    """Client for Checkout.com payment integration.

    Provides webhook signature verification and checkout session creation.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._webhook_secret = settings.checkout_webhook_secret.get_secret_value()
        self._secret_key = settings.checkout_secret_key.get_secret_value()

    # =========================================================================
    # WEBHOOK VERIFICATION
    # =========================================================================

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Checkout.com webhook HMAC-SHA256 signature.

        T321: FR-048 - Webhook signature verification

        Args:
            payload: Raw request body bytes
            signature: Cko-Signature header value

        Returns:
            True if signature is valid
        """
        if not signature:
            return False

        try:
            expected = hmac.new(
                self._webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            logger.warning("Webhook signature verification failed")
            return False

    # =========================================================================
    # CHECKOUT SESSION
    # =========================================================================

    async def create_checkout_session(
        self,
        user_id: str,
        email: str,
    ) -> dict[str, Any]:
        """Create a Checkout.com payment link for subscription.

        Args:
            user_id: Internal user ID for metadata
            email: User email for the checkout form

        Returns:
            Dict with checkout_url and session_id
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CHECKOUT_API_BASE}/payment-links",
                headers={
                    "Authorization": f"Bearer {self._secret_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": 999,  # $9.99 in cents
                    "currency": "USD",
                    "billing": {"address": {"country": "US"}},
                    "description": "Perpetua Flow Pro Subscription",
                    "metadata": {
                        "user_id": user_id,
                        "plan": "pro_monthly",
                    },
                    "customer": {"email": email},
                    "processing_channel_id": "pc_perpetua",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "checkout_url": data.get("redirect_url", data.get("_links", {}).get("redirect", {}).get("href", "")),
                "session_id": data.get("id", ""),
            }

    async def cancel_subscription(self, checkout_subscription_id: str) -> bool:
        """Cancel a subscription via Checkout.com API.

        Args:
            checkout_subscription_id: Checkout.com subscription ID

        Returns:
            True if cancellation succeeded
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CHECKOUT_API_BASE}/subscriptions/{checkout_subscription_id}/cancel",
                    headers={
                        "Authorization": f"Bearer {self._secret_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                return True
        except httpx.HTTPStatusError:
            logger.error(
                f"Failed to cancel subscription {checkout_subscription_id}",
                exc_info=True,
            )
            return False


def get_checkout_client(settings: Settings) -> CheckoutClient:
    """Factory function to create CheckoutClient.

    Args:
        settings: Application settings

    Returns:
        Configured CheckoutClient instance
    """
    return CheckoutClient(settings)
