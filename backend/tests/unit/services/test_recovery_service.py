"""Unit tests for RecoveryService.

Phase 18: User Story 13 - Task Deletion and Recovery (FR-062 to FR-064)

T335: Test: Delete creates tombstone with serialized data (FR-062)
T336: Test: Max 3 tombstones per user (FIFO) (FR-062)
T337: Test: Recovery restores original ID and timestamps (FR-063)
T338: Test: Recovered task does not trigger achievements (FR-064)
T339: Test: Recovered task does not affect streaks (FR-064)
"""

from datetime import datetime, timedelta, UTC
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.subtask import Subtask
from src.models.task import TaskInstance
from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.schemas.enums import (
    CompletedBy,
    SubtaskSource,
    TaskPriority,
    TombstoneEntityType,
    UserTier,
)
from src.services.recovery_service import (
    RecoveryService,
    TombstoneNotFoundError,
    TaskIDCollisionError,
)


# =============================================================================
# HELPERS
# =============================================================================


async def _create_test_user(session: AsyncSession, tier: UserTier = UserTier.FREE) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        google_id=f"google-{uuid4()}",
        email=f"test-{uuid4()}@example.com",
        name="Recovery Test User",
        tier=tier,
    )
    session.add(user)
    await session.flush()
    return user


async def _create_tombstone(
    session: AsyncSession,
    user: User,
    *,
    entity_id: UUID | None = None,
    deleted_at: datetime | None = None,
    completed: bool = False,
    subtasks: list[dict] | None = None,
) -> DeletionTombstone:
    """Create a tombstone for testing."""
    eid = entity_id or uuid4()
    now = deleted_at or datetime.now(UTC)
    tombstone = DeletionTombstone(
        id=uuid4(),
        user_id=user.id,
        entity_type=TombstoneEntityType.TASK,
        entity_id=eid,
        entity_data={
            "id": str(eid),
            "title": "Deleted Task",
            "description": "A task that was deleted",
            "priority": TaskPriority.MEDIUM.value,
            "due_date": (now + timedelta(days=7)).isoformat(),
            "estimated_duration": 30,
            "focus_time_seconds": 0,
            "completed": completed,
            "completed_at": now.isoformat() if completed else None,
            "completed_by": CompletedBy.MANUAL.value if completed else None,
            "created_at": (now - timedelta(days=1)).isoformat(),
            "subtasks": subtasks or [],
        },
        deleted_at=now,
    )
    session.add(tombstone)
    await session.flush()
    return tombstone


# =============================================================================
# T335: Delete creates tombstone with serialized data (FR-062)
# =============================================================================


@pytest.mark.asyncio
async def test_tombstone_contains_serialized_entity_data(
    db_session: AsyncSession,
) -> None:
    """T335: Tombstone entity_data preserves full task state including subtasks."""
    user = await _create_test_user(db_session)
    original_id = uuid4()
    original_created_at = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)

    subtask_data = [
        {"id": str(uuid4()), "title": "Sub 1", "completed": True, "order_index": 0, "source": "user"},
        {"id": str(uuid4()), "title": "Sub 2", "completed": False, "order_index": 1, "source": "ai"},
    ]

    tombstone = await _create_tombstone(
        db_session,
        user,
        entity_id=original_id,
        deleted_at=datetime.now(UTC),
        subtasks=subtask_data,
    )

    service = RecoveryService(db_session)
    result = await service.get_tombstone(user=user, tombstone_id=tombstone.id)

    assert result.entity_type == TombstoneEntityType.TASK
    assert result.entity_id == original_id
    assert result.entity_data["title"] == "Deleted Task"
    assert len(result.entity_data["subtasks"]) == 2
    assert result.entity_data["subtasks"][0]["title"] == "Sub 1"
    assert result.entity_data["subtasks"][1]["source"] == "ai"


# =============================================================================
# T336: Max 3 tombstones per user (FIFO) (FR-062)
# =============================================================================


