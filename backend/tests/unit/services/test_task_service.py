"""Unit tests for TaskService.

RED phase tests for Phase 4: User Story 2 - Task Creation and Management.

T090-T105: Tests for task and subtask CRUD operations.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.task import TaskInstance
from src.models.subtask import Subtask
from src.models.user import User
from src.schemas.enums import (
    CompletedBy,
    SubtaskSource,
    TaskPriority,
    UserTier,
)
from src.schemas.task import TaskCreate, TaskUpdate, ForceCompleteRequest
from src.schemas.subtask import SubtaskCreate


# =============================================================================
# Service Import (will fail initially - TDD RED phase)
# =============================================================================

from src.services.task_service import (
    TaskService,
    TaskServiceError,
    TaskNotFoundError,
    TaskVersionConflictError,
    TaskArchivedError,
    SubtaskLimitExceededError,
    TaskLimitExceededError,
    TaskDueDateExceededError,
)


# =============================================================================
# Task Creation Tests (T090-T092)
# =============================================================================


class TestTaskCreation:
    """Tests for task creation functionality (FR-007)."""

    @pytest.mark.asyncio
    async def test_create_task_with_title_priority_due_date(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T090: Create task with title, priority, due_date.

        FR-007: User can create a task with title (required), priority, due date.
        """
        service = TaskService(db_session, settings)

        due_date = datetime.now(UTC) + timedelta(days=7)
        task_data = TaskCreate(
            title="Complete quarterly report",
            priority=TaskPriority.HIGH,
            due_date=due_date,
        )

        task = await service.create_task(user=test_user, data=task_data)

        assert task.id is not None
        assert task.title == "Complete quarterly report"
        assert task.priority == TaskPriority.HIGH
        assert task.due_date is not None
        assert task.user_id == test_user.id
        assert task.completed is False
        assert task.hidden is False
        assert task.archived is False
        assert task.version == 1

    @pytest.mark.asyncio
    async def test_task_title_validation_1_to_200_chars(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T091: Task title validation 1-200 chars.

        Title must be between 1 and 200 characters.
        """
        service = TaskService(db_session, settings)

        # Test valid title at minimum length
        task_data = TaskCreate(title="A")
        task = await service.create_task(user=test_user, data=task_data)
        assert task.title == "A"

        # Test valid title at maximum length
        long_title = "A" * 200
        task_data = TaskCreate(title=long_title)
        task = await service.create_task(user=test_user, data=task_data)
        assert task.title == long_title
        assert len(task.title) == 200

    @pytest.mark.asyncio
    async def test_description_max_length_enforced_by_tier(
        self,
        db_session: AsyncSession,
        test_user: User,
        pro_user: User,
        settings: Settings,
    ):
        """T092: Description max length enforced by tier (FR-007).

        Free tier: 1000 chars max
        Pro tier: 2000 chars max
        """
        service = TaskService(db_session, settings)

        # Free user - 1000 char limit
        short_desc = "A" * 1000
        task_data = TaskCreate(title="Test", description=short_desc)
        task = await service.create_task(user=test_user, data=task_data)
        assert len(task.description) == 1000

        # Free user - exceeding 1000 chars should fail
        long_desc = "A" * 1001
        task_data = TaskCreate(title="Test", description=long_desc)
        with pytest.raises(TaskServiceError):
            await service.create_task(user=test_user, data=task_data)

        # Pro user - 2000 char limit
        pro_desc = "A" * 2000
        task_data = TaskCreate(title="Test", description=pro_desc)
        task = await service.create_task(user=pro_user, data=task_data)
        assert len(task.description) == 2000


# =============================================================================
# Task Update Tests with Optimistic Locking (T093)
# =============================================================================


class TestTaskUpdate:
    """Tests for task update with optimistic locking (FR-014)."""

    @pytest.mark.asyncio
    async def test_update_task_with_optimistic_locking_returns_409_on_stale_version(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T093: Update task with optimistic locking returns 409 on stale version.

        FR-014: Optimistic locking prevents stale updates.
        """
        service = TaskService(db_session, settings)

        # Create a task
        task_data = TaskCreate(title="Original title")
        task = await service.create_task(user=test_user, data=task_data)
        original_version = task.version

        # First update succeeds
        update_data = TaskUpdate(title="Updated title", version=original_version)
        updated_task = await service.update_task(
            user=test_user, task_id=task.id, data=update_data
        )
        assert updated_task.version == original_version + 1

        # Second update with stale version should fail with 409
        stale_update = TaskUpdate(title="Stale update", version=original_version)
        with pytest.raises(TaskVersionConflictError):
            await service.update_task(user=test_user, task_id=task.id, data=stale_update)


# =============================================================================
# Task Completion Tests (T094-T097)
# =============================================================================


class TestTaskCompletion:
    """Tests for task completion functionality (FR-008 to FR-011)."""

    @pytest.mark.asyncio
    async def test_complete_task_sets_completed_at_and_completed_by(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T094: Complete task sets completed_at and completed_by (FR-008)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Test task")
        task = await service.create_task(user=test_user, data=task_data)

        # Complete the task manually
        update_data = TaskUpdate(completed=True, version=task.version)
        completed_task = await service.update_task(
            user=test_user, task_id=task.id, data=update_data
        )

        assert completed_task.completed is True
        assert completed_task.completed_at is not None
        assert completed_task.completed_by == CompletedBy.MANUAL

    @pytest.mark.asyncio
    async def test_auto_complete_task_when_all_subtasks_complete(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T095: Auto-complete task when all subtasks complete (FR-009)."""
        service = TaskService(db_session, settings)

        # Create task with subtasks
        task_data = TaskCreate(title="Task with subtasks")
        task = await service.create_task(user=test_user, data=task_data)

        # Add subtasks
        subtask1 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Subtask 1"),
        )
        subtask2 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Subtask 2"),
        )

        # Complete first subtask
        await service.update_subtask(
            user=test_user, subtask_id=subtask1.id, completed=True
        )

        # Refresh task - should still be incomplete
        task = await service.get_task(user=test_user, task_id=task.id)
        assert task.completed is False

        # Complete second subtask
        await service.update_subtask(
            user=test_user, subtask_id=subtask2.id, completed=True
        )

        # Refresh task - should be auto-completed
        task = await service.get_task(user=test_user, task_id=task.id)
        assert task.completed is True
        assert task.completed_by == CompletedBy.AUTO

    @pytest.mark.asyncio
    async def test_force_complete_marks_all_subtasks_complete(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T096: Force-complete marks all subtasks complete (FR-010)."""
        service = TaskService(db_session, settings)

        # Create task with subtasks
        task_data = TaskCreate(title="Task with subtasks")
        task = await service.create_task(user=test_user, data=task_data)

        # Add incomplete subtasks
        await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Subtask 1"),
        )
        await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Subtask 2"),
        )

        # Force complete the task
        completed_task = await service.force_complete_task(
            user=test_user,
            task_id=task.id,
            data=ForceCompleteRequest(version=task.version),
        )

        assert completed_task.completed is True
        assert completed_task.completed_by == CompletedBy.FORCE

        # Check all subtasks are completed
        task_with_subtasks = await service.get_task(
            user=test_user, task_id=task.id, include_subtasks=True
        )
        for subtask in task_with_subtasks.subtasks:
            assert subtask.completed is True

    @pytest.mark.asyncio
    async def test_cannot_complete_archived_task_returns_409(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T097: Cannot complete archived task returns 409 (FR-011)."""
        service = TaskService(db_session, settings)

        # Create and archive a task
        task_data = TaskCreate(title="Archived task")
        task = await service.create_task(user=test_user, data=task_data)

        # Archive the task
        update_data = TaskUpdate(archived=True, version=task.version)
        archived_task = await service.update_task(
            user=test_user, task_id=task.id, data=update_data
        )

        # Try to complete the archived task
        complete_data = TaskUpdate(completed=True, version=archived_task.version)
        with pytest.raises(TaskArchivedError):
            await service.update_task(
                user=test_user, task_id=task.id, data=complete_data
            )


# =============================================================================
# Task Deletion Tests (T098-T099)
# =============================================================================


class TestTaskDeletion:
    """Tests for task deletion functionality (FR-012)."""

    @pytest.mark.asyncio
    async def test_soft_delete_sets_hidden_flag(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T098: Soft delete sets hidden flag (FR-012)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="To be soft deleted")
        task = await service.create_task(user=test_user, data=task_data)

        # Soft delete the task
        deleted_task = await service.soft_delete_task(
            user=test_user, task_id=task.id
        )

        assert deleted_task.hidden is True

        # Task should still be retrievable with include_hidden=True
        retrieved = await service.get_task(
            user=test_user, task_id=task.id, include_hidden=True
        )
        assert retrieved is not None
        assert retrieved.hidden is True

    @pytest.mark.asyncio
    async def test_hard_delete_creates_tombstone(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T099: Hard delete creates tombstone (FR-012)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="To be hard deleted")
        task = await service.create_task(user=test_user, data=task_data)
        task_id = task.id

        # Hard delete the task
        tombstone = await service.hard_delete_task(
            user=test_user, task_id=task_id
        )

        assert tombstone is not None
        assert tombstone.entity_id == task_id
        assert tombstone.user_id == test_user.id
        assert "title" in tombstone.entity_data
        assert tombstone.entity_data["title"] == "To be hard deleted"

        # Task should no longer be retrievable
        with pytest.raises(TaskNotFoundError):
            await service.get_task(user=test_user, task_id=task_id)


# =============================================================================
# Subtask Tests (T101-T105)
# =============================================================================


class TestSubtasks:
    """Tests for subtask functionality (FR-019 to FR-021)."""

    @pytest.mark.asyncio
    async def test_create_subtask_with_correct_order_index(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T101: Create subtask with correct order_index."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Parent task")
        task = await service.create_task(user=test_user, data=task_data)

        # Create subtasks and verify order indices
        subtask1 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="First subtask"),
        )
        assert subtask1.order_index == 0

        subtask2 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Second subtask"),
        )
        assert subtask2.order_index == 1

        subtask3 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Third subtask"),
        )
        assert subtask3.order_index == 2

    @pytest.mark.asyncio
    async def test_free_user_limited_to_4_subtasks(
        self,
        db_session: AsyncSession,
        test_user: User,  # Free tier
        settings: Settings,
    ):
        """T102: Free user limited to 4 subtasks (FR-019)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Parent task")
        task = await service.create_task(user=test_user, data=task_data)

        # Create 4 subtasks (should succeed)
        for i in range(4):
            await service.create_subtask(
                user=test_user,
                task_id=task.id,
                data=SubtaskCreate(title=f"Subtask {i + 1}"),
            )

        # 5th subtask should fail
        with pytest.raises(SubtaskLimitExceededError):
            await service.create_subtask(
                user=test_user,
                task_id=task.id,
                data=SubtaskCreate(title="Subtask 5"),
            )

    @pytest.mark.asyncio
    async def test_pro_user_limited_to_10_subtasks(
        self,
        db_session: AsyncSession,
        pro_user: User,
        settings: Settings,
    ):
        """T103: Pro user limited to 10 subtasks (FR-019)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Parent task")
        task = await service.create_task(user=pro_user, data=task_data)

        # Create 10 subtasks (should succeed)
        for i in range(10):
            await service.create_subtask(
                user=pro_user,
                task_id=task.id,
                data=SubtaskCreate(title=f"Subtask {i + 1}"),
            )

        # 11th subtask should fail
        with pytest.raises(SubtaskLimitExceededError):
            await service.create_subtask(
                user=pro_user,
                task_id=task.id,
                data=SubtaskCreate(title="Subtask 11"),
            )

    @pytest.mark.asyncio
    async def test_reorder_subtasks_maintains_gapless_indices(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T104: Reorder subtasks maintains gapless indices (FR-020)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Parent task")
        task = await service.create_task(user=test_user, data=task_data)

        # Create 3 subtasks
        subtask1 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="First"),
        )
        subtask2 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Second"),
        )
        subtask3 = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="Third"),
        )

        # Reorder: Third, First, Second
        reordered = await service.reorder_subtasks(
            user=test_user,
            task_id=task.id,
            subtask_ids=[subtask3.id, subtask1.id, subtask2.id],
        )

        assert reordered[0].id == subtask3.id
        assert reordered[0].order_index == 0
        assert reordered[1].id == subtask1.id
        assert reordered[1].order_index == 1
        assert reordered[2].id == subtask2.id
        assert reordered[2].order_index == 2

    @pytest.mark.asyncio
    async def test_subtask_source_tracked_user_vs_ai(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T105: Subtask source tracked (user vs ai) (FR-021)."""
        service = TaskService(db_session, settings)

        task_data = TaskCreate(title="Parent task")
        task = await service.create_task(user=test_user, data=task_data)

        # User-created subtask
        user_subtask = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="User subtask"),
            source=SubtaskSource.USER,
        )
        assert user_subtask.source == SubtaskSource.USER

        # AI-created subtask
        ai_subtask = await service.create_subtask(
            user=test_user,
            task_id=task.id,
            data=SubtaskCreate(title="AI subtask"),
            source=SubtaskSource.AI,
        )
        assert ai_subtask.source == SubtaskSource.AI


