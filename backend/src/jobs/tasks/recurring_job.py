"""Background job for recurring task instance generation.

Phase 6: User Story 3 - Recurring Task Templates (FR-016, FR-017)

T150: Implement recurring_task_generate job type
T151: Add job scheduling on task completion
T152: Add retry logic for failed generation
"""

import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.task import TaskTemplate
from src.services.recurring_service import get_recurring_service


logger = logging.getLogger(__name__)


# =============================================================================
# JOB CONFIGURATION
# =============================================================================

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = [60, 300, 900]  # 1min, 5min, 15min


@dataclass
class RecurringTaskJobPayload:
    """Payload for recurring task generation job."""

    template_id: UUID
    triggered_by_task_id: UUID | None = None
    retry_count: int = 0


# =============================================================================
# JOB HANDLER (T150)
# =============================================================================


async def handle_recurring_task_generate(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Handle recurring task generation job.

    T150: Implement recurring_task_generate job type

    This job is triggered when:
    1. A recurring task instance is completed (T151)
    2. A scheduled job runs to generate upcoming instances

    Args:
        payload: Job payload with template_id and optional metadata
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary with generation status
    """
    template_id = UUID(payload["template_id"])
    triggered_by = payload.get("triggered_by_task_id")
    retry_count = payload.get("retry_count", 0)

    logger.info(
        f"Processing recurring task generation job for template {template_id}, "
        f"retry={retry_count}"
    )

    try:
        # Get the template
        query = select(TaskTemplate).where(TaskTemplate.id == template_id)
        result = await session.execute(query)
        template = result.scalar_one_or_none()

        if template is None:
            logger.warning(f"Template {template_id} not found, skipping job")
            return {
                "status": "skipped",
                "reason": "template_not_found",
                "template_id": str(template_id),
            }

        if not template.active:
            logger.info(f"Template {template_id} is inactive, skipping generation")
            return {
                "status": "skipped",
                "reason": "template_inactive",
                "template_id": str(template_id),
            }

        # Generate next instance
        service = get_recurring_service(session, settings)
        instance = await service.generate_next_instance(template)

        if instance is None:
            logger.info(f"No more instances for template {template_id}")
            return {
                "status": "completed",
                "reason": "no_more_occurrences",
                "template_id": str(template_id),
            }

        await session.commit()

        logger.info(
            f"Generated instance {instance.id} for template {template_id}, "
            f"due={instance.due_date}"
        )

        return {
            "status": "success",
            "template_id": str(template_id),
            "instance_id": str(instance.id),
            "due_date": instance.due_date.isoformat() if instance.due_date else None,
        }

    except Exception as e:
        logger.error(
            f"Error generating recurring task for template {template_id}: {e}",
            exc_info=True,
        )

        # T152: Retry logic
        if retry_count < MAX_RETRIES:
            return {
                "status": "retry",
                "template_id": str(template_id),
                "retry_count": retry_count + 1,
                "retry_delay": RETRY_DELAY_SECONDS[retry_count],
                "error": str(e),
            }

        # Max retries exceeded
        return {
            "status": "failed",
            "template_id": str(template_id),
            "error": str(e),
            "retries_exhausted": True,
        }


# =============================================================================
# JOB SCHEDULING (T151)
# =============================================================================


def create_recurring_task_job(
    template_id: UUID,
    triggered_by_task_id: UUID | None = None,
    scheduled_at: datetime | None = None,
) -> dict[str, Any]:
    """Create a job payload for recurring task generation.

    T151: Add job scheduling on task completion

    Args:
        template_id: The template to generate from
        triggered_by_task_id: The task that triggered this generation (if completion-triggered)
        scheduled_at: When to run the job (defaults to now)

    Returns:
        Job payload dictionary ready for queue insertion
    """
    return {
        "job_type": "recurring_task_generate",
        "payload": {
            "template_id": str(template_id),
            "triggered_by_task_id": str(triggered_by_task_id) if triggered_by_task_id else None,
            "retry_count": 0,
        },
        "scheduled_at": scheduled_at or datetime.now(UTC),
        "max_retries": MAX_RETRIES,
    }


async def schedule_recurring_task_generation(
    session: AsyncSession,
    template_id: UUID,
    triggered_by_task_id: UUID | None = None,
) -> None:
    """Schedule a recurring task generation job.

    T151: Add job scheduling on task completion

    This function is called when a recurring task instance is completed
    to schedule generation of the next instance.

    Args:
        session: Database session
        template_id: The template to generate from
        triggered_by_task_id: The completed task that triggered this
    """
    from src.models.job_queue import JobQueue
    from src.schemas.enums import JobStatus, JobType

    job = JobQueue(
        job_type=JobType.RECURRING_TASK_GENERATE,
        payload={
            "template_id": str(template_id),
            "triggered_by_task_id": str(triggered_by_task_id) if triggered_by_task_id else None,
            "retry_count": 0,
        },
        status=JobStatus.PENDING,
        scheduled_at=datetime.now(UTC),
        max_retries=MAX_RETRIES,
    )

    session.add(job)
    await session.flush()

    logger.info(
        f"Scheduled recurring task generation job {job.id} for template {template_id}"
    )


# =============================================================================
# RETRY HANDLING (T152)
# =============================================================================


async def reschedule_failed_job(
    session: AsyncSession,
    job_id: UUID,
    retry_count: int,
    original_payload: dict[str, Any],
) -> None:
    """Reschedule a failed job with exponential backoff.

    T152: Add retry logic for failed generation

    Args:
        session: Database session
        job_id: The failed job ID
        retry_count: Current retry count
        original_payload: The original job payload
    """
    from src.models.job_queue import JobQueue
    from src.schemas.enums import JobStatus, JobType
    from datetime import timedelta

    if retry_count >= MAX_RETRIES:
        logger.error(f"Job {job_id} exceeded max retries, marking as failed")
        return

    delay_seconds = RETRY_DELAY_SECONDS[min(retry_count, len(RETRY_DELAY_SECONDS) - 1)]
    scheduled_at = datetime.now(UTC) + timedelta(seconds=delay_seconds)

    # Update payload with new retry count
    new_payload = {**original_payload, "retry_count": retry_count + 1}

    job = JobQueue(
        job_type=JobType.RECURRING_TASK_GENERATE,
        payload=new_payload,
        status=JobStatus.PENDING,
        scheduled_at=scheduled_at,
        max_retries=MAX_RETRIES - retry_count - 1,
    )

    session.add(job)
    await session.flush()

    logger.info(
        f"Rescheduled job for template {original_payload.get('template_id')} "
        f"at {scheduled_at} (retry {retry_count + 1})"
    )
