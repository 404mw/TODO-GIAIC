"""Reminder model for task notifications.

T035: Reminder model per data-model.md Entity 6 (FR-025)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import NotificationMethod, ReminderType

if TYPE_CHECKING:
    from src.models.task import TaskInstance
    from src.models.user import User


class ReminderBase(SQLModel):
    """Base fields for Reminder model."""

    type: ReminderType = Field(
        sa_type=sa.Enum("before", "after", "absolute", name="reminder_type", create_type=False),
        nullable=False,
        description="Reminder timing type (before/after/absolute)",
    )
    offset_minutes: int | None = Field(
        default=None,
        description="Minutes before/after due date (can be negative for 'before')",
    )
    method: NotificationMethod = Field(
        default=NotificationMethod.IN_APP,
        sa_type=sa.Enum("push", "in_app", name="notification_method", create_type=False),
        nullable=False,
        description="Notification delivery method",
    )


class Reminder(ReminderBase, BaseModel, table=True):
    """Reminder database model.

    A scheduled notification tied to a task's due date.

    Per data-model.md Entity 6.

    Constraints:
    - Max 5 reminders per task
    - Relative reminders recalculate when task due date changes
    - Recovered tasks do NOT retroactively fire past reminders
    """

    __tablename__ = "reminders"

    # Foreign keys
    task_id: UUID = Field(
        foreign_key="task_instances.id",
        nullable=False,
        index=True,
        description="Associated task",
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Reminder owner",
    )

    # Scheduled time (calculated from task due_date and offset)
    scheduled_at: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        description="Calculated notification time (UTC)",
    )

    # Firing status
    fired: bool = Field(
        default=False,
        nullable=False,
        description="Whether notification was sent",
    )
    fired_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        description="When notification was sent (UTC)",
    )

    # Relationships
    task: "TaskInstance" = Relationship(back_populates="reminders")
    user: "User" = Relationship(back_populates="reminders")
