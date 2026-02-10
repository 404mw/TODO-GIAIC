"""Subtask event handlers for domain events.

T134: [US4] Implement subtask completion handler for auto-complete check

This module provides event handlers for subtask-related events:
- SubtaskCompletedHandler: Checks if task should be auto-completed (FR-009)

Event handlers follow a simple function-based pattern for ease of use.
They can be called directly from services or through a future event bus.
"""

from datetime import datetime, UTC
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.subtask import Subtask
from src.models.task import TaskInstance
from src.schemas.enums import CompletedBy

if TYPE_CHECKING:
    from src.models.user import User


# =============================================================================
# SUBTASK COMPLETION HANDLER (T134, FR-009)
# =============================================================================


async def handle_subtask_completed(
    session: AsyncSession,
    user_id: UUID,
    task_id: UUID,
) -> TaskInstance | None:
    """Handle subtask completion and check for task auto-completion.

    T134: Implement subtask completion handler for auto-complete check

    This handler is triggered when a subtask is marked as completed.
    It checks if all subtasks for the parent task are now completed,
    and if so, automatically completes the parent task.

    FR-009: When the final subtask is completed, the parent task is
    automatically marked complete with completed_by='auto'.

    Args:
        session: Database session
        user_id: The user ID (for ownership verification)
        task_id: The parent task ID to check

    Returns:
        The auto-completed TaskInstance if triggered, None otherwise

    Example:
        ```python
        # In TaskService.update_subtask after marking subtask complete:
        if completed is True:
            await handle_subtask_completed(
                session=self.session,
                user_id=user.id,
                task_id=subtask.task_id,
            )
        ```
    """
    # Get task with subtasks
    query = (
        select(TaskInstance)
        .where(
            TaskInstance.id == task_id,
            TaskInstance.user_id == user_id,
            TaskInstance.hidden == False,
        )
    )
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        return None

    # Eagerly load subtasks
    await session.refresh(task, ["subtasks"])

    # Skip if task already completed or has no subtasks
    if task.completed or not task.subtasks:
        return None

    # Check if all subtasks are completed
    all_completed = all(s.completed for s in task.subtasks)

    if not all_completed:
        return None

    # Auto-complete the task
    task.completed = True
    task.completed_at = datetime.now(UTC)
    task.completed_by = CompletedBy.AUTO
    task.version += 1

    session.add(task)
    await session.flush()
    await session.refresh(task)

    return task


async def check_auto_complete_eligibility(
    session: AsyncSession,
    task_id: UUID,
) -> dict:
    """Check if a task is eligible for auto-completion.

    Utility function to inspect auto-completion status without triggering it.

    Args:
        session: Database session
        task_id: The task ID to check

    Returns:
        Dictionary with eligibility info:
        - task_found: bool
        - task_completed: bool
        - total_subtasks: int
        - completed_subtasks: int
        - eligible_for_auto_complete: bool
    """
    query = select(TaskInstance).where(TaskInstance.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        return {
            "task_found": False,
            "task_completed": False,
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "eligible_for_auto_complete": False,
        }

    await session.refresh(task, ["subtasks"])

    total = len(task.subtasks)
    completed = sum(1 for s in task.subtasks if s.completed)
    eligible = total > 0 and completed == total and not task.completed

    return {
        "task_found": True,
        "task_completed": task.completed,
        "total_subtasks": total,
        "completed_subtasks": completed,
        "eligible_for_auto_complete": eligible,
    }


# =============================================================================
# EVENT TYPES (for future event bus integration)
# =============================================================================


class SubtaskEvent:
    """Base class for subtask events."""

    def __init__(self, subtask_id: UUID, task_id: UUID, user_id: UUID):
        self.subtask_id = subtask_id
        self.task_id = task_id
        self.user_id = user_id
        self.timestamp = datetime.now(UTC)


class SubtaskCompletedEvent(SubtaskEvent):
    """Event fired when a subtask is marked as completed.

    Used to trigger auto-completion check (FR-009).
    """

    pass


class SubtaskCreatedEvent(SubtaskEvent):
    """Event fired when a new subtask is created."""

    pass


class SubtaskDeletedEvent(SubtaskEvent):
    """Event fired when a subtask is deleted."""

    pass


class SubtasksReorderedEvent:
    """Event fired when subtasks are reordered."""

    def __init__(self, task_id: UUID, user_id: UUID, new_order: list[UUID]):
        self.task_id = task_id
        self.user_id = user_id
        self.new_order = new_order
        self.timestamp = datetime.now(UTC)
