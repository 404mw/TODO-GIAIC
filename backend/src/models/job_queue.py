"""Job Queue model for background processing.

T043: JobQueue model per research.md Section 4
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON

from src.schemas.enums import JobStatus, JobType


class JobQueue(SQLModel, table=True):
    """Job Queue database model.

    PostgreSQL-based job queue with SKIP LOCKED for concurrent processing.

    Per research.md Section 4.

    Job Types:
    - reminder_fire: Fire reminder notification
    - streak_calculate: Daily streak calculation (UTC 00:00)
    - credit_expire: Daily credit expiration (UTC 00:00)
    - subscription_check: Daily subscription status check
    - recurring_task_generate: Generate next recurring task instance
    """

    __tablename__ = "job_queue"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Job ID",
    )

    # Job definition
    job_type: JobType = Field(
        nullable=False,
        index=True,
        description="Type of background job",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, default=dict, nullable=False),
        description="Job-specific payload data",
    )

    # Status tracking
    status: JobStatus = Field(
        default=JobStatus.PENDING,
        nullable=False,
        index=True,
        description="Current job status",
    )

    # Scheduling
    scheduled_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When job should run (UTC)",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When job started processing (UTC)",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When job completed (UTC)",
    )

    # Retry handling
    attempts: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Number of execution attempts",
    )
    max_attempts: int = Field(
        default=3,
        ge=1,
        nullable=False,
        description="Maximum retry attempts",
    )
    last_error: str | None = Field(
        default=None,
        description="Last error message",
    )

    # Locking (for SKIP LOCKED pattern)
    locked_at: datetime | None = Field(
        default=None,
        index=True,
        description="When job was locked for processing",
    )
    locked_by: str | None = Field(
        default=None,
        description="Worker ID that locked the job",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Job creation time (UTC)",
    )

    @property
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.attempts < self.max_attempts

    @property
    def is_locked(self) -> bool:
        """Check if job is currently locked."""
        return self.locked_at is not None
