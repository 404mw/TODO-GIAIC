"""Unit tests for reminder job handler.

Phase 8: User Story 8 - Reminder System (Priority: P3)

T181: Test reminder fires at scheduled time
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.models.user import User
from src.models.notification import Notification
from src.schemas.enums import (
    NotificationMethod,
    NotificationType,
    ReminderType,
    TaskPriority,
    UserTier,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def task_with_reminder(db_session: AsyncSession, test_user: User) -> TaskInstance:
    """Create a task with a due reminder."""
    due_date = datetime.now(UTC) + timedelta(hours=24)
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Task with reminder",
        description="",
        priority=TaskPriority.MEDIUM,
        due_date=due_date,
        completed=False,
        hidden=False,
        archived=False,
        version=1,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def due_reminder(
    db_session: AsyncSession,
    test_user: User,
    task_with_reminder: TaskInstance,
) -> Reminder:
    """Create a reminder that is due now (scheduled_at in the past)."""
    reminder = Reminder(
        id=uuid4(),
        task_id=task_with_reminder.id,
        user_id=test_user.id,
        type=ReminderType.BEFORE,
        offset_minutes=60,
        scheduled_at=datetime.now(UTC) - timedelta(minutes=5),  # Due 5 mins ago
        method=NotificationMethod.IN_APP,
        fired=False,
        fired_at=None,
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)
    return reminder


@pytest.fixture
async def future_reminder(
    db_session: AsyncSession,
    test_user: User,
    task_with_reminder: TaskInstance,
) -> Reminder:
    """Create a reminder that is not yet due."""
    reminder = Reminder(
        id=uuid4(),
        task_id=task_with_reminder.id,
        user_id=test_user.id,
        type=ReminderType.BEFORE,
        offset_minutes=60,
        scheduled_at=datetime.now(UTC) + timedelta(hours=1),  # Due in 1 hour
        method=NotificationMethod.IN_APP,
        fired=False,
        fired_at=None,
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)
    return reminder


# =============================================================================
# T181: Test reminder fires at scheduled time
# =============================================================================


class TestReminderFiresAtScheduledTime:
    """Tests for reminder firing at scheduled time."""

    @pytest.mark.asyncio
    async def test_reminder_fires_when_due(
        self,
        db_session: AsyncSession,
        settings: Settings,
        due_reminder: Reminder,
        task_with_reminder: TaskInstance,
        test_user: User,
    ):
        """T181: Reminder fires at scheduled time.

        When the reminder_fire job processes a due reminder:
        1. The reminder.fired should be set to True
        2. The reminder.fired_at should be set to current time
        3. A notification should be created for the user
        """
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        # Should have fired 1 reminder
        assert fired_count == 1

        # Refresh the reminder
        await db_session.refresh(due_reminder)

        # Reminder should be marked as fired
        assert due_reminder.fired == True
        assert due_reminder.fired_at is not None

        # Check notification was created
        from sqlmodel import select
        result = await db_session.execute(
            select(Notification).where(
                Notification.user_id == test_user.id,
                Notification.type == NotificationType.REMINDER,
            )
        )
        notification = result.scalar_one_or_none()

        assert notification is not None
        assert task_with_reminder.title in notification.body

    @pytest.mark.asyncio
    async def test_future_reminder_not_fired(
        self,
        db_session: AsyncSession,
        settings: Settings,
        future_reminder: Reminder,
    ):
        """Test that reminders not yet due are not fired."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        # Should not have fired any reminders
        assert fired_count == 0

        # Refresh the reminder
        await db_session.refresh(future_reminder)

        # Reminder should NOT be marked as fired
        assert future_reminder.fired == False
        assert future_reminder.fired_at is None

    @pytest.mark.asyncio
    async def test_already_fired_reminder_not_reprocessed(
        self,
        db_session: AsyncSession,
        settings: Settings,
        due_reminder: Reminder,
    ):
        """Test that already-fired reminders are not processed again."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Mark as already fired
        due_reminder.fired = True
        due_reminder.fired_at = datetime.now(UTC) - timedelta(minutes=10)
        db_session.add(due_reminder)
        await db_session.commit()

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        # Should not have fired any reminders (already fired)
        assert fired_count == 0

    @pytest.mark.asyncio
    async def test_reminder_for_completed_task_not_fired(
        self,
        db_session: AsyncSession,
        settings: Settings,
        due_reminder: Reminder,
        task_with_reminder: TaskInstance,
    ):
        """Test that reminders for completed tasks are not fired."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Mark task as completed
        task_with_reminder.completed = True
        task_with_reminder.completed_at = datetime.now(UTC)
        db_session.add(task_with_reminder)
        await db_session.commit()

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        # Should not have fired - task is completed
        assert fired_count == 0

        # Refresh the reminder
        await db_session.refresh(due_reminder)
        assert due_reminder.fired == False

    @pytest.mark.asyncio
    async def test_push_notification_created_for_push_method(
        self,
        db_session: AsyncSession,
        settings: Settings,
        test_user: User,
        task_with_reminder: TaskInstance,
    ):
        """Test that push notification is created for push method reminders."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Create a push reminder that's due
        reminder = Reminder(
            id=uuid4(),
            task_id=task_with_reminder.id,
            user_id=test_user.id,
            type=ReminderType.BEFORE,
            offset_minutes=60,
            scheduled_at=datetime.now(UTC) - timedelta(minutes=5),
            method=NotificationMethod.PUSH,
            fired=False,
        )
        db_session.add(reminder)
        await db_session.commit()

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        assert fired_count == 1

        # Check notification was created
        from sqlmodel import select
        result = await db_session.execute(
            select(Notification).where(
                Notification.user_id == test_user.id,
            )
        )
        notification = result.scalar_one_or_none()

        assert notification is not None
        # Note: Actual push notification delivery is handled separately
