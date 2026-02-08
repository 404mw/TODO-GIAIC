"""Unit tests for Recovery API endpoints."""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException

from src.api.recovery import list_tombstones, recover_task, RECOVERY_WINDOW_DAYS
from src.services.recovery_service import (
    TombstoneNotFoundError,
    TaskIDCollisionError,
)


def _make_tombstone(**overrides):
    t = MagicMock()
    t.id = uuid4()
    t.entity_type = "task"
    t.entity_id = uuid4()
    t.entity_data = {"title": "Deleted Task", "priority": "medium"}
    t.deleted_at = datetime.now(UTC) - timedelta(days=1)
    for k, v in overrides.items():
        setattr(t, k, v)
    return t


def _make_task(**overrides):
    t = MagicMock()
    t.id = uuid4()
    t.title = "Recovered Task"
    t.description = "A recovered task"
    t.priority = "medium"
    t.due_date = None
    t.estimated_duration = None
    t.focus_time_seconds = 0
    t.completed = False
    t.completed_at = None
    t.completed_by = None
    t.hidden = False
    t.archived = False
    t.version = 1
    t.created_at = datetime.now(UTC)
    t.updated_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(t, k, v)
    return t


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = uuid4()
    return u


@pytest.fixture
def mock_service():
    return AsyncMock()


class TestListTombstones:
    @pytest.mark.asyncio
    async def test_success_with_tombstones(self, mock_user, mock_service):
        t1 = _make_tombstone(deleted_at=datetime.now(UTC) - timedelta(days=1))
        t2 = _make_tombstone(deleted_at=datetime.now(UTC) - timedelta(hours=2))
        mock_service.list_tombstones.return_value = [t1, t2]

        result = await list_tombstones(user=mock_user, service=mock_service)

        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_filters_out_expired(self, mock_user, mock_service):
        expired = _make_tombstone(
            deleted_at=datetime.now(UTC) - timedelta(days=RECOVERY_WINDOW_DAYS + 1)
        )
        valid = _make_tombstone(deleted_at=datetime.now(UTC) - timedelta(days=1))
        mock_service.list_tombstones.return_value = [expired, valid]

        result = await list_tombstones(user=mock_user, service=mock_service)

        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_empty_list(self, mock_user, mock_service):
        mock_service.list_tombstones.return_value = []

        result = await list_tombstones(user=mock_user, service=mock_service)

        assert len(result.data) == 0


class TestRecoverTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        tombstone = _make_tombstone()
        mock_service.get_tombstone.return_value = tombstone

        task = _make_task()
        task.template_id = None
        mock_service.recover_task.return_value = task

        result = await recover_task(
            tombstone_id=tombstone.id, user=mock_user, service=mock_service,
        )

        assert result.data.id == task.id

    @pytest.mark.asyncio
    async def test_tombstone_not_found(self, mock_user, mock_service):
        mock_service.get_tombstone.side_effect = TombstoneNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await recover_task(
                tombstone_id=uuid4(), user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_recovery_window_expired(self, mock_user, mock_service):
        tombstone = _make_tombstone(
            deleted_at=datetime.now(UTC) - timedelta(days=RECOVERY_WINDOW_DAYS + 1)
        )
        mock_service.get_tombstone.return_value = tombstone

        with pytest.raises(HTTPException) as exc_info:
            await recover_task(
                tombstone_id=tombstone.id, user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_task_id_collision(self, mock_user, mock_service):
        tombstone = _make_tombstone()
        mock_service.get_tombstone.return_value = tombstone
        mock_service.recover_task.side_effect = TaskIDCollisionError("Collision")

        with pytest.raises(HTTPException) as exc_info:
            await recover_task(
                tombstone_id=tombstone.id, user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_recover_tombstone_not_found_on_recover(self, mock_user, mock_service):
        tombstone = _make_tombstone()
        mock_service.get_tombstone.return_value = tombstone
        mock_service.recover_task.side_effect = TombstoneNotFoundError("Gone")

        with pytest.raises(HTTPException) as exc_info:
            await recover_task(
                tombstone_id=tombstone.id, user=mock_user, service=mock_service,
            )
        assert exc_info.value.status_code == 404