# =============================================================================
# Task Duration Validation Tests (T130a, T130b)
# =============================================================================


class TestTaskDurationValidation:
    """Tests for 30-day max duration validation (FR-013)."""

    @pytest.mark.asyncio
    async def test_task_creation_fails_if_due_date_exceeds_30_days(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T130a: Task creation fails if due_date > created_at + 30 days (FR-013)."""
        service = TaskService(db_session, settings)

        # Due date exactly 31 days from now should fail
        invalid_due_date = datetime.now(UTC) + timedelta(days=31)
        task_data = TaskCreate(
            title="Task with too far due date",
            due_date=invalid_due_date,
        )

        with pytest.raises(TaskDueDateExceededError):
            await service.create_task(user=test_user, data=task_data)

    @pytest.mark.asyncio
    async def test_task_creation_succeeds_with_due_date_at_30_days(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T130a (cont.): Task creation succeeds with due_date at exactly 30 days."""
        service = TaskService(db_session, settings)

        # Due date exactly 30 days from now should succeed
        valid_due_date = datetime.now(UTC) + timedelta(days=30)
        task_data = TaskCreate(
            title="Task with valid due date",
            due_date=valid_due_date,
        )

        task = await service.create_task(user=test_user, data=task_data)
        assert task.due_date is not None