@pytest.mark.asyncio
async def test_list_tombstones_returns_max_3(
    db_session: AsyncSession,
) -> None:
    """T336: User can have max 3 tombstones; list returns all active ones."""
    user = await _create_test_user(db_session)
    service = RecoveryService(db_session)

    # Create 3 tombstones
    for i in range(3):
        await _create_tombstone(
            db_session,
            user,
            deleted_at=datetime.now(UTC) + timedelta(seconds=i),
        )

    tombstones = await service.list_tombstones(user=user)
    assert len(tombstones) == 3


@pytest.mark.asyncio
async def test_tombstone_not_found_raises_error(
    db_session: AsyncSession,
) -> None:
    """T336: Accessing nonexistent tombstone raises TombstoneNotFoundError."""
    user = await _create_test_user(db_session)
    service = RecoveryService(db_session)

    with pytest.raises(TombstoneNotFoundError):
        await service.get_tombstone(user=user, tombstone_id=uuid4())


@pytest.mark.asyncio
async def test_tombstone_belongs_to_other_user_raises_error(
    db_session: AsyncSession,
) -> None:
    """T336: Accessing another user's tombstone raises TombstoneNotFoundError."""
    user1 = await _create_test_user(db_session)
    user2 = await _create_test_user(db_session)

    tombstone = await _create_tombstone(db_session, user1)

    service = RecoveryService(db_session)
    with pytest.raises(TombstoneNotFoundError):
        await service.get_tombstone(user=user2, tombstone_id=tombstone.id)


# =============================================================================
# T337: Recovery restores original ID and timestamps (FR-063)
# =============================================================================


@pytest.mark.asyncio
async def test_recover_task_restores_original_id(
    db_session: AsyncSession,
) -> None:
    """T337: Recovered task has same ID as original."""
    user = await _create_test_user(db_session)
    original_id = uuid4()

    tombstone = await _create_tombstone(
        db_session, user, entity_id=original_id
    )

    service = RecoveryService(db_session)
    recovered_task = await service.recover_task(user=user, tombstone_id=tombstone.id)

    assert recovered_task.id == original_id


@pytest.mark.asyncio
async def test_recover_task_restores_original_created_at(
    db_session: AsyncSession,
) -> None:
    """T337: Recovered task preserves original created_at timestamp."""
    user = await _create_test_user(db_session)
    original_id = uuid4()
    original_created = datetime(2026, 1, 10, 8, 0, 0, tzinfo=UTC)

    tombstone = DeletionTombstone(
        id=uuid4(),
        user_id=user.id,
        entity_type=TombstoneEntityType.TASK,
        entity_id=original_id,
        entity_data={
            "id": str(original_id),
            "title": "Original Task",
            "description": "Desc",
            "priority": TaskPriority.HIGH.value,
            "due_date": None,
            "estimated_duration": None,
            "focus_time_seconds": 120,
            "completed": False,
            "completed_at": None,
            "completed_by": None,
            "created_at": original_created.isoformat(),
            "subtasks": [],
        },
        deleted_at=datetime.now(UTC),
    )
    db_session.add(tombstone)
    await db_session.flush()

    service = RecoveryService(db_session)
    recovered_task = await service.recover_task(user=user, tombstone_id=tombstone.id)

    assert recovered_task.title == "Original Task"
    assert recovered_task.priority == TaskPriority.HIGH
    assert recovered_task.focus_time_seconds == 120
    # created_at should be restored from tombstone data
    assert recovered_task.created_at.year == 2026
    assert recovered_task.created_at.month == 1
    assert recovered_task.created_at.day == 10


