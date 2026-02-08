"""Mock-based unit tests for TaskService.

Covers uncovered code paths beyond the integration tests in test_task_service.py:
- list_tasks with various filters (due_before, due_after, priority, hidden)
- force_complete_task (archived, version conflict)
- complete_task (archived, version conflict)
- delete_task subtask cascade + tombstone enforcement
- update_subtask (title, completion toggling)
- delete_subtask reordering
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from uuid import uuid4

from src.schemas.enums import CompletedBy, TaskPriority, SubtaskSource


def _make_service():
    from src.services.task_service import TaskService

    session = AsyncMock()
    settings = MagicMock()
    settings.free_max_tasks = 50
    settings.pro_max_tasks = 500
    settings.max_subtasks_per_task = 20
    settings.max_due_date_days = 365
    service = TaskService(session, settings)
    return service, session, settings


def _make_user(**overrides):
    u = MagicMock()
    u.id = uuid4()
    u.is_pro = False
    for k, v in overrides.items():
        setattr(u, k, v)
    return u


def _make_task(**overrides):
    t = MagicMock()
    t.id = uuid4()
    t.user_id = uuid4()
    t.title = "Test Task"
    t.description = None
    t.priority = TaskPriority.MEDIUM
    t.completed = False
    t.completed_at = None
    t.completed_by = None
    t.archived = False
    t.hidden = False
    t.version = 1
    t.subtasks = []
    t.created_at = datetime.now(UTC)
    t.updated_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(t, k, v)
    return t


def _make_subtask(**overrides):
    s = MagicMock()
    s.id = uuid4()
    s.task_id = uuid4()
    s.title = "Test Subtask"
    s.completed = False
    s.completed_at = None
    s.order_index = 0
    s.source = SubtaskSource.USER
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


class TestListTasksFilters:
    @pytest.mark.asyncio
    async def test_list_with_priority_filter(self):
        service, session, _ = _make_service()
        user = _make_user()

        count_result = MagicMock()
        count_result.scalar.return_value = 1
        task_result = MagicMock()
        task_result.scalars.return_value.unique.return_value.all.return_value = [_make_task()]

        session.execute.side_effect = [count_result, task_result]

        tasks, total = await service.list_tasks(
            user=user, priority=TaskPriority.HIGH, offset=0, limit=25,
        )

        assert total == 1
        assert len(tasks) == 1

    @pytest.mark.asyncio
    async def test_list_with_due_before_filter(self):
        service, session, _ = _make_service()
        user = _make_user()

        count_result = MagicMock()
        count_result.scalar.return_value = 0
        task_result = MagicMock()
        task_result.scalars.return_value.unique.return_value.all.return_value = []

        session.execute.side_effect = [count_result, task_result]

        tasks, total = await service.list_tasks(
            user=user, due_before=datetime.now(UTC), offset=0, limit=25,
        )

        assert total == 0

    @pytest.mark.asyncio
    async def test_list_with_due_after_filter(self):
        service, session, _ = _make_service()
        user = _make_user()

        count_result = MagicMock()
        count_result.scalar.return_value = 2
        task_result = MagicMock()
        task_result.scalars.return_value.unique.return_value.all.return_value = [_make_task(), _make_task()]

        session.execute.side_effect = [count_result, task_result]

        tasks, total = await service.list_tasks(
            user=user, due_after=datetime.now(UTC), offset=0, limit=25,
        )

        assert total == 2

    @pytest.mark.asyncio
    async def test_list_with_hidden_flag(self):
        service, session, _ = _make_service()
        user = _make_user()

        count_result = MagicMock()
        count_result.scalar.return_value = 3
        task_result = MagicMock()
        task_result.scalars.return_value.unique.return_value.all.return_value = [_make_task()] * 3

        session.execute.side_effect = [count_result, task_result]

        tasks, total = await service.list_tasks(
            user=user, hidden=True, offset=0, limit=25,
        )

        assert total == 3

    @pytest.mark.asyncio
    async def test_list_completed_filter(self):
        service, session, _ = _make_service()
        user = _make_user()

        count_result = MagicMock()
        count_result.scalar.return_value = 5
        task_result = MagicMock()
        task_result.scalars.return_value.unique.return_value.all.return_value = [_make_task(completed=True)] * 5

        session.execute.side_effect = [count_result, task_result]

        tasks, total = await service.list_tasks(
            user=user, completed=True, offset=0, limit=25,
        )

        assert total == 5


class TestCompleteTaskErrors:
    @pytest.mark.asyncio
    async def test_archived_task_raises(self):
        from src.services.task_service import TaskArchivedError

        service, session, _ = _make_service()
        user = _make_user()
        task = _make_task(archived=True, user_id=user.id)

        # Mock get_task
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        with pytest.raises(TaskArchivedError):
            await service.complete_task(
                user=user, task_id=task.id, completed_by=CompletedBy.MANUAL,
            )

    @pytest.mark.asyncio
    @patch("src.services.task_service.record_task_version_conflict")
    async def test_version_conflict_raises(self, mock_record):
        from src.services.task_service import TaskVersionConflictError

        service, session, _ = _make_service()
        user = _make_user()
        task = _make_task(version=2, user_id=user.id)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        with pytest.raises(TaskVersionConflictError):
            await service.complete_task(
                user=user, task_id=task.id,
                completed_by=CompletedBy.MANUAL, version=1,
            )


class TestForceCompleteTaskErrors:
    @pytest.mark.asyncio
    async def test_archived_task_raises(self):
        from src.services.task_service import TaskArchivedError
        from src.schemas.task import ForceCompleteRequest

        service, session, _ = _make_service()
        user = _make_user()
        task = _make_task(archived=True, user_id=user.id)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        data = MagicMock(spec=ForceCompleteRequest)
        data.version = 1

        with pytest.raises(TaskArchivedError):
            await service.force_complete_task(user=user, task_id=task.id, data=data)

    @pytest.mark.asyncio
    @patch("src.services.task_service.record_task_version_conflict")
    async def test_version_conflict_raises(self, mock_record):
        from src.services.task_service import TaskVersionConflictError
        from src.schemas.task import ForceCompleteRequest

        service, session, _ = _make_service()
        user = _make_user()
        task = _make_task(version=5, user_id=user.id)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = task
        session.execute.return_value = result_mock

        data = MagicMock(spec=ForceCompleteRequest)
        data.version = 3

        with pytest.raises(TaskVersionConflictError):
            await service.force_complete_task(user=user, task_id=task.id, data=data)


class TestDeleteSubtaskReorder:
    @pytest.mark.asyncio
    async def test_reorders_remaining_subtasks(self):
        service, session, _ = _make_service()
        user = _make_user()

        subtask = _make_subtask(order_index=1)
        # get_subtask mock
        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = subtask

        remaining_s1 = _make_subtask(order_index=2)
        remaining_s2 = _make_subtask(order_index=3)

        remaining_result = MagicMock()
        remaining_result.scalars.return_value.all.return_value = [remaining_s1, remaining_s2]

        session.execute.side_effect = [get_result, remaining_result]

        await service.delete_subtask(user=user, subtask_id=subtask.id)

        assert remaining_s1.order_index == 1
        assert remaining_s2.order_index == 2


class TestUpdateSubtaskFields:
    @pytest.mark.asyncio
    async def test_update_title(self):
        service, session, _ = _make_service()
        user = _make_user()
        subtask = _make_subtask()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = subtask
        session.execute.return_value = result_mock

        result = await service.update_subtask(
            user=user, subtask_id=subtask.id, title="Updated Title",
        )

        assert subtask.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_mark_completed(self):
        service, session, _ = _make_service()
        user = _make_user()
        subtask = _make_subtask(completed=False)

        # get_subtask query
        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = subtask

        # _check_auto_complete -> get_task query returns already-completed task
        # so auto-complete is skipped
        auto_task = _make_task(completed=True)
        auto_result = MagicMock()
        auto_result.scalar_one_or_none.return_value = auto_task

        session.execute.side_effect = [get_result, auto_result]

        result = await service.update_subtask(
            user=user, subtask_id=subtask.id, completed=True,
        )

        assert subtask.completed is True
        assert subtask.completed_at is not None

    @pytest.mark.asyncio
    async def test_mark_uncompleted(self):
        service, session, _ = _make_service()
        user = _make_user()
        subtask = _make_subtask(completed=True, completed_at=datetime.now(UTC))

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = subtask
        session.execute.return_value = result_mock

        result = await service.update_subtask(
            user=user, subtask_id=subtask.id, completed=False,
        )

        assert subtask.completed is False
        assert subtask.completed_at is None


class TestEnforceTombstoneLimit:
    @pytest.mark.asyncio
    async def test_under_limit_no_deletion(self):
        service, session, _ = _make_service()

        count_result = MagicMock()
        count_result.scalar.return_value = 1
        session.execute.return_value = count_result

        await service._enforce_tombstone_limit(uuid4())
        # Only one call for count, no deletion
        assert session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_at_limit_deletes_oldest(self):
        service, session, _ = _make_service()

        count_result = MagicMock()
        count_result.scalar.return_value = 3

        oldest_tombstone = MagicMock()
        oldest_result = MagicMock()
        oldest_result.scalars.return_value.all.return_value = [oldest_tombstone]

        session.execute.side_effect = [count_result, oldest_result]

        await service._enforce_tombstone_limit(uuid4())
        session.delete.assert_called_once_with(oldest_tombstone)
