"""Authentication models for session management.

T044: RefreshToken model per authentication.md
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.user import User


class RefreshToken(SQLModel, table=True):
    """Refresh Token database model.

    Stores refresh tokens for JWT token rotation.

    Per authentication.md and plan.md AD-001.

    Token rotation: Each refresh issues new access + refresh tokens.
    Old refresh token is invalidated after use.
    """

    __tablename__ = "refresh_tokens"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Token ID",
    )

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Token owner",
    )

    # Token data
    token_hash: str = Field(
        nullable=False,
        unique=True,
        index=True,
        description="SHA-256 hash of the refresh token",
    )

    # Expiration
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Token expiration time (UTC)",
    )

    # Revocation (revoked_at IS NULL = not revoked)
    revoked_at: datetime | None = Field(
        default=None,
        description="When token was revoked (UTC)",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Token creation time (UTC)",
    )

    # NOTE: The following fields are in the design docs but not yet in the database migration
    # TODO: Create migration to add these fields:
    # - device_info: str | None (User agent or device identifier)
    # - ip_address: str | None (Client IP address)
    # - last_used_at: datetime | None (Last time token was used)

    # Relationships
    user: "User" = Relationship(back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)."""
        if self.revoked_at is not None:
            return False
        return datetime.utcnow() < self.expires_at
