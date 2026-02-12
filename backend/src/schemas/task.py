"""Task schemas for request/response validation.

T047: Task schemas per api-specification.md Section 4 (FR-007, FR-058)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.schemas.enums import CompletedBy, TaskPriority


class TaskCreate(BaseModel):
    """Request body for creating a task.

    Per api-specification.md Section 4.3.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task name (1-200 chars)",
    )
    description: str | None = Field(
        default="",
        max_length=2000,
        description="Task description (max 1000/2000 by tier)",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority",
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task due date (UTC)",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Estimated duration in minutes (1-720)",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    """Request body for updating a task.

    Per api-specification.md Section 4.4 (FR-058 PATCH semantics).

    Omitted fields remain unchanged.
    Null explicitly clears a field (where allowed).
    Version required for optimistic locking.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task name",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Task description",
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="Task priority",
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task due date (UTC)",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Estimated duration in minutes",
    )
    completed: bool | None = Field(
        default=None,
        description="Completion status",
    )
    hidden: bool | None = Field(
        default=None,
        description="Soft-delete flag",
    )
    archived: bool | None = Field(
        default=None,
        description="Archive flag",
    )
    version: int = Field(
        ge=1,
        description="Current version for optimistic locking",
    )


class ForceCompleteRequest(BaseModel):
    """Request body for force-completing a task.

    Per api-specification.md Section 4.5.
    """

    version: int = Field(
        ge=1,
        description="Current version for optimistic locking",
    )


class TaskResponse(BaseModel):
    """Task response without nested resources.

    Per api-specification.md Section 4.1 (list view).
    """

    id: UUID = Field(description="Task ID")
    user_id: UUID = Field(description="Task owner ID")
    title: str = Field(description="Task name")
    description: str = Field(description="Task description")
    priority: TaskPriority = Field(description="Task priority")
    due_date: datetime | None = Field(description="Task due date")
    estimated_duration: int | None = Field(description="Estimated duration in minutes")
    focus_time_seconds: int = Field(description="Accumulated focus time")
    completed: bool = Field(description="Completion status")
    completed_at: datetime | None = Field(description="Completion timestamp")
    completed_by: CompletedBy | None = Field(description="How task was completed")
    hidden: bool = Field(description="Soft-delete flag")
    archived: bool = Field(description="Archive flag")
    template_id: UUID | None = Field(description="Source template ID")
    subtask_count: int = Field(default=0, description="Total subtask count")
    subtask_completed_count: int = Field(default=0, description="Completed subtasks")
    version: int = Field(description="Version for optimistic locking")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        from_attributes = True


class SubtaskInTask(BaseModel):
    """Subtask embedded in task detail response."""

    id: UUID = Field(description="Subtask ID")
    title: str = Field(description="Subtask name")
    completed: bool = Field(description="Completion status")
    completed_at: datetime | None = Field(description="Completion timestamp")
    order_index: int = Field(description="Display order")
    source: str = Field(description="Creation source (user/ai)")

    class Config:
        from_attributes = True


class ReminderInTask(BaseModel):
    """Reminder embedded in task detail response."""

    id: UUID = Field(description="Reminder ID")
    type: str = Field(description="Reminder type (before/after/absolute)")
    offset_minutes: int | None = Field(description="Minutes offset")
    scheduled_at: datetime = Field(description="Scheduled notification time")
    method: str = Field(description="Notification method")
    fired: bool = Field(description="Whether notification was sent")

    class Config:
        from_attributes = True


class TaskDetailResponse(BaseModel):
    """Task response with nested subtasks and reminders.

    Per api-specification.md Section 4.2 (detail view).
    """

    id: UUID = Field(description="Task ID")
    user_id: UUID = Field(description="Task owner ID")
    title: str = Field(description="Task name")
    description: str = Field(description="Task description")
    priority: TaskPriority = Field(description="Task priority")
    due_date: datetime | None = Field(description="Task due date")
    estimated_duration: int | None = Field(description="Estimated duration in minutes")
    focus_time_seconds: int = Field(description="Accumulated focus time")
    completed: bool = Field(description="Completion status")
    completed_at: datetime | None = Field(description="Completion timestamp")
    completed_by: CompletedBy | None = Field(description="How task was completed")
    hidden: bool = Field(description="Soft-delete flag")
    archived: bool = Field(description="Archive flag")
    template_id: UUID | None = Field(description="Source template ID")
    version: int = Field(description="Version for optimistic locking")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    subtasks: list[SubtaskInTask] = Field(
        default_factory=list,
        description="Task subtasks",
    )
    reminders: list[ReminderInTask] = Field(
        default_factory=list,
        description="Task reminders",
    )

    class Config:
        from_attributes = True


class TaskListFilters(BaseModel):
    """Query parameters for listing tasks."""

    completed: bool | None = Field(
        default=None,
        description="Filter by completion status",
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="Filter by priority",
    )
    hidden: bool = Field(
        default=False,
        description="Include hidden tasks",
    )
    due_before: datetime | None = Field(
        default=None,
        description="Tasks due before date",
    )
    due_after: datetime | None = Field(
        default=None,
        description="Tasks due after date",
    )


class UnlockedAchievementCompact(BaseModel):
    """Compact achievement info for task completion response.

    Per US9 AS4: Task completion response includes unlocked achievements.
    """

    id: str = Field(description="Achievement ID (e.g., 'tasks_5')")
    name: str = Field(description="Achievement name")
    perk_type: str | None = Field(
        default=None,
        description="Type of perk granted (max_tasks, max_notes, daily_credits)",
    )
    perk_value: int | None = Field(
        default=None,
        description="Value of the perk",
    )


class TaskCompletionResponse(BaseModel):
    """Task response after completion with any unlocked achievements.

    T305b: Per plan.md Achievement Notification Delivery.

    When a task is completed, the response includes:
    - The completed task data
    - Any achievements unlocked by this completion
    """

    task: TaskDetailResponse = Field(description="The completed task")
    unlocked_achievements: list[UnlockedAchievementCompact] = Field(
        default_factory=list,
        description="Achievements unlocked by this task completion",
    )
    streak: int = Field(
        default=0,
        description="Current streak after completion",
    )

    class Config:
        from_attributes = True
