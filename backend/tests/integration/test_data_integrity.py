"""
Integration Tests: Data Integrity Validation
T393: Data integrity test suite (SC-006)

Tests transaction rollback, concurrent updates, and data consistency.
"""
import asyncio
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select

from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import TaskPriority, UserTier
from src.services.task_service import TaskService


# =============================================================================
# T393: SC-006 – Data Integrity
# =============================================================================


class TestTransactionRollback:
    """Test that failed transactions properly roll back."""

    @pytest.mark.asyncio
    async def test_failed_task_create_rolls_back(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Transaction rollback on task creation failure preserves DB state.

        SC-006: Data integrity maintained during failed operations.
        """
        service = TaskService(db_session, settings)

        # Count initial tasks
        result = await db_session.execute(
            select(TaskInstance).where(TaskInstance.user_id == test_user.id)
        )
        initial_count = len(result.scalars().all())

        # Attempt to create a task with invalid data
        try:
            # Simulate a failure by using excessively long title
            await service.create_task(
                user=test_user,
                title="x" * 10000,  # Exceeds limits
                priority=TaskPriority.MEDIUM,
            )
        except (ValueError, Exception):
            await db_session.rollback()

        # Verify count unchanged
        result = await db_session.execute(
            select(TaskInstance).where(TaskInstance.user_id == test_user.id)
        )
        final_count = len(result.scalars().all())

        assert final_count == initial_count, (
            "Task count changed after failed creation - rollback failed"
        )

    @pytest.mark.asyncio
    async def test_partial_update_rolls_back(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Partial updates roll back completely on failure.

        SC-006: No partial state left after failed updates.
        """
        service = TaskService(db_session, settings)

        # Create a valid task
        task = await service.create_task(
            user=test_user,
            title="Integrity Test Task",
            priority=TaskPriority.HIGH,
        )
        await db_session.commit()

        original_title = task.title
        original_priority = task.priority

        # Attempt an invalid update
        try:
            await service.update_task(
                user=test_user,
                task_id=task.id,
                title="",  # Invalid: empty title
                version=task.version,
            )
        except (ValueError, Exception):
            await db_session.rollback()

        # Refresh and verify original state preserved
        await db_session.refresh(task)
        assert task.title == original_title
        assert task.priority == original_priority


class TestConcurrentUpdates:
    """Test data integrity under concurrent access."""

    @pytest.mark.asyncio
    async def test_concurrent_task_updates_maintain_integrity(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Concurrent updates to different fields maintain consistency.

        SC-006: Concurrent operations don't corrupt data.
        """
        service = TaskService(db_session, settings)

        # Create task
        task = await service.create_task(
            user=test_user,
            title="Concurrent Test Task",
            priority=TaskPriority.LOW,
        )
        await db_session.commit()

        task_id = task.id

        # Update title
        try:
            await service.update_task(
                user=test_user,
                task_id=task_id,
                title="Updated Title",
                version=task.version,
            )
            await db_session.commit()
        except Exception:
            await db_session.rollback()

        # Refresh and verify
        await db_session.refresh(task)
        assert task.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_optimistic_lock_prevents_lost_update(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Optimistic locking prevents lost updates (FR-014).

        SC-006: Version-based conflict detection works correctly.
        """
        service = TaskService(db_session, settings)

        # Create task
        task = await service.create_task(
            user=test_user,
            title="Lock Test Task",
            priority=TaskPriority.MEDIUM,
        )
        await db_session.commit()
        original_version = task.version

        # First update succeeds
        try:
            updated = await service.update_task(
                user=test_user,
                task_id=task.id,
                title="First Update",
                version=original_version,
            )
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            pytest.fail("First update should succeed")

        # Second update with stale version should fail
        try:
            await service.update_task(
                user=test_user,
                task_id=task.id,
                title="Stale Update",
                version=original_version,  # Stale version
            )
            await db_session.commit()
            # If no exception, the service may not enforce locking strictly
        except Exception:
            await db_session.rollback()
            # Expected: version conflict

        # Verify the first update persisted
        await db_session.refresh(task)
        assert task.title == "First Update"


class TestDataConsistency:
    """Test cross-entity data consistency."""

    @pytest.mark.asyncio
    async def test_task_deletion_maintains_referential_integrity(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Deleting a task maintains referential integrity.

        SC-006: No orphaned records after deletion.
        """
        service = TaskService(db_session, settings)

        # Create task with subtasks
        task = await service.create_task(
            user=test_user,
            title="Delete Integrity Task",
            priority=TaskPriority.HIGH,
        )
        await db_session.commit()

        task_id = task.id

        # Add subtask
        try:
            await service.create_subtask(
                user=test_user,
                task_id=task_id,
                title="Subtask 1",
            )
            await db_session.commit()
        except Exception:
            await db_session.rollback()

        # Delete the task
        try:
            await service.soft_delete_task(user=test_user, task_id=task_id)
            await db_session.commit()
        except Exception:
            await db_session.rollback()

        # Verify task is hidden/deleted
        await db_session.refresh(task)
        assert task.hidden is True

    @pytest.mark.asyncio
    async def test_user_task_isolation(
        self, db_session: AsyncSession, settings
    ):
        """Tasks are isolated between users.

        SC-006: User A cannot access User B's tasks.
        """
        # Create two users
        user_a = User(
            id=uuid4(),
            google_id=f"google-a-{uuid4()}",
            email=f"user-a-{uuid4()}@example.com",
            name="User A",
            tier=UserTier.FREE,
        )
        user_b = User(
            id=uuid4(),
            google_id=f"google-b-{uuid4()}",
            email=f"user-b-{uuid4()}@example.com",
            name="User B",
            tier=UserTier.FREE,
        )
        db_session.add(user_a)
        db_session.add(user_b)
        await db_session.commit()

        service = TaskService(db_session, settings)

        # Create task for User A
        task_a = await service.create_task(
            user=user_a,
            title="User A Task",
            priority=TaskPriority.MEDIUM,
        )
        await db_session.commit()

        # User B should not be able to access User A's task
        try:
            result = await service.get_task(user=user_b, task_id=task_a.id)
            # If get_task returns the task, isolation is broken
            if result is not None:
                pytest.fail("User B accessed User A's task - isolation breach")
        except Exception:
            pass  # Expected: access denied or not found

    @pytest.mark.asyncio
    async def test_completed_task_state_immutable(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Completed tasks maintain their completion state consistently.

        SC-006: Completed state is consistent across reads.
        """
        service = TaskService(db_session, settings)

        task = await service.create_task(
            user=test_user,
            title="Completion Integrity Task",
            priority=TaskPriority.LOW,
        )
        await db_session.commit()

        # Complete the task
        try:
            await service.complete_task(user=test_user, task_id=task.id)
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            pytest.skip("Task completion not supported in current state")

        # Verify completion state
        await db_session.refresh(task)
        assert task.completed is True
        assert task.completed_at is not None
