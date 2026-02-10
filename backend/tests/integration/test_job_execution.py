"""Integration tests for job execution end-to-end.

T218: Integration test for job execution end-to-end
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from src.jobs.queue import JobQueueManager
from src.jobs.worker import JobWorker, JobMetrics
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
    settings.database_url = "postgresql+asyncpg://test:test@localhost/test"
    return settings


class TestJobQueueIntegration:
    """Integration tests for job queue operations."""

    @pytest.mark.asyncio
    async def test_enqueue_and_retrieve_job(self, mock_session, mock_settings):
        """T218: Test enqueueing and retrieving a job."""
        queue = JobQueueManager(mock_session, mock_settings)

        # Enqueue a job
        job = await queue.enqueue(
            job_type=JobType.REMINDER_FIRE,
            payload={"reminder_id": str(uuid4())},
        )

        assert job is not None
        assert job.job_type == JobType.REMINDER_FIRE
        assert job.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_complete_job_flow(self, mock_session, mock_settings):
        """T218: Test completing a job updates status."""
        queue = JobQueueManager(mock_session, mock_settings)

        # Create a job
        job = await queue.enqueue(
            job_type=JobType.STREAK_CALCULATE,
            payload={},
        )

        # Complete the job
        await queue.complete(job.id, {"result": "success"})

        # Verify execute was called to update status
        assert mock_session.execute.call_count >= 1

    @pytest.mark.asyncio
    async def test_fail_and_retry_job(self, mock_session, mock_settings):
        """T218: Test job failure triggers retry."""
        queue = JobQueueManager(mock_session, mock_settings)

        # Create a job
        job = await queue.enqueue(
            job_type=JobType.CREDIT_EXPIRE,
            payload={},
            max_attempts=3,
        )

        # Mock the job for failure handling
        mock_job = MagicMock()
        mock_job.can_retry = True
        mock_job.attempts = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        # Fail the job
        will_retry = await queue.fail(job.id, "Test error", retry=True)

        assert will_retry is True


class TestJobWorkerIntegration:
    """Integration tests for job worker."""

    def test_worker_metrics_tracking(self):
        """T218: Test worker metrics are tracked correctly."""
        metrics = JobMetrics()

        # Record successes
        metrics.record_success(1.5)
        metrics.record_success(2.0)

        assert metrics.jobs_processed == 2
        assert metrics.jobs_succeeded == 2
        assert metrics.avg_processing_time == 1.75

        # Record failure with retry
        metrics.record_failure(will_retry=True)

        assert metrics.jobs_processed == 3
        assert metrics.jobs_failed == 1
        assert metrics.jobs_retried == 1

        # Record failure without retry (dead)
        metrics.record_failure(will_retry=False)

        assert metrics.jobs_processed == 4
        assert metrics.jobs_failed == 2
        assert metrics.jobs_dead == 1

    def test_worker_handler_registration(self, mock_settings):
        """T218: Test worker handler registration."""
        worker = JobWorker(mock_settings, worker_id="test-worker")

        async def mock_handler(payload, session, settings):
            return {"status": "success"}

        worker.register_handler(JobType.REMINDER_FIRE, mock_handler)

        assert JobType.REMINDER_FIRE in worker._handlers

    def test_worker_multiple_handler_registration(self, mock_settings):
        """T218: Test registering multiple handlers at once."""
        worker = JobWorker(mock_settings, worker_id="test-worker")

        async def handler1(payload, session, settings):
            return {"status": "success"}

        async def handler2(payload, session, settings):
            return {"status": "success"}

        handlers = {
            JobType.REMINDER_FIRE: handler1,
            JobType.STREAK_CALCULATE: handler2,
        }

        worker.register_handlers(handlers)

        assert len(worker._handlers) == 2


class TestJobHandlerExecution:
    """Integration tests for job handler execution."""

    @pytest.mark.asyncio
    async def test_streak_job_handler(self, mock_session, mock_settings):
        """T218: Test streak calculation job handler execution."""
        from src.jobs.tasks.streak_job import handle_streak_calculate

        # Mock empty user list
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await handle_streak_calculate({}, mock_session, mock_settings)

        assert result["status"] == "success"
        assert result["users_processed"] == 0

    @pytest.mark.asyncio
    async def test_credit_job_handler(self, mock_session, mock_settings):
        """T218: Test credit expiration job handler execution."""
        from src.jobs.tasks.credit_job import handle_credit_expire

        # Mock empty results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        with patch(
            "src.jobs.tasks.credit_job._expire_daily_credits",
            return_value=0,
        ), patch(
            "src.jobs.tasks.credit_job._process_subscription_carryover",
            return_value={"users_processed": 0, "carried_over": 0, "expired": 0},
        ), patch(
            "src.jobs.tasks.credit_job._grant_daily_credits",
            return_value=0,
        ):
            result = await handle_credit_expire({}, mock_session, mock_settings)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_subscription_job_handler(self, mock_session, mock_settings):
        """T218: Test subscription check job handler execution."""
        from src.jobs.tasks.subscription_job import handle_subscription_check

        # Mock empty results
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await handle_subscription_check({}, mock_session, mock_settings)

        assert result["status"] == "success"


class TestJobMetricsExport:
    """Tests for job metrics export."""

    def test_metrics_to_dict(self):
        """T218: Test metrics export to dictionary."""
        metrics = JobMetrics()
        metrics.record_success(1.0)
        metrics.record_failure(will_retry=True)

        data = metrics.to_dict()

        assert "jobs_processed" in data
        assert "jobs_succeeded" in data
        assert "jobs_failed" in data
        assert "avg_processing_time_seconds" in data
        assert data["jobs_processed"] == 2
        assert data["jobs_succeeded"] == 1
        assert data["jobs_failed"] == 1
