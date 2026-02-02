"""Background job for firing task reminders.

Phase 8: User Story 8 - Reminder System (FR-028)

T188: Implement reminder_fire job type
T189: Implement reminder scheduling in job queue
T190: Implement notification creation on reminder fire
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.models.notification import Notification
from src.models.reminder import Reminder
from src.models.task import TaskInstance
from src.schemas.enums import JobStatus, JobType, NotificationType


logger = logging.getLogger(__name__)


# =============================================================================
# JOB CONFIGURATION
# =============================================================================

MAX_RETRIES = 3
BATCH_SIZE = 100  # Process reminders in batches


# =============================================================================
# JOB HANDLER (T188)
# =============================================================================


async def process_due_reminders(
    session: AsyncSession,
    settings: Settings,
) -> int:
    """Process all due reminders and fire notifications.

    T188: Implement reminder_fire job type

    This job runs periodically (e.g., every minute) to find and fire
    reminders that are due.

    Args:
        session: Database session
        settings: Application settings

    Returns:
        Number of reminders fired
    """
    now = datetime.now(UTC)

    # Find all due reminders that haven't been fired
    # and whose tasks are not completed/hidden
    query = (
        select(Reminder)
        .join(TaskInstance, Reminder.task_id == TaskInstance.id)
        .where(
            Reminder.fired == False,
            Reminder.scheduled_at <= now,
            TaskInstance.completed == False,
            TaskInstance.hidden == False,
        )
        .limit(BATCH_SIZE)
    )

    result = await session.execute(query)
    reminders = result.scalars().all()

    if not reminders:
        logger.debug("No due reminders to process")
        return 0

    logger.info(f"Processing {len(reminders)} due reminders")

    fired_count = 0
    for reminder in reminders:
        try:
            await _fire_reminder(session, reminder)
            fired_count += 1
        except Exception as e:
            logger.error(
                f"Error firing reminder {reminder.id}: {e}",
                exc_info=True,
            )

    await session.commit()

    logger.info(f"Fired {fired_count} reminders")
    return fired_count


async def _fire_reminder(
    session: AsyncSession,
    reminder: Reminder,
) -> None:
    """Fire a single reminder and create notification.

    T190: Implement notification creation on reminder fire (FR-028)

    Args:
        session: Database session
        reminder: The reminder to fire
    """
    now = datetime.now(UTC)

    # Get the task for notification content
    task_query = select(TaskInstance).where(TaskInstance.id == reminder.task_id)
    result = await session.execute(task_query)
    task = result.scalar_one_or_none()

    if task is None:
        logger.warning(f"Task {reminder.task_id} not found for reminder {reminder.id}")
        # Mark as fired anyway to prevent reprocessing
        reminder.fired = True
        reminder.fired_at = now
        session.add(reminder)
        return

    # Create notification (FR-028)
    notification_title = "Task Reminder"
    notification_body = _build_notification_body(reminder, task)
    action_url = f"/tasks/{task.id}"

    notification = Notification(
        id=uuid4(),
        user_id=reminder.user_id,
        type=NotificationType.REMINDER,
        title=notification_title,
        body=notification_body,
        action_url=action_url,
        read=False,
        read_at=None,
    )

    session.add(notification)

    # Mark reminder as fired
    reminder.fired = True
    reminder.fired_at = now
    session.add(reminder)

    logger.info(
        f"Fired reminder {reminder.id} for task '{task.title}' "
        f"(user={reminder.user_id})"
    )


def _build_notification_body(reminder: Reminder, task: TaskInstance) -> str:
    """Build notification body text based on reminder type.

    Args:
        reminder: The reminder
        task: The associated task

    Returns:
        Notification body text
    """
    task_title = task.title
    if len(task_title) > 50:
        task_title = task_title[:47] + "..."

    reminder_type = reminder.type.value if hasattr(reminder.type, 'value') else str(reminder.type)
    if reminder_type == "before" and reminder.offset_minutes:
        if reminder.offset_minutes >= 60:
            hours = reminder.offset_minutes // 60
            if hours == 1:
                return f"'{task_title}' is due in 1 hour"
            return f"'{task_title}' is due in {hours} hours"
        return f"'{task_title}' is due in {reminder.offset_minutes} minutes"

    elif reminder_type == "after" and reminder.offset_minutes:
        if reminder.offset_minutes >= 60:
            hours = reminder.offset_minutes // 60
            if hours == 1:
                return f"'{task_title}' was due 1 hour ago"
            return f"'{task_title}' was due {hours} hours ago"
        return f"'{task_title}' was due {reminder.offset_minutes} minutes ago"

    else:  # absolute
        if task.due_date:
            return f"Reminder for '{task_title}' (due {task.due_date.strftime('%b %d at %H:%M')})"
        return f"Reminder for '{task_title}'"


# =============================================================================
# JOB SCHEDULING (T189)
# =============================================================================


async def schedule_reminder_fire_job(
    session: AsyncSession,
    reminder_id: UUID,
    scheduled_at: datetime,
) -> None:
    """Schedule a job to fire a specific reminder.

    T189: Implement reminder scheduling in job queue

    Args:
        session: Database session
        reminder_id: The reminder ID to fire
        scheduled_at: When to fire the reminder
    """
    from src.models.job_queue import JobQueue

    job = JobQueue(
        job_type=JobType.REMINDER_FIRE,
        payload={
            "reminder_id": str(reminder_id),
        },
        status=JobStatus.PENDING,
        scheduled_at=scheduled_at,
        max_retries=MAX_RETRIES,
    )

    session.add(job)
    await session.flush()

    logger.debug(f"Scheduled reminder fire job {job.id} for {scheduled_at}")


async def handle_reminder_fire_job(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Handle a scheduled reminder fire job.

    This is for individual reminder firing when using scheduled jobs
    per reminder instead of batch processing.

    Args:
        payload: Job payload with reminder_id
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary
    """
    reminder_id = UUID(payload["reminder_id"])

    logger.info(f"Processing reminder fire job for reminder {reminder_id}")

    # Get the reminder
    query = select(Reminder).where(Reminder.id == reminder_id)
    result = await session.execute(query)
    reminder = result.scalar_one_or_none()

    if reminder is None:
        logger.warning(f"Reminder {reminder_id} not found")
        return {
            "status": "skipped",
            "reason": "reminder_not_found",
            "reminder_id": str(reminder_id),
        }

    if reminder.fired:
        logger.info(f"Reminder {reminder_id} already fired")
        return {
            "status": "skipped",
            "reason": "already_fired",
            "reminder_id": str(reminder_id),
        }

    # Check if task is still valid
    task_query = select(TaskInstance).where(TaskInstance.id == reminder.task_id)
    result = await session.execute(task_query)
    task = result.scalar_one_or_none()

    if task is None or task.completed or task.hidden:
        logger.info(f"Task for reminder {reminder_id} is no longer valid")
        # Mark as fired to prevent reprocessing
        reminder.fired = True
        reminder.fired_at = datetime.now(UTC)
        session.add(reminder)
        await session.commit()
        return {
            "status": "skipped",
            "reason": "task_invalid",
            "reminder_id": str(reminder_id),
        }

    # Fire the reminder
    await _fire_reminder(session, reminder)
    await session.commit()

    return {
        "status": "success",
        "reminder_id": str(reminder_id),
        "task_id": str(reminder.task_id),
    }


# =============================================================================
# BATCH PROCESSING SCHEDULER
# =============================================================================


def create_reminder_batch_job(scheduled_at: datetime | None = None) -> dict[str, Any]:
    """Create a job payload for batch reminder processing.

    This is used for scheduling the periodic batch job that processes
    all due reminders.

    Args:
        scheduled_at: When to run the job (defaults to now)

    Returns:
        Job payload dictionary
    """
    return {
        "job_type": "reminder_fire_batch",
        "payload": {},
        "scheduled_at": scheduled_at or datetime.now(UTC),
        "max_retries": 1,  # Batch job, no retry needed
    }
