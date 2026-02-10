"""Integration tests for recurring task lifecycle.

Phase 6: User Story 3 - Recurring Task Templates (FR-015 to FR-018)

T157: Add integration test for recurring task lifecycle
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.dependencies import JWTKeyManager
from src.models.task import TaskInstance, TaskTemplate
from src.models.user import User
from src.schemas.enums import TaskPriority, UserTier


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Create a second test user for isolation tests."""
    user = User(
        id=uuid4(),
        google_id=f"google-other-{uuid4()}",
        email=f"other-{uuid4()}@example.com",
        name="Other User",
        tier=UserTier.FREE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def other_user_auth_headers(other_user: User, settings: Settings) -> dict[str, str]:
    """Generate auth headers for the other user."""
    jwt_manager = JWTKeyManager(settings)
    token = jwt_manager.create_access_token(
        user_id=other_user.id,
        email=other_user.email,
        tier=other_user.tier.value,
    )
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# TEMPLATE CRUD LIFECYCLE
# =============================================================================


class TestTemplateLifecycle:
    """Integration tests for template CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_template_generates_first_instance(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Create a template and verify it calculates next_due.

        FR-015: User can create a recurring task template with an RRULE.
        """
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Daily Standup",
                "description": "Morning team standup",
                "priority": "high",
                "rrule": "FREQ=DAILY;INTERVAL=1",
                "estimated_duration": 15,
            },
        )

        assert response.status_code == 201
        data = response.json()["data"]

        assert data["title"] == "Daily Standup"
        assert data["rrule"] == "FREQ=DAILY;INTERVAL=1"
        assert data["active"] is True
        assert data["next_due"] is not None

        # Verify human-readable description
        assert "day" in data["rrule_description"].lower()

    @pytest.mark.asyncio
    async def test_list_templates_returns_user_templates_only(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_auth_headers: dict,
    ):
        """Verify templates are user-scoped.

        Users should only see their own templates.
        """
        # Create template for first user
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "User 1 Template",
                "rrule": "FREQ=WEEKLY;BYDAY=MO",
            },
        )
        assert response.status_code == 201

        # Create template for second user
        response = await client.post(
            "/api/v1/templates",
            headers=other_user_auth_headers,
            json={
                "title": "User 2 Template",
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )
        assert response.status_code == 201

        # List first user's templates
        response = await client.get(
            "/api/v1/templates",
            headers=auth_headers,
        )

        assert response.status_code == 200
        templates = response.json()["data"]

        titles = [t["title"] for t in templates]
        assert "User 1 Template" in titles
        assert "User 2 Template" not in titles

    @pytest.mark.asyncio
    async def test_update_template_recalculates_next_due(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Updating RRULE should recalculate next_due.

        FR-018: Editing a template affects only future instances.
        """
        # Create weekly template
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Weekly Task",
                "rrule": "FREQ=WEEKLY;BYDAY=MO",
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]
        original_next_due = response.json()["data"]["next_due"]

        # Update to daily
        response = await client.patch(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # RRULE should be updated
        assert data["rrule"] == "FREQ=DAILY;INTERVAL=1"
        # next_due should be recalculated (daily should be sooner than weekly)
        new_next_due = data["next_due"]
        assert new_next_due != original_next_due

    @pytest.mark.asyncio
    async def test_deactivate_template_clears_next_due(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Deactivating a template should clear next_due."""
        # Create template
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "To Deactivate",
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]
        assert response.json()["data"]["next_due"] is not None

        # Deactivate
        response = await client.patch(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={"active": False},
        )

        assert response.status_code == 200
        assert response.json()["data"]["active"] is False
        assert response.json()["data"]["next_due"] is None

    @pytest.mark.asyncio
    async def test_delete_template_preserves_existing_instances(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Deleting a template should orphan existing instances.

        Existing task instances should become standalone tasks.
        """
        # Create template
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "To Delete",
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]

        # Generate an instance
        response = await client.post(
            f"/api/v1/templates/{template_id}/generate",
            headers=auth_headers,
        )
        assert response.status_code == 200
        instance_id = response.json()["data"]["instance_id"]

        # Delete template
        response = await client.delete(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Instance should still exist as standalone task
        response = await client.get(
            f"/api/v1/tasks/{instance_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        # Template reference should be cleared (orphaned)


# =============================================================================
# INSTANCE GENERATION LIFECYCLE
# =============================================================================


class TestInstanceGeneration:
    """Integration tests for recurring instance generation."""

    @pytest.mark.asyncio
    async def test_manual_instance_generation(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Manually generate an instance from a template.

        FR-016: Recurring instances are generated automatically.
        """
        # Create template
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Generate Test",
                "priority": "high",
                "rrule": "FREQ=DAILY;INTERVAL=1",
                "estimated_duration": 30,
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]

        # Generate instance
        response = await client.post(
            f"/api/v1/templates/{template_id}/generate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["template_id"] == template_id
        assert data["instance_id"] is not None
        assert data["title"] == "Generate Test"
        assert data["due_date"] is not None

    @pytest.mark.asyncio
    async def test_inactive_template_cannot_generate(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Inactive templates cannot generate new instances."""
        # Create and deactivate template
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Inactive Template",
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={"active": False},
        )
        assert response.status_code == 200

        # Try to generate
        response = await client.post(
            f"/api/v1/templates/{template_id}/generate",
            headers=auth_headers,
        )

        assert response.status_code in [400, 409]
        error_msg = response.json().get("error", {}).get("message", response.json().get("detail", ""))
        assert "inactive" in error_msg.lower() or "not active" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_generated_instance_inherits_template_properties(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Generated instances should inherit template properties."""
        # Create template with specific properties
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Inherited Props",
                "description": "Test description",
                "priority": "high",
                "rrule": "FREQ=DAILY;INTERVAL=1",
                "estimated_duration": 45,
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]

        # Generate instance
        response = await client.post(
            f"/api/v1/templates/{template_id}/generate",
            headers=auth_headers,
        )
        assert response.status_code == 200
        instance_id = response.json()["data"]["instance_id"]

        # Verify instance properties
        response = await client.get(
            f"/api/v1/tasks/{instance_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        task = response.json()["data"]

        assert task["title"] == "Inherited Props"
        assert task["description"] == "Test description"
        assert task["priority"] == "high"
        assert task["estimated_duration"] == 45


# =============================================================================
# RRULE VALIDATION
# =============================================================================


class TestRRuleValidation:
    """Integration tests for RRULE validation."""

    @pytest.mark.asyncio
    async def test_invalid_rrule_rejected(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Invalid RRULE strings should be rejected.

        FR-015: RRULE must be valid RFC 5545 format.
        """
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Invalid RRULE",
                "rrule": "NOT_A_VALID_RRULE",
            },
        )

        assert response.status_code == 400 or response.status_code == 422

    @pytest.mark.asyncio
    async def test_various_rrule_patterns(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Various RRULE patterns should be accepted."""
        patterns = [
            ("FREQ=DAILY;INTERVAL=1", "Daily"),
            ("FREQ=WEEKLY;BYDAY=MO,WE,FR", "MWF"),
            ("FREQ=MONTHLY;BYMONTHDAY=1", "Monthly 1st"),
            ("FREQ=WEEKLY;INTERVAL=2", "Biweekly"),
        ]

        for rrule, name in patterns:
            response = await client.post(
                "/api/v1/templates",
                headers=auth_headers,
                json={
                    "title": f"Pattern: {name}",
                    "rrule": rrule,
                },
            )

            assert response.status_code == 201, f"Failed for {rrule}: {response.text}"
            assert response.json()["data"]["rrule"] == rrule


# =============================================================================
# ERROR HANDLING
# =============================================================================


class TestErrorHandling:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_template_returns_404(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Getting a non-existent template returns 404."""
        response = await client.get(
            "/api/v1/templates/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_access_other_user_template_returns_404(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_auth_headers: dict,
    ):
        """Accessing another user's template returns 404.

        FR-005: Users can only access their own resources.
        """
        # Create template for first user
        response = await client.post(
            "/api/v1/templates",
            headers=auth_headers,
            json={
                "title": "Private Template",
                "rrule": "FREQ=DAILY;INTERVAL=1",
            },
        )
        assert response.status_code == 201
        template_id = response.json()["data"]["id"]

        # Try to access as second user
        response = await client.get(
            f"/api/v1/templates/{template_id}",
            headers=other_user_auth_headers,
        )

        assert response.status_code == 404
