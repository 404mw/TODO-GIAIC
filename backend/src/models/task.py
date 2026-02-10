"""Task models for task management.

T031: TaskInstance model per data-model.md Entity 2 (FR-014)
T032: TaskTemplate model per data-model.md Entity 3 (FR-015)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel, VersionedModel
from src.schemas.enums import CompletedBy, TaskPriority

if TYPE_CHECKING:
    from src.models.reminder import Reminder
    from src.models.subtask import Subtask
    from src.models.user import User


class TaskInstanceBase(SQLModel):
    """Base fields for TaskInstance model."""

    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task name (1-200 chars)",
    )
    description: str = Field(
        default="",
        max_length=2000,  # Pro tier limit; service validates per tier
        description="Markdown-supported description (max 1000/2000 chars by tier)",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        sa_type=sa.Enum("low", "medium", "high", name="task_priority", create_type=False),
        nullable=False,
        description="Task priority level",
    )
    due_date: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        description="Task deadline (UTC)",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Time estimate in minutes (1-720)",
    )


class TaskInstance(TaskInstanceBase, VersionedModel, table=True):
    """Task Instance database model.

    A concrete task occurrence with title, description, priority,
    due date, completion status, and focus time tracking.

    Per data-model.md Entity 2.
    """

    __tablename__ = "task_instances"

    # Foreign keys
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Task owner",
    )
    template_id: UUID | None = Field(
        default=None,
        foreign_key="task_templates.id",
        index=True,
        description="Source template for recurring tasks",
    )

    # Focus time tracking
    focus_time_seconds: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Accumulated focus mode time in seconds",
    )

    # Completion tracking
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status",
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        description="Completion timestamp (UTC)",
    )
    completed_by: CompletedBy | None = Field(
        default=None,
        sa_type=sa.Enum("manual", "auto", "force", name="completed_by", create_type=False),
        description="How task was completed (manual/auto/force)",
    )

    # Soft delete and archive
    hidden: bool = Field(
        default=False,
        nullable=False,
        description="Soft-delete flag",
    )
    archived: bool = Field(
        default=False,
        nullable=False,
        description="Archive flag (readonly, not deleted)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="task_instances")
    template: Optional["TaskTemplate"] = Relationship(back_populates="instances")
    subtasks: list["Subtask"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    reminders: list["Reminder"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    @property
    def is_active(self) -> bool:
        """Check if task is active (not completed, hidden, or archived)."""
        return not self.completed and not self.hidden and not self.archived

    @property
    def can_complete(self) -> bool:
        """Check if task can be completed (not archived)."""
        return not self.archived


class TaskTemplate(BaseModel, table=True):
    """Task Template database model.

    A recurring task definition with recurrence rules that spawns task instances.

    Per data-model.md Entity 3.
    """

    __tablename__ = "task_templates"

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Template owner",
    )

    # Template fields
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Template name (1-200 chars)",
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Template description",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        sa_type=sa.Enum("low", "medium", "high", name="task_priority", create_type=False),
        nullable=False,
        description="Default priority",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Default duration in minutes (1-720)",
    )

    # Recurrence
    rrule: str = Field(
        nullable=False,
        description="Recurrence rule (RFC 5545 RRULE format)",
    )
    next_due: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        description="Next instance due date (UTC)",
    )
    active: bool = Field(
        default=True,
        nullable=False,
        description="Whether template generates instances",
    )

    # Relationships
    user: "User" = Relationship(back_populates="task_templates")
    instances: list["TaskInstance"] = Relationship(back_populates="template")
