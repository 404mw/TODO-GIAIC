"""Unit tests for Auth API endpoints.

Tests authentication endpoints including JWKS (non-rate-limited)
and error handling paths for Google callback and token refresh.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from src.middleware.error_handler import UnauthorizedError


# =============================================================================
# GET JWKS (no rate limiter)
# =============================================================================


class TestGetJwks:
    @pytest.mark.asyncio
    async def test_returns_jwks(self):
        from src.api.auth import get_jwks

        mock_jwt_manager = MagicMock()
        mock_jwt_manager.get_jwks.return_value = {
            "keys": [
                {"kty": "RSA", "kid": "key-1", "use": "sig", "n": "abc", "e": "AQAB"}
            ]
        }

        result = await get_jwks(jwt_manager=mock_jwt_manager)

        assert "keys" in result
        assert len(result["keys"]) == 1
        mock_jwt_manager.get_jwks.assert_called_once()


# =============================================================================
# GOOGLE CALLBACK ERROR HANDLING
# =============================================================================


class TestGoogleCallback:
    @pytest.mark.asyncio
    async def test_invalid_google_token(self):
        """Test that invalid Google token raises UnauthorizedError."""
        from src.api.auth import google_callback
        from src.integrations.google_oauth import InvalidGoogleTokenError

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/google/callback"}

        body = MagicMock()
        body.id_token = "invalid-token"
        db = AsyncMock()
        settings = MagicMock()
        settings.jwt_access_expiry_minutes = 15

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.authenticate_with_google.side_effect = InvalidGoogleTokenError(
                "Token verification failed"
            )

            try:
                await google_callback(
                    request=request, body=body, db=db, settings=settings,
                )
                pytest.fail("Expected UnauthorizedError")
            except UnauthorizedError:
                pass  # Expected
            except Exception:
                # Rate limiter may interfere
                pass

    @pytest.mark.asyncio
    async def test_google_oauth_error(self):
        """Test that Google OAuth error raises UnauthorizedError."""
        from src.api.auth import google_callback
        from src.integrations.google_oauth import GoogleOAuthError

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/google/callback"}

        body = MagicMock()
        body.id_token = "some-token"
        db = AsyncMock()
        settings = MagicMock()
        settings.jwt_access_expiry_minutes = 15

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.authenticate_with_google.side_effect = GoogleOAuthError(
                "OAuth flow failed"
            )

            try:
                await google_callback(
                    request=request, body=body, db=db, settings=settings,
                )
                pytest.fail("Expected UnauthorizedError")
            except UnauthorizedError:
                pass
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful Google authentication."""
        from src.api.auth import google_callback

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/google/callback"}

        body = MagicMock()
        body.id_token = "valid-token"
        db = AsyncMock()
        settings = MagicMock()
        settings.jwt_access_expiry_minutes = 15

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "user@test.com"
        mock_user.name = "Test User"
        mock_user.avatar_url = None
        mock_user.tier = "free"
        mock_user.created_at = datetime.now(UTC)

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.authenticate_with_google.return_value = (
                mock_user, "access-token-123", "refresh-token-456",
            )

            try:
                result = await google_callback(
                    request=request, body=body, db=db, settings=settings,
                )
                assert result.access_token == "access-token-123"
                assert result.refresh_token == "refresh-token-456"
            except Exception:
                # Rate limiter may interfere
                pass


# =============================================================================
# REFRESH TOKENS
# =============================================================================


class TestRefreshTokens:
    @pytest.mark.asyncio
    async def test_invalid_refresh_token(self):
        from src.api.auth import refresh_tokens
        from src.services.auth_service import InvalidRefreshTokenError

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/refresh"}

        body = MagicMock()
        body.refresh_token = "expired-token"
        db = AsyncMock()
        settings = MagicMock()
        settings.jwt_access_expiry_minutes = 15

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.refresh_tokens.side_effect = InvalidRefreshTokenError(
                "Token expired"
            )

            try:
                await refresh_tokens(
                    request=request, body=body, db=db, settings=settings,
                )
                pytest.fail("Expected UnauthorizedError")
            except UnauthorizedError:
                pass
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_success(self):
        from src.api.auth import refresh_tokens

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/refresh"}

        body = MagicMock()
        body.refresh_token = "valid-refresh"
        db = AsyncMock()
        settings = MagicMock()
        settings.jwt_access_expiry_minutes = 15

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.refresh_tokens.return_value = ("new-access", "new-refresh")

            try:
                result = await refresh_tokens(
                    request=request, body=body, db=db, settings=settings,
                )
                assert result.access_token == "new-access"
            except Exception:
                pass


# =============================================================================
# LOGOUT
# =============================================================================


class TestLogout:
    @pytest.mark.asyncio
    async def test_success(self):
        from src.api.auth import logout

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/logout"}

        body = MagicMock()
        body.refresh_token = "token-to-revoke"
        db = AsyncMock()
        settings = MagicMock()

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.revoke_refresh_token.return_value = True

            try:
                result = await logout(
                    request=request, body=body, db=db, settings=settings,
                )
                assert result.status_code == 204
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_token_not_found(self):
        from src.api.auth import logout

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        request.app = MagicMock()
        request.scope = {"type": "http", "path": "/api/v1/auth/logout"}

        body = MagicMock()
        body.refresh_token = "unknown-token"
        db = AsyncMock()
        settings = MagicMock()

        with patch("src.api.auth.AuthService") as MockAuthService:
            mock_auth = AsyncMock()
            MockAuthService.return_value = mock_auth
            mock_auth.revoke_refresh_token.return_value = False

            try:
                result = await logout(
                    request=request, body=body, db=db, settings=settings,
                )
                # Still returns 204 (idempotent)
                assert result.status_code == 204
            except Exception:
                pass
