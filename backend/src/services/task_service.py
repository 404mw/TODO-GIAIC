"""Task service for task and subtask management.

Phase 4: User Story 2 - Task Creation and Management (FR-007 to FR-014)

T106-T118: TaskService implementation with CRUD operations.
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.config import Settings
from src.models.subtask import Subtask
from src.models.task import TaskInstance
from src.models.tombstone import DeletionTombstone
from src.models.user import User
from src.schemas.enums import (
    CompletedBy,
    SubtaskSource,
    TaskPriority,
    TombstoneEntityType,
)
from src.schemas.subtask import SubtaskCreate
from src.schemas.task import TaskCreate, TaskUpdate, ForceCompleteRequest

# Import metrics (T130)
from src.middleware.metrics import (
    record_task_operation,
    record_task_completion,
    record_task_deletion,
    record_task_version_conflict,
    record_task_limit_reached,
    record_task_due_date_exceeded,
)


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class TaskServiceError(Exception):
    """Base exception for task service errors."""

    pass


class TaskNotFoundError(TaskServiceError):
    """Raised when task is not found or user doesn't have access."""

    pass


class TaskVersionConflictError(TaskServiceError):
    """Raised when optimistic locking detects a stale version (409)."""

    pass


class TaskArchivedError(TaskServiceError):
    """Raised when trying to modify an archived task (409)."""

    pass


class TaskLimitExceededError(TaskServiceError):
    """Raised when user has reached their task limit (409)."""

    pass


class TaskDueDateExceededError(TaskServiceError):
    """Raised when due date exceeds 30 days from creation (FR-013)."""

    pass


class SubtaskNotFoundError(TaskServiceError):
    """Raised when subtask is not found or user doesn't have access."""

    pass


class SubtaskLimitExceededError(TaskServiceError):
    """Raised when user has reached subtask limit for a task (409)."""

    pass


# =============================================================================
# CONSTANTS
# =============================================================================

MAX_TASK_DURATION_DAYS = 30
MAX_TOMBSTONES_PER_USER = 3

# Import limit utilities from centralized module (T133, T135)
from src.lib.limits import (
    get_description_limit,
    get_effective_subtask_limit,
)


# =============================================================================
# TASK SERVICE
# =============================================================================


