"""Deletion Tombstone model for task recovery.

T041: DeletionTombstone model per data-model.md Entity 12 (FR-062)
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON

from src.schemas.enums import TombstoneEntityType

if TYPE_CHECKING:
    from src.models.user import User


class DeletionTombstone(SQLModel, table=True):
    """Deletion Tombstone database model.

    Serialized deleted entity for recovery.

    Per data-model.md Entity 12.

    Constraints:
    - Max 3 tombstones per user (FIFO - oldest dropped on 4th deletion)
    - Recovered tasks restore original ID and timestamps
    - Recovered tasks do NOT trigger achievements or affect streaks
    """

    __tablename__ = "deletion_tombstones"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Tombstone ID",
    )

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Data owner",
    )

    # Entity reference
    entity_type: TombstoneEntityType = Field(
        nullable=False,
        description="Deleted entity type (task/note)",
    )
    entity_id: UUID = Field(
        nullable=False,
        description="Original entity ID",
    )

    # Serialized data
    entity_data: dict = Field(
        sa_column=Column(JSON, nullable=False),
        description="Serialized entity state",
    )

    # Deletion timestamp (immutable)
    deleted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
        description="Deletion time (UTC)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="tombstones")
