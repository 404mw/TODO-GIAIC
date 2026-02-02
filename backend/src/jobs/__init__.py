"""Background job system for async processing.

This module provides:
- PostgreSQL-based job queue with SKIP LOCKED pattern
- Job worker with polling, retry logic, and dead letter handling
- All 5 job types: reminder, streak, credit, subscription, recurring
"""

# Job queue
from src.jobs.queue import (
    JobQueueManager,
    enqueue_job,
    get_job_queue,
)

# Job worker
from src.jobs.worker import (
    JobMetrics,
    JobWorker,
    create_worker,
    run_worker,
)

# Job handlers
from src.jobs.tasks import (
    # Handler registry
    JobHandler,
    get_all_handlers,
    # Recurring task job
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    RecurringTaskJobPayload,
    create_recurring_task_job,
    handle_recurring_task_generate,
    reschedule_failed_job,
    schedule_recurring_task_generation,
    # Reminder job
    create_reminder_batch_job,
    handle_reminder_fire_job,
    process_due_reminders,
    schedule_reminder_fire_job,
    # Streak job
    calculate_user_streak,
    handle_streak_calculate,
    # Credit job
    grant_kickstart_credits,
    handle_credit_expire,
    # Subscription job
    handle_payment_failed,
    handle_payment_success,
    handle_subscription_check,
)

__all__ = [
    # Queue
    "JobQueueManager",
    "enqueue_job",
    "get_job_queue",
    # Worker
    "JobMetrics",
    "JobWorker",
    "create_worker",
    "run_worker",
    # Handler registry
    "JobHandler",
    "get_all_handlers",
    # Recurring task job
    "MAX_RETRIES",
    "RETRY_DELAY_SECONDS",
    "RecurringTaskJobPayload",
    "create_recurring_task_job",
    "handle_recurring_task_generate",
    "reschedule_failed_job",
    "schedule_recurring_task_generation",
    # Reminder job
    "create_reminder_batch_job",
    "handle_reminder_fire_job",
    "process_due_reminders",
    "schedule_reminder_fire_job",
    # Streak job
    "calculate_user_streak",
    "handle_streak_calculate",
    # Credit job
    "grant_kickstart_credits",
    "handle_credit_expire",
    # Subscription job
    "handle_payment_failed",
    "handle_payment_success",
    "handle_subscription_check",
]