class TaskService:
    """Service for task and subtask operations.

    Handles:
    - Task CRUD with tier-based validation
    - Subtask management with limits
    - Optimistic locking
    - Auto-completion logic
    - Soft/hard deletion with tombstones
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # TASK CRUD (T106-T113)
    # =========================================================================

    async def create_task(
        self, user: User, data: TaskCreate
    ) -> TaskInstance:
        """Create a new task with tier-based validation.

        T106: TaskService.create_task with tier-based validation

        Args:
            user: The task owner
            data: Task creation data

        Returns:
            The created TaskInstance

        Raises:
            TaskServiceError: If description exceeds tier limit
            TaskDueDateExceededError: If due date > 30 days from now (FR-013)
            TaskLimitExceededError: If user has reached task limit
        """
        # Validate description length based on tier (using centralized limits)
        description = data.description or ""
        max_desc_length = get_description_limit(user.tier)
        if len(description) > max_desc_length:
            raise TaskServiceError(
                f"Description exceeds {max_desc_length} character limit for "
                f"{'Pro' if user.is_pro else 'Free'} tier"
            )

        # Validate due date is within 30 days (FR-013)
        if data.due_date is not None:
            max_due_date = datetime.now(UTC) + timedelta(days=MAX_TASK_DURATION_DAYS)
            if data.due_date > max_due_date:
                record_task_due_date_exceeded()
                raise TaskDueDateExceededError(
                    f"Due date cannot exceed {MAX_TASK_DURATION_DAYS} days from creation"
                )

        # Create the task
        task = TaskInstance(
            id=uuid4(),
            user_id=user.id,
            title=data.title.strip(),
            description=description,
            priority=data.priority,
            due_date=data.due_date,
            estimated_duration=data.estimated_duration,
            completed=False,
            hidden=False,
            archived=False,
            version=1,
        )

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # T130: Record task creation metric
        tier = "pro" if user.is_pro else "free"
        record_task_operation("create", tier)

        return task

    async def get_task(
        self,
        user: User,
        task_id: UUID,
        include_hidden: bool = False,
        include_subtasks: bool = False,
    ) -> TaskInstance:
        """Get a task by ID with ownership check.

        T107: TaskService.get_task with user ownership check

        Args:
            user: The requesting user
            task_id: The task ID to retrieve
            include_hidden: Include hidden (soft-deleted) tasks
            include_subtasks: Eagerly load subtasks

        Returns:
            The TaskInstance

        Raises:
            TaskNotFoundError: If task not found or user doesn't own it
        """
        query = select(TaskInstance).where(
            TaskInstance.id == task_id,
            TaskInstance.user_id == user.id,
        )

        if not include_hidden:
            query = query.where(TaskInstance.hidden == False)

        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        if include_subtasks:
            # Eagerly load subtasks and reminders
            await self.session.refresh(task, ["subtasks", "reminders"])

        return task

    async def list_tasks(
        self,
        user: User,
        offset: int = 0,
        limit: int = 25,
        completed: bool | None = None,
        priority: TaskPriority | None = None,
        hidden: bool = False,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
    ) -> tuple[Sequence[TaskInstance], int]:
        """List tasks with pagination and filters.

        T108: TaskService.list_tasks with pagination and filters (FR-060)

        Args:
            user: The requesting user
            offset: Pagination offset
            limit: Items per page (max 100)
            completed: Filter by completion status
            priority: Filter by priority
            hidden: Include hidden tasks
            due_before: Tasks due before this date
            due_after: Tasks due after this date

        Returns:
            Tuple of (tasks, total_count)
        """
        # Build base query
        query = select(TaskInstance).where(TaskInstance.user_id == user.id)

        # Apply filters
        if not hidden:
            query = query.where(TaskInstance.hidden == False)

        if completed is not None:
            query = query.where(TaskInstance.completed == completed)

        if priority is not None:
            query = query.where(TaskInstance.priority == priority)

        if due_before is not None:
            query = query.where(TaskInstance.due_date <= due_before)

        if due_after is not None:
            query = query.where(TaskInstance.due_date >= due_after)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering with eager loading
        query = (
            query.options(selectinload(TaskInstance.subtasks))
            .order_by(TaskInstance.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))
        )

        result = await self.session.execute(query)
        tasks = result.scalars().unique().all()

        return tasks, total

    async def update_task(
        self, user: User, task_id: UUID, data: TaskUpdate
    ) -> TaskInstance:
        """Update a task with optimistic locking.

        T109: TaskService.update_task with optimistic locking (FR-014)

        Args:
            user: The requesting user
            task_id: The task ID to update
            data: Update data with version for optimistic locking

        Returns:
            The updated TaskInstance

        Raises:
            TaskNotFoundError: If task not found
            TaskVersionConflictError: If version mismatch (stale update)
            TaskArchivedError: If trying to modify archived task
        """
        task = await self.get_task(user=user, task_id=task_id, include_hidden=True)

        # Check version for optimistic locking
        if task.version != data.version:
            record_task_version_conflict()
            raise TaskVersionConflictError(
                f"Version conflict: expected {data.version}, got {task.version}"
            )

        # Check if task is archived and we're trying to modify it (except un-archiving)
        if task.archived and data.archived is not False:
            if data.completed is not None or data.title is not None:
                raise TaskArchivedError("Cannot modify archived task")

        # Handle completion tracking (check before applying updates)
        was_completed = task.completed
        if data.completed is True and not was_completed:
            task.completed_at = datetime.now(UTC)
            task.completed_by = CompletedBy.MANUAL

        # Apply updates
        update_fields = data.model_dump(exclude_unset=True, exclude={"version"})

        for field, value in update_fields.items():
            if value is not None or field in {"description", "due_date", "estimated_duration"}:
                setattr(task, field, value)

        # Increment version
        task.version += 1

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # T130: Record task update metric
        tier = "pro" if user.is_pro else "free"
        record_task_operation("update", tier)

        return task

    async def complete_task(
        self,
        user: User,
        task_id: UUID,
        completed_by: CompletedBy,
        version: int | None = None,
    ) -> TaskInstance:
        """Complete a task with specified completion type.

        T110: TaskService.complete_task with completion tracking (FR-008)

        Args:
            user: The requesting user
            task_id: The task ID to complete
            completed_by: How the task was completed
            version: Optional version for optimistic locking

        Returns:
            The completed TaskInstance
        """
        task = await self.get_task(user=user, task_id=task_id)

        if task.archived:
            raise TaskArchivedError("Cannot complete archived task")

        if version is not None and task.version != version:
            record_task_version_conflict()
            raise TaskVersionConflictError(
                f"Version conflict: expected {version}, got {task.version}"
            )

        task.completed = True
        task.completed_at = datetime.now(UTC)
        task.completed_by = completed_by
        task.version += 1

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # T130: Record task completion metrics
        tier = "pro" if user.is_pro else "free"
        record_task_operation("complete", tier)
        record_task_completion(completed_by.value)

        return task

    async def force_complete_task(
        self,
        user: User,
        task_id: UUID,
        data: ForceCompleteRequest,
    ) -> TaskInstance:
        """Force-complete task and all its subtasks.

        T111: TaskService.force_complete_task (FR-010)

        Args:
            user: The requesting user
            task_id: The task ID to force-complete
            data: Request with version for optimistic locking

        Returns:
            The force-completed TaskInstance
        """
        task = await self.get_task(user=user, task_id=task_id, include_subtasks=True)

        if task.archived:
            raise TaskArchivedError("Cannot complete archived task")

        if task.version != data.version:
            record_task_version_conflict()
            raise TaskVersionConflictError(
                f"Version conflict: expected {data.version}, got {task.version}"
            )

        now = datetime.now(UTC)

        # Complete all incomplete subtasks
        for subtask in task.subtasks:
            if not subtask.completed:
                subtask.completed = True
                subtask.completed_at = now
                self.session.add(subtask)

        # Complete the task
        task.completed = True
        task.completed_at = now
        task.completed_by = CompletedBy.FORCE
        task.version += 1

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # T130: Record force completion metrics
        tier = "pro" if user.is_pro else "free"
        record_task_operation("force_complete", tier)
        record_task_completion("force")

        return task

    async def soft_delete_task(
        self, user: User, task_id: UUID
    ) -> TaskInstance:
        """Soft-delete a task by setting hidden flag.

        T112: TaskService.soft_delete_task (FR-012)

        Args:
            user: The requesting user
            task_id: The task ID to soft-delete

        Returns:
            The soft-deleted TaskInstance
        """
        task = await self.get_task(user=user, task_id=task_id)

        task.hidden = True
        task.version += 1

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # T130: Record soft delete metric
        tier = "pro" if user.is_pro else "free"
        record_task_operation("soft_delete", tier)
        record_task_deletion("soft")

        return task

    async def hard_delete_task(
        self, user: User, task_id: UUID
    ) -> DeletionTombstone:
        """Hard-delete a task and create a tombstone for recovery.

        T113: TaskService.hard_delete_task with tombstone (FR-012)

        Args:
            user: The requesting user
            task_id: The task ID to hard-delete

        Returns:
            The created DeletionTombstone
        """
        task = await self.get_task(
            user=user, task_id=task_id, include_hidden=True, include_subtasks=True
        )

        # Serialize task data for tombstone
        entity_data = {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "estimated_duration": task.estimated_duration,
            "focus_time_seconds": task.focus_time_seconds,
            "completed": task.completed,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "completed_by": task.completed_by.value if task.completed_by else None,
            "created_at": task.created_at.isoformat(),
            "subtasks": [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "completed": s.completed,
                    "order_index": s.order_index,
                    "source": s.source.value,
                }
                for s in task.subtasks
            ],
        }

        # Manage tombstone limit (FIFO - max 3)
        await self._enforce_tombstone_limit(user.id)

        # Create tombstone
        tombstone = DeletionTombstone(
            id=uuid4(),
            user_id=user.id,
            entity_type=TombstoneEntityType.TASK,
            entity_id=task.id,
            entity_data=entity_data,
            deleted_at=datetime.now(UTC),
        )

        self.session.add(tombstone)

        # Delete subtasks first (cascade should handle this, but explicit for clarity)
        for subtask in task.subtasks:
            await self.session.delete(subtask)

        # Delete task
        await self.session.delete(task)

        await self.session.flush()

        # T130: Record hard delete metric
        tier = "pro" if user.is_pro else "free"
        record_task_operation("hard_delete", tier)
        record_task_deletion("hard")

        return tombstone

    async def _enforce_tombstone_limit(self, user_id: UUID) -> None:
        """Enforce max 3 tombstones per user (FIFO).

        Deletes oldest tombstones if limit exceeded.
        """
        # Count existing tombstones
        count_query = select(func.count()).where(
            DeletionTombstone.user_id == user_id
        )
        result = await self.session.execute(count_query)
        count = result.scalar() or 0

        if count >= MAX_TOMBSTONES_PER_USER:
            # Delete oldest tombstones to make room
            excess = count - MAX_TOMBSTONES_PER_USER + 1
            oldest_query = (
                select(DeletionTombstone)
                .where(DeletionTombstone.user_id == user_id)
                .order_by(DeletionTombstone.deleted_at.asc())
                .limit(excess)
            )
            result = await self.session.execute(oldest_query)
            oldest_tombstones = result.scalars().all()

            for tombstone in oldest_tombstones:
                await self.session.delete(tombstone)

    async def _check_auto_complete(
        self, user: User, task_id: UUID
    ) -> TaskInstance | None:
        """Check if task should be auto-completed and complete it if so.

        T114: Implement subtask auto-completion check (FR-009)

        Returns:
            The auto-completed task if triggered, None otherwise
        """
        task = await self.get_task(
            user=user, task_id=task_id, include_subtasks=True
        )

        # Task already completed or no subtasks
        if task.completed or not task.subtasks:
            return None

        # Check if all subtasks are completed
        all_completed = all(s.completed for s in task.subtasks)

        if all_completed:
            return await self.complete_task(
                user=user,
                task_id=task_id,
                completed_by=CompletedBy.AUTO,
            )

        return None

    # =========================================================================
    # SUBTASK CRUD (T115-T118)
    # =========================================================================

    async def create_subtask(
        self,
        user: User,
        task_id: UUID,
        data: SubtaskCreate,
        source: SubtaskSource = SubtaskSource.USER,
    ) -> Subtask:
        """Create a subtask with tier-based limit check.

        T115: TaskService.create_subtask with limit check (FR-019)

        Args:
            user: The requesting user
            task_id: The parent task ID
            data: Subtask creation data
            source: Creation source (user or ai)

        Returns:
            The created Subtask

        Raises:
            TaskNotFoundError: If parent task not found
            SubtaskLimitExceededError: If subtask limit reached
        """
        # Verify parent task exists and user owns it
        task = await self.get_task(user=user, task_id=task_id, include_subtasks=True)

        # Check subtask limit based on tier (using centralized limits with achievement support)
        # T133: Uses get_effective_subtask_limit which supports future achievement perks
        max_subtasks = get_effective_subtask_limit(user.tier)
        if len(task.subtasks) >= max_subtasks:
            raise SubtaskLimitExceededError(
                f"Subtask limit of {max_subtasks} reached for "
                f"{'Pro' if user.is_pro else 'Free'} tier"
            )

        # Determine order index (append at end)
        max_order = max((s.order_index for s in task.subtasks), default=-1)

        subtask = Subtask(
            id=uuid4(),
            task_id=task_id,
            title=data.title.strip(),
            completed=False,
            order_index=max_order + 1,
            source=source,
        )

        self.session.add(subtask)
        await self.session.flush()
        await self.session.refresh(subtask)

        return subtask

    async def get_subtask(
        self, user: User, subtask_id: UUID
    ) -> Subtask:
        """Get a subtask with ownership check via parent task.

        Args:
            user: The requesting user
            subtask_id: The subtask ID

        Returns:
            The Subtask

        Raises:
            SubtaskNotFoundError: If subtask not found or user doesn't own parent
        """
        query = (
            select(Subtask)
            .join(TaskInstance, Subtask.task_id == TaskInstance.id)
            .where(
                Subtask.id == subtask_id,
                TaskInstance.user_id == user.id,
            )
        )

        result = await self.session.execute(query)
        subtask = result.scalar_one_or_none()

        if subtask is None:
            raise SubtaskNotFoundError(f"Subtask {subtask_id} not found")

        return subtask

    async def update_subtask(
        self,
        user: User,
        subtask_id: UUID,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Subtask:
        """Update a subtask and check for task auto-completion.

        T116: TaskService.update_subtask

        Args:
            user: The requesting user
            subtask_id: The subtask ID
            title: New title (optional)
            completed: New completion status (optional)

        Returns:
            The updated Subtask
        """
        subtask = await self.get_subtask(user=user, subtask_id=subtask_id)

        if title is not None:
            subtask.title = title.strip()

        if completed is not None:
            subtask.completed = completed
            if completed:
                subtask.completed_at = datetime.now(UTC)
            else:
                subtask.completed_at = None

        self.session.add(subtask)
        await self.session.flush()
        await self.session.refresh(subtask)

        # Check for auto-completion if subtask was completed
        if completed is True:
            await self._check_auto_complete(user=user, task_id=subtask.task_id)
            # Refresh subtask after auto-complete since session state changed
            await self.session.refresh(subtask)

        return subtask

    async def delete_subtask(
        self, user: User, subtask_id: UUID
    ) -> None:
        """Delete a subtask and reorder remaining subtasks.

        T117: TaskService.delete_subtask with reordering

        Args:
            user: The requesting user
            subtask_id: The subtask ID to delete
        """
        subtask = await self.get_subtask(user=user, subtask_id=subtask_id)
        task_id = subtask.task_id
        deleted_order = subtask.order_index

        # Delete the subtask
        await self.session.delete(subtask)

        # Reorder remaining subtasks
        remaining_query = (
            select(Subtask)
            .where(
                Subtask.task_id == task_id,
                Subtask.order_index > deleted_order,
            )
            .order_by(Subtask.order_index.asc())
        )
        result = await self.session.execute(remaining_query)
        remaining = result.scalars().all()

        for s in remaining:
            s.order_index -= 1
            self.session.add(s)

        await self.session.flush()

    async def reorder_subtasks(
        self,
        user: User,
        task_id: UUID,
        subtask_ids: list[UUID],
    ) -> list[Subtask]:
        """Reorder subtasks to maintain gapless indices.

        T118: TaskService.reorder_subtasks (FR-020)

        Args:
            user: The requesting user
            task_id: The parent task ID
            subtask_ids: Subtask IDs in desired order

        Returns:
            The reordered subtasks
        """
        # Verify parent task
        await self.get_task(user=user, task_id=task_id)

        # Get all subtasks and verify they belong to this task
        result = await self.session.execute(
            select(Subtask).where(Subtask.task_id == task_id)
        )
        subtasks = {s.id: s for s in result.scalars().all()}

        # Verify all IDs are valid
        for sid in subtask_ids:
            if sid not in subtasks:
                raise SubtaskNotFoundError(f"Subtask {sid} not found in task")

        # Apply new order
        reordered = []
        for index, subtask_id in enumerate(subtask_ids):
            subtask = subtasks[subtask_id]
            subtask.order_index = index
            self.session.add(subtask)
            reordered.append(subtask)

        await self.session.flush()

        # Refresh all to get updated values
        for subtask in reordered:
            await self.session.refresh(subtask)

        return reordered


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_task_service(session: AsyncSession, settings: Settings) -> TaskService:
    """Get a TaskService instance."""
    return TaskService(session, settings)
