"""Focus session model for focus mode tracking.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)

Tracks active focus sessions for accumulating focus_time_seconds on tasks.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.task import TaskInstance
    from src.models.user import User


class FocusSession(BaseModel, table=True):
    """Focus session database model.

    Tracks an active or completed focus session for a task.
    Duration is calculated on end and added to task.focus_time_seconds.
    """

    __tablename__ = "focus_sessions"

    # Foreign keys
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Session owner",
    )
    task_id: UUID = Field(
        foreign_key="task_instances.id",
        nullable=False,
        index=True,
        description="Task being focused on",
    )

    # Session timing
    started_at: datetime = Field(
        nullable=False,
        description="When the focus session started (UTC)",
    )
    ended_at: datetime | None = Field(
        default=None,
        description="When the focus session ended (UTC)",
    )
    duration_seconds: int | None = Field(
        default=None,
        ge=0,
        description="Calculated duration in seconds",
    )

    # Relationships
    user: "User" = Relationship()
    task: "TaskInstance" = Relationship()

    @property
    def is_active(self) -> bool:
        """Check if session is still active (not ended)."""
        return self.ended_at is None
