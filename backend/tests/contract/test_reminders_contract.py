"""Contract tests for reminder endpoints.

Phase 8: User Story 8 - Reminder System (Priority: P3)

T182: Contract test for reminder endpoints per api-specification.md Section 7
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import (
    NotificationMethod,
    ReminderType,
    TaskPriority,
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
async def existing_reminder(
    db_session: AsyncSession,
    test_user: User,
    task_with_due_date: TaskInstance,
) -> Reminder:
    """Create an existing reminder for update/delete tests."""
    scheduled_at = task_with_due_date.due_date - timedelta(minutes=60)
    reminder = Reminder(
        id=uuid4(),
        task_id=task_with_due_date.id,
        user_id=test_user.id,
        type=ReminderType.BEFORE,
        offset_minutes=60,
        scheduled_at=scheduled_at,
        method=NotificationMethod.IN_APP,
        fired=False,
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)
    return reminder


# =============================================================================
# T182: Contract test for reminder endpoints
# =============================================================================


class TestCreateReminderContract:
    """Contract tests for POST /api/v1/tasks/:task_id/reminders."""

    @pytest.mark.asyncio
    async def test_create_before_reminder_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_with_due_date: TaskInstance,
        idempotency_key: str,
    ):
        """Test create 'before' reminder returns correct response schema."""
        response = await client.post(
            f"/api/v1/tasks/{task_with_due_date.id}/reminders",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "push",
            },
        )

        assert response.status_code == 201

        data = response.json()["data"]

        # Verify response schema per api-specification.md Section 7.1
        assert "id" in data
        assert "task_id" in data
        assert data["task_id"] == str(task_with_due_date.id)
        assert data["type"] == "before"
        assert data["offset_minutes"] == 60
        assert "scheduled_at" in data
        assert data["method"] == "push"
        assert data["fired"] == False
        assert "fired_at" in data
        assert data["fired_at"] is None
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_absolute_reminder_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_with_due_date: TaskInstance,
        idempotency_key: str,
    ):
        """Test create 'absolute' reminder returns correct response schema."""
        scheduled_at = (datetime.now(UTC) + timedelta(hours=12)).isoformat()

        response = await client.post(
            f"/api/v1/tasks/{task_with_due_date.id}/reminders",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "type": "absolute",
                "scheduled_at": scheduled_at,
                "method": "in_app",
            },
        )

        assert response.status_code == 201

        data = response.json()["data"]

        assert data["type"] == "absolute"
        assert data["offset_minutes"] is None
        assert "scheduled_at" in data
        assert data["method"] == "in_app"

    @pytest.mark.asyncio
    async def test_create_reminder_validation_error(
        self,
        client: AsyncClient,
        auth_headers: dict,
        task_with_due_date: TaskInstance,
        idempotency_key: str,
    ):
        """Test create reminder with invalid data returns 400."""
        response = await client.post(
            f"/api/v1/tasks/{task_with_due_date.id}/reminders",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "type": "before",
                # Missing required offset_minutes for 'before' type
                "method": "in_app",
            },
        )

        assert response.status_code == 400
        assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_create_reminder_task_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        idempotency_key: str,
    ):
        """Test create reminder for non-existent task returns 404."""
        fake_task_id = uuid4()

        response = await client.post(
            f"/api/v1/tasks/{fake_task_id}/reminders",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "in_app",
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_reminder_limit_exceeded(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
        test_user: User,
        task_with_due_date: TaskInstance,
    ):
        """Test create reminder when limit exceeded returns 409."""
        # Create 5 reminders to hit the limit
        for i in range(5):
            scheduled_at = task_with_due_date.due_date - timedelta(minutes=15 * (i + 1))
            reminder = Reminder(
                id=uuid4(),
                task_id=task_with_due_date.id,
                user_id=test_user.id,
                type=ReminderType.BEFORE,
                offset_minutes=15 * (i + 1),
                scheduled_at=scheduled_at,
                method=NotificationMethod.IN_APP,
                fired=False,
            )
            db_session.add(reminder)
        await db_session.commit()

        # Try to create 6th reminder
        response = await client.post(
            f"/api/v1/tasks/{task_with_due_date.id}/reminders",
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            json={
                "type": "before",
                "offset_minutes": 90,
                "method": "in_app",
            },
        )

        assert response.status_code == 409
        assert "error" in response.json()


class TestUpdateReminderContract:
    """Contract tests for PATCH /api/v1/reminders/:id."""

    @pytest.mark.asyncio
    async def test_update_reminder_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        existing_reminder: Reminder,
        idempotency_key: str,
    ):
        """Test update reminder returns correct response schema."""
        response = await client.patch(
            f"/api/v1/reminders/{existing_reminder.id}",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "offset_minutes": 30,
            },
        )

        assert response.status_code == 200

        data = response.json()["data"]

        assert data["id"] == str(existing_reminder.id)
        assert data["offset_minutes"] == 30
        # scheduled_at should be recalculated
        assert "scheduled_at" in data

    @pytest.mark.asyncio
    async def test_update_reminder_method(
        self,
        client: AsyncClient,
        auth_headers: dict,
        existing_reminder: Reminder,
        idempotency_key: str,
    ):
        """Test update reminder method."""
        response = await client.patch(
            f"/api/v1/reminders/{existing_reminder.id}",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "method": "push",
            },
        )

        assert response.status_code == 200
        assert response.json()["data"]["method"] == "push"

    @pytest.mark.asyncio
    async def test_update_reminder_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        idempotency_key: str,
    ):
        """Test update non-existent reminder returns 404."""
        fake_reminder_id = uuid4()

        response = await client.patch(
            f"/api/v1/reminders/{fake_reminder_id}",
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "offset_minutes": 30,
            },
        )

        assert response.status_code == 404


class TestDeleteReminderContract:
    """Contract tests for DELETE /api/v1/reminders/:id."""

    @pytest.mark.asyncio
    async def test_delete_reminder_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        existing_reminder: Reminder,
    ):
        """Test delete reminder returns 204."""
        response = await client.delete(
            f"/api/v1/reminders/{existing_reminder.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_reminder_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test delete non-existent reminder returns 404."""
        fake_reminder_id = uuid4()

        response = await client.delete(
            f"/api/v1/reminders/{fake_reminder_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_reminder_unauthorized(
        self,
        client: AsyncClient,
        existing_reminder: Reminder,
    ):
        """Test delete reminder without auth returns 401."""
        response = await client.delete(
            f"/api/v1/reminders/{existing_reminder.id}",
        )

        assert response.status_code == 401


class TestReminderAuthorizationContract:
    """Contract tests for reminder authorization."""

    @pytest.mark.asyncio
    async def test_cannot_create_reminder_for_other_users_task(
        self,
        client: AsyncClient,
        pro_auth_headers: dict,  # Different user
        task_with_due_date: TaskInstance,  # Owned by test_user
        idempotency_key: str,
    ):
        """Test cannot create reminder for task owned by another user."""
        response = await client.post(
            f"/api/v1/tasks/{task_with_due_date.id}/reminders",
            headers={**pro_auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "type": "before",
                "offset_minutes": 60,
                "method": "in_app",
            },
        )

        # Should be 404 (task not found for this user) or 403
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_cannot_update_other_users_reminder(
        self,
        client: AsyncClient,
        pro_auth_headers: dict,  # Different user
        existing_reminder: Reminder,  # Owned by test_user
        idempotency_key: str,
    ):
        """Test cannot update reminder owned by another user."""
        response = await client.patch(
            f"/api/v1/reminders/{existing_reminder.id}",
            headers={**pro_auth_headers, "Idempotency-Key": idempotency_key},
            json={
                "offset_minutes": 30,
            },
        )

        assert response.status_code == 404
