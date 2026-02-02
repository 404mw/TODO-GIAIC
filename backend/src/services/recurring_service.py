"""Recurring task service for template and instance management.

Phase 6: User Story 3 - Recurring Task Templates (FR-015 to FR-018)

T146-T149: RecurringTaskService implementation.
"""

import logging
from datetime import datetime, timezone, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.lib.rrule import (
    InvalidRRuleError as RRuleInvalidError,
    calculate_next_due,
    validate_rrule,
)
from src.models.task import TaskInstance, TaskTemplate
from src.models.user import User
from src.schemas.enums import CompletedBy, TaskPriority


logger = logging.getLogger(__name__)


def _ensure_naive_utc(dt: datetime) -> datetime:
    """Ensure datetime is naive UTC for consistent comparisons with DB values."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# =============================================================================
# EXCEPTIONS
# =============================================================================


class RecurringServiceError(Exception):
    """Base exception for recurring service errors."""

    pass


class TemplateNotFoundError(RecurringServiceError):
    """Raised when template is not found or user doesn't have access."""

    pass


class InvalidRRuleError(RecurringServiceError):
    """Raised when an RRULE string is invalid."""

    def __init__(self, rrule_string: str, message: str | None = None):
        self.rrule_string = rrule_string
        self.message = message or f"Invalid RRULE: {rrule_string}"
        super().__init__(self.message)


class TemplateUpdateForbiddenError(RecurringServiceError):
    """Raised when attempting a forbidden template update."""

    pass


# =============================================================================
# RECURRING TASK SERVICE
# =============================================================================


