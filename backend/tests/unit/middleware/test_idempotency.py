"""Unit tests for IdempotencyMiddleware."""

import pytest
import json
from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.middleware.idempotency import (
    IdempotencyMiddleware,
    cleanup_expired_idempotency_keys,
    IDEMPOTENCY_TTL_HOURS,
)


def _make_request(method="POST", path="/api/test", body=b'{"key":"value"}',
                  has_key=True, has_user=True, has_session=True):
    request = MagicMock()
    request.method = method
    request.url.path = path

    # Use a proper dict for headers lookup
    headers_data = {}
    if has_key:
        headers_data["Idempotency-Key"] = "idem-key-123"

    request.headers = MagicMock()
    request.headers.get = lambda k, d=None: headers_data.get(k, d)

    # Body as coroutine
    async def get_body():
        return body
    request.body = get_body

    request.state = MagicMock()
    if has_user:
        request.state.user = MagicMock()
        request.state.user.id = uuid4()
    else:
        request.state.user = None

    if has_session:
        request.state.db_session = AsyncMock()

    return request


class TestIdempotencyMiddleware:
    def test_hash_request(self):
        middleware = IdempotencyMiddleware(app=MagicMock())
        h1 = middleware._hash_request(b'{"a":1}')
        h2 = middleware._hash_request(b'{"a":1}')
        h3 = middleware._hash_request(b'{"a":2}')

        assert h1 == h2
        assert h1 != h3

    @pytest.mark.asyncio
    async def test_get_method_bypasses(self):
        middleware = IdempotencyMiddleware(app=MagicMock())
        request = _make_request(method="GET")
        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(request, call_next)
        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_key_proceeds_normally(self):
        middleware = IdempotencyMiddleware(app=MagicMock())
        request = _make_request(has_key=False)
        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(request, call_next)
        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_user_proceeds_normally(self):
        middleware = IdempotencyMiddleware(app=MagicMock())
        request = _make_request(has_user=False)
        # Override state to not have user attribute at all
        state = MagicMock(spec=[])
        request.state = state
        call_next = AsyncMock(return_value=MagicMock())

        await middleware.dispatch(request, call_next)
        call_next.assert_called_once()


class TestCleanupExpiredKeys:
    @pytest.mark.asyncio
    async def test_cleanup_returns_count(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.rowcount = 5
        session.execute.return_value = result_mock

        count = await cleanup_expired_idempotency_keys(session)
        assert count == 5
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_zero_expired(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.rowcount = 0
        session.execute.return_value = result_mock

        count = await cleanup_expired_idempotency_keys(session)
        assert count == 0
