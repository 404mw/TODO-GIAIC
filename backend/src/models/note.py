"""Note model for quick capture and voice recording.

T034: Note model per data-model.md Entity 5
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import Enum as SQLAEnum

from src.models.base import BaseModel
from src.schemas.enums import TranscriptionStatus

if TYPE_CHECKING:
    from src.models.user import User


class NoteBase(SQLModel):
    """Base fields for Note model."""

    content: str = Field(
        min_length=1,
        max_length=2000,
        nullable=False,
        description="Note text content (1-2000 chars)",
    )


class Note(NoteBase, BaseModel, table=True):
    """Note database model.

    A quick-capture text or voice recording that can be converted to a task.

    Per data-model.md Entity 5.

    Constraints:
    - Max 10 notes (free tier)
    - Max 25 notes (pro tier)
    - Voice recording max 300 seconds
    - Voice transcription: Pro users only
    """

    __tablename__ = "notes"

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Note owner",
    )

    # Archive status (after task conversion)
    archived: bool = Field(
        default=False,
        nullable=False,
        description="Archived after task conversion",
    )

    # Voice recording fields (Pro only)
    voice_url: str | None = Field(
        default=None,
        description="Audio file URL (S3/R2)",
    )
    voice_duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=300,
        description="Recording duration (1-300 seconds)",
    )
    transcription_status: TranscriptionStatus | None = Field(
        default=None,
        sa_column=Column(
            SQLAEnum(TranscriptionStatus, values_callable=lambda x: [e.value for e in x]),
            nullable=True,
        ),
        description="Voice transcription state",
    )

    # Relationships
    user: "User" = Relationship(back_populates="notes")

    @property
    def is_voice_note(self) -> bool:
        """Check if this is a voice note."""
        return self.voice_url is not None
