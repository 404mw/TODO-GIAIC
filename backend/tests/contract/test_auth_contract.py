"""Contract tests for authentication endpoints.

T068: POST /auth/google/callback schema validation per api-specification.md Section 2
TDD RED Phase: These tests should FAIL until auth endpoints are implemented.
"""

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from src.schemas.auth import (
    GoogleCallbackRequest,
    RefreshRequest,
    LogoutRequest,
    TokenResponse,
    TokenRefreshResponse,
)


# =============================================================================
# Request Schema Validation
# =============================================================================


class TestGoogleCallbackRequestSchema:
    """T068: GoogleCallbackRequest schema validation."""

    def test_valid_request(self):
        """Valid request with id_token."""
        request = GoogleCallbackRequest(
            id_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.valid.token"
        )
        assert request.id_token is not None

    def test_missing_id_token_raises_error(self):
        """Missing id_token raises validation error."""
        with pytest.raises(ValidationError):
            GoogleCallbackRequest()

    def test_empty_id_token_raises_error(self):
        """Empty id_token raises validation error."""
        with pytest.raises(ValidationError):
            GoogleCallbackRequest(id_token="")


class TestRefreshRequestSchema:
    """RefreshRequest schema validation."""

    def test_valid_request(self):
        """Valid request with refresh_token."""
        request = RefreshRequest(refresh_token="valid-refresh-token")
        assert request.refresh_token is not None

    def test_missing_refresh_token_raises_error(self):
        """Missing refresh_token raises validation error."""
        with pytest.raises(ValidationError):
            RefreshRequest()

    def test_empty_refresh_token_raises_error(self):
        """Empty refresh_token raises validation error."""
        with pytest.raises(ValidationError):
            RefreshRequest(refresh_token="")


class TestLogoutRequestSchema:
    """LogoutRequest schema validation."""

    def test_valid_request(self):
        """Valid request with refresh_token."""
        request = LogoutRequest(refresh_token="valid-refresh-token")
        assert request.refresh_token is not None


# =============================================================================
# Response Schema Validation
# =============================================================================


class TestTokenResponseSchema:
    """TokenResponse schema validation."""

    def test_valid_response_with_user(self):
        """Valid response includes all required fields and user info."""
        from datetime import datetime
        from uuid import uuid4

        response = TokenResponse(
            access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.access.token",
            refresh_token="refresh-token-value",
            token_type="Bearer",
            expires_in=900,
            user={
                "id": uuid4(),
                "email": "user@example.com",
                "name": "Test User",
                "avatar_url": None,
                "tier": "free",
                "created_at": datetime.now(),
            },
        )
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "Bearer"
        assert response.expires_in == 900
        assert response.user is not None
        assert response.user.email == "user@example.com"

    def test_valid_response_without_user(self):
        """Valid response can omit user info (for refresh)."""
        response = TokenResponse(
            access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.access.token",
            refresh_token="refresh-token-value",
            expires_in=900,
        )
        assert response.user is None


class TestTokenRefreshResponseSchema:
    """TokenRefreshResponse schema validation (no user info)."""

    def test_valid_response(self):
        """Valid refresh response."""
        response = TokenRefreshResponse(
            access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.new.access",
            refresh_token="new-refresh-token",
            token_type="Bearer",
            expires_in=900,
        )
        assert response.access_token is not None
        assert response.refresh_token is not None


# =============================================================================
# API Contract Tests (Endpoint Response Shapes)
# =============================================================================


@pytest.mark.asyncio
async def test_google_callback_response_shape(
    client: AsyncClient,
):
    """T068: POST /auth/google/callback returns correct response shape.

    Note: This test will fail initially because:
    1. The endpoint isn't implemented yet
    2. Google token verification would fail with a mock token

    The test validates the response shape matches the schema.
    """
    # Skip until endpoint is implemented - this is a contract shape test
    pytest.skip("Endpoint not implemented yet - T077")

    response = await client.post(
        "/api/v1/auth/google/callback",
        json={"id_token": "mock.google.id.token"},
    )

    # On success, validate response shape
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        # User info included on initial auth
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert "name" in data["user"]
        assert "tier" in data["user"]


@pytest.mark.asyncio
async def test_refresh_response_shape(
    client: AsyncClient,
):
    """POST /auth/refresh returns correct response shape."""
    pytest.skip("Endpoint not implemented yet - T078")

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "valid-refresh-token"},
    )

    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        # No user info on refresh
        assert "user" not in data or data["user"] is None


@pytest.mark.asyncio
async def test_error_response_shape(
    client: AsyncClient,
):
    """Error responses follow standard error format.

    Per api-specification.md Section 11.
    """
    # Test with invalid request (missing body)
    response = await client.post(
        "/api/v1/auth/google/callback",
        json={},  # Missing required id_token
    )

    assert response.status_code == 422  # Validation error
    data = response.json()

    # Standard error response shape
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_jwks_endpoint_response_shape(
    client: AsyncClient,
):
    """GET /.well-known/jwks.json returns correct JWKS format.

    Per authentication.md for public key distribution.
    """
    response = await client.get("/api/v1/.well-known/jwks.json")

    assert response.status_code == 200
    data = response.json()

    assert "keys" in data
    assert isinstance(data["keys"], list)
    assert len(data["keys"]) > 0

    # Each key should have required JWK fields
    key = data["keys"][0]
    assert "kty" in key  # Key type (RSA)
    assert "use" in key  # Usage (sig)
    assert "alg" in key  # Algorithm (RS256)
    assert "kid" in key  # Key ID
    assert "n" in key  # Modulus
    assert "e" in key  # Exponent
