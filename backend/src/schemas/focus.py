"""Focus mode schemas for request/response validation.

Phase 16: User Story 12 - Focus Mode Tracking (FR-045)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FocusStartRequest(BaseModel):
    """Request body for starting a focus session."""

    task_id: UUID = Field(description="Task to focus on")
    focus_duration: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Optional user-set focus goal in minutes (1–FOCUS_SESSION_TIMEOUT_MINUTES). "
            "Stored as a goal only; does not trigger auto-stop."
        ),
    )


class FocusEndRequest(BaseModel):
    """Request body for ending a focus session."""

    task_id: UUID = Field(description="Task to end focus for")


class FocusSessionResponse(BaseModel):
    """Response for a focus session."""

    id: UUID = Field(description="Session ID")
    task_id: UUID = Field(description="Task being focused on")
    goal_duration_minutes: int | None = Field(
        default=None,
        description="User-set focus goal in minutes (informational only)",
    )
    started_at: datetime = Field(description="Session start time (UTC)")
    ended_at: datetime | None = Field(description="Session end time (UTC)")
    duration_seconds: int | None = Field(description="Duration in seconds")

    class Config:
        from_attributes = True
