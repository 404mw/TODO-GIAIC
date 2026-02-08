"""Unit tests for LoggingMiddleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.middleware.logging import LoggingMiddleware, get_logger


def _make_request(path="/api/test", method="GET", has_user=False, forwarded_for=None, real_ip=None):
    request = MagicMock()
    request.method = method
    request.url.path = path
    request.query_params = None

    headers = {}
    if forwarded_for:
        headers["X-Forwarded-For"] = forwarded_for
    if real_ip:
        headers["X-Real-IP"] = real_ip

    request.headers = MagicMock()
    request.headers.get = lambda k, d=None: headers.get(k, d)

    request.client = MagicMock()
    request.client.host = "127.0.0.1"

    request.state = MagicMock()
    request.state.request_id = "req-123"
    if has_user:
        from uuid import uuid4
        request.state.user = MagicMock()
        request.state.user.id = uuid4()
    else:
        request.state.user = None

    return request


class TestLoggingMiddleware:
    @pytest.mark.asyncio
    async def test_excludes_health_paths(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(path="/health/live")
        response = MagicMock()
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result == response

    @pytest.mark.asyncio
    async def test_excludes_metrics_path(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(path="/metrics")
        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(request, call_next)
        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_logs_normal_request(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(path="/api/tasks")
        response = MagicMock()
        response.status_code = 200
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result == response

    @pytest.mark.asyncio
    async def test_logs_with_user(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(path="/api/tasks", has_user=True)
        response = MagicMock()
        response.status_code = 200
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert result == response

    @pytest.mark.asyncio
    async def test_logs_exception(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request()
        call_next = AsyncMock(side_effect=RuntimeError("boom"))

        with pytest.raises(RuntimeError, match="boom"):
            await middleware.dispatch(request, call_next)

    @pytest.mark.asyncio
    async def test_logs_query_params(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request()
        request.query_params = MagicMock()
        request.query_params.__bool__ = lambda self: True
        request.query_params.__str__ = lambda self: "page=1&limit=25"
        response = MagicMock()
        response.status_code = 200
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert result == response


class TestGetClientIP:
    def test_forwarded_for(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(forwarded_for="1.2.3.4, 5.6.7.8")

        ip = middleware._get_client_ip(request)
        assert ip == "1.2.3.4"

    def test_real_ip(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request(real_ip="10.0.0.1")

        ip = middleware._get_client_ip(request)
        assert ip == "10.0.0.1"

    def test_client_host(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request()

        ip = middleware._get_client_ip(request)
        assert ip == "127.0.0.1"

    def test_no_client(self):
        middleware = LoggingMiddleware(app=MagicMock())
        request = _make_request()
        request.client = None

        ip = middleware._get_client_ip(request)
        assert ip == "unknown"


class TestGetLogger:
    def test_returns_logger(self):
        log = get_logger()
        assert log is not None
