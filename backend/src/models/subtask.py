"""Subtask model for task child items.

T033: Subtask model per data-model.md Entity 4 (FR-021)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import SubtaskSource

if TYPE_CHECKING:
    from src.models.task import TaskInstance


class SubtaskBase(SQLModel):
    """Base fields for Subtask model."""

    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Subtask name (1-200 chars)",
    )


class Subtask(SubtaskBase, BaseModel, table=True):
    """Subtask database model.

    A child item of a task with title, completion status, and ordering.

    Per data-model.md Entity 4.

    Constraints:
    - Max 4 subtasks per task (free tier)
    - Max 10 subtasks per task (pro tier)
    - order_index must be gapless (0, 1, 2, ...)
    """

    __tablename__ = "subtasks"

    # Foreign key
    task_id: UUID = Field(
        foreign_key="task_instances.id",
        nullable=False,
        index=True,
        description="Parent task",
    )

    # Completion tracking
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Completion timestamp (UTC)",
    )

    # Ordering
    order_index: int = Field(
        ge=0,
        nullable=False,
        description="Display order (0-indexed, gapless)",
    )

    # Source tracking (FR-021)
    source: SubtaskSource = Field(
        default=SubtaskSource.USER,
        nullable=False,
        description="Creation source (user or ai)",
    )

    # Relationships
    task: "TaskInstance" = Relationship(back_populates="subtasks")
