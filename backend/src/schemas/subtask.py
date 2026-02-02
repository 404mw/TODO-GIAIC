"""Subtask schemas for request/response validation.

T048: Subtask schemas per api-specification.md Section 5
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.schemas.enums import SubtaskSource


class SubtaskCreate(BaseModel):
    """Request body for creating a subtask.

    Per api-specification.md Section 5.1.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Subtask name (1-200 chars)",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class SubtaskUpdate(BaseModel):
    """Request body for updating a subtask.

    Per api-specification.md Section 5.2.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Subtask name",
    )
    completed: bool | None = Field(
        default=None,
        description="Completion status",
    )


class SubtaskReorderRequest(BaseModel):
    """Request body for reordering subtasks.

    Per api-specification.md Section 5.3.
    """

    subtask_ids: list[UUID] = Field(
        min_length=1,
        description="Subtask IDs in desired order",
    )


class SubtaskResponse(BaseModel):
    """Subtask response.

    Per api-specification.md Section 5.1 response.
    """

    id: UUID = Field(description="Subtask ID")
    task_id: UUID = Field(description="Parent task ID")
    title: str = Field(description="Subtask name")
    completed: bool = Field(description="Completion status")
    completed_at: datetime | None = Field(description="Completion timestamp")
    order_index: int = Field(description="Display order (0-indexed)")
    source: SubtaskSource = Field(description="Creation source (user/ai)")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        from_attributes = True


class SubtaskOrderResponse(BaseModel):
    """Response for subtask reorder operation."""

    id: UUID = Field(description="Subtask ID")
    order_index: int = Field(description="New order index")
