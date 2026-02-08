"""Unit tests for Reminder API endpoints."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException

from src.api.reminders import (
    create_reminder,
    update_reminder,
    delete_reminder,
)
from src.services.reminder_service import (
    ReminderLimitExceededError,
    ReminderNotFoundError,
    ReminderServiceError,
    TaskNoDueDateError,
    TaskNotFoundError,
)
from src.schemas.enums import ReminderType


def _make_reminder(**overrides):
    r = MagicMock()
    r.id = uuid4()
    r.task_id = uuid4()
    r.type = ReminderType.BEFORE
    r.offset_minutes = 30
    r.scheduled_at = datetime.now(UTC)
    r.method = "push"
    r.fired = False
    r.fired_at = None
    r.created_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(r, k, v)
    return r


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = uuid4()
    return u


@pytest.fixture
def mock_service():
    return AsyncMock()


class TestCreateReminder:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        reminder = _make_reminder()
        mock_service.create_reminder.return_value = reminder

        result = await create_reminder(
            task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
        )

        assert result.data.id == reminder.id

    @pytest.mark.asyncio
    async def test_task_not_found(self, mock_user, mock_service):
        mock_service.create_reminder.side_effect = TaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await create_reminder(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_no_due_date(self, mock_user, mock_service):
        mock_service.create_reminder.side_effect = TaskNoDueDateError("No due date")

        with pytest.raises(HTTPException) as exc_info:
            await create_reminder(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_limit_exceeded(self, mock_user, mock_service):
        mock_service.create_reminder.side_effect = ReminderLimitExceededError("Max 5")

        with pytest.raises(HTTPException) as exc_info:
            await create_reminder(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.create_reminder.side_effect = ReminderServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await create_reminder(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400


class TestUpdateReminder:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        reminder = _make_reminder()
        mock_service.update_reminder.return_value = reminder

        result = await update_reminder(
            reminder_id=reminder.id, data=MagicMock(), user=mock_user, service=mock_service,
        )

        assert result.data.id == reminder.id

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.update_reminder.side_effect = ReminderNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await update_reminder(
                reminder_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.update_reminder.side_effect = ReminderServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await update_reminder(
                reminder_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400


class TestDeleteReminder:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        result = await delete_reminder(
            reminder_id=uuid4(), user=mock_user, service=mock_service,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.delete_reminder.side_effect = ReminderNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_reminder(
                reminder_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.delete_reminder.side_effect = ReminderServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await delete_reminder(
                reminder_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400