@pytest.mark.asyncio
async def test_recover_task_restores_subtasks(
    db_session: AsyncSession,
) -> None:
    """T337: Recovered task includes its original subtasks."""
    user = await _create_test_user(db_session)
    original_id = uuid4()
    sub1_id = str(uuid4())
    sub2_id = str(uuid4())

    tombstone = await _create_tombstone(
        db_session,
        user,
        entity_id=original_id,
        subtasks=[
            {"id": sub1_id, "title": "Step 1", "completed": True, "order_index": 0, "source": "user"},
            {"id": sub2_id, "title": "Step 2", "completed": False, "order_index": 1, "source": "ai"},
        ],
    )

    service = RecoveryService(db_session)
    recovered_task = await service.recover_task(user=user, tombstone_id=tombstone.id)

    # Verify subtasks restored
    stmt = select(Subtask).where(Subtask.task_id == recovered_task.id)
    result = await db_session.execute(stmt)
    subtasks = result.scalars().all()

    assert len(subtasks) == 2
    titles = {s.title for s in subtasks}
    assert "Step 1" in titles
    assert "Step 2" in titles


@pytest.mark.asyncio
async def test_recover_task_removes_tombstone(
    db_session: AsyncSession,
) -> None:
    """T337: After recovery, the tombstone is deleted."""
    user = await _create_test_user(db_session)
    tombstone = await _create_tombstone(db_session, user)
    tombstone_id = tombstone.id

    service = RecoveryService(db_session)
    await service.recover_task(user=user, tombstone_id=tombstone_id)

    # Tombstone should be gone
    stmt = select(DeletionTombstone).where(DeletionTombstone.id == tombstone_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_recover_task_id_collision_raises_error(
    db_session: AsyncSession,
) -> None:
    """T337: If original task ID already exists, raise TaskIDCollisionError."""
    user = await _create_test_user(db_session)
    original_id = uuid4()

    # Create a task that occupies the original ID
    existing_task = TaskInstance(
        id=original_id,
        user_id=user.id,
        title="Existing Task",
        priority=TaskPriority.MEDIUM,
    )
    db_session.add(existing_task)
    await db_session.flush()

    # Create tombstone with same entity_id
    tombstone = await _create_tombstone(db_session, user, entity_id=original_id)

    service = RecoveryService(db_session)
    with pytest.raises(TaskIDCollisionError):
        await service.recover_task(user=user, tombstone_id=tombstone.id)


# =============================================================================
# T338: Recovered task does not trigger achievements (FR-064)
# =============================================================================


@pytest.mark.asyncio
async def test_recover_task_returns_skip_achievements_flag(
    db_session: AsyncSession,
) -> None:
    """T338: Recovered task is marked so it does NOT trigger achievement checks.

    The recovered task should have a flag/metadata indicating it was recovered,
    which downstream handlers use to skip achievement processing.
    """
    user = await _create_test_user(db_session)

    # Tombstone for a completed task
    tombstone = await _create_tombstone(db_session, user, completed=True)

    service = RecoveryService(db_session)
    recovered_task = await service.recover_task(user=user, tombstone_id=tombstone.id)

    # Recovered task should be marked as recovered (no achievement triggers)
    assert recovered_task.completed == True
    # The is_recovered flag should be set on the result
    assert hasattr(recovered_task, "_is_recovered") or service.last_recovery_was_flagged


# =============================================================================
# T339: Recovered task does not affect streaks (FR-064)
# =============================================================================


@pytest.mark.asyncio
async def test_recover_task_does_not_increment_streak(
    db_session: AsyncSession,
) -> None:
    """T339: Recovering a completed task does NOT count toward streak.

    Streak logic must skip recovered tasks to prevent gaming the system.
    The RecoveryService must indicate this through the recovery context.
    """
    user = await _create_test_user(db_session)

    tombstone = await _create_tombstone(db_session, user, completed=True)

    service = RecoveryService(db_session)
    recovered_task = await service.recover_task(user=user, tombstone_id=tombstone.id)

    # The service should track that this recovery should skip streak updates
    assert service.skip_achievement_processing is True
    assert service.skip_streak_processing is True
