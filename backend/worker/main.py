"""Worker service entry point.

T205: Implement worker main.py with signal handling
T219: Implement daily job scheduler for streak, credit, subscription jobs

This module provides:
- Main entry point for the background job worker
- Signal handling for graceful shutdown
- Daily scheduled job creation (UTC 00:00)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, time as dt_time, UTC

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import get_settings, Settings
from src.jobs.queue import get_job_queue
from src.jobs.worker import create_worker
from src.schemas.enums import JobType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DailyJobScheduler:
    """Scheduler for daily jobs that run at UTC 00:00.

    T219: Daily job scheduler implementation

    Jobs scheduled:
    - streak_calculate: Calculate daily streaks
    - credit_expire: Expire/grant credits
    - subscription_check: Check subscription statuses
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the scheduler.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._running = False
        self._task: asyncio.Task | None = None
        self._engine = None
        self._session_factory = None

    async def _init_db(self) -> None:
        """Initialize database connection."""
        self._engine = create_async_engine(
            self.settings.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
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
        """Start the scheduler."""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Daily job scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._close_db()
        logger.info("Daily job scheduler stopped")

    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        await self._init_db()

        while self._running:
            try:
                # Calculate time until next UTC midnight
                now = datetime.now(UTC)
                tomorrow = (now + timedelta(days=1)).date()
                next_midnight = datetime.combine(
                    tomorrow,
                    dt_time.min,
                ).replace(tzinfo=UTC)

                seconds_until_midnight = (next_midnight - now).total_seconds()

                logger.info(
                    f"Waiting {seconds_until_midnight:.0f}s until next UTC midnight"
                )

                # Wait until midnight (or until stopped)
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(seconds_until_midnight),
                        timeout=seconds_until_midnight + 1,
                    )
                except asyncio.TimeoutError:
                    pass

                if not self._running:
                    break

                # Schedule daily jobs
                await self._schedule_daily_jobs()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retrying

    async def _schedule_daily_jobs(self) -> None:
        """Schedule all daily jobs.

        T219: Schedule streak, credit, and subscription jobs
        """
        now = datetime.now(UTC)
        logger.info(f"Scheduling daily jobs at {now}")

        async with await self._get_session() as session:
            queue = get_job_queue(session, self.settings)

            # Schedule streak calculation
            await queue.enqueue(
                job_type=JobType.STREAK_CALCULATE,
                payload={"date": now.date().isoformat()},
                scheduled_at=now,
                max_attempts=3,
            )

            # Schedule credit expiration/grant
            await queue.enqueue(
                job_type=JobType.CREDIT_EXPIRE,
                payload={"date": now.date().isoformat()},
                scheduled_at=now + timedelta(seconds=30),  # Slight delay
                max_attempts=3,
            )

            # Schedule subscription check
            await queue.enqueue(
                job_type=JobType.SUBSCRIPTION_CHECK,
                payload={"date": now.date().isoformat()},
                scheduled_at=now + timedelta(seconds=60),  # Slight delay
                max_attempts=3,
            )

            await session.commit()

        logger.info("Daily jobs scheduled successfully")


async def main() -> None:
    """Main entry point for the worker service.

    T205: Worker entry point with signal handling
    """
    settings = get_settings()

    logger.info("=" * 50)
    logger.info("Starting Perpetua Flow Worker Service")
    logger.info("=" * 50)

    # Create and start the daily scheduler
    scheduler = DailyJobScheduler(settings)
    await scheduler.start()

    # Create and start the worker
    worker = create_worker(settings)
    worker.setup_signal_handlers()

    try:
        # Run the worker (this blocks until shutdown)
        await worker.start()
    finally:
        # Clean up scheduler
        await scheduler.stop()

    logger.info("Worker service stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
        sys.exit(1)
