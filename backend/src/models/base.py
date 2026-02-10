"""Base model classes with common fields and behaviors.

All database models should inherit from BaseModel to get:
- UUID primary key
- created_at and updated_at timestamps
- Consistent field validation
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin providing created_at and updated_at timestamp fields.

    These timestamps are automatically managed:
    - created_at: Set once at creation time, never modified
    - updated_at: Updated on every modification
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Record creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
        nullable=False,
        description="Last update timestamp (UTC)",
    )


class BaseModel(TimestampMixin):
    """Base model for all database entities.

    Provides:
    - UUID primary key (id)
    - Automatic timestamp management
    - Consistent configuration
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique identifier",
    )

    class Config:
        """SQLModel configuration."""

        # Use enum values instead of names in JSON
        use_enum_values = True
        # Validate field assignments
        validate_assignment = True


class VersionedModel(BaseModel):
    """Base model with optimistic locking support via version field.

    Increment version on every update and check for conflicts.
    """

    version: int = Field(
        default=1,
        ge=1,
        nullable=False,
        description="Optimistic locking version (increment on each update)",
    )
