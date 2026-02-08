"""Unit tests for rate limiting middleware."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.middleware.rate_limit import (
    get_rate_limit_key,
    get_ip_key,
    rate_limit_exceeded_handler,
    setup_rate_limiting,
    get_limiter,
)


def _make_request(user_claims=None, client_host="127.0.0.1"):
    request = MagicMock()
    request.state = MagicMock()
    if user_claims:
        request.state.user_claims = user_claims
    else:
        request.state.user_claims = None
    request.client = MagicMock()
    request.client.host = client_host
    # For get_remote_address compatibility
    request.headers = {}
    return request


class TestGetRateLimitKey:
    def test_authenticated_user(self):
        request = _make_request(user_claims={"sub": "user-123"})

        key = get_rate_limit_key(request)
        assert key == "user:user-123"

    def test_unauthenticated_user(self):
        request = _make_request()

        key = get_rate_limit_key(request)
        assert key.startswith("ip:")


class TestGetIpKey:
    def test_returns_ip_key(self):
        request = _make_request(client_host="192.168.1.1")

        key = get_ip_key(request)
        assert key.startswith("ip:")


class TestRateLimitExceededHandler:
    def test_returns_429(self):
        request = _make_request()
        request.state.request_id = "req-123"

        exc = MagicMock()
        exc.detail = "5 per 1 minute"

        response = rate_limit_exceeded_handler(request, exc)

        assert response.status_code == 429

    def test_without_request_id(self):
        request = _make_request()
        request.state = MagicMock(spec=[])  # No request_id attribute

        exc = MagicMock()
        exc.detail = "10 per 1 minute"

        response = rate_limit_exceeded_handler(request, exc)
        assert response.status_code == 429

    def test_with_no_detail(self):
        request = _make_request()
        request.state.request_id = None

        exc = MagicMock()
        exc.detail = None

        response = rate_limit_exceeded_handler(request, exc)
        assert response.status_code == 429


class TestSetupRateLimiting:
    def test_configures_app(self):
        app = MagicMock()

        setup_rate_limiting(app)

        assert app.state.limiter is not None
        app.add_exception_handler.assert_called_once()


class TestGetLimiter:
    def test_returns_limiter(self):
        lim = get_limiter()
        assert lim is not None
