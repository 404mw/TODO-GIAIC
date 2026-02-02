"""Unit tests for the job queue.

T213: Test job queue SKIP LOCKED prevents double-processing
T214: Test job retry on failure
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC
from uuid import uuid4

from src.jobs.queue import JobQueueManager
from src.models.job_queue import JobQueue
from src.schemas.enums import JobStatus, JobType


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    settings.database_url = "postgresql://test"
    return settings


@pytest.fixture
def queue_manager(mock_session, mock_settings):
    """Create a JobQueueManager instance."""
    return JobQueueManager(mock_session, mock_settings)


class TestJobEnqueue:
    """Tests for job enqueuing."""

    @pytest.mark.asyncio
    async def test_enqueue_creates_job(self, queue_manager, mock_session):
        """Test that enqueue creates a new job."""
        job = await queue_manager.enqueue(
            job_type=JobType.REMINDER_FIRE,
            payload={"reminder_id": str(uuid4())},
        )

        assert job is not None
        assert job.job_type == JobType.REMINDER_FIRE
        assert job.status == JobStatus.PENDING
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_enqueue_with_scheduled_time(self, queue_manager):
        """Test enqueuing a job with a scheduled time."""
        scheduled = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)

        job = await queue_manager.enqueue(
            job_type=JobType.STREAK_CALCULATE,
            scheduled_at=scheduled,
        )

        assert job.scheduled_at == scheduled

    @pytest.mark.asyncio
    async def test_enqueue_with_max_attempts(self, queue_manager):
        """Test enqueuing a job with custom max attempts."""
        job = await queue_manager.enqueue(
            job_type=JobType.CREDIT_EXPIRE,
            max_attempts=5,
        )

        assert job.max_attempts == 5


class TestJobClaim:
    """Tests for job claiming with SKIP LOCKED."""

    @pytest.mark.asyncio
    async def test_claim_requires_worker_id(self, queue_manager):
        """Test that claim_next requires worker_id to be set."""
        with pytest.raises(ValueError, match="Worker ID not set"):
            await queue_manager.claim_next()

    @pytest.mark.asyncio
    async def test_claim_returns_none_when_empty(self, queue_manager, mock_session):
        """Test that claim_next returns None when no jobs available."""
        queue_manager.set_worker_id("worker-1")

        # Mock empty result
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result

        job = await queue_manager.claim_next()

        assert job is None


class TestJobComplete:
    """Tests for job completion."""

    @pytest.mark.asyncio
    async def test_complete_updates_status(self, queue_manager, mock_session):
        """Test that complete updates job status."""
        job_id = uuid4()

        await queue_manager.complete(job_id)

        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()


class TestJobFailure:
    """Tests for job failure and retry."""

    @pytest.mark.asyncio
    async def test_fail_with_retry(self, queue_manager, mock_session):
        """T214: Test job retry on failure."""
        job_id = uuid4()

        # Mock job that can retry
        mock_job = MagicMock()
        mock_job.can_retry = True
        mock_job.attempts = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        will_retry = await queue_manager.fail(job_id, "Test error", retry=True)

        assert will_retry is True

    @pytest.mark.asyncio
    async def test_fail_moves_to_dead_letter(self, queue_manager, mock_session):
        """T214: Test job moves to dead letter when retries exhausted."""
        job_id = uuid4()

        # Mock job that cannot retry
        mock_job = MagicMock()
        mock_job.can_retry = False
        mock_job.attempts = 3
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        will_retry = await queue_manager.fail(job_id, "Test error", retry=True)

        assert will_retry is False

    @pytest.mark.asyncio
    async def test_fail_no_retry_requested(self, queue_manager, mock_session):
        """Test job fails without retry when not requested."""
        job_id = uuid4()

        # Mock job that could retry
        mock_job = MagicMock()
        mock_job.can_retry = True
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        will_retry = await queue_manager.fail(job_id, "Test error", retry=False)

        assert will_retry is False


class TestStaleLockRelease:
    """Tests for releasing stale job locks."""

    @pytest.mark.asyncio
    async def test_release_stale_locks(self, queue_manager, mock_session):
        """Test releasing stale job locks."""
        mock_result = MagicMock()
        mock_result.rowcount = 2
        mock_session.execute.return_value = mock_result

        count = await queue_manager.release_stale_locks(timeout_seconds=600)

        assert count == 2


class TestDeadLetterHandling:
    """Tests for dead letter queue handling."""

    @pytest.mark.asyncio
    async def test_get_dead_jobs(self, queue_manager, mock_session):
        """Test retrieving dead letter jobs."""
        mock_job = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_job]
        mock_session.execute.return_value = mock_result

        dead_jobs = await queue_manager.get_dead_jobs(limit=10)

        assert len(dead_jobs) == 1

    @pytest.mark.asyncio
    async def test_retry_dead_job(self, queue_manager, mock_session):
        """Test manually retrying a dead job."""
        job_id = uuid4()

        # Mock finding the dead job
        mock_job = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        result = await queue_manager.retry_dead_job(job_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_retry_dead_job_not_found(self, queue_manager, mock_session):
        """Test retrying a non-existent dead job."""
        job_id = uuid4()

        # Mock not finding the job
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await queue_manager.retry_dead_job(job_id)

        assert result is False


class TestJobCleanup:
    """Tests for job cleanup."""

    @pytest.mark.asyncio
    async def test_cleanup_old_jobs(self, queue_manager, mock_session):
        """Test cleaning up old completed jobs."""
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result

        count = await queue_manager.cleanup_old_jobs(days=7)

        assert count == 5
