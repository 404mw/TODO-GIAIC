"""Integration tests for reminder lifecycle.

Phase 8: User Story 8 - Reminder System (Priority: P3)

T194: Integration test for complete reminder lifecycle.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.notification import Notification
from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import (
    NotificationMethod,
    NotificationType,
    ReminderType,
    TaskPriority,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def task_for_reminders(db_session: AsyncSession, test_user: User) -> TaskInstance:
    """Create a task with a due date for reminder lifecycle tests."""
    due_date = datetime.now(UTC) + timedelta(hours=24)
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Integration Test Task",
        description="Testing reminder lifecycle",
        priority=TaskPriority.HIGH,
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


# =============================================================================
# T194: INTEGRATION TESTS
# =============================================================================


class TestReminderLifecycle:
    """Integration tests for complete reminder lifecycle."""

    @pytest.mark.asyncio
    async def test_create_update_delete_reminder_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_for_reminders: TaskInstance,
    ):
        """T194: Test complete reminder lifecycle: create -> update -> delete."""
        task_id = str(task_for_reminders.id)

        # Step 1: Create a reminder
        create_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "in_app",
            },
        )

        assert create_response.status_code == 201
        reminder_data = create_response.json()["data"]
        reminder_id = reminder_data["id"]

        assert reminder_data["type"] == "before"
        assert reminder_data["offset_minutes"] == 60
        assert reminder_data["fired"] == False

        # Verify scheduled_at is 60 minutes before due date
        scheduled_at = datetime.fromisoformat(
            reminder_data["scheduled_at"].replace("Z", "+00:00")
        )
        expected_scheduled = task_for_reminders.due_date - timedelta(minutes=60)
        # Allow small time drift
        assert abs((scheduled_at - expected_scheduled).total_seconds()) < 2

        # Step 2: Update the reminder offset
        update_response = await client.patch(
            f"/api/v1/reminders/{reminder_id}",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "offset_minutes": 30,
            },
        )

        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]

        assert updated_data["offset_minutes"] == 30
        # Verify scheduled_at was recalculated
        new_scheduled_at = datetime.fromisoformat(
            updated_data["scheduled_at"].replace("Z", "+00:00")
        )
        expected_new_scheduled = task_for_reminders.due_date - timedelta(minutes=30)
        assert abs((new_scheduled_at - expected_new_scheduled).total_seconds()) < 2

        # Step 3: Update the notification method
        method_update_response = await client.patch(
            f"/api/v1/reminders/{reminder_id}",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "method": "push",
            },
        )

        assert method_update_response.status_code == 200
        assert method_update_response.json()["data"]["method"] == "push"

        # Step 4: Delete the reminder
        delete_response = await client.delete(
            f"/api/v1/reminders/{reminder_id}",
            headers=auth_headers,
        )

        assert delete_response.status_code == 204

        # Step 5: Verify reminder is gone
        get_response = await client.patch(
            f"/api/v1/reminders/{reminder_id}",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={"offset_minutes": 45},
        )

        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_multiple_reminders_with_different_types(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_for_reminders: TaskInstance,
    ):
        """Test creating multiple reminders with different types."""
        task_id = str(task_for_reminders.id)

        # Create 'before' reminder
        before_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "in_app",
            },
        )
        assert before_response.status_code == 201

        # Create 'after' reminder
        after_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "after",
                "offset_minutes": 30,
                "method": "push",
            },
        )
        assert after_response.status_code == 201

        # Create 'absolute' reminder
        absolute_time = (datetime.now(UTC) + timedelta(hours=12)).isoformat()
        absolute_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "absolute",
                "scheduled_at": absolute_time,
                "method": "in_app",
            },
        )
        assert absolute_response.status_code == 201

        # Verify different types
        assert before_response.json()["data"]["type"] == "before"
        assert after_response.json()["data"]["type"] == "after"
        assert absolute_response.json()["data"]["type"] == "absolute"

    @pytest.mark.asyncio
    async def test_reminder_limit_enforcement(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_for_reminders: TaskInstance,
    ):
        """Test that reminder limit of 5 per task is enforced."""
        task_id = str(task_for_reminders.id)

        # Create 5 reminders (at limit)
        for i in range(5):
            response = await client.post(
                f"/api/v1/tasks/{task_id}/reminders",
                headers={**auth_headers, "Idempotency-Key": str(uuid4())},
                json={
                    "type": "before",
                    "offset_minutes": 15 * (i + 1),
                    "method": "in_app",
                },
            )
            assert response.status_code == 201, f"Failed creating reminder {i+1}"

        # 6th reminder should fail
        exceeded_response = await client.post(
            f"/api/v1/tasks/{task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "before",
                "offset_minutes": 90,
                "method": "in_app",
            },
        )

        assert exceeded_response.status_code == 409
        assert "limit" in exceeded_response.json()["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_reminder_firing_creates_notification(
        self,
        db_session: AsyncSession,
        settings: Settings,
        test_user: User,
        task_for_reminders: TaskInstance,
    ):
        """Test that firing a due reminder creates a notification."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Create a reminder that is already due
        reminder = Reminder(
            id=uuid4(),
            task_id=task_for_reminders.id,
            user_id=test_user.id,
            type=ReminderType.BEFORE,
            offset_minutes=60,
            scheduled_at=datetime.now(UTC) - timedelta(minutes=5),  # Due 5 mins ago
            method=NotificationMethod.IN_APP,
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

        # Verify notification was created
        from sqlmodel import select
        result = await db_session.execute(
            select(Notification).where(
                Notification.user_id == test_user.id,
                Notification.type == NotificationType.REMINDER,
            )
        )
        notification = result.scalar_one_or_none()

        assert notification is not None
        assert task_for_reminders.title in notification.body
        assert notification.read == False

        # Verify reminder is marked as fired
        await db_session.refresh(reminder)
        assert reminder.fired == True
        assert reminder.fired_at is not None

    @pytest.mark.asyncio
    async def test_reminder_not_fired_for_completed_task(
        self,
        db_session: AsyncSession,
        settings: Settings,
        test_user: User,
        task_for_reminders: TaskInstance,
    ):
        """Test that reminders don't fire for completed tasks."""
        from src.jobs.tasks.reminder_job import process_due_reminders

        # Mark task as completed
        task_for_reminders.completed = True
        task_for_reminders.completed_at = datetime.now(UTC)
        db_session.add(task_for_reminders)

        # Create a due reminder
        reminder = Reminder(
            id=uuid4(),
            task_id=task_for_reminders.id,
            user_id=test_user.id,
            type=ReminderType.BEFORE,
            offset_minutes=60,
            scheduled_at=datetime.now(UTC) - timedelta(minutes=5),
            method=NotificationMethod.IN_APP,
            fired=False,
        )
        db_session.add(reminder)
        await db_session.commit()

        # Process due reminders
        fired_count = await process_due_reminders(
            session=db_session,
            settings=settings,
        )

        # Should not fire for completed task
        assert fired_count == 0

        # Reminder should still be unfired
        await db_session.refresh(reminder)
        assert reminder.fired == False

    @pytest.mark.asyncio
    async def test_relative_reminder_fails_without_due_date(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that creating relative reminder fails if task has no due date."""
        # Create task without due date
        task = TaskInstance(
            id=uuid4(),
            user_id=test_user.id,
            title="No Due Date Task",
            description="",
            priority=TaskPriority.MEDIUM,
            due_date=None,  # No due date
            completed=False,
            hidden=False,
            archived=False,
            version=1,
        )
        db_session.add(task)
        await db_session.commit()

        # Try to create relative reminder
        response = await client.post(
            f"/api/v1/tasks/{task.id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "in_app",
            },
        )

        assert response.status_code == 400
        assert "due date" in response.json()["error"]["message"].lower()
