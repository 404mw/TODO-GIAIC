"""Note schemas for request/response validation.

T049: Note schemas per api-specification.md Section 6
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from src.schemas.enums import TranscriptionStatus, TaskPriority


class NoteCreate(BaseModel):
    """Request body for creating a note.

    Per api-specification.md Section 6.2.
    """

    content: str = Field(
        min_length=1,
        max_length=2000,
        description="Note text content (1-2000 chars)",
    )
    voice_url: str | None = Field(
        default=None,
        description="Audio file URL (Pro only)",
    )
    voice_duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=300,
        description="Recording duration in seconds (1-300, Pro only)",
    )

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()

    @model_validator(mode="after")
    def voice_fields_together(self) -> "NoteCreate":
        """Ensure voice fields are provided together."""
        has_url = self.voice_url is not None
        has_duration = self.voice_duration_seconds is not None
        if has_url != has_duration:
            raise ValueError(
                "voice_url and voice_duration_seconds must be provided together"
            )
        return self


class NoteUpdate(BaseModel):
    """Request body for updating a note.

    Per api-specification.md Section 6 (PATCH).
    """

    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="Note text content",
    )


class NoteResponse(BaseModel):
    """Note response.

    Per api-specification.md Section 6.1.
    """

    id: UUID = Field(description="Note ID")
    content: str = Field(description="Note text content")
    archived: bool = Field(description="Whether note is archived")
    voice_url: str | None = Field(description="Audio file URL")
    voice_duration_seconds: int | None = Field(description="Recording duration")
    transcription_status: TranscriptionStatus | None = Field(
        description="Voice transcription status"
    )
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        from_attributes = True


class NoteListFilters(BaseModel):
    """Query parameters for listing notes."""

    archived: bool = Field(
        default=False,
        description="Include archived notes",
    )


class SubtaskSuggestion(BaseModel):
    """AI-suggested subtask from note conversion."""

    title: str = Field(
        max_length=200,
        description="Suggested subtask title",
    )


class TaskSuggestion(BaseModel):
    """AI-suggested task from note conversion.

    Per api-specification.md Section 6.3.
    """

    title: str = Field(description="Suggested task title")
    description: str | None = Field(
        default=None,
        description="Suggested task description",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Suggested priority",
    )
    due_date: datetime | None = Field(
        default=None,
        description="Suggested due date",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Estimated duration in minutes",
    )
    subtasks: list[SubtaskSuggestion] = Field(
        default_factory=list,
        description="Suggested subtasks (max 4)",
    )


class NoteConvertResponse(BaseModel):
    """Response for note conversion to task.

    Per api-specification.md Section 6.3.
    T259: Response schema for POST /api/v1/notes/:id/convert
    """

    task_suggestion: TaskSuggestion = Field(
        description="AI-suggested task details"
    )
    note_understanding: str = Field(
        description="AI's understanding of the note content",
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="AI confidence in the conversion (0-1)",
    )
    credits_used: int = Field(
        description="Credits consumed for conversion",
    )
    credits_remaining: int = Field(
        description="Remaining AI credits after conversion",
    )
