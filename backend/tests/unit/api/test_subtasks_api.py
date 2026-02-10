"""Unit tests for Subtask API endpoints."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException

from src.api.subtasks import (
    create_subtask,
    reorder_subtasks,
    update_subtask,
    delete_subtask,
)
from src.services.task_service import (
    SubtaskLimitExceededError,
    SubtaskNotFoundError,
    TaskNotFoundError,
    TaskServiceError,
)
from src.schemas.enums import SubtaskSource


def _make_subtask(**overrides):
    s = MagicMock()
    s.id = uuid4()
    s.task_id = uuid4()
    s.title = "Test Subtask"
    s.completed = False
    s.completed_at = None
    s.order_index = 0
    s.source = SubtaskSource.USER
    s.created_at = datetime.now(UTC)
    s.updated_at = datetime.now(UTC)
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


class TestCreateSubtask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        subtask = _make_subtask()
        mock_service.create_subtask.return_value = subtask

        result = await create_subtask(
            task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
        )

        assert result.data.id == subtask.id

    @pytest.mark.asyncio
    async def test_task_not_found(self, mock_user, mock_service):
        mock_service.create_subtask.side_effect = TaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await create_subtask(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_limit_exceeded(self, mock_user, mock_service):
        mock_service.create_subtask.side_effect = SubtaskLimitExceededError("Limit")

        with pytest.raises(HTTPException) as exc_info:
            await create_subtask(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.create_subtask.side_effect = TaskServiceError("Bad")

        with pytest.raises(HTTPException) as exc_info:
            await create_subtask(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400


class TestReorderSubtasks:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        s1 = _make_subtask(order_index=0)
        s2 = _make_subtask(order_index=1)
        mock_service.reorder_subtasks.return_value = [s1, s2]

        data = MagicMock()
        data.subtask_ids = [s1.id, s2.id]

        result = await reorder_subtasks(
            task_id=uuid4(), data=data, user=mock_user, service=mock_service,
        )

        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_task_not_found(self, mock_user, mock_service):
        mock_service.reorder_subtasks.side_effect = TaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await reorder_subtasks(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_subtask_not_found(self, mock_user, mock_service):
        mock_service.reorder_subtasks.side_effect = SubtaskNotFoundError("Bad ID")

        with pytest.raises(HTTPException) as exc_info:
            await reorder_subtasks(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.reorder_subtasks.side_effect = TaskServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await reorder_subtasks(
                task_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400


class TestUpdateSubtask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        subtask = _make_subtask()
        mock_service.update_subtask.return_value = subtask

        data = MagicMock()
        data.title = "Updated"
        data.completed = None

        result = await update_subtask(
            subtask_id=subtask.id, data=data, user=mock_user, service=mock_service,
        )

        assert result.data.id == subtask.id

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.update_subtask.side_effect = SubtaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await update_subtask(
                subtask_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.update_subtask.side_effect = TaskServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await update_subtask(
                subtask_id=uuid4(), data=MagicMock(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400


class TestDeleteSubtask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        result = await delete_subtask(
            subtask_id=uuid4(), user=mock_user, service=mock_service,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.delete_subtask.side_effect = SubtaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_subtask(
                subtask_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.delete_subtask.side_effect = TaskServiceError("Error")

        with pytest.raises(HTTPException) as exc_info:
            await delete_subtask(
                subtask_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 400
