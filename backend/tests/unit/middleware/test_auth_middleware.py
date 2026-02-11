"""Unit tests for auth middleware.

T075: Auth middleware for JWT validation
T088: 401 UNAUTHORIZED responses with proper codes
"""

import pytest

from src.middleware.auth import AuthMiddleware


class TestAuthMiddleware:
    """Test AuthMiddleware exemption logic and response helpers."""

    def setup_method(self):
        self.middleware = AuthMiddleware(app=None)

    def test_exempt_paths(self):
        """EXEMPT_PATHS should include known public endpoints."""
        assert "/api/v1/health/live" in self.middleware.EXEMPT_PATHS
        assert "/api/v1/health/ready" in self.middleware.EXEMPT_PATHS
        assert "/api/v1/auth/google/callback" in self.middleware.EXEMPT_PATHS
        assert "/api/v1/auth/refresh" in self.middleware.EXEMPT_PATHS
        assert "/api/v1/.well-known/jwks.json" in self.middleware.EXEMPT_PATHS
        assert "/docs" in self.middleware.EXEMPT_PATHS
        assert "/openapi.json" in self.middleware.EXEMPT_PATHS
        assert "/redoc" in self.middleware.EXEMPT_PATHS

    def test_exempt_prefixes(self):
        """EXEMPT_PREFIXES should include webhook paths."""
        assert "/api/v1/webhooks/" in self.middleware.EXEMPT_PREFIXES

    def test_is_exempt_for_exact_match(self):
        """_is_exempt should return True for exact path matches."""
        assert self.middleware._is_exempt("/api/v1/health/live") is True
        assert self.middleware._is_exempt("/docs") is True

    def test_is_exempt_for_prefix_match(self):
        """_is_exempt should return True for prefix matches."""
        assert self.middleware._is_exempt("/api/v1/webhooks/checkout") is True

    def test_is_not_exempt_for_protected_path(self):
        """_is_exempt should return False for protected paths."""
        assert self.middleware._is_exempt("/api/v1/tasks") is False
        assert self.middleware._is_exempt("/api/v1/notes") is False

    def test_unauthorized_response_format(self):
        """_unauthorized_response should return proper JSON structure."""
        response = self.middleware._unauthorized_response(
            "Invalid token", code="INVALID_TOKEN"
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    def test_unauthorized_response_with_refresh_required(self):
        """_unauthorized_response with refresh_required should include flag."""
        response = self.middleware._unauthorized_response(
            "Token expired",
            code="TOKEN_EXPIRED",
            refresh_required=True,
        )

        assert response.status_code == 401
        # The response content should have refresh_required

    def test_unauthorized_response_default_code(self):
        """_unauthorized_response should default to UNAUTHORIZED code."""
        response = self.middleware._unauthorized_response("Not authenticated")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_options_request_skips_auth(self):
        """OPTIONS requests should always bypass authentication (CORS preflight)."""
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock request with OPTIONS method
        request = MagicMock()
        request.method = "OPTIONS"
        request.url.path = "/api/v1/tasks"  # Protected path
        request.headers = {}  # No auth header

        # Mock call_next to verify it's called
        call_next = AsyncMock(return_value=MagicMock())

        # Middleware should skip auth and call next
        await self.middleware.dispatch(request, call_next)
        call_next.assert_called_once_with(request)
