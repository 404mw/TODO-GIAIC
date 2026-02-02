"""Unit tests for ReminderService.

Phase 8: User Story 8 - Reminder System (Priority: P3)

T177: Test create before reminder calculates scheduled_at
T178: Test reminder limit 5 per task enforced (FR-025)
T179: Test relative reminder recalculates when due date changes (FR-026)
T180: Test recovered task does not fire past reminders (FR-027)
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import (
    NotificationMethod,
    ReminderType,
    TaskPriority,
    UserTier,
)
from src.schemas.reminder import ReminderCreate, ReminderUpdate
from src.services.reminder_service import (
    ReminderService,
    ReminderNotFoundError,
    ReminderLimitExceededError,
    TaskNoDueDateError,
    get_reminder_service,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def task_with_due_date(db_session: AsyncSession, test_user: User) -> TaskInstance:
    """Create a task with a due date for reminder tests."""
    due_date = datetime.now(UTC) + timedelta(hours=24)
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Task with due date",
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
async def task_without_due_date(db_session: AsyncSession, test_user: User) -> TaskInstance:
    """Create a task without a due date for reminder tests."""
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Task without due date",
        description="",
        priority=TaskPriority.MEDIUM,
        due_date=None,
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
def reminder_service(db_session: AsyncSession, settings: Settings) -> ReminderService:
    """Create a ReminderService instance."""
    return get_reminder_service(db_session, settings)


# =============================================================================
# T177: Test create before reminder calculates scheduled_at
# =============================================================================


class TestCreateBeforeReminder:
    """Tests for creating 'before' type reminders with scheduled_at calculation."""

    @pytest.mark.asyncio
    async def test_create_before_reminder_calculates_scheduled_at(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """T177: Create before reminder calculates scheduled_at correctly.

        When creating a 'before' reminder with offset_minutes=60,
        scheduled_at should be task.due_date - 60 minutes.
        """
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,  # 60 minutes before
            method=NotificationMethod.IN_APP,
        )

        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # scheduled_at should be 60 minutes before due_date
        expected_scheduled_at = task_with_due_date.due_date - timedelta(minutes=60)
        assert reminder.scheduled_at == expected_scheduled_at
        assert reminder.type == ReminderType.BEFORE
        assert reminder.offset_minutes == 60
        assert reminder.fired == False

    @pytest.mark.asyncio
    async def test_create_after_reminder_calculates_scheduled_at(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test creating 'after' reminder calculates scheduled_at correctly."""
        data = ReminderCreate(
            type=ReminderType.AFTER,
            offset_minutes=30,  # 30 minutes after
            method=NotificationMethod.PUSH,
        )

        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # scheduled_at should be 30 minutes after due_date
        expected_scheduled_at = task_with_due_date.due_date + timedelta(minutes=30)
        assert reminder.scheduled_at == expected_scheduled_at
        assert reminder.type == ReminderType.AFTER

    @pytest.mark.asyncio
    async def test_create_absolute_reminder_uses_provided_scheduled_at(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test creating 'absolute' reminder uses provided scheduled_at."""
        scheduled_time = datetime.now(UTC) + timedelta(hours=12)
        data = ReminderCreate(
            type=ReminderType.ABSOLUTE,
            scheduled_at=scheduled_time,
            method=NotificationMethod.IN_APP,
        )

        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # Compare as naive UTC (service strips tzinfo for DB compat)
        expected = scheduled_time.replace(tzinfo=None)
        assert reminder.scheduled_at == expected
        assert reminder.type == ReminderType.ABSOLUTE
        assert reminder.offset_minutes is None

    @pytest.mark.asyncio
    async def test_create_relative_reminder_fails_without_due_date(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_without_due_date: TaskInstance,
    ):
        """Test creating relative reminder fails if task has no due date."""
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,
            method=NotificationMethod.IN_APP,
        )

        with pytest.raises(TaskNoDueDateError):
            await reminder_service.create_reminder(
                user=test_user,
                task_id=task_without_due_date.id,
                data=data,
            )


# =============================================================================
# T178: Test reminder limit 5 per task enforced (FR-025)
# =============================================================================


class TestReminderLimitEnforced:
    """Tests for max 5 reminders per task limit (FR-025)."""

    @pytest.mark.asyncio
    async def test_reminder_limit_enforced_at_five(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """T178: Reminder limit of 5 per task is enforced (FR-025).

        Creating the 6th reminder should raise ReminderLimitExceededError.
        """
        # Create 5 reminders (at limit)
        for i in range(5):
            data = ReminderCreate(
                type=ReminderType.BEFORE,
                offset_minutes=15 * (i + 1),  # 15, 30, 45, 60, 75 minutes
                method=NotificationMethod.IN_APP,
            )
            await reminder_service.create_reminder(
                user=test_user,
                task_id=task_with_due_date.id,
                data=data,
            )

        # 6th reminder should fail
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=90,
            method=NotificationMethod.IN_APP,
        )

        with pytest.raises(ReminderLimitExceededError) as exc_info:
            await reminder_service.create_reminder(
                user=test_user,
                task_id=task_with_due_date.id,
                data=data,
            )

        assert "5" in str(exc_info.value)  # Should mention the limit


# =============================================================================
# T179: Test relative reminder recalculates when due date changes (FR-026)
# =============================================================================


class TestReminderRecalculation:
    """Tests for reminder recalculation when task due date changes (FR-026)."""

    @pytest.mark.asyncio
    async def test_relative_reminder_recalculates_on_due_date_change(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """T179: Relative reminder recalculates when due date changes (FR-026).

        When task due_date changes, 'before' and 'after' reminders should
        recalculate their scheduled_at based on new due_date.
        """
        # Create a 'before' reminder
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        original_scheduled_at = reminder.scheduled_at

        # Change task due date (add 2 hours)
        new_due_date = task_with_due_date.due_date + timedelta(hours=2)

        # Recalculate reminders for the task
        updated_reminders = await reminder_service.recalculate_reminders_for_task(
            task_id=task_with_due_date.id,
            new_due_date=new_due_date,
        )

        # scheduled_at should have shifted by 2 hours
        updated_reminder = updated_reminders[0]
        expected_new_scheduled_at = new_due_date - timedelta(minutes=60)

        assert updated_reminder.scheduled_at == expected_new_scheduled_at
        assert updated_reminder.scheduled_at != original_scheduled_at

    @pytest.mark.asyncio
    async def test_absolute_reminder_not_recalculated_on_due_date_change(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test absolute reminders are NOT recalculated when due date changes."""
        # Create an 'absolute' reminder
        scheduled_time = datetime.now(UTC) + timedelta(hours=12)
        data = ReminderCreate(
            type=ReminderType.ABSOLUTE,
            scheduled_at=scheduled_time,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # Change task due date
        new_due_date = task_with_due_date.due_date + timedelta(hours=2)

        # Recalculate reminders for the task
        updated_reminders = await reminder_service.recalculate_reminders_for_task(
            task_id=task_with_due_date.id,
            new_due_date=new_due_date,
        )

        # Absolute reminder should NOT change
        updated_reminder = next(
            r for r in updated_reminders if r.id == reminder.id
        )
        # Compare as naive UTC (service strips tzinfo for DB compat)
        expected = scheduled_time.replace(tzinfo=None)
        assert updated_reminder.scheduled_at == expected


# =============================================================================
# T180: Test recovered task does not fire past reminders (FR-027)
# =============================================================================


class TestRecoveredTaskReminders:
    """Tests for recovered task reminder handling (FR-027)."""

    @pytest.mark.asyncio
    async def test_recovered_task_skips_past_reminders(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """T180: Recovered task does not fire past reminders (FR-027).

        When a task is recovered, reminders with scheduled_at in the past
        should be marked as 'skipped' and not fire.
        """
        # Create a reminder scheduled in the past
        past_time = datetime.now(UTC) - timedelta(hours=1)
        data = ReminderCreate(
            type=ReminderType.ABSOLUTE,
            scheduled_at=past_time,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # Skip past reminders for recovered task
        skipped_count = await reminder_service.skip_past_reminders_for_task(
            task_id=task_with_due_date.id,
            skip_before=datetime.now(UTC),
        )

        # Refresh and check reminder state
        reminder = await reminder_service.get_reminder(
            user=test_user,
            reminder_id=reminder.id,
        )

        # Reminder should be marked as fired (to prevent actual firing)
        # but with a special "skipped" indication
        assert reminder.fired == True
        assert skipped_count == 1


# =============================================================================
# ADDITIONAL TESTS - Update and Delete
# =============================================================================


class TestReminderUpdateDelete:
    """Tests for reminder update and delete operations."""

    @pytest.mark.asyncio
    async def test_update_reminder_offset(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test updating reminder offset recalculates scheduled_at."""
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # Update offset to 30 minutes
        update_data = ReminderUpdate(offset_minutes=30)
        updated = await reminder_service.update_reminder(
            user=test_user,
            reminder_id=reminder.id,
            data=update_data,
        )

        expected_scheduled_at = task_with_due_date.due_date - timedelta(minutes=30)
        assert updated.offset_minutes == 30
        assert updated.scheduled_at == expected_scheduled_at

    @pytest.mark.asyncio
    async def test_delete_reminder(
        self,
        reminder_service: ReminderService,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test deleting a reminder."""
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        await reminder_service.delete_reminder(
            user=test_user,
            reminder_id=reminder.id,
        )

        with pytest.raises(ReminderNotFoundError):
            await reminder_service.get_reminder(
                user=test_user,
                reminder_id=reminder.id,
            )

    @pytest.mark.asyncio
    async def test_cannot_access_other_users_reminder(
        self,
        reminder_service: ReminderService,
        test_user: User,
        pro_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test that users cannot access reminders they don't own."""
        data = ReminderCreate(
            type=ReminderType.BEFORE,
            offset_minutes=60,
            method=NotificationMethod.IN_APP,
        )
        reminder = await reminder_service.create_reminder(
            user=test_user,
            task_id=task_with_due_date.id,
            data=data,
        )

        # Pro user should not be able to access test_user's reminder
        with pytest.raises(ReminderNotFoundError):
            await reminder_service.get_reminder(
                user=pro_user,
                reminder_id=reminder.id,
            )
