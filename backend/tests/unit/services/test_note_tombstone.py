"""Unit tests for legacy note tombstone recovery.

Task 7.1 / FR-013: Migration tolerance — note tombstone with legacy `task_id`
field is silently ignored during recovery.

Before v1.2, notes were task-scoped and `task_id` was serialized into
tombstone entity_data. After v1.2, notes are standalone. The
RecoveryService.recover_tombstone() must silently ignore any `task_id`
present in entity_data and restore the note scoped only to `user_id`.
"""

from datetime import datetime, UTC
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.schemas.enums import TombstoneEntityType, UserTier
from src.services.recovery_service import (
    RecoveryService,
    TombstoneNotFoundError,
)


# =============================================================================
# HELPERS
# =============================================================================


async def _create_user(session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        google_id=f"google-{uuid4()}",
        email=f"user-{uuid4()}@example.com",
        name="Test User",
        tier=UserTier.FREE,
    )
    session.add(user)
    await session.flush()
    return user


async def _create_note_tombstone(
    session: AsyncSession,
    user: User,
    *,
    include_legacy_task_id: bool = False,
) -> DeletionTombstone:
    """Create a NOTE tombstone, optionally with a legacy `task_id` field."""
    note_id = uuid4()
    entity_data: dict = {
        "id": str(note_id),
        "user_id": str(user.id),
        "content": "My note content from v1.1",
        "archived": False,
        "voice_url": None,
        "voice_duration_seconds": None,
        "transcription_status": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    if include_legacy_task_id:
        # Simulate v1.1 note tombstone that serialized a task_id
        entity_data["task_id"] = str(uuid4())

    tombstone = DeletionTombstone(
        id=uuid4(),
        user_id=user.id,
        entity_type=TombstoneEntityType.NOTE,
        entity_id=note_id,
        entity_data=entity_data,
        deleted_at=datetime.now(UTC),
    )
    session.add(tombstone)
    await session.flush()
    return tombstone


# =============================================================================
# FR-013: LEGACY NOTE TOMBSTONE RECOVERY
# =============================================================================


@pytest.mark.asyncio
async def test_recover_tombstone_note_with_legacy_task_id_silently_ignored(
    db_session: AsyncSession,
) -> None:
    """Task 7.1 / FR-013: Note tombstone with legacy `task_id` is silently ignored.

    Steps:
    1. Create a NOTE tombstone whose entity_data includes a `task_id`
       (simulating a tombstone created by a pre-v1.2 client)
    2. Call RecoveryService.recover_tombstone()
    3. Verify the returned object is a Note (not a Task)
    4. Verify the Note is scoped only to user_id (no task linkage)
    5. Verify the `task_id` field was silently ignored (Note model has no task_id)
    6. Verify original note content is preserved
    """
    from src.models.note import Note

    user = await _create_user(db_session)
    tombstone = await _create_note_tombstone(
        db_session, user, include_legacy_task_id=True
    )
    original_note_id = tombstone.entity_id

    service = RecoveryService(db_session)
    result = await service.recover_tombstone(user=user, tombstone_id=tombstone.id)

    # Result should be a Note instance
    assert isinstance(result, Note)

    # Original note ID preserved
    assert result.id == original_note_id

    # Note is scoped to user_id only (no task_id on the Note model)
    assert result.user_id == user.id
    assert not hasattr(result, "task_id") or result.task_id is None  # type: ignore[attr-defined]

    # Content preserved from tombstone
    assert result.content == "My note content from v1.1"

    # Not archived by default
    assert result.archived is False


@pytest.mark.asyncio
async def test_recover_tombstone_note_without_legacy_task_id(
    db_session: AsyncSession,
) -> None:
    """FR-013: Note tombstone without task_id (modern v1.2 format) also recovers correctly."""
    from src.models.note import Note

    user = await _create_user(db_session)
    tombstone = await _create_note_tombstone(
        db_session, user, include_legacy_task_id=False
    )

    service = RecoveryService(db_session)
    result = await service.recover_tombstone(user=user, tombstone_id=tombstone.id)

    assert isinstance(result, Note)
    assert result.user_id == user.id
    assert result.content == "My note content from v1.1"


@pytest.mark.asyncio
async def test_recover_tombstone_removes_tombstone_after_note_recovery(
    db_session: AsyncSession,
) -> None:
    """FR-013: Tombstone is deleted after successful note recovery."""
    from sqlmodel import select

    user = await _create_user(db_session)
    tombstone = await _create_note_tombstone(
        db_session, user, include_legacy_task_id=True
    )
    tombstone_id = tombstone.id

    service = RecoveryService(db_session)
    await service.recover_tombstone(user=user, tombstone_id=tombstone_id)

    # Tombstone should be deleted
    stmt = select(DeletionTombstone).where(DeletionTombstone.id == tombstone_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_recover_tombstone_other_user_raises_not_found(
    db_session: AsyncSession,
) -> None:
    """FR-013: User cannot recover another user's note tombstone."""
    user1 = await _create_user(db_session)
    user2 = await _create_user(db_session)
    tombstone = await _create_note_tombstone(db_session, user1)

    service = RecoveryService(db_session)
    with pytest.raises(TombstoneNotFoundError):
        await service.recover_tombstone(user=user2, tombstone_id=tombstone.id)
