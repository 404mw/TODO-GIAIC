"""Unit tests for security headers middleware.

T411: Add security headers to all API responses.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from starlette.requests import Request
from starlette.responses import Response

from src.middleware.security import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    @pytest.mark.asyncio
    async def test_adds_x_content_type_options(self):
        """Should add X-Content-Type-Options: nosniff."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-Content-Type-Options"] == "nosniff"

    @pytest.mark.asyncio
    async def test_adds_x_frame_options(self):
        """Should add X-Frame-Options: DENY."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.asyncio
    async def test_adds_xss_protection(self):
        """Should add X-XSS-Protection."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert result.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.asyncio
    async def test_adds_strict_transport_security(self):
        """Should add HSTS header."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert "max-age=31536000" in result.headers["Strict-Transport-Security"]

    @pytest.mark.asyncio
    async def test_adds_referrer_policy(self):
        """Should add Referrer-Policy."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    @pytest.mark.asyncio
    async def test_adds_permissions_policy(self):
        """Should add Permissions-Policy."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert "camera=()" in result.headers["Permissions-Policy"]

    @pytest.mark.asyncio
    async def test_adds_content_security_policy(self):
        """Should add Content-Security-Policy."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert "default-src 'none'" in result.headers["Content-Security-Policy"]

    @pytest.mark.asyncio
    async def test_removes_server_header(self):
        """Should remove Server header if present."""
        middleware = SecurityHeadersMiddleware(app=None)

        response = Response(content="test")
        response.headers["Server"] = "uvicorn"

        async def call_next(request):
            return response

        request = MagicMock(spec=Request)
        result = await middleware.dispatch(request, call_next)

        assert "Server" not in result.headers
