"""Unit tests for Task API endpoints.

Tests all task CRUD endpoint functions directly with mocked dependencies.
"""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from src.api.tasks import (
    list_tasks,
    get_task,
    create_task,
    update_task,
    force_complete_task,
    delete_task,
)
from src.services.task_service import (
    TaskArchivedError,
    TaskDueDateExceededError,
    TaskLimitExceededError,
    TaskNotFoundError,
    TaskServiceError,
    TaskVersionConflictError,
)
from src.schemas.enums import CompletedBy, TaskPriority


def _make_task(**overrides):
    """Create a mock task with proper typed attributes."""
    task = MagicMock()
    task.id = uuid4()
    task.title = "Test Task"
    task.description = "A test description"
    task.priority = TaskPriority.MEDIUM
    task.due_date = None
    task.estimated_duration = None
    task.focus_time_seconds = 0
    task.completed = False
    task.completed_at = None
    task.completed_by = None
    task.hidden = False
    task.archived = False
    task.template_id = None
    task.version = 1
    task.created_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    task.subtasks = []
    task.reminders = []
    for k, v in overrides.items():
        setattr(task, k, v)
    return task


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.tier = "free"
    user.is_pro = False
    return user


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    s = MagicMock()
    s.free_max_subtasks = 5
    s.pro_max_subtasks = 10
    return s


# =============================================================================
# LIST TASKS
# =============================================================================


class TestListTasks:
    @pytest.mark.asyncio
    async def test_empty_list(self, mock_user, mock_service):
        mock_service.list_tasks.return_value = ([], 0)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.pagination.total == 0
        assert result.data == []
        assert result.pagination.has_more is False

    @pytest.mark.asyncio
    async def test_with_tasks(self, mock_user, mock_service):
        task = _make_task()
        mock_service.list_tasks.return_value = ([task], 1)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.pagination.total == 1
        assert len(result.data) == 1
        assert result.data[0].title == "Test Task"

    @pytest.mark.asyncio
    async def test_with_subtasks(self, mock_user, mock_service):
        sub1 = MagicMock(completed=True)
        sub2 = MagicMock(completed=False)
        task = _make_task(subtasks=[sub1, sub2])
        mock_service.list_tasks.return_value = ([task], 1)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.data[0].subtask_count == 2
        assert result.data[0].subtask_completed_count == 1

    @pytest.mark.asyncio
    async def test_has_more_pagination(self, mock_user, mock_service):
        task = _make_task()
        mock_service.list_tasks.return_value = ([task], 50)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.pagination.has_more is True

    @pytest.mark.asyncio
    async def test_no_more_pages(self, mock_user, mock_service):
        task = _make_task()
        mock_service.list_tasks.return_value = ([task], 1)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.pagination.has_more is False

    @pytest.mark.asyncio
    async def test_none_subtasks(self, mock_user, mock_service):
        """Tasks with no subtasks loaded (None instead of [])."""
        task = _make_task(subtasks=None)
        mock_service.list_tasks.return_value = ([task], 1)

        result = await list_tasks(
            user=mock_user, service=mock_service,
            offset=0, limit=25, completed=None, priority=None,
            hidden=False, due_before=None, due_after=None,
        )

        assert result.data[0].subtask_count == 0


# =============================================================================
# GET TASK
# =============================================================================


class TestGetTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        task = _make_task()
        mock_service.get_task.return_value = task

        result = await get_task(
            task_id=task.id, user=mock_user, service=mock_service,
        )

        assert result.data.id == task.id

    @pytest.mark.asyncio
    async def test_with_subtasks(self, mock_user, mock_service):
        sub = MagicMock()
        sub.id = uuid4()
        sub.title = "Subtask"
        sub.completed = False
        sub.completed_at = None
        sub.order_index = 0
        sub.source = MagicMock(value="user")
        task = _make_task(subtasks=[sub])
        mock_service.get_task.return_value = task

        result = await get_task(
            task_id=task.id, user=mock_user, service=mock_service,
        )

        assert len(result.data.subtasks) == 1

    @pytest.mark.asyncio
    async def test_with_reminders(self, mock_user, mock_service):
        reminder = MagicMock()
        reminder.id = uuid4()
        reminder.type = MagicMock(value="before")
        reminder.offset_minutes = 15
        reminder.scheduled_at = datetime.now(UTC)
        reminder.method = MagicMock(value="push")
        reminder.fired = False
        task = _make_task(reminders=[reminder])
        mock_service.get_task.return_value = task

        result = await get_task(
            task_id=task.id, user=mock_user, service=mock_service,
        )

        assert len(result.data.reminders) == 1

    @pytest.mark.asyncio
    async def test_with_no_reminders_attr(self, mock_user, mock_service):
        task = _make_task()
        # Remove reminders attribute entirely
        del task.reminders
        mock_service.get_task.return_value = task

        result = await get_task(
            task_id=task.id, user=mock_user, service=mock_service,
        )

        assert result.data.reminders == []

    @pytest.mark.asyncio
    async def test_with_null_method_reminder(self, mock_user, mock_service):
        reminder = MagicMock()
        reminder.id = uuid4()
        reminder.type = MagicMock(value="before")
        reminder.offset_minutes = 15
        reminder.scheduled_at = datetime.now(UTC)
        reminder.method = None
        reminder.fired = False
        task = _make_task(reminders=[reminder])
        mock_service.get_task.return_value = task

        result = await get_task(
            task_id=task.id, user=mock_user, service=mock_service,
        )

        assert result.data.reminders[0].method == "push"

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.get_task.side_effect = TaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_task(
                task_id=uuid4(), user=mock_user, service=mock_service,
            )

        assert exc_info.value.status_code == 404


