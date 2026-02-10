"""Background job task handlers.

All 5 job types per plan.md Background Job Types section:
- reminder_fire: Fire reminder notification (T207)
- streak_calculate: Daily streak calculation at UTC 00:00 (T208)
- credit_expire: Daily credit expiration at UTC 00:00 (T209)
- subscription_check: Daily subscription status check (T210)
- recurring_task_generate: Generate next recurring task instance (T211)
"""

from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.schemas.enums import JobType

# Import all job handlers
from src.jobs.tasks.recurring_job import (
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    RecurringTaskJobPayload,
    create_recurring_task_job,
    handle_recurring_task_generate,
    reschedule_failed_job,
    schedule_recurring_task_generation,
)
from src.jobs.tasks.reminder_job import (
    create_reminder_batch_job,
    handle_reminder_fire_job,
    process_due_reminders,
    schedule_reminder_fire_job,
)
from src.jobs.tasks.streak_job import (
    calculate_user_streak,
    handle_streak_calculate,
)
from src.jobs.tasks.credit_job import (
    grant_kickstart_credits,
    handle_credit_expire,
)
from src.jobs.tasks.subscription_job import (
    handle_payment_failed,
    handle_payment_success,
    handle_subscription_check,
)


# Type alias for job handlers
JobHandler = Callable[[dict[str, Any], AsyncSession, Settings], Coroutine[Any, Any, dict[str, Any]]]


def get_all_handlers() -> dict[JobType, JobHandler]:
    """Get all job handlers mapped by job type.

    Returns:
        Dictionary mapping JobType to handler function
    """
    return {
        JobType.REMINDER_FIRE: handle_reminder_fire_job,
        JobType.STREAK_CALCULATE: handle_streak_calculate,
        JobType.CREDIT_EXPIRE: handle_credit_expire,
        JobType.SUBSCRIPTION_CHECK: handle_subscription_check,
        JobType.RECURRING_TASK_GENERATE: handle_recurring_task_generate,
    }


__all__ = [
    # Handler registry
    "get_all_handlers",
    "JobHandler",
    # Recurring task job (T211)
    "MAX_RETRIES",
    "RETRY_DELAY_SECONDS",
    "RecurringTaskJobPayload",
    "create_recurring_task_job",
    "handle_recurring_task_generate",
    "reschedule_failed_job",
    "schedule_recurring_task_generation",
    # Reminder job (T207)
    "create_reminder_batch_job",
    "handle_reminder_fire_job",
    "process_due_reminders",
    "schedule_reminder_fire_job",
    # Streak job (T208)
    "calculate_user_streak",
    "handle_streak_calculate",
    # Credit job (T209)
    "grant_kickstart_credits",
    "handle_credit_expire",
    # Subscription job (T210)
    "handle_payment_failed",
    "handle_payment_success",
    "handle_subscription_check",
]
