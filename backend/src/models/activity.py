"""Activity Log model for audit trail.

T040: ActivityLog model per data-model.md Entity 11 (FR-052)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON

from src.schemas.enums import ActivitySource, EntityType

if TYPE_CHECKING:
    from src.models.user import User


class ActivityLog(SQLModel, table=True):
    """Activity Log database model.

    Audit trail of user and system actions.

    Per data-model.md Entity 11.

    Retention: 30 days rolling window (auto-purge older entries)

    Indexed Actions:
    - task_created, task_updated, task_completed, task_deleted, task_recovered
    - subtask_created, subtask_completed
    - note_created, note_converted
    - ai_chat, ai_subtask_generation
    - subscription_created, subscription_renewed, subscription_cancelled
    """

    __tablename__ = "activity_logs"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Log entry ID",
    )

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User context",
    )

    # Entity reference
    entity_type: EntityType = Field(
        nullable=False,
        index=True,
        description="Target entity type",
    )
    entity_id: UUID = Field(
        nullable=False,
        index=True,
        description="Target entity ID",
    )

    # Action details
    action: str = Field(
        nullable=False,
        index=True,
        description="Action performed (e.g., 'task_created')",
    )
    source: ActivitySource = Field(
        nullable=False,
        description="Who initiated (user/ai/system)",
    )

    # Additional context
    extra_data: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, default=dict, nullable=False),
        description="Action-specific data (mapped to 'metadata' column in DB)",
    )
    request_id: UUID | None = Field(
        default=None,
        description="Request correlation ID",
    )

    # Timestamp (immutable)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Event timestamp (UTC)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="activity_logs")
