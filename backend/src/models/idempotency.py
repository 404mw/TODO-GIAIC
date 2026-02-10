"""Idempotency Key model for request deduplication.

T045: IdempotencyKey model per research.md Section 12 (FR-059)
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class IdempotencyKey(SQLModel, table=True):
    """Idempotency Key database model.

    Stores request idempotency keys for POST/PATCH deduplication.

    Per research.md Section 12 and FR-059.

    Client sends Idempotency-Key header with unique identifier.
    Server stores response for duplicate detection within TTL window.
    """

    __tablename__ = "idempotency_keys"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Record ID",
    )

    # Key identification
    key: str = Field(
        nullable=False,
        index=True,
        description="Client-provided idempotency key",
    )
    user_id: UUID = Field(
        nullable=False,
        index=True,
        description="User who made the request",
    )

    # Request fingerprint
    request_path: str = Field(
        nullable=False,
        description="API endpoint path",
    )
    request_method: str = Field(
        nullable=False,
        description="HTTP method (POST, PATCH)",
    )
    request_hash: str = Field(
        nullable=False,
        description="Hash of request body for conflict detection",
    )

    # Response storage
    response_status: int = Field(
        nullable=False,
        description="HTTP status code of original response",
    )
    response_body: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Serialized response body",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Request time (UTC)",
    )
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Key expiration time (UTC)",
    )

    @property
    def is_expired(self) -> bool:
        """Check if idempotency key has expired."""
        return datetime.utcnow() > self.expires_at

    class Config:
        """Model configuration."""

        # Composite unique constraint: (key, user_id)
        # Handled in migration
        pass
