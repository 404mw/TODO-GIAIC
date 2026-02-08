"""Unit tests for Focus Mode API endpoints."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException

from src.api.focus import start_focus_session, end_focus_session
from src.services.focus_service import (
    FocusSessionActiveError,
    FocusSessionNotFoundError,
    FocusTaskNotFoundError,
)


def _make_session(**overrides):
    s = MagicMock()
    s.id = uuid4()
    s.task_id = uuid4()
    s.started_at = datetime.now(UTC)
    s.ended_at = None
    s.duration_seconds = None
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = uuid4()
    return u


@pytest.fixture
def mock_service():
    return AsyncMock()


class TestStartFocusSession:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        session = _make_session()
        mock_service.start_session.return_value = session
        data = MagicMock()
        data.task_id = session.task_id

        result = await start_focus_session(
            data=data, user=mock_user, service=mock_service,
        )

        assert result.data.id == session.id

    @pytest.mark.asyncio
    async def test_task_not_found(self, mock_user, mock_service):
        mock_service.start_session.side_effect = FocusTaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await start_focus_session(
                data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_session_already_active(self, mock_user, mock_service):
        mock_service.start_session.side_effect = FocusSessionActiveError("Active")

        with pytest.raises(HTTPException) as exc_info:
            await start_focus_session(
                data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 409


class TestEndFocusSession:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        session = _make_session(ended_at=datetime.now(UTC), duration_seconds=1200)
        mock_service.end_session.return_value = session
        data = MagicMock()
        data.task_id = session.task_id

        result = await end_focus_session(
            data=data, user=mock_user, service=mock_service,
        )

        assert result.data.duration_seconds == 1200

    @pytest.mark.asyncio
    async def test_session_not_found(self, mock_user, mock_service):
        mock_service.end_session.side_effect = FocusSessionNotFoundError("No session")

        with pytest.raises(HTTPException) as exc_info:
            await end_focus_session(
                data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_task_not_found(self, mock_user, mock_service):
        mock_service.end_session.side_effect = FocusTaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await end_focus_session(
                data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404
