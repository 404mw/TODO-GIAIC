"""Unit tests for Checkout.com client integration.

T315: Test webhook signature verification (FR-048)
"""

import hashlib
import hmac
import json
from unittest.mock import AsyncMock, patch

import pytest

from src.config import Settings


# =============================================================================
# T315: WEBHOOK SIGNATURE VERIFICATION (FR-048)
# =============================================================================


class TestCheckoutWebhookSignature:
    """Test Checkout.com HMAC-SHA256 webhook signature verification."""

    def _sign_payload(self, payload: bytes, secret: str) -> str:
        """Helper to create valid signature."""
        return hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

    def test_valid_signature_accepted(self, settings: Settings):
        """Valid HMAC-SHA256 signature should be accepted."""
        from src.integrations.checkout_client import CheckoutClient

        client = CheckoutClient(settings)
        secret = settings.checkout_webhook_secret.get_secret_value()
        payload = b'{"event_type": "payment_captured", "data": {}}'
        signature = self._sign_payload(payload, secret)

        assert client.verify_signature(payload, signature) is True

    def test_invalid_signature_rejected(self, settings: Settings):
        """Invalid signature should be rejected."""
        from src.integrations.checkout_client import CheckoutClient

        client = CheckoutClient(settings)
        payload = b'{"event_type": "payment_captured", "data": {}}'

        assert client.verify_signature(payload, "invalid-signature") is False

    def test_tampered_payload_rejected(self, settings: Settings):
        """Signature for different payload should be rejected."""
        from src.integrations.checkout_client import CheckoutClient

        client = CheckoutClient(settings)
        secret = settings.checkout_webhook_secret.get_secret_value()
        original_payload = b'{"event_type": "payment_captured", "data": {}}'
        signature = self._sign_payload(original_payload, secret)

        tampered_payload = b'{"event_type": "payment_captured", "data": {"amount": 999999}}'
        assert client.verify_signature(tampered_payload, signature) is False

    def test_empty_signature_rejected(self, settings: Settings):
        """Empty signature should be rejected."""
        from src.integrations.checkout_client import CheckoutClient

        client = CheckoutClient(settings)
        payload = b'{"event_type": "payment_captured"}'

        assert client.verify_signature(payload, "") is False

    @pytest.mark.asyncio
    async def test_create_checkout_session(self, settings: Settings, mock_checkout):
        """Should create a checkout session via Checkout.com API."""
        from src.integrations.checkout_client import CheckoutClient

        mock_checkout.post("https://api.checkout.com/payment-links").respond(
            json={
                "id": "pl_test_123",
                "redirect_url": "https://checkout.com/pay/pl_test_123",
            }
        )

        client = CheckoutClient(settings)
        result = await client.create_checkout_session(
            user_id="user-123",
            email="test@example.com",
        )

        assert result["checkout_url"] is not None
        assert result["session_id"] is not None
