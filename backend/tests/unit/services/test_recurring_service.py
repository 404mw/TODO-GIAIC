"""Unit tests for RecurringTaskService.

RED phase tests for Phase 6: User Story 3 - Recurring Task Templates.

T139-T143: Tests for recurring task template CRUD and instance generation.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.task import TaskInstance, TaskTemplate
from src.models.user import User
from src.schemas.enums import TaskPriority


# =============================================================================
# Service Import (will fail initially - TDD RED phase)
# =============================================================================

from src.services.recurring_service import (
    RecurringTaskService,
    RecurringServiceError,
    TemplateNotFoundError,
    InvalidRRuleError,
    TemplateUpdateForbiddenError,
)


# =============================================================================
# Template Creation Tests (T139)
# =============================================================================


class TestTemplateCreation:
    """Tests for recurring task template creation (FR-015)."""

    @pytest.mark.asyncio
    async def test_create_recurring_task_template_with_rrule(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T139: Create recurring task template with RRULE (FR-015).

        User can create a recurring task template with an RRULE definition.
        The template should have all fields populated correctly and
        next_due should be calculated automatically.
        """
        service = RecurringTaskService(db_session, settings)

        # Create a daily recurring template
        template = await service.create_template(
            user=test_user,
            title="Daily standup",
            description="Team standup meeting",
            priority=TaskPriority.HIGH,
            rrule="FREQ=DAILY;INTERVAL=1",
            estimated_duration=15,
        )

        assert template.id is not None
        assert template.user_id == test_user.id
        assert template.title == "Daily standup"
        assert template.description == "Team standup meeting"
        assert template.priority == TaskPriority.HIGH
        assert template.rrule == "FREQ=DAILY;INTERVAL=1"
        assert template.estimated_duration == 15
        assert template.active is True
        assert template.next_due is not None  # Should be calculated

    @pytest.mark.asyncio
    async def test_create_template_calculates_initial_next_due(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T139 (cont.): Template creation calculates initial next_due.

        When a template is created, next_due should be calculated
        based on the RRULE from the current time.
        """
        service = RecurringTaskService(db_session, settings)

        before_create = datetime.now(UTC).replace(tzinfo=None)

        template = await service.create_template(
            user=test_user,
            title="Weekly review",
            rrule="FREQ=WEEKLY;BYDAY=FR",
        )

        after_create = datetime.now(UTC).replace(tzinfo=None)

        # next_due should be calculated and be in the future
        assert template.next_due is not None
        assert template.next_due >= before_create
        # Should be within a week for weekly recurrence
        assert template.next_due <= after_create + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_create_template_validates_rrule_format(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T139 (cont.): Template creation validates RRULE format.

        Invalid RRULE strings should be rejected.
        """
        service = RecurringTaskService(db_session, settings)

        # Invalid RRULE should raise error
        with pytest.raises(InvalidRRuleError):
            await service.create_template(
                user=test_user,
                title="Invalid recurring",
                rrule="INVALID_RRULE_FORMAT",
            )


# =============================================================================
# Instance Generation Tests (T141, T142)
# =============================================================================


class TestInstanceGeneration:
    """Tests for recurring task instance generation (FR-016, FR-017)."""

    @pytest.mark.asyncio
    async def test_next_instance_generated_on_completion(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T141: Next instance generated on completion (FR-016).

        When a recurring task instance is completed, the next instance
        should be automatically generated based on the template.
        """
        service = RecurringTaskService(db_session, settings)

        # Create a daily recurring template
        template = await service.create_template(
            user=test_user,
            title="Daily task",
            rrule="FREQ=DAILY;INTERVAL=1",
        )

        # Generate the first instance
        first_instance = await service.generate_next_instance(template)

        assert first_instance is not None
        assert first_instance.template_id == template.id
        assert first_instance.title == template.title
        assert first_instance.user_id == test_user.id
        assert first_instance.completed is False

        # Record the first instance's due date
        first_due = first_instance.due_date

        # Complete the first instance and generate next
        completed_instance, next_instance = await service.complete_and_generate_next(
            template_id=template.id,
            instance=first_instance,
        )

        assert completed_instance.completed is True
        assert next_instance is not None
        assert next_instance.id != first_instance.id
        assert next_instance.template_id == template.id

        # Next instance should have due date 1 day after first
        if first_due and next_instance.due_date:
            time_diff = next_instance.due_date - first_due
            assert time_diff >= timedelta(hours=23)  # Account for DST

    @pytest.mark.asyncio
    async def test_completion_not_rolled_back_if_generation_fails(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T142: Completion not rolled back if generation fails (FR-017).

        If generating the next instance fails, the completion of the
        current instance should NOT be rolled back.
        """
        service = RecurringTaskService(db_session, settings)

        # Create a template with finite recurrence (e.g., COUNT=1)
        template = await service.create_template(
            user=test_user,
            title="One-time recurring",
            rrule="FREQ=DAILY;COUNT=1",
        )

        # Generate and complete the only instance
        instance = await service.generate_next_instance(template)
        assert instance is not None

        # Complete the instance - generation of next should fail silently
        # but completion should still succeed
        completed, next_instance = await service.complete_and_generate_next(
            template_id=template.id,
            instance=instance,
        )

        assert completed.completed is True
        assert next_instance is None  # No more instances possible


# =============================================================================
# Template Update Tests (T143)
# =============================================================================


class TestTemplateUpdate:
    """Tests for recurring task template update restrictions (FR-018)."""

    @pytest.mark.asyncio
    async def test_cannot_edit_recurrence_on_past_instances(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T143: Cannot edit recurrence on past instances (FR-018).

        Editing a template's recurrence rule should only affect future
        instances. Past/completed instances are immutable.
        """
        service = RecurringTaskService(db_session, settings)

        # Create template and generate first instance
        template = await service.create_template(
            user=test_user,
            title="Weekly task",
            rrule="FREQ=WEEKLY;BYDAY=MO",
        )

        first_instance = await service.generate_next_instance(template)

        # Complete the instance
        completed, _ = await service.complete_and_generate_next(
            template_id=template.id,
            instance=first_instance,
        )

        # Now update the template's RRULE
        updated_template = await service.update_template(
            user=test_user,
            template_id=template.id,
            rrule="FREQ=DAILY;INTERVAL=1",
            apply_to_future_only=True,
        )

        # The completed instance should remain unchanged
        refreshed_instance = await service.get_instance(first_instance.id)
        assert refreshed_instance.completed is True
        # Instance's attributes inherited from old template should be intact

        # New instances should use the updated RRULE
        assert updated_template.rrule == "FREQ=DAILY;INTERVAL=1"

    @pytest.mark.asyncio
    async def test_update_template_future_only_option(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T143 (cont.): Update template with future-only option.

        When apply_to_future_only=True, only future instances are affected.
        """
        service = RecurringTaskService(db_session, settings)

        template = await service.create_template(
            user=test_user,
            title="Test template",
            description="Original description",
            rrule="FREQ=DAILY;INTERVAL=1",
        )

        # Generate an instance
        instance = await service.generate_next_instance(template)
        original_title = instance.title

        # Update template
        await service.update_template(
            user=test_user,
            template_id=template.id,
            title="Updated title",
            apply_to_future_only=True,
        )

        # Existing instance should keep original title
        refreshed_instance = await service.get_instance(instance.id)
        assert refreshed_instance.title == original_title

    @pytest.mark.asyncio
    async def test_deactivate_template_stops_generation(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """T143 (cont.): Deactivating template stops instance generation.

        When a template is deactivated (active=False), no new instances
        should be generated.
        """
        service = RecurringTaskService(db_session, settings)

        template = await service.create_template(
            user=test_user,
            title="Test template",
            rrule="FREQ=DAILY;INTERVAL=1",
        )

        # Deactivate the template
        await service.update_template(
            user=test_user,
            template_id=template.id,
            active=False,
        )

        # Trying to generate should return None or raise
        instance = await service.generate_next_instance(template)
        assert instance is None


# =============================================================================
# Template Deletion Tests
# =============================================================================


class TestTemplateDeletion:
    """Tests for recurring task template deletion."""

    @pytest.mark.asyncio
    async def test_delete_template_preserves_existing_instances(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """Deleting a template should preserve existing task instances.

        The instances become standalone tasks (orphaned from template).
        """
        service = RecurringTaskService(db_session, settings)

        template = await service.create_template(
            user=test_user,
            title="To be deleted",
            rrule="FREQ=DAILY;INTERVAL=1",
        )

        instance = await service.generate_next_instance(template)
        instance_id = instance.id

        # Delete the template
        await service.delete_template(
            user=test_user,
            template_id=template.id,
        )

        # Instance should still exist but have no template reference
        orphaned = await service.get_instance(instance_id)
        assert orphaned is not None
        assert orphaned.template_id is None  # Orphaned

    @pytest.mark.asyncio
    async def test_delete_nonexistent_template_raises_error(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """Deleting a non-existent template should raise TemplateNotFoundError."""
        service = RecurringTaskService(db_session, settings)

        with pytest.raises(TemplateNotFoundError):
            await service.delete_template(
                user=test_user,
                template_id=uuid4(),
            )


# =============================================================================
# Template Listing Tests
# =============================================================================


class TestTemplateListing:
    """Tests for listing recurring task templates."""

    @pytest.mark.asyncio
    async def test_list_user_templates(
        self,
        db_session: AsyncSession,
        test_user: User,
        pro_user: User,
        settings: Settings,
    ):
        """List templates returns only the user's templates."""
        service = RecurringTaskService(db_session, settings)

        # Create templates for test_user
        await service.create_template(
            user=test_user,
            title="User 1 Template 1",
            rrule="FREQ=DAILY;INTERVAL=1",
        )
        await service.create_template(
            user=test_user,
            title="User 1 Template 2",
            rrule="FREQ=WEEKLY;BYDAY=MO",
        )

        # Create template for pro_user
        await service.create_template(
            user=pro_user,
            title="User 2 Template",
            rrule="FREQ=MONTHLY;BYMONTHDAY=1",
        )

        # List test_user's templates
        templates = await service.list_templates(user=test_user)

        assert len(templates) == 2
        titles = [t.title for t in templates]
        assert "User 1 Template 1" in titles
        assert "User 1 Template 2" in titles
        assert "User 2 Template" not in titles

    @pytest.mark.asyncio
    async def test_list_templates_includes_active_only_by_default(
        self,
        db_session: AsyncSession,
        test_user: User,
        settings: Settings,
    ):
        """List templates excludes inactive templates by default."""
        service = RecurringTaskService(db_session, settings)

        # Create active template
        await service.create_template(
            user=test_user,
            title="Active Template",
            rrule="FREQ=DAILY;INTERVAL=1",
        )

        # Create and deactivate template
        inactive = await service.create_template(
            user=test_user,
            title="Inactive Template",
            rrule="FREQ=DAILY;INTERVAL=1",
        )
        await service.update_template(
            user=test_user,
            template_id=inactive.id,
            active=False,
        )

        # List without include_inactive
        templates = await service.list_templates(user=test_user)
        assert len(templates) == 1
        assert templates[0].title == "Active Template"

        # List with include_inactive
        all_templates = await service.list_templates(
            user=test_user, include_inactive=True
        )
        assert len(all_templates) == 2