class RecurringTaskService:
    """Service for recurring task template and instance management.

    Handles:
    - Template CRUD with RRULE validation
    - Instance generation from templates
    - Completion-triggered generation
    - Template updates with future-only option

    Per research.md Section 10 (RRULE processing).
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # TEMPLATE CRUD (T146, T149)
    # =========================================================================

    async def create_template(
        self,
        user: User,
        title: str,
        rrule: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_duration: int | None = None,
    ) -> TaskTemplate:
        """Create a recurring task template with RRULE validation.

        T146: RecurringTaskService.create_template

        Args:
            user: The template owner
            title: Template title (1-200 chars)
            rrule: RFC 5545 RRULE string
            description: Template description
            priority: Default priority for generated instances
            estimated_duration: Default duration in minutes

        Returns:
            The created TaskTemplate

        Raises:
            InvalidRRuleError: If RRULE is invalid
        """
        # Validate RRULE format
        if not validate_rrule(rrule):
            raise InvalidRRuleError(rrule, "Invalid RRULE format")

        # Calculate initial next_due (naive UTC for DB compat)
        # Truncate microseconds to avoid RRULE second-precision mismatch
        now = _ensure_naive_utc(datetime.now(UTC)).replace(microsecond=0)
        next_due = calculate_next_due(rrule, after=now, dtstart=now)

        # If no occurrence strictly after now, try including now itself
        # (handles COUNT=1 where the only occurrence is at dtstart)
        if next_due is None:
            from src.lib.rrule import parse_rrule
            rule = parse_rrule(rrule, dtstart=now)
            next_due = rule.after(now, inc=True)

        template = TaskTemplate(
            id=uuid4(),
            user_id=user.id,
            title=title.strip(),
            description=description,
            priority=priority,
            estimated_duration=estimated_duration,
            rrule=rrule,
            next_due=next_due,
            active=True,
        )

        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)

        return template

    async def get_template(
        self,
        user: User,
        template_id: UUID,
    ) -> TaskTemplate:
        """Get a template by ID with ownership check.

        Args:
            user: The requesting user
            template_id: The template ID

        Returns:
            The TaskTemplate

        Raises:
            TemplateNotFoundError: If template not found or user doesn't own it
        """
        query = select(TaskTemplate).where(
            TaskTemplate.id == template_id,
            TaskTemplate.user_id == user.id,
        )

        result = await self.session.execute(query)
        template = result.scalar_one_or_none()

        if template is None:
            raise TemplateNotFoundError(f"Template {template_id} not found")

        return template

    async def list_templates(
        self,
        user: User,
        include_inactive: bool = False,
        offset: int = 0,
        limit: int = 25,
    ) -> Sequence[TaskTemplate]:
        """List user's templates with optional inactive filter.

        Args:
            user: The requesting user
            include_inactive: Include inactive templates
            offset: Pagination offset
            limit: Items per page

        Returns:
            List of TaskTemplates
        """
        query = select(TaskTemplate).where(TaskTemplate.user_id == user.id)

        if not include_inactive:
            query = query.where(TaskTemplate.active == True)

        query = (
            query.order_by(TaskTemplate.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_template(
        self,
        user: User,
        template_id: UUID,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        estimated_duration: int | None = None,
        rrule: str | None = None,
        active: bool | None = None,
        apply_to_future_only: bool = True,
    ) -> TaskTemplate:
        """Update a template with optional future-only semantics.

        T149: RecurringTaskService.update_template with future-only option (FR-018)

        Args:
            user: The requesting user
            template_id: The template ID
            title: New title
            description: New description
            priority: New priority
            estimated_duration: New duration
            rrule: New RRULE (validated)
            active: New active status
            apply_to_future_only: If True, don't modify existing instances

        Returns:
            The updated TaskTemplate

        Raises:
            TemplateNotFoundError: If template not found
            InvalidRRuleError: If new RRULE is invalid
        """
        template = await self.get_template(user=user, template_id=template_id)

        # Validate new RRULE if provided
        if rrule is not None and not validate_rrule(rrule):
            raise InvalidRRuleError(rrule, "Invalid RRULE format")

        # Apply updates
        if title is not None:
            template.title = title.strip()

        if description is not None:
            template.description = description

        if priority is not None:
            template.priority = priority

        if estimated_duration is not None:
            template.estimated_duration = estimated_duration

        if rrule is not None:
            template.rrule = rrule
            # Recalculate next_due with new RRULE (naive UTC for DB compat)
            now = _ensure_naive_utc(datetime.now(UTC))
            template.next_due = calculate_next_due(rrule, after=now, dtstart=now)

        if active is not None:
            template.active = active
            if not active:
                # Clear next_due when deactivating
                template.next_due = None

        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)

        return template

    async def delete_template(
        self,
        user: User,
        template_id: UUID,
    ) -> None:
        """Delete a template, orphaning its existing instances.

        Args:
            user: The requesting user
            template_id: The template ID to delete

        Raises:
            TemplateNotFoundError: If template not found
        """
        template = await self.get_template(user=user, template_id=template_id)

        # Orphan existing instances (set template_id to NULL)
        instances_query = select(TaskInstance).where(
            TaskInstance.template_id == template_id
        )
        result = await self.session.execute(instances_query)
        instances = result.scalars().all()

        for instance in instances:
            instance.template_id = None
            self.session.add(instance)

        # Delete template
        await self.session.delete(template)
        await self.session.flush()

    # =========================================================================
    # INSTANCE GENERATION (T147)
    # =========================================================================

    async def generate_next_instance(
        self,
        template: TaskTemplate,
    ) -> TaskInstance | None:
        """Generate the next task instance from a template.

        T147: RecurringTaskService.generate_next_instance (FR-016)

        Args:
            template: The template to generate from

        Returns:
            The created TaskInstance, or None if template is inactive
            or no more occurrences exist
        """
        # Don't generate if template is inactive
        if not template.active:
            return None

        # Calculate due date for this instance (naive UTC for DB compat)
        # Truncate microseconds to avoid RRULE second-precision mismatch
        now = _ensure_naive_utc(datetime.now(UTC)).replace(microsecond=0)
        due_date = _ensure_naive_utc(template.next_due) if template.next_due else None

        # If next_due is in the past, calculate a new one
        if due_date is None or due_date < now:
            due_date = calculate_next_due(
                template.rrule, after=now, dtstart=now
            )

        # No more occurrences possible
        if due_date is None:
            return None

        # Create the instance
        instance = TaskInstance(
            id=uuid4(),
            user_id=template.user_id,
            template_id=template.id,
            title=template.title,
            description=template.description,
            priority=template.priority,
            due_date=due_date,
            estimated_duration=template.estimated_duration,
            completed=False,
            hidden=False,
            archived=False,
            version=1,
        )

        # Update template's next_due for the following occurrence
        next_next_due = calculate_next_due(
            template.rrule, after=due_date, dtstart=due_date
        )
        template.next_due = next_next_due

        self.session.add(instance)
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(instance)

        return instance

    async def complete_and_generate_next(
        self,
        template_id: UUID,
        instance: TaskInstance,
    ) -> tuple[TaskInstance, TaskInstance | None]:
        """Complete an instance and generate the next one.

        T147 (cont.): Completion-triggered generation (FR-016)
        T142: Completion not rolled back if generation fails (FR-017)

        Args:
            template_id: The template ID
            instance: The instance to complete

        Returns:
            Tuple of (completed_instance, next_instance or None)

        Note:
            Even if next instance generation fails, the completion
            of the current instance is NOT rolled back (FR-017).
        """
        # Complete the current instance first
        instance.completed = True
        instance.completed_at = _ensure_naive_utc(datetime.now(UTC))
        instance.completed_by = CompletedBy.MANUAL
        instance.version += 1

        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)

        # Try to generate next instance (don't fail if this fails)
        next_instance = None
        try:
            query = select(TaskTemplate).where(TaskTemplate.id == template_id)
            result = await self.session.execute(query)
            template = result.scalar_one_or_none()

            if template is not None:
                next_instance = await self.generate_next_instance(template)
        except Exception:
            # FR-017: Don't roll back completion if generation fails
            # Log the error but continue
            pass

        return instance, next_instance

    # =========================================================================
    # INSTANCE RETRIEVAL
    # =========================================================================

    async def get_instance(
        self,
        instance_id: UUID,
    ) -> TaskInstance:
        """Get a task instance by ID.

        Args:
            instance_id: The instance ID

        Returns:
            The TaskInstance

        Raises:
            RecurringServiceError: If instance not found
        """
        query = select(TaskInstance).where(TaskInstance.id == instance_id)
        result = await self.session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise RecurringServiceError(f"Instance {instance_id} not found")

        return instance

    async def list_instances_for_template(
        self,
        user: User,
        template_id: UUID,
        include_completed: bool = True,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[Sequence[TaskInstance], int]:
        """List task instances for a specific template.

        Args:
            user: The requesting user
            template_id: The template ID
            include_completed: Include completed instances
            offset: Pagination offset
            limit: Items per page

        Returns:
            Tuple of (instances, total_count)
        """
        # Verify template ownership
        await self.get_template(user=user, template_id=template_id)

        query = select(TaskInstance).where(
            TaskInstance.template_id == template_id,
            TaskInstance.hidden == False,
        )

        if not include_completed:
            query = query.where(TaskInstance.completed == False)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = (
            query.order_by(TaskInstance.due_date.asc())
            .offset(offset)
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        instances = result.scalars().all()

        return instances, total


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_recurring_service(
    session: AsyncSession, settings: Settings
) -> RecurringTaskService:
    """Get a RecurringTaskService instance."""
    return RecurringTaskService(session, settings)
