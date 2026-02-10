"""Pydantic schemas for recurring task templates.

Phase 6: User Story 3 - Recurring Task Templates (FR-015 to FR-018)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.lib.rrule import validate_rrule, to_human_readable
from src.schemas.enums import TaskPriority


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class TemplateCreate(BaseModel):
    """Request schema for creating a recurring task template."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Template title (1-200 characters)",
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Template description",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Default priority for generated instances",
    )
    rrule: str = Field(
        ...,
        description="RFC 5545 RRULE recurrence rule (e.g., 'FREQ=DAILY;INTERVAL=1')",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Default estimated duration in minutes (1-720)",
    )

    @field_validator("rrule")
    @classmethod
    def validate_rrule_format(cls, v: str) -> str:
        """Validate that the RRULE is a valid RFC 5545 format."""
        if not validate_rrule(v):
            raise ValueError("Invalid RRULE format. Must be a valid RFC 5545 RRULE.")
        return v

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        """Strip whitespace from title."""
        return v.strip()


class TemplateUpdate(BaseModel):
    """Request schema for updating a recurring task template."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New template title",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="New template description",
    )
    priority: TaskPriority | None = Field(
        default=None,
        description="New default priority",
    )
    rrule: str | None = Field(
        default=None,
        description="New RRULE recurrence rule",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="New estimated duration in minutes",
    )
    active: bool | None = Field(
        default=None,
        description="Activate or deactivate the template",
    )
    apply_to_future_only: bool = Field(
        default=True,
        description="Only affect future instances, not existing ones (FR-018)",
    )

    @field_validator("rrule")
    @classmethod
    def validate_rrule_format(cls, v: str | None) -> str | None:
        """Validate that the RRULE is a valid RFC 5545 format."""
        if v is not None and not validate_rrule(v):
            raise ValueError("Invalid RRULE format. Must be a valid RFC 5545 RRULE.")
        return v

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str | None) -> str | None:
        """Strip whitespace from title."""
        if v is not None:
            return v.strip()
        return v


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class TemplateResponse(BaseModel):
    """Response schema for a single recurring task template."""

    id: UUID
    user_id: UUID
    title: str
    description: str
    priority: TaskPriority
    rrule: str
    rrule_description: str = Field(
        ...,
        description="Human-readable description of the recurrence pattern",
    )
    estimated_duration: int | None
    next_due: datetime | None = Field(
        description="Next scheduled instance due date (UTC)",
    )
    active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, template) -> "TemplateResponse":
        """Create response from TaskTemplate model."""
        return cls(
            id=template.id,
            user_id=template.user_id,
            title=template.title,
            description=template.description,
            priority=template.priority,
            rrule=template.rrule,
            rrule_description=to_human_readable(template.rrule),
            estimated_duration=template.estimated_duration,
            next_due=template.next_due,
            active=template.active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )


class TemplateListResponse(BaseModel):
    """Response schema for a list of templates with pagination."""

    items: list[TemplateResponse]
    total: int
    offset: int
    limit: int
    has_more: bool


class GenerateInstanceResponse(BaseModel):
    """Response schema for manual instance generation."""

    template_id: UUID
    instance_id: UUID
    title: str
    due_date: datetime | None
    message: str = Field(
        default="Instance generated successfully",
    )
