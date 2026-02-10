"""Unit tests for subtask event handlers."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.events.subtask_handlers import (
    handle_subtask_completed,
    check_auto_complete_eligibility,
    SubtaskEvent,
    SubtaskCompletedEvent,
    SubtaskCreatedEvent,
    SubtaskDeletedEvent,
    SubtasksReorderedEvent,
)
from src.schemas.enums import CompletedBy


def _make_task(**overrides):
    t = MagicMock()
    t.id = uuid4()
    t.user_id = uuid4()
    t.completed = False
    t.completed_at = None
    t.completed_by = None
    t.hidden = False
    t.version = 1
    t.subtasks = []
    for k, v in overrides.items():
        setattr(t, k, v)
    return t


def _make_subtask(completed=False, **overrides):
    s = MagicMock()
    s.id = uuid4()
    s.completed = completed
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


class TestHandleSubtaskCompleted:
    @pytest.mark.asyncio
    async def test_task_not_found_returns_none(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        result = await handle_subtask_completed(
            session=session, user_id=uuid4(), task_id=uuid4(),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_task_already_completed_returns_none(self):
        session = AsyncMock()
        task = _make_task(completed=True)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await handle_subtask_completed(
            session=session, user_id=task.user_id, task_id=task.id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_no_subtasks_returns_none(self):
        session = AsyncMock()
        task = _make_task(subtasks=[])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await handle_subtask_completed(
            session=session, user_id=task.user_id, task_id=task.id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_not_all_completed_returns_none(self):
        session = AsyncMock()
        s1 = _make_subtask(completed=True)
        s2 = _make_subtask(completed=False)
        task = _make_task(subtasks=[s1, s2])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await handle_subtask_completed(
            session=session, user_id=task.user_id, task_id=task.id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_all_completed_auto_completes_task(self):
        session = AsyncMock()
        s1 = _make_subtask(completed=True)
        s2 = _make_subtask(completed=True)
        task = _make_task(subtasks=[s1, s2])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await handle_subtask_completed(
            session=session, user_id=task.user_id, task_id=task.id,
        )

        assert result is not None
        assert task.completed is True
        assert task.completed_by == CompletedBy.AUTO
        assert task.version == 2


class TestCheckAutoCompleteEligibility:
    @pytest.mark.asyncio
    async def test_task_not_found(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        result = await check_auto_complete_eligibility(
            session=session, task_id=uuid4(),
        )

        assert result["task_found"] is False
        assert result["eligible_for_auto_complete"] is False

    @pytest.mark.asyncio
    async def test_eligible_task(self):
        session = AsyncMock()
        s1 = _make_subtask(completed=True)
        s2 = _make_subtask(completed=True)
        task = _make_task(subtasks=[s1, s2])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await check_auto_complete_eligibility(
            session=session, task_id=task.id,
        )

        assert result["task_found"] is True
        assert result["total_subtasks"] == 2
        assert result["completed_subtasks"] == 2
        assert result["eligible_for_auto_complete"] is True

    @pytest.mark.asyncio
    async def test_partially_completed(self):
        session = AsyncMock()
        s1 = _make_subtask(completed=True)
        s2 = _make_subtask(completed=False)
        task = _make_task(subtasks=[s1, s2])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await check_auto_complete_eligibility(
            session=session, task_id=task.id,
        )

        assert result["eligible_for_auto_complete"] is False

    @pytest.mark.asyncio
    async def test_already_completed_task(self):
        session = AsyncMock()
        s1 = _make_subtask(completed=True)
        task = _make_task(completed=True, subtasks=[s1])
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        result = await check_auto_complete_eligibility(
            session=session, task_id=task.id,
        )

        assert result["task_completed"] is True
        assert result["eligible_for_auto_complete"] is False


class TestSubtaskEventClasses:
    def test_subtask_event(self):
        subtask_id = uuid4()
        task_id = uuid4()
        user_id = uuid4()

        event = SubtaskEvent(subtask_id, task_id, user_id)
        assert event.subtask_id == subtask_id
        assert event.task_id == task_id
        assert event.user_id == user_id
        assert event.timestamp is not None

    def test_subtask_completed_event(self):
        event = SubtaskCompletedEvent(uuid4(), uuid4(), uuid4())
        assert isinstance(event, SubtaskEvent)

    def test_subtask_created_event(self):
        event = SubtaskCreatedEvent(uuid4(), uuid4(), uuid4())
        assert isinstance(event, SubtaskEvent)

    def test_subtask_deleted_event(self):
        event = SubtaskDeletedEvent(uuid4(), uuid4(), uuid4())
        assert isinstance(event, SubtaskEvent)

    def test_subtasks_reordered_event(self):
        task_id = uuid4()
        user_id = uuid4()
        order = [uuid4(), uuid4()]

        event = SubtasksReorderedEvent(task_id, user_id, order)
        assert event.task_id == task_id
        assert event.user_id == user_id
        assert event.new_order == order
        assert event.timestamp is not None