# =============================================================================
# CREATE TASK
# =============================================================================


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        task = _make_task()
        mock_service.create_task.return_value = task

        result = await create_task(
            data=MagicMock(), user=mock_user,
            service=mock_service, idempotency_key="key-1",
        )

        assert result.data.id == task.id
        assert result.data.subtask_count == 0

    @pytest.mark.asyncio
    async def test_due_date_exceeded(self, mock_user, mock_service):
        mock_service.create_task.side_effect = TaskDueDateExceededError("Too far")

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key="key-1",
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_limit_exceeded(self, mock_user, mock_service):
        mock_service.create_task.side_effect = TaskLimitExceededError("Limit")

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key="key-1",
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.create_task.side_effect = TaskServiceError("Bad data")

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key="key-1",
            )

        assert exc_info.value.status_code == 400


# =============================================================================
# UPDATE TASK
# =============================================================================


class TestUpdateTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        task = _make_task()
        mock_service.update_task.return_value = task
        mock_service.get_task.return_value = task

        result = await update_task(
            task_id=task.id, data=MagicMock(), user=mock_user,
            service=mock_service, idempotency_key=None,
        )

        assert result.data.id == task.id

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.update_task.side_effect = TaskNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await update_task(
                task_id=uuid4(), data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key=None,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_version_conflict(self, mock_user, mock_service):
        mock_service.update_task.side_effect = TaskVersionConflictError("Stale")

        with pytest.raises(HTTPException) as exc_info:
            await update_task(
                task_id=uuid4(), data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key=None,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_archived(self, mock_user, mock_service):
        mock_service.update_task.side_effect = TaskArchivedError("Archived")

        with pytest.raises(HTTPException) as exc_info:
            await update_task(
                task_id=uuid4(), data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key=None,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_service_error(self, mock_user, mock_service):
        mock_service.update_task.side_effect = TaskServiceError("Bad")

        with pytest.raises(HTTPException) as exc_info:
            await update_task(
                task_id=uuid4(), data=MagicMock(), user=mock_user,
                service=mock_service, idempotency_key=None,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_subtask_counts_after_update(self, mock_user, mock_service):
        task = _make_task()
        sub = MagicMock(completed=True)
        task_with_subs = _make_task(id=task.id, subtasks=[sub])
        mock_service.update_task.return_value = task
        mock_service.get_task.return_value = task_with_subs

        result = await update_task(
            task_id=task.id, data=MagicMock(), user=mock_user,
            service=mock_service, idempotency_key=None,
        )

        assert result.data.subtask_count == 1
        assert result.data.subtask_completed_count == 1


# =============================================================================
# FORCE COMPLETE TASK
# =============================================================================


class TestForceCompleteTask:
    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service, mock_settings):
        mock_service.force_complete_task.side_effect = TaskNotFoundError("Nope")

        with pytest.raises(HTTPException) as exc_info:
            await force_complete_task(
                task_id=uuid4(), data=MagicMock(),
                user=mock_user, service=mock_service, settings=mock_settings,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_version_conflict(self, mock_user, mock_service, mock_settings):
        mock_service.force_complete_task.side_effect = TaskVersionConflictError("V")

        with pytest.raises(HTTPException) as exc_info:
            await force_complete_task(
                task_id=uuid4(), data=MagicMock(),
                user=mock_user, service=mock_service, settings=mock_settings,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_archived(self, mock_user, mock_service, mock_settings):
        mock_service.force_complete_task.side_effect = TaskArchivedError("Arc")

        with pytest.raises(HTTPException) as exc_info:
            await force_complete_task(
                task_id=uuid4(), data=MagicMock(),
                user=mock_user, service=mock_service, settings=mock_settings,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    @patch("src.services.achievement_service.get_achievement_service")
    async def test_success(
        self, mock_get_ach, mock_user, mock_service, mock_settings,
    ):
        now = datetime.now(UTC)
        task = _make_task(completed=True, completed_at=now, completed_by=CompletedBy.FORCE)
        mock_service.force_complete_task.return_value = task
        mock_service.get_task.return_value = task
        mock_service.session = MagicMock()

        mock_ach = AsyncMock()
        mock_state = MagicMock(current_streak=3)
        mock_ach.get_or_create_achievement_state.return_value = mock_state
        mock_ach.is_focus_completion.return_value = False
        mock_ach.check_and_unlock.return_value = []
        mock_get_ach.return_value = mock_ach

        result = await force_complete_task(
            task_id=task.id, data=MagicMock(),
            user=mock_user, service=mock_service, settings=mock_settings,
        )

        assert result.data.streak == 3
        assert result.data.unlocked_achievements == []
        mock_ach.update_streak.assert_awaited_once()
        mock_ach.increment_lifetime_tasks.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.services.achievement_service.get_achievement_service")
    async def test_success_with_focus_completion(
        self, mock_get_ach, mock_user, mock_service, mock_settings,
    ):
        now = datetime.now(UTC)
        task = _make_task(
            completed=True, completed_at=now,
            completed_by=CompletedBy.FORCE, focus_time_seconds=1800,
        )
        mock_service.force_complete_task.return_value = task
        mock_service.get_task.return_value = task
        mock_service.session = MagicMock()

        mock_ach = AsyncMock()
        mock_state = MagicMock(current_streak=1)
        mock_ach.get_or_create_achievement_state.return_value = mock_state
        mock_ach.is_focus_completion.return_value = True
        mock_ach.check_and_unlock.return_value = []
        mock_get_ach.return_value = mock_ach

        result = await force_complete_task(
            task_id=task.id, data=MagicMock(),
            user=mock_user, service=mock_service, settings=mock_settings,
        )

        mock_ach.increment_focus_completions.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.services.achievement_service.get_achievement_service")
    async def test_success_with_unlocked_achievements(
        self, mock_get_ach, mock_user, mock_service, mock_settings,
    ):
        now = datetime.now(UTC)
        task = _make_task(completed=True, completed_at=now, completed_by=CompletedBy.FORCE)
        mock_service.force_complete_task.return_value = task
        mock_service.get_task.return_value = task
        mock_service.session = MagicMock()

        mock_ach = AsyncMock()
        mock_state = MagicMock(current_streak=7)
        mock_ach.get_or_create_achievement_state.return_value = mock_state
        mock_ach.is_focus_completion.return_value = False
        mock_ach.check_and_unlock.return_value = [
            {
                "id": "streak_7",
                "name": "Week Warrior",
                "perk": {"type": MagicMock(value="bonus_subtasks"), "value": 2},
            }
        ]
        mock_get_ach.return_value = mock_ach

        result = await force_complete_task(
            task_id=task.id, data=MagicMock(),
            user=mock_user, service=mock_service, settings=mock_settings,
        )

        assert len(result.data.unlocked_achievements) == 1
        assert result.data.unlocked_achievements[0].name == "Week Warrior"

    @pytest.mark.asyncio
    @patch("src.services.achievement_service.get_achievement_service")
    async def test_success_achievement_no_perk(
        self, mock_get_ach, mock_user, mock_service, mock_settings,
    ):
        """Achievement without perk field."""
        now = datetime.now(UTC)
        task = _make_task(completed=True, completed_at=now, completed_by=CompletedBy.FORCE)
        mock_service.force_complete_task.return_value = task
        mock_service.get_task.return_value = task
        mock_service.session = MagicMock()

        mock_ach = AsyncMock()
        mock_state = MagicMock(current_streak=1)
        mock_ach.get_or_create_achievement_state.return_value = mock_state
        mock_ach.is_focus_completion.return_value = False
        mock_ach.check_and_unlock.return_value = [
            {"id": "first_task", "name": "First Steps"}
        ]
        mock_get_ach.return_value = mock_ach

        result = await force_complete_task(
            task_id=task.id, data=MagicMock(),
            user=mock_user, service=mock_service, settings=mock_settings,
        )

        assert result.data.unlocked_achievements[0].perk_type is None


# =============================================================================
# DELETE TASK
# =============================================================================


class TestDeleteTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_service):
        tombstone = MagicMock()
        tombstone.id = uuid4()
        tombstone.deleted_at = datetime.now(UTC)
        mock_service.hard_delete_task.return_value = tombstone

        result = await delete_task(
            task_id=uuid4(), user=mock_user, service=mock_service,
        )

        assert result.data.tombstone_id == tombstone.id
        assert result.data.recoverable_until is not None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_service):
        mock_service.hard_delete_task.side_effect = TaskNotFoundError("Nope")

        with pytest.raises(HTTPException) as exc_info:
            await delete_task(
                task_id=uuid4(), user=mock_user, service=mock_service,
            )

        assert exc_info.value.status_code == 404
