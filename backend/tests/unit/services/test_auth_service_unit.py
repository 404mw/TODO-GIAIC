"""Mock-based unit tests for AuthService.

Covers uncovered code paths:
- verify_google_token
- revoke_refresh_token (found and not found)
- authenticate_with_google (success and failure paths)
- get_auth_service factory
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


def _make_service():
    from src.services.auth_service import AuthService

    session = AsyncMock()
    settings = MagicMock()
    settings.jwt_secret = "test-secret-key"
    settings.jwt_algorithm = "HS256"
    settings.access_token_expire_minutes = 30
    settings.refresh_token_expire_days = 7
    settings.google_client_id = "test-client-id"
    service = AuthService(session, settings)
    return service, session, settings


class TestVerifyGoogleToken:
    @pytest.mark.asyncio
    async def test_delegates_to_google_client(self):
        service, _, _ = _make_service()
        expected = {"sub": "123", "email": "test@example.com"}
        service.google_client = AsyncMock()
        service.google_client.verify_id_token.return_value = expected

        result = await service.verify_google_token("fake-token")
        assert result == expected
        service.google_client.verify_id_token.assert_called_once_with("fake-token")


class TestRevokeRefreshToken:
    @pytest.mark.asyncio
    async def test_revokes_existing_token(self):
        service, session, _ = _make_service()

        token_record = MagicMock()
        token_record.revoked = False
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = token_record
        session.execute.return_value = result_mock

        result = await service.revoke_refresh_token("some-refresh-token")

        assert result is True
        assert token_record.revoked is True
        assert token_record.revoked_at is not None

    @pytest.mark.asyncio
    async def test_returns_false_if_not_found(self):
        service, session, _ = _make_service()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        result = await service.revoke_refresh_token("nonexistent-token")
        assert result is False


class TestAuthenticateWithGoogle:
    @pytest.mark.asyncio
    @patch("src.services.auth_service.record_auth_operation")
    @patch("src.services.auth_service.record_auth_latency")
    async def test_success(self, mock_latency, mock_operation):
        service, session, _ = _make_service()

        google_data = {
            "sub": "google_123",
            "email": "user@gmail.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
        }
        service.verify_google_token = AsyncMock(return_value=google_data)

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "user@gmail.com"
        service.create_or_update_user = AsyncMock(return_value=mock_user)
        service.generate_tokens = AsyncMock(
            return_value=("access_token", "refresh_token")
        )

        user, access, refresh = await service.authenticate_with_google("id-token")

        assert user == mock_user
        assert access == "access_token"
        assert refresh == "refresh_token"
        mock_operation.assert_called_with("login", "success")

    @pytest.mark.asyncio
    @patch("src.services.auth_service.record_auth_operation")
    @patch("src.services.auth_service.record_auth_latency")
    async def test_failure_records_metrics(self, mock_latency, mock_operation):
        service, _, _ = _make_service()
        service.verify_google_token = AsyncMock(
            side_effect=Exception("Token invalid")
        )

        with pytest.raises(Exception, match="Token invalid"):
            await service.authenticate_with_google("bad-token")

        mock_operation.assert_called_with("login", "failure")


class TestGetAuthServiceFactory:
    def test_returns_service_instance(self):
        from src.services.auth_service import AuthService, get_auth_service

        session = AsyncMock()
        settings = MagicMock()
        settings.jwt_secret = "secret"
        settings.jwt_algorithm = "HS256"
        settings.access_token_expire_minutes = 30
        settings.refresh_token_expire_days = 7
        settings.google_client_id = "client-id"
        result = get_auth_service(session, settings)
        assert isinstance(result, AuthService)
