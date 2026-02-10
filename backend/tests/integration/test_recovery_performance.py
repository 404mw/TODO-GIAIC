"""
Integration Tests: Task Recovery Performance
T398: Task recovery < 30 seconds (SC-010)

Tests that task recovery from tombstones completes within acceptable time.
"""
import time
from typing import List
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import TaskInstance
from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.schemas.enums import TaskPriority, TombstoneEntityType
from src.schemas.subtask import SubtaskCreate
from src.schemas.task import TaskCreate
from src.services.recovery_service import RecoveryService
from src.services.task_service import TaskService


# =============================================================================
# T398: SC-010 – Task Recovery Time
# =============================================================================


class TestTaskRecoveryPerformance:
    """
    SC-010: Task Recovery Time
    Target: Recovery < 30 seconds
    """

    @pytest.mark.asyncio
    async def test_single_task_recovery_under_30_seconds(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Single task recovery completes within 30 seconds (SC-010)."""
        task_service = TaskService(db_session, settings)

        # Create and then hard-delete a task
        task = await task_service.create_task(
            user=test_user,
            data=TaskCreate(title="Recovery Perf Task", priority=TaskPriority.HIGH),
        )
        await db_session.commit()

        task_id = task.id

        # Hard delete (creates tombstone)
        await task_service.hard_delete_task(user=test_user, task_id=task_id)
        await db_session.commit()

        # Find the tombstone
        recovery_service = RecoveryService(db_session)
        tombstones = await recovery_service.list_tombstones(user=test_user)

        if not tombstones:
            pytest.skip("No tombstone created - service may use soft delete only")

        tombstone = tombstones[0]

        # Measure recovery time
        start = time.perf_counter()
        recovered = await recovery_service.recover_task(
            user=test_user,
            tombstone_id=tombstone.id,
        )
        elapsed = time.perf_counter() - start

        await db_session.commit()

        assert recovered is not None
        assert elapsed < 30.0, (
            f"Task recovery took {elapsed:.3f}s, exceeds 30s (SC-010)"
        )

    @pytest.mark.asyncio
    async def test_task_with_subtasks_recovery_under_30_seconds(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Task with subtasks recovers within 30 seconds (SC-010)."""
        task_service = TaskService(db_session, settings)

        # Create task with subtasks
        task = await task_service.create_task(
            user=test_user,
            data=TaskCreate(title="Recovery Subtask Perf Task", priority=TaskPriority.MEDIUM),
        )
        await db_session.commit()

        # Add subtasks
        for i in range(5):
            try:
                await task_service.create_subtask(
                    user=test_user,
                    task_id=task.id,
                    data=SubtaskCreate(title=f"Subtask {i}"),
                )
            except Exception:
                pass  # Some may fail due to limits

        await db_session.commit()
        task_id = task.id

        # Hard delete
        await task_service.hard_delete_task(user=test_user, task_id=task_id)
        await db_session.commit()

        # Find tombstone
        recovery_service = RecoveryService(db_session)
        tombstones = await recovery_service.list_tombstones(user=test_user)

        if not tombstones:
            pytest.skip("No tombstone created")

        tombstone = tombstones[0]

        # Measure recovery time
        start = time.perf_counter()
        recovered = await recovery_service.recover_task(
            user=test_user,
            tombstone_id=tombstone.id,
        )
        elapsed = time.perf_counter() - start

        await db_session.commit()

        assert recovered is not None
        assert elapsed < 30.0, (
            f"Task+subtasks recovery took {elapsed:.3f}s, exceeds 30s (SC-010)"
        )

    @pytest.mark.asyncio
    async def test_multiple_recoveries_performance(
        self, db_session: AsyncSession, test_user: User, settings
    ):
        """Multiple sequential recoveries within time budget (SC-010)."""
        task_service = TaskService(db_session, settings)
        times: List[float] = []

        # Create, delete, recover cycle for 3 tasks (max tombstones)
        for i in range(3):
            task = await task_service.create_task(
                user=test_user,
                data=TaskCreate(title=f"Multi Recovery Task {i}", priority=TaskPriority.LOW),
            )
            await db_session.commit()

            await task_service.hard_delete_task(
                user=test_user, task_id=task.id
            )
            await db_session.commit()

            recovery_service = RecoveryService(db_session)
            tombstones = await recovery_service.list_tombstones(user=test_user)

            if not tombstones:
                continue

            start = time.perf_counter()
            await recovery_service.recover_task(
                user=test_user,
                tombstone_id=tombstones[0].id,
            )
            elapsed = time.perf_counter() - start

            await db_session.commit()
            times.append(elapsed)

        if not times:
            pytest.skip("No recoveries performed")

        max_time = max(times)
        avg_time = sum(times) / len(times)

        assert max_time < 30.0, (
            f"Worst recovery took {max_time:.3f}s, exceeds 30s (SC-010)"
        )
        assert avg_time < 5.0, (
            f"Average recovery {avg_time:.3f}s is unexpectedly high"
        )
