"""Reminder schemas for request/response validation.

T050: Reminder schemas per api-specification.md Section 7
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.schemas.enums import NotificationMethod, ReminderType


class ReminderCreate(BaseModel):
    """Request body for creating a reminder.

    Per api-specification.md Section 7.1.
    """

    type: ReminderType = Field(
        description="Reminder timing type (before/after/absolute)",
    )
    offset_minutes: int | None = Field(
        default=None,
        description="Minutes offset from due date (for before/after types)",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Specific time (for absolute type)",
    )
    method: NotificationMethod = Field(
        default=NotificationMethod.IN_APP,
        description="Notification delivery method",
    )

    @model_validator(mode="after")
    def validate_reminder_type(self) -> "ReminderCreate":
        """Validate fields based on reminder type."""
        if self.type in (ReminderType.BEFORE, ReminderType.AFTER):
            if self.offset_minutes is None:
                raise ValueError(
                    f"offset_minutes required for {self.type.value} reminder type"
                )
            if self.offset_minutes <= 0:
                raise ValueError("offset_minutes must be positive")
        elif self.type == ReminderType.ABSOLUTE:
            if self.scheduled_at is None:
                raise ValueError("scheduled_at required for absolute reminder type")
        return self


class ReminderUpdate(BaseModel):
    """Request body for updating a reminder.

    Per api-specification.md Section 7.2.
    """

    offset_minutes: int | None = Field(
        default=None,
        ge=1,
        description="Minutes offset from due date",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Specific time (for absolute type)",
    )
    method: NotificationMethod | None = Field(
        default=None,
        description="Notification delivery method",
    )


class ReminderResponse(BaseModel):
    """Reminder response.

    Per api-specification.md Section 7.1 response.
    """

    id: UUID = Field(description="Reminder ID")
    task_id: UUID = Field(description="Associated task ID")
    type: ReminderType = Field(description="Reminder timing type")
    offset_minutes: int | None = Field(description="Minutes offset")
    scheduled_at: datetime = Field(description="Calculated notification time")
    method: NotificationMethod = Field(description="Notification method")
    fired: bool = Field(description="Whether notification was sent")
    fired_at: datetime | None = Field(description="When notification was sent")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True
