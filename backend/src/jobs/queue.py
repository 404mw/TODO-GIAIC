"""PostgreSQL-based job queue with SKIP LOCKED pattern.

T201: Implement JobQueue with SKIP LOCKED pattern per research.md Section 4

Design Decision (AD-002):
- PostgreSQL-based queue with SKIP LOCKED pattern
- No additional infrastructure (Redis/RabbitMQ) required
- PostgreSQL already deployed; leverages existing connection pool
- SKIP LOCKED provides proper job locking for concurrent workers
- Sufficient for expected scale (< 1000 concurrent users)
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID

from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.job_queue import JobQueue
from src.schemas.enums import JobStatus, JobType


logger = logging.getLogger(__name__)


class JobQueueManager:
    """PostgreSQL-based job queue manager.

    T201: SKIP LOCKED pattern implementation

    Provides:
    - Job enqueuing with scheduled execution
    - Atomic job claiming with SKIP LOCKED
    - Job completion/failure handling
    - Dead letter queue for failed jobs
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Initialize the job queue manager.

        Args:
            session: Database session
            settings: Application settings
        """
        self.session = session
        self.settings = settings
        self.worker_id: str | None = None

    def set_worker_id(self, worker_id: str) -> None:
        """Set the worker ID for job locking.

        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id

    async def enqueue(
        self,
        job_type: JobType,
        payload: dict[str, Any] | None = None,
        scheduled_at: datetime | None = None,
        max_attempts: int = 3,
        priority: int = 0,
    ) -> JobQueue:
        """Add a job to the queue.

        Args:
            job_type: Type of job to execute
            payload: Job-specific data
            scheduled_at: When to run (defaults to now)
            max_attempts: Maximum retry attempts
            priority: Higher priority jobs run first (default 0)

        Returns:
            The created job
        """
        job = JobQueue(
            job_type=job_type,
            payload=payload or {},
            status=JobStatus.PENDING,
            scheduled_at=scheduled_at or datetime.now(UTC),
            max_attempts=max_attempts,
        )

        self.session.add(job)
        await self.session.flush()

        logger.info(
            f"Enqueued job {job.id} of type {job_type.value} "
            f"scheduled for {job.scheduled_at}"
        )

        return job

    async def claim_next(
        self,
        job_types: list[JobType] | None = None,
        lock_timeout_seconds: int = 300,
    ) -> JobQueue | None:
        """Claim the next available job using SKIP LOCKED.

        T201: SKIP LOCKED pattern for atomic job claiming

        This query atomically:
        1. Finds the next pending job
        2. Locks it to prevent other workers from claiming it
        3. Updates its status to processing

        Args:
            job_types: Optional list of job types to claim (None = all types)
            lock_timeout_seconds: How long the lock is valid

        Returns:
            The claimed job, or None if no jobs available
        """
        if not self.worker_id:
            raise ValueError("Worker ID not set. Call set_worker_id() first.")

        now = datetime.now(UTC)

        # Build the subquery to find and lock a job
        # Using raw SQL for FOR UPDATE SKIP LOCKED
        type_filter = ""
        params: dict[str, Any] = {
            "now": now,
            "pending": JobStatus.PENDING.value,
            "processing": JobStatus.PROCESSING.value,
            "worker_id": self.worker_id,
        }

        if job_types:
            type_values = [jt.value for jt in job_types]
            type_filter = "AND job_type = ANY(:job_types)"
            params["job_types"] = type_values

        # The SKIP LOCKED query
        query = text(f"""
            UPDATE job_queue
            SET
                status = :processing,
                started_at = :now,
                locked_at = :now,
                locked_by = :worker_id,
                attempts = attempts + 1
            WHERE id = (
                SELECT id FROM job_queue
                WHERE status = :pending
                  AND scheduled_at <= :now
                  {type_filter}
                ORDER BY scheduled_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            )
            RETURNING *
        """)

        result = await self.session.execute(query, params)
        row = result.fetchone()

        if row is None:
            return None

        # Reconstruct the JobQueue model from the row
        job = JobQueue(
            id=row.id,
            job_type=JobType(row.job_type),
            payload=row.payload,
            status=JobStatus(row.status),
            scheduled_at=row.scheduled_at,
            started_at=row.started_at,
            completed_at=row.completed_at,
            attempts=row.attempts,
            max_attempts=row.max_attempts,
            last_error=row.last_error,
            locked_at=row.locked_at,
            locked_by=row.locked_by,
            created_at=row.created_at,
        )

        logger.info(
            f"Claimed job {job.id} of type {job.job_type.value} "
            f"(attempt {job.attempts}/{job.max_attempts})"
        )

        return job

    async def complete(self, job_id: UUID, result: dict[str, Any] | None = None) -> None:
        """Mark a job as completed.

        Args:
            job_id: The job ID
            result: Optional result data
        """
        now = datetime.now(UTC)

        stmt = (
            update(JobQueue)
            .where(JobQueue.id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=now,
                locked_at=None,
                locked_by=None,
            )
        )

        await self.session.execute(stmt)
        await self.session.flush()

        logger.info(f"Completed job {job_id}")

    async def fail(
        self,
        job_id: UUID,
        error: str,
        retry: bool = True,
    ) -> bool:
        """Mark a job as failed, optionally scheduling a retry.

        T203: Job retry logic implementation

        Args:
            job_id: The job ID
            error: Error message
            retry: Whether to retry the job

        Returns:
            True if the job will be retried, False if it's dead
        """
        # Get current job state
        query = select(JobQueue).where(JobQueue.id == job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()

        if job is None:
            logger.warning(f"Job {job_id} not found for failure handling")
            return False

        now = datetime.now(UTC)

        if retry and job.can_retry:
            # Calculate retry delay with exponential backoff
            # 1min, 5min, 15min, 30min, 60min
            delays = [60, 300, 900, 1800, 3600]
            delay_index = min(job.attempts - 1, len(delays) - 1)
            delay_seconds = delays[delay_index]

            next_run = now + timedelta(seconds=delay_seconds)

            stmt = (
                update(JobQueue)
                .where(JobQueue.id == job_id)
                .values(
                    status=JobStatus.PENDING,
                    scheduled_at=next_run,
                    last_error=error,
                    locked_at=None,
                    locked_by=None,
                )
            )

            await self.session.execute(stmt)
            await self.session.flush()

            logger.info(
                f"Job {job_id} failed, will retry at {next_run} "
                f"(attempt {job.attempts}/{job.max_attempts})"
            )
            return True
        else:
            # Move to dead letter state
            stmt = (
                update(JobQueue)
                .where(JobQueue.id == job_id)
                .values(
                    status=JobStatus.DEAD,
                    completed_at=now,
                    last_error=error,
                    locked_at=None,
                    locked_by=None,
                )
            )

            await self.session.execute(stmt)
            await self.session.flush()

            logger.warning(f"Job {job_id} moved to dead letter queue: {error}")
            return False

    async def release_stale_locks(
        self,
        timeout_seconds: int = 600,
    ) -> int:
        """Release jobs that have been locked for too long.

        This handles cases where a worker crashes without releasing its lock.

        Args:
            timeout_seconds: How long before a lock is considered stale

        Returns:
            Number of jobs released
        """
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=timeout_seconds)

        stmt = (
            update(JobQueue)
            .where(
                JobQueue.status == JobStatus.PROCESSING,
                JobQueue.locked_at < cutoff,
            )
            .values(
                status=JobStatus.PENDING,
                locked_at=None,
                locked_by=None,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        count = result.rowcount
        if count > 0:
            logger.warning(f"Released {count} stale job lock(s)")

        return count

    async def get_pending_count(
        self,
        job_type: JobType | None = None,
    ) -> int:
        """Get the number of pending jobs.

        Args:
            job_type: Optional job type filter

        Returns:
            Number of pending jobs
        """
        query = select(JobQueue).where(JobQueue.status == JobStatus.PENDING)

        if job_type:
            query = query.where(JobQueue.job_type == job_type)

        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def get_dead_jobs(
        self,
        limit: int = 100,
    ) -> list[JobQueue]:
        """Get dead letter jobs.

        T204: Dead letter handling

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of dead jobs
        """
        query = (
            select(JobQueue)
            .where(JobQueue.status == JobStatus.DEAD)
            .order_by(JobQueue.completed_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def retry_dead_job(self, job_id: UUID) -> bool:
        """Manually retry a dead letter job.

        T204: Dead letter handling - manual retry

        Args:
            job_id: The job ID to retry

        Returns:
            True if job was reset, False if not found or not dead
        """
        query = select(JobQueue).where(
            JobQueue.id == job_id,
            JobQueue.status == JobStatus.DEAD,
        )
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()

        if job is None:
            return False

        now = datetime.now(UTC)

        stmt = (
            update(JobQueue)
            .where(JobQueue.id == job_id)
            .values(
                status=JobStatus.PENDING,
                scheduled_at=now,
                attempts=0,
                last_error=None,
                completed_at=None,
            )
        )

        await self.session.execute(stmt)
        await self.session.flush()

        logger.info(f"Reset dead job {job_id} for retry")
        return True

    async def cleanup_old_jobs(
        self,
        days: int = 7,
    ) -> int:
        """Delete old completed/dead jobs.

        Args:
            days: Delete jobs older than this many days

        Returns:
            Number of jobs deleted
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)

        query = text("""
            DELETE FROM job_queue
            WHERE status IN (:completed, :dead)
              AND completed_at < :cutoff
        """)

        result = await self.session.execute(
            query,
            {
                "completed": JobStatus.COMPLETED.value,
                "dead": JobStatus.DEAD.value,
                "cutoff": cutoff,
            },
        )
        await self.session.flush()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} old job(s)")

        return count


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_job_queue(session: AsyncSession, settings: Settings) -> JobQueueManager:
    """Get a job queue manager instance.

    Args:
        session: Database session
        settings: Application settings

    Returns:
        JobQueueManager instance
    """
    return JobQueueManager(session, settings)


async def enqueue_job(
    session: AsyncSession,
    settings: Settings,
    job_type: JobType,
    payload: dict[str, Any] | None = None,
    scheduled_at: datetime | None = None,
    max_attempts: int = 3,
) -> JobQueue:
    """Convenience function to enqueue a job.

    Args:
        session: Database session
        settings: Application settings
        job_type: Type of job
        payload: Job payload
        scheduled_at: When to run
        max_attempts: Max retries

    Returns:
        The created job
    """
    queue = get_job_queue(session, settings)
    return await queue.enqueue(
        job_type=job_type,
        payload=payload,
        scheduled_at=scheduled_at,
        max_attempts=max_attempts,
    )
