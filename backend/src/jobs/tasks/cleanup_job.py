"""Background job for activity log retention cleanup.

T360: Implement 30-day retention cleanup job (FR-053)

This job runs daily to:
- Delete activity log entries older than 30 days
- Report cleanup statistics
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.activity import ActivityLog


logger = logging.getLogger(__name__)

# Retention period in days (FR-053)
RETENTION_DAYS = 30


async def handle_activity_cleanup(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Process activity log cleanup for 30-day retention.

    T360: 30-day retention cleanup job (FR-053)

    Deletes all activity log entries older than 30 days.
    Runs daily as a scheduled background job.

    Args:
        payload: Job payload (usually empty, may contain custom retention_days)
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary with cleanup summary
    """
    retention_days = payload.get("retention_days", RETENTION_DAYS)
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)

    logger.info(
        f"Starting activity log cleanup: removing entries before {cutoff_date.isoformat()}"
    )

    try:
        # Count entries to be deleted
        count_query = select(func.count()).where(
            ActivityLog.created_at < cutoff_date
        )
        count_result = await session.execute(count_query)
        entries_to_delete = count_result.scalar() or 0

        if entries_to_delete == 0:
            logger.info("No activity log entries to clean up")
            return {
                "status": "success",
                "entries_deleted": 0,
                "cutoff_date": cutoff_date.isoformat(),
                "retention_days": retention_days,
            }

        # Delete expired entries in batches to avoid long locks
        batch_size = 1000
        total_deleted = 0

        while total_deleted < entries_to_delete:
            # Find IDs to delete in this batch
            batch_query = (
                select(ActivityLog.id)
                .where(ActivityLog.created_at < cutoff_date)
                .limit(batch_size)
            )
            batch_result = await session.execute(batch_query)
            batch_ids = [row[0] for row in batch_result.all()]

            if not batch_ids:
                break

            # Delete batch
            delete_stmt = delete(ActivityLog).where(
                ActivityLog.id.in_(batch_ids)
            )
            await session.execute(delete_stmt)
            await session.flush()

            total_deleted += len(batch_ids)

            logger.debug(
                f"Deleted batch of {len(batch_ids)} entries "
                f"({total_deleted}/{entries_to_delete} total)"
            )

        logger.info(
            f"Activity log cleanup complete: deleted {total_deleted} entries "
            f"older than {retention_days} days"
        )

        return {
            "status": "success",
            "entries_deleted": total_deleted,
            "cutoff_date": cutoff_date.isoformat(),
            "retention_days": retention_days,
        }

    except Exception as e:
        logger.error(f"Activity log cleanup failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "cutoff_date": cutoff_date.isoformat(),
            "retention_days": retention_days,
        }
