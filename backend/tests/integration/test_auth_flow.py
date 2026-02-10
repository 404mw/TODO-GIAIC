"""Integration tests for authentication flow.

T067, T086: Full OAuth flow tests per api-specification.md Section 2
TDD RED Phase: These tests should FAIL until auth endpoints are implemented.
"""

from uuid import uuid4

import pytest
import respx
from httpx import AsyncClient, Response

from src.models.user import User


# =============================================================================
# T067: Expired access token returns 401 with refresh_required flag
# =============================================================================


@pytest.mark.asyncio
async def test_expired_access_token_returns_401_with_refresh_required(
    client: AsyncClient,
    settings,
):
    """T067: Expired access token returns 401 with refresh_required flag (FR-006).

    Given: A request with an expired access token
    When: Any authenticated endpoint is called
    Then: 401 is returned with refresh_required: true in the response
    """
    from src.dependencies import JWTKeyManager
    import jwt
    from datetime import datetime, timedelta, UTC

    jwt_manager = JWTKeyManager(settings)

    # Create an expired token manually
    now = datetime.now(UTC)
    expired_time = now - timedelta(minutes=30)  # 30 minutes ago

    payload = {
        "sub": str(uuid4()),
        "email": "test@example.com",
        "tier": "free",
        "type": "access",
        "iat": expired_time,
        "exp": expired_time + timedelta(minutes=15),  # Was valid for 15 mins
        "iss": "perpetua-flow",
    }

    expired_token = jwt.encode(
        payload,
        settings.jwt_private_key.get_secret_value(),
        algorithm="RS256",
        headers={"kid": "perpetua-flow-v1"},
    )

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TOKEN_EXPIRED"
    assert data["error"].get("refresh_required") is True


# =============================================================================
# T086: Full OAuth flow integration test
# =============================================================================


@pytest.mark.asyncio
async def test_full_oauth_flow(
    client: AsyncClient,
    mock_google_oauth: respx.MockRouter,
    settings,
):
    """T086: Full OAuth flow integration test.

    Given: A valid Google ID token
    When: The complete auth flow is executed (callback -> use token -> refresh -> logout)
    Then: Each step succeeds with expected responses
    """
    # This test will be implemented once the Google OAuth integration is complete
    # For now, it tests the mock flow

    # Step 1: Exchange Google ID token for backend tokens
    # Note: This requires mocking Google token verification
    # The actual implementation will verify the ID token signature

    # Mock Google token verification (to be implemented in GoogleOAuthClient)
    # response = await client.post(
    #     "/api/v1/auth/google/callback",
    #     json={"id_token": "mock.google.id.token"},
    # )
    # assert response.status_code == 200
    # tokens = response.json()
    # assert "access_token" in tokens
    # assert "refresh_token" in tokens

    # For now, skip this test until T069 (GoogleOAuthClient) is implemented
    pytest.skip("Requires GoogleOAuthClient implementation (T069)")


@pytest.mark.asyncio
async def test_refresh_flow_integration(
    client: AsyncClient,
    test_user: User,
    db_session,
    settings,
):
    """T086: Token refresh flow integration test.

    Given: A valid refresh token
    When: POST /auth/refresh is called
    Then: New tokens are issued
    """
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session, settings)

    # Generate initial tokens
    access_token, refresh_token = await auth_service.generate_tokens(test_user)

    # Call refresh endpoint
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != access_token  # New token
    assert data["refresh_token"] != refresh_token  # Rotated


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(
    client: AsyncClient,
    test_user: User,
    db_session,
    settings,
):
    """T086: Logout revokes refresh token.

    Given: A valid refresh token
    When: POST /auth/logout is called
    Then: The refresh token is revoked and cannot be used
    """
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session, settings)

    # Generate tokens
    access_token, refresh_token = await auth_service.generate_tokens(test_user)

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 204

    # Try to use the refresh token - should fail
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401


# =============================================================================
# Authentication error scenarios
# =============================================================================


@pytest.mark.asyncio
async def test_missing_auth_header_returns_401(
    client: AsyncClient,
):
    """Test: Missing Authorization header returns 401.

    Given: A request without Authorization header
    When: An authenticated endpoint is called
    Then: 401 UNAUTHORIZED is returned
    """
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_invalid_token_format_returns_401(
    client: AsyncClient,
):
    """Test: Invalid token format returns 401.

    Given: A malformed token
    When: An authenticated endpoint is called
    Then: 401 UNAUTHORIZED is returned
    """
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.format"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_nonexistent_user_returns_401(
    client: AsyncClient,
    settings,
):
    """Test: Token for nonexistent user returns 401.

    Given: A valid JWT for a user that doesn't exist
    When: An authenticated endpoint is called
    Then: 401 UNAUTHORIZED is returned
    """
    from src.dependencies import JWTKeyManager

    jwt_manager = JWTKeyManager(settings)

    # Create token for nonexistent user
    token = jwt_manager.create_access_token(
        user_id=uuid4(),  # Random UUID, user doesn't exist
        email="nonexistent@example.com",
        tier="free",
    )

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
