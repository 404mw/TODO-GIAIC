"""AISessionCounter model for DB-backed per-session AI request counting.

Task 4.3a: Replace in-memory _task_request_counters with DB-backed table
for multi-process safety (NFR-004 Horizontal Scaling).
"""

from datetime import datetime, timedelta, UTC
from uuid import UUID

from sqlmodel import Field, SQLModel


class AISessionCounter(SQLModel, table=True):
    """Tracks per-session, per-task AI request counts in the database.

    Replaces the in-memory _task_request_counters dict in AIService.
    Shared across all app instances via the database, enabling horizontal scaling.

    Composite unique constraint on (session_id, task_id) enables atomic upsert.
    Counters expire 24 hours after creation to prevent unbounded table growth.
    """

    __tablename__ = "ai_session_counters"

    # Integer PK for efficient upsert (no UUID overhead needed)
    id: int | None = Field(default=None, primary_key=True)

    # session_id comes from JWT `jti` claim (unique per login session)
    session_id: str = Field(
        nullable=False,
        index=True,
        description="JWT jti claim identifying the user session",
    )
    task_id: UUID = Field(
        nullable=False,
        index=True,
        description="Task ID being rate-limited",
    )
    count: int = Field(
        default=0,
        nullable=False,
        description="Number of AI requests made in this session for this task",
    )
    expires_at: datetime = Field(
        nullable=False,
        description="Counter expiry timestamp (24h from creation, UTC)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Counter creation timestamp (UTC)",
    )

    # Unique constraint (session_id, task_id) is defined in the migration
    # to keep model code clean and consistent with other models.

    @classmethod
    def expiry(cls) -> datetime:
        """Return a 24-hour expiry timestamp from now."""
        return datetime.now(UTC) + timedelta(hours=24)
