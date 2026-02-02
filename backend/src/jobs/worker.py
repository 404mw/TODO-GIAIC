"""Background job worker implementation.

T202: Implement job worker with polling
T203: Implement job retry logic with max_retries
T204: Implement dead letter handling for failed jobs
T220: Add job monitoring metrics
"""

import asyncio
import logging
import signal
import uuid
from datetime import datetime, UTC
from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import Settings, get_settings
from src.jobs.queue import JobQueueManager
from src.models.job_queue import JobQueue
from src.schemas.enums import JobStatus, JobType


logger = logging.getLogger(__name__)


# Type for job handlers
JobHandler = Callable[[dict[str, Any], AsyncSession, Settings], Coroutine[Any, Any, dict[str, Any]]]


class JobMetrics:
    """Simple in-memory job metrics.

    T220: Job monitoring metrics
    """

    def __init__(self) -> None:
        """Initialize metrics."""
        self.jobs_processed: int = 0
        self.jobs_succeeded: int = 0
        self.jobs_failed: int = 0
        self.jobs_retried: int = 0
        self.jobs_dead: int = 0
        self.last_job_at: datetime | None = None
        self.processing_times: list[float] = []

    def record_success(self, duration_seconds: float) -> None:
        """Record a successful job."""
        self.jobs_processed += 1
        self.jobs_succeeded += 1
        self.last_job_at = datetime.now(UTC)
        self._record_duration(duration_seconds)

    def record_failure(self, will_retry: bool) -> None:
        """Record a failed job."""
        self.jobs_processed += 1
        self.jobs_failed += 1
        self.last_job_at = datetime.now(UTC)
        if will_retry:
            self.jobs_retried += 1
        else:
            self.jobs_dead += 1

    def _record_duration(self, duration: float) -> None:
        """Record processing duration (keep last 100)."""
        self.processing_times.append(duration)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)

    @property
    def avg_processing_time(self) -> float:
        """Get average processing time in seconds."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    def to_dict(self) -> dict[str, Any]:
        """Export metrics as dictionary."""
        return {
            "jobs_processed": self.jobs_processed,
            "jobs_succeeded": self.jobs_succeeded,
            "jobs_failed": self.jobs_failed,
            "jobs_retried": self.jobs_retried,
            "jobs_dead": self.jobs_dead,
            "avg_processing_time_seconds": round(self.avg_processing_time, 3),
            "last_job_at": self.last_job_at.isoformat() if self.last_job_at else None,
        }


class JobWorker:
    """Background job worker.

    T202: Job worker with polling implementation

    This worker:
    - Polls the job queue for available jobs
    - Executes jobs using registered handlers
    - Handles retries and dead lettering
    - Supports graceful shutdown
    """

    def __init__(
        self,
        settings: Settings,
        worker_id: str | None = None,
        poll_interval: float = 1.0,
        batch_size: int = 1,
    ) -> None:
        """Initialize the worker.

        Args:
            settings: Application settings
            worker_id: Unique identifier for this worker
            poll_interval: Seconds between queue polls
            batch_size: Number of jobs to claim per poll
        """
        self.settings = settings
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.poll_interval = poll_interval
        self.batch_size = batch_size

        self._handlers: dict[JobType, JobHandler] = {}
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._engine = None
        self._session_factory = None
        self.metrics = JobMetrics()

    def register_handler(self, job_type: JobType, handler: JobHandler) -> None:
        """Register a handler for a job type.

        Args:
            job_type: The job type to handle
            handler: Async function to process the job
        """
        self._handlers[job_type] = handler
        logger.info(f"Registered handler for {job_type.value}")

    def register_handlers(self, handlers: dict[JobType, JobHandler]) -> None:
        """Register multiple handlers at once.

        Args:
            handlers: Mapping of job types to handlers
        """
        for job_type, handler in handlers.items():
            self.register_handler(job_type, handler)

    async def _init_db(self) -> None:
        """Initialize database connection."""
        self._engine = create_async_engine(
            self.settings.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        self._session_factory = sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def _close_db(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()

    async def _get_session(self) -> AsyncSession:
        """Get a database session."""
        if not self._session_factory:
            await self._init_db()
        return self._session_factory()

    async def start(self) -> None:
        """Start the worker.

        T202: Main polling loop implementation
        """
        logger.info(f"Starting worker {self.worker_id}")
        self._running = True

        try:
            await self._init_db()
            await self._run_loop()
        finally:
            await self._close_db()
            logger.info(f"Worker {self.worker_id} stopped")

    async def stop(self) -> None:
        """Stop the worker gracefully."""
        logger.info(f"Stopping worker {self.worker_id}")
        self._running = False
        self._shutdown_event.set()

    async def _run_loop(self) -> None:
        """Main worker loop."""
        while self._running:
            try:
                # Release stale locks periodically
                async with await self._get_session() as session:
                    queue = JobQueueManager(session, self.settings)
                    await queue.release_stale_locks()
                    await session.commit()

                # Process jobs
                jobs_processed = await self._poll_and_process()

                # If no jobs, wait before polling again
                if jobs_processed == 0:
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(),
                            timeout=self.poll_interval,
                        )
                    except asyncio.TimeoutError:
                        pass

            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    async def _poll_and_process(self) -> int:
        """Poll for jobs and process them.

        Returns:
            Number of jobs processed
        """
        processed = 0

        for _ in range(self.batch_size):
            async with await self._get_session() as session:
                queue = JobQueueManager(session, self.settings)
                queue.set_worker_id(self.worker_id)

                job = await queue.claim_next()

                if job is None:
                    break

                try:
                    await self._process_job(job, session, queue)
                    processed += 1
                except Exception as e:
                    logger.error(
                        f"Error processing job {job.id}: {e}",
                        exc_info=True,
                    )

                await session.commit()

        return processed

    async def _process_job(
        self,
        job: JobQueue,
        session: AsyncSession,
        queue: JobQueueManager,
    ) -> None:
        """Process a single job.

        T203: Retry logic implementation
        T204: Dead letter handling

        Args:
            job: The job to process
            session: Database session
            queue: Job queue manager
        """
        handler = self._handlers.get(job.job_type)

        if handler is None:
            logger.error(f"No handler registered for job type {job.job_type.value}")
            await queue.fail(
                job.id,
                f"No handler for job type: {job.job_type.value}",
                retry=False,
            )
            self.metrics.record_failure(will_retry=False)
            return

        start_time = datetime.now(UTC)

        try:
            logger.info(f"Processing job {job.id} ({job.job_type.value})")

            # Execute the handler
            result = await handler(job.payload, session, self.settings)

            # Check result for special statuses
            status = result.get("status", "success")

            if status == "success":
                await queue.complete(job.id, result)
                duration = (datetime.now(UTC) - start_time).total_seconds()
                self.metrics.record_success(duration)
                logger.info(f"Job {job.id} completed successfully")

            elif status == "retry":
                # Handler explicitly requested retry
                await queue.fail(
                    job.id,
                    result.get("error", "Handler requested retry"),
                    retry=True,
                )
                self.metrics.record_failure(will_retry=True)

            elif status == "skipped":
                # Job was skipped (not an error)
                await queue.complete(job.id, result)
                duration = (datetime.now(UTC) - start_time).total_seconds()
                self.metrics.record_success(duration)
                logger.info(f"Job {job.id} skipped: {result.get('reason')}")

            else:
                # Unknown status, treat as failure
                await queue.fail(
                    job.id,
                    result.get("error", f"Unknown status: {status}"),
                    retry=True,
                )
                self.metrics.record_failure(will_retry=True)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job.id} failed with error: {error_msg}")

            will_retry = await queue.fail(job.id, error_msg, retry=True)
            self.metrics.record_failure(will_retry=will_retry)

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown.

        T205: Signal handling for worker
        """
        loop = asyncio.get_event_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._handle_signal, sig)
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                signal.signal(sig, self._handle_signal_sync)

    def _handle_signal(self, sig: signal.Signals) -> None:
        """Handle shutdown signal (Unix)."""
        logger.info(f"Received signal {sig.name}, shutting down...")
        asyncio.create_task(self.stop())

    def _handle_signal_sync(self, sig: int, frame: Any) -> None:
        """Handle shutdown signal (Windows)."""
        logger.info(f"Received signal {sig}, shutting down...")
        self._running = False
        self._shutdown_event.set()


# =============================================================================
# WORKER FACTORY
# =============================================================================


def create_worker(
    settings: Settings | None = None,
    worker_id: str | None = None,
    poll_interval: float = 1.0,
) -> JobWorker:
    """Create a configured job worker.

    Args:
        settings: Application settings
        worker_id: Unique worker identifier
        poll_interval: Polling interval in seconds

    Returns:
        Configured JobWorker instance
    """
    if settings is None:
        settings = get_settings()

    worker = JobWorker(
        settings=settings,
        worker_id=worker_id,
        poll_interval=poll_interval,
    )

    # Register all job handlers
    from src.jobs.tasks import get_all_handlers
    worker.register_handlers(get_all_handlers())

    return worker


async def run_worker(
    settings: Settings | None = None,
    worker_id: str | None = None,
) -> None:
    """Run a job worker (blocking).

    Args:
        settings: Application settings
        worker_id: Unique worker identifier
    """
    worker = create_worker(settings, worker_id)
    worker.setup_signal_handlers()
    await worker.start()
