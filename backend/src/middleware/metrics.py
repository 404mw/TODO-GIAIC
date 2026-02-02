"""Prometheus metrics middleware for observability (FR-066).

Exposes metrics for:
- Request latency (histogram)
- Request count by status code
- Error rates
- Active requests (gauge)
"""

import time
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

# =============================================================================
# METRICS DEFINITIONS
# =============================================================================

# Request latency histogram (p50, p90, p95, p99)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=["method", "path", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Request counter by status code
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "path", "status_code"],
)

# Error counter (4xx and 5xx)
ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors (4xx and 5xx)",
    labelnames=["method", "path", "status_code"],
)

# Active requests gauge
ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Number of active HTTP requests",
    labelnames=["method"],
)

# AI credit consumption counter
AI_CREDITS_CONSUMED = Counter(
    "ai_credits_consumed_total",
    "Total AI credits consumed",
    labelnames=["operation"],
)

# Database query latency
DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    labelnames=["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

# =============================================================================
# SUBTASK METRICS (T137)
# =============================================================================

# Subtask operations counter
SUBTASK_OPERATIONS = Counter(
    "subtask_operations_total",
    "Total subtask operations",
    labelnames=["operation", "tier"],
)

# Subtask limit reached counter
SUBTASK_LIMIT_REACHED = Counter(
    "subtask_limit_reached_total",
    "Number of times subtask limit was reached",
    labelnames=["tier"],
)

# Task auto-completion counter
TASK_AUTO_COMPLETED = Counter(
    "task_auto_completed_total",
    "Tasks auto-completed when all subtasks finished",
)

# Subtask reorder operations
SUBTASK_REORDER_OPERATIONS = Counter(
    "subtask_reorder_total",
    "Total subtask reorder operations",
)

# Subtasks per task histogram (to understand usage patterns)
SUBTASKS_PER_TASK = Histogram(
    "subtasks_per_task",
    "Number of subtasks per task at time of operation",
    labelnames=["operation"],
    buckets=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
)

# =============================================================================
# NOTE METRICS (T176)
# =============================================================================

# Note operations counter
NOTE_OPERATIONS = Counter(
    "note_operations_total",
    "Total note operations",
    labelnames=["operation", "tier", "note_type"],
)

# Note limit reached counter
NOTE_LIMIT_REACHED = Counter(
    "note_limit_reached_total",
    "Number of times note limit was reached",
    labelnames=["tier"],
)

# Voice note operations counter
VOICE_NOTE_OPERATIONS = Counter(
    "voice_note_operations_total",
    "Total voice note operations",
    labelnames=["operation"],
)

# Voice note duration histogram
VOICE_NOTE_DURATION = Histogram(
    "voice_note_duration_seconds",
    "Voice note recording duration in seconds",
    buckets=(15, 30, 60, 120, 180, 240, 300),
)

# Note to task conversion counter
NOTE_TO_TASK_CONVERSIONS = Counter(
    "note_to_task_conversions_total",
    "Notes converted to tasks",
)


# =============================================================================
# TASK OPERATION METRICS (T130)
# =============================================================================

# Task operations counter
TASK_OPERATIONS = Counter(
    "task_operations_total",
    "Total task operations",
    labelnames=["operation", "tier"],
)

# Task completion counter by completion type
TASK_COMPLETIONS = Counter(
    "task_completions_total",
    "Total task completions by type",
    labelnames=["completed_by"],
)

# Task deletion counter
TASK_DELETIONS = Counter(
    "task_deletions_total",
    "Total task deletions",
    labelnames=["deletion_type"],
)

# Task version conflicts (optimistic locking)
TASK_VERSION_CONFLICTS = Counter(
    "task_version_conflicts_total",
    "Total optimistic locking version conflicts",
)

# Task limit reached counter
TASK_LIMIT_REACHED = Counter(
    "task_limit_reached_total",
    "Number of times task limit was reached",
    labelnames=["tier"],
)

# Task due date exceeded counter
TASK_DUE_DATE_EXCEEDED = Counter(
    "task_due_date_exceeded_total",
    "Number of times task due date exceeded 30-day limit",
)


# =============================================================================
# TASK OPERATION METRICS HELPERS (T130)
# =============================================================================


def record_task_operation(operation: str, tier: str) -> None:
    """Record task operation.

    T130: Add metrics for task operations

    Args:
        operation: The operation type (create, update, delete, complete, force_complete, soft_delete, hard_delete)
        tier: User tier (free, pro)
    """
    TASK_OPERATIONS.labels(operation=operation, tier=tier).inc()


def record_task_completion(completed_by: str) -> None:
    """Record task completion by type.

    Args:
        completed_by: Completion type (manual, auto, force)
    """
    TASK_COMPLETIONS.labels(completed_by=completed_by).inc()


def record_task_deletion(deletion_type: str) -> None:
    """Record task deletion.

    Args:
        deletion_type: Deletion type (soft, hard)
    """
    TASK_DELETIONS.labels(deletion_type=deletion_type).inc()


def record_task_version_conflict() -> None:
    """Record optimistic locking version conflict."""
    TASK_VERSION_CONFLICTS.inc()


def record_task_limit_reached(tier: str) -> None:
    """Record when task limit is reached.

    Args:
        tier: User tier (free, pro)
    """
    TASK_LIMIT_REACHED.labels(tier=tier).inc()


def record_task_due_date_exceeded() -> None:
    """Record when task due date exceeds 30-day limit."""
    TASK_DUE_DATE_EXCEEDED.inc()


# =============================================================================
# AUTH METRICS (T084)
# =============================================================================

# Auth operations counter
AUTH_OPERATIONS = Counter(
    "auth_operations_total",
    "Total authentication operations",
    labelnames=["operation", "status"],
)

# Auth operation latency
AUTH_LATENCY = Histogram(
    "auth_operation_duration_seconds",
    "Authentication operation latency in seconds",
    labelnames=["operation"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)


# =============================================================================
# AUTH METRICS HELPERS (T084)
# =============================================================================


def record_auth_operation(operation: str, status: str) -> None:
    """Record authentication operation.

    T084: Add metrics for auth operations

    Args:
        operation: The operation type (login, token_refresh, logout)
        status: Operation status (success, failure)
    """
    AUTH_OPERATIONS.labels(operation=operation, status=status).inc()


def record_auth_latency(operation: str, duration: float) -> None:
    """Record authentication operation latency.

    Args:
        operation: The operation type (login, token_refresh, logout)
        duration: Operation duration in seconds
    """
    AUTH_LATENCY.labels(operation=operation).observe(duration)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for all requests.

    Tracks:
    - Request latency (histogram)
    - Request count by method/path/status
    - Error count (4xx and 5xx)
    - Active requests (gauge)
    """

    # Paths to exclude from metrics (to avoid cardinality explosion)
    EXCLUDE_PATHS = {"/metrics", "/health/live", "/health/ready"}

    # Path normalization patterns (to reduce cardinality)
    PATH_PATTERNS = {
        "tasks": "/api/v1/tasks/{id}",
        "subtasks": "/api/v1/subtasks/{id}",
        "notes": "/api/v1/notes/{id}",
        "reminders": "/api/v1/reminders/{id}",
        "notifications": "/api/v1/notifications/{id}",
        "tombstones": "/api/v1/recovery/tombstones/{id}",
    }

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and collect metrics."""
        # Skip metrics for excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        method = request.method
        path = self._normalize_path(request.url.path)

        # Track active requests
        ACTIVE_REQUESTS.labels(method=method).inc()

        # Measure request duration
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            status_code = str(response.status_code)

            # Record metrics
            REQUEST_LATENCY.labels(
                method=method, path=path, status_code=status_code
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=method, path=path, status_code=status_code
            ).inc()

            # Track errors
            if response.status_code >= 400:
                ERROR_COUNT.labels(
                    method=method, path=path, status_code=status_code
                ).inc()

            return response

        except Exception:
            duration = time.perf_counter() - start_time

            # Record error metrics
            REQUEST_LATENCY.labels(
                method=method, path=path, status_code="500"
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=method, path=path, status_code="500"
            ).inc()

            ERROR_COUNT.labels(
                method=method, path=path, status_code="500"
            ).inc()

            raise

        finally:
            # Always decrement active requests
            ACTIVE_REQUESTS.labels(method=method).dec()

    def _normalize_path(self, path: str) -> str:
        """Normalize path to reduce cardinality.

        Replaces UUIDs and IDs with placeholders.
        """
        import re

        # Replace UUIDs with {id}
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{id}",
            path,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs with {id}
        path = re.sub(r"/\d+", "/{id}", path)

        return path


def metrics_endpoint() -> Response:
    """Generate Prometheus metrics endpoint response."""
    return PlainTextResponse(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# =============================================================================
# HELPER FUNCTIONS FOR MANUAL METRICS
# =============================================================================


def record_credit_consumption(operation: str, amount: int = 1) -> None:
    """Record AI credit consumption.

    Args:
        operation: The operation type (chat, subtask, conversion, transcription)
        amount: Number of credits consumed
    """
    AI_CREDITS_CONSUMED.labels(operation=operation).inc(amount)


def record_db_query(operation: str, duration: float) -> None:
    """Record database query latency.

    Args:
        operation: The operation type (select, insert, update, delete)
        duration: Query duration in seconds
    """
    DB_QUERY_LATENCY.labels(operation=operation).observe(duration)


# =============================================================================
# SUBTASK METRICS HELPERS (T137)
# =============================================================================


def record_subtask_operation(operation: str, tier: str) -> None:
    """Record subtask operation.

    T137: Add metrics for subtask operations

    Args:
        operation: The operation type (create, update, delete, complete)
        tier: User tier (free, pro)
    """
    SUBTASK_OPERATIONS.labels(operation=operation, tier=tier).inc()


def record_subtask_limit_reached(tier: str) -> None:
    """Record when subtask limit is reached.

    Args:
        tier: User tier (free, pro)
    """
    SUBTASK_LIMIT_REACHED.labels(tier=tier).inc()


def record_task_auto_completed() -> None:
    """Record task auto-completion event."""
    TASK_AUTO_COMPLETED.inc()


def record_subtask_reorder() -> None:
    """Record subtask reorder operation."""
    SUBTASK_REORDER_OPERATIONS.inc()


def record_subtasks_count(operation: str, count: int) -> None:
    """Record number of subtasks at time of operation.

    Args:
        operation: The operation type (create, delete, complete)
        count: Number of subtasks on the task
    """
    SUBTASKS_PER_TASK.labels(operation=operation).observe(count)


# =============================================================================
# NOTE METRICS HELPERS (T176)
# =============================================================================


def record_note_operation(operation: str, tier: str, note_type: str = "text") -> None:
    """Record note operation.

    T176: Add metrics for note operations

    Args:
        operation: The operation type (create, update, delete, archive)
        tier: User tier (free, pro)
        note_type: Note type (text, voice)
    """
    NOTE_OPERATIONS.labels(operation=operation, tier=tier, note_type=note_type).inc()


def record_note_limit_reached(tier: str) -> None:
    """Record when note limit is reached.

    Args:
        tier: User tier (free, pro)
    """
    NOTE_LIMIT_REACHED.labels(tier=tier).inc()


def record_voice_note_operation(operation: str) -> None:
    """Record voice note operation.

    Args:
        operation: The operation type (create, transcribe, play)
    """
    VOICE_NOTE_OPERATIONS.labels(operation=operation).inc()


def record_voice_note_duration(duration_seconds: int) -> None:
    """Record voice note duration.

    Args:
        duration_seconds: Recording duration in seconds
    """
    VOICE_NOTE_DURATION.observe(duration_seconds)


def record_note_to_task_conversion() -> None:
    """Record note to task conversion event."""
    NOTE_TO_TASK_CONVERSIONS.inc()


# =============================================================================
# REMINDER METRICS (T195)
# =============================================================================

# Reminder operations counter
REMINDER_OPERATIONS = Counter(
    "reminder_operations_total",
    "Total reminder operations",
    labelnames=["operation", "reminder_type"],
)

# Reminder limit reached counter
REMINDER_LIMIT_REACHED = Counter(
    "reminder_limit_reached_total",
    "Number of times reminder limit was reached",
)

# Reminder fired counter
REMINDER_FIRED = Counter(
    "reminder_fired_total",
    "Total reminders fired",
    labelnames=["method"],
)

# Reminder skipped (recovered task) counter
REMINDER_SKIPPED = Counter(
    "reminder_skipped_total",
    "Total reminders skipped for recovered tasks",
)

# Reminder recalculation counter
REMINDER_RECALCULATED = Counter(
    "reminder_recalculated_total",
    "Total reminder recalculations due to due date changes",
)

# Reminder latency (time from scheduled to fired)
REMINDER_LATENCY = Histogram(
    "reminder_fire_latency_seconds",
    "Latency between scheduled time and actual fire time",
    buckets=(1, 5, 10, 30, 60, 120, 300, 600),
)


# =============================================================================
# REMINDER METRICS HELPERS (T195)
# =============================================================================


def record_reminder_operation(operation: str, reminder_type: str) -> None:
    """Record reminder operation.

    T195: Add metrics for reminder operations

    Args:
        operation: The operation type (create, update, delete)
        reminder_type: Reminder type (before, after, absolute)
    """
    REMINDER_OPERATIONS.labels(operation=operation, reminder_type=reminder_type).inc()


def record_reminder_limit_reached() -> None:
    """Record when reminder limit is reached."""
    REMINDER_LIMIT_REACHED.inc()


def record_reminder_fired(method: str) -> None:
    """Record when a reminder fires.

    Args:
        method: Notification method (push, in_app)
    """
    REMINDER_FIRED.labels(method=method).inc()


def record_reminder_skipped() -> None:
    """Record when a reminder is skipped for recovered task."""
    REMINDER_SKIPPED.inc()


def record_reminder_recalculated() -> None:
    """Record when reminders are recalculated."""
    REMINDER_RECALCULATED.inc()


def record_reminder_latency(scheduled_at_epoch: float, fired_at_epoch: float) -> None:
    """Record latency between scheduled and actual fire time.

    Args:
        scheduled_at_epoch: Scheduled time as Unix timestamp
        fired_at_epoch: Actual fire time as Unix timestamp
    """
    latency = max(0, fired_at_epoch - scheduled_at_epoch)
    REMINDER_LATENCY.observe(latency)


# =============================================================================
# AI SUBTASK GENERATION METRICS (T251)
# =============================================================================

# Subtask generation requests counter
AI_SUBTASK_GENERATION_REQUESTS = Counter(
    "ai_subtask_generation_requests_total",
    "Total AI subtask generation requests",
    labelnames=["tier", "status"],
)

# Subtask generation latency
AI_SUBTASK_GENERATION_LATENCY = Histogram(
    "ai_subtask_generation_duration_seconds",
    "AI subtask generation latency in seconds",
    labelnames=["tier"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 30.0),
)

# Generated subtasks count histogram
AI_SUBTASKS_GENERATED = Histogram(
    "ai_subtasks_generated_count",
    "Number of subtasks generated per request",
    labelnames=["tier"],
    buckets=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
)

# Subtask generation failures counter
AI_SUBTASK_GENERATION_FAILURES = Counter(
    "ai_subtask_generation_failures_total",
    "AI subtask generation failures",
    labelnames=["reason"],
)


# =============================================================================
# AI SUBTASK GENERATION METRICS HELPERS (T251)
# =============================================================================


def record_subtask_generation_request(tier: str, status: str) -> None:
    """Record AI subtask generation request.

    T251: Add metrics for subtask generation

    Args:
        tier: User tier (free, pro)
        status: Request status (success, failure, insufficient_credits)
    """
    AI_SUBTASK_GENERATION_REQUESTS.labels(tier=tier, status=status).inc()


def record_subtask_generation_latency(tier: str, duration: float) -> None:
    """Record AI subtask generation latency.

    Args:
        tier: User tier (free, pro)
        duration: Generation duration in seconds
    """
    AI_SUBTASK_GENERATION_LATENCY.labels(tier=tier).observe(duration)


def record_subtasks_generated_count(tier: str, count: int) -> None:
    """Record number of subtasks generated.

    Args:
        tier: User tier (free, pro)
        count: Number of subtasks generated
    """
    AI_SUBTASKS_GENERATED.labels(tier=tier).observe(count)


def record_subtask_generation_failure(reason: str) -> None:
    """Record AI subtask generation failure.

    Args:
        reason: Failure reason (insufficient_credits, ai_unavailable, task_not_found, timeout)
    """
    AI_SUBTASK_GENERATION_FAILURES.labels(reason=reason).inc()


# =============================================================================
# CREDIT SYSTEM METRICS (T288)
# =============================================================================

# Credit grant counter by type
CREDIT_GRANTS = Counter(
    "credit_grants_total",
    "Total credits granted",
    labelnames=["credit_type"],
)

# Credit consumption counter by operation and type
CREDIT_CONSUMPTION = Counter(
    "credit_consumption_total",
    "Total credits consumed by operation",
    labelnames=["operation", "credit_type"],
)

# Credit consumption latency
CREDIT_CONSUMPTION_LATENCY = Histogram(
    "credit_consumption_duration_seconds",
    "Credit consumption operation latency in seconds",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)

# Credit expiration counter
CREDIT_EXPIRATIONS = Counter(
    "credit_expirations_total",
    "Total credits expired",
    labelnames=["credit_type"],
)

# Credit carryover counter
CREDIT_CARRYOVER = Counter(
    "credit_carryover_total",
    "Total credits carried over to next month",
)

# Insufficient credits errors
INSUFFICIENT_CREDITS = Counter(
    "insufficient_credits_total",
    "Number of times insufficient credits error occurred",
    labelnames=["operation"],
)

# Credit balance gauge (last recorded balance)
CREDIT_BALANCE = Gauge(
    "credit_balance_current",
    "Current credit balance by type (sampled on operations)",
    labelnames=["credit_type"],
)


# =============================================================================
# CREDIT METRICS HELPERS (T288)
# =============================================================================


def record_credit_grant(credit_type: str, amount: int) -> None:
    """Record credit grant.

    T288: Add credit consumption metrics (FR-066)

    Args:
        credit_type: Credit type (kickstart, daily, subscription, purchased)
        amount: Number of credits granted
    """
    CREDIT_GRANTS.labels(credit_type=credit_type).inc(amount)


def record_credit_consumed(operation: str, credit_type: str, amount: int) -> None:
    """Record credit consumption with breakdown by type.

    Args:
        operation: Operation type (chat, subtask, conversion, transcription)
        credit_type: Credit type consumed from (daily, subscription, purchased, kickstart)
        amount: Number of credits consumed
    """
    CREDIT_CONSUMPTION.labels(operation=operation, credit_type=credit_type).inc(amount)


def record_credit_consumption_latency(duration: float) -> None:
    """Record credit consumption latency.

    Args:
        duration: Operation duration in seconds
    """
    CREDIT_CONSUMPTION_LATENCY.observe(duration)


def record_credit_expiration(credit_type: str, amount: int) -> None:
    """Record credit expiration.

    Args:
        credit_type: Credit type that expired (daily, subscription)
        amount: Number of credits expired
    """
    CREDIT_EXPIRATIONS.labels(credit_type=credit_type).inc(amount)


def record_credit_carryover(amount: int) -> None:
    """Record credit carryover.

    Args:
        amount: Number of credits carried over
    """
    CREDIT_CARRYOVER.inc(amount)


def record_insufficient_credits(operation: str) -> None:
    """Record insufficient credits error.

    Args:
        operation: Operation that failed due to insufficient credits
    """
    INSUFFICIENT_CREDITS.labels(operation=operation).inc()


# =============================================================================
# SUBSCRIPTION/WEBHOOK METRICS (T334)
# =============================================================================

# Webhook events processed counter
WEBHOOK_EVENTS_PROCESSED = Counter(
    "webhook_events_processed_total",
    "Total webhook events processed",
    labelnames=["event_type", "status"],
)

# Webhook processing latency
WEBHOOK_PROCESSING_LATENCY = Histogram(
    "webhook_processing_duration_seconds",
    "Webhook event processing latency in seconds (SC-008: <30s)",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 30.0),
)

# Subscription status changes counter
SUBSCRIPTION_STATUS_CHANGES = Counter(
    "subscription_status_changes_total",
    "Total subscription status changes",
    labelnames=["from_status", "to_status"],
)

# Payment failure counter
PAYMENT_FAILURES = Counter(
    "payment_failures_total",
    "Total payment failures",
    labelnames=["retry_count"],
)

# Grace period entries counter
GRACE_PERIOD_ENTRIES = Counter(
    "grace_period_entries_total",
    "Total subscriptions entering grace period",
)

# Tier downgrade counter
TIER_DOWNGRADES = Counter(
    "tier_downgrades_total",
    "Total tier downgrades (grace expiration)",
)

# Credit purchases counter
CREDIT_PURCHASES = Counter(
    "credit_purchases_total",
    "Total credit purchase operations",
    labelnames=["status"],
)

# Credit purchases amount histogram
CREDIT_PURCHASE_AMOUNT = Histogram(
    "credit_purchase_amount",
    "Credits purchased per transaction",
    buckets=(10, 25, 50, 100, 200, 300, 400, 500),
)


# =============================================================================
# SUBSCRIPTION/WEBHOOK METRICS HELPERS (T334)
# =============================================================================


def record_webhook_event(event_type: str, status: str) -> None:
    """Record webhook event processing.

    T334: Add webhook processing metrics (SC-008)

    Args:
        event_type: Webhook event type (payment_captured, payment_declined, etc.)
        status: Processing status (success, duplicate, error)
    """
    WEBHOOK_EVENTS_PROCESSED.labels(event_type=event_type, status=status).inc()


def record_webhook_latency(duration: float) -> None:
    """Record webhook processing latency.

    Args:
        duration: Processing duration in seconds
    """
    WEBHOOK_PROCESSING_LATENCY.observe(duration)


def record_subscription_status_change(from_status: str, to_status: str) -> None:
    """Record subscription status change.

    Args:
        from_status: Previous status
        to_status: New status
    """
    SUBSCRIPTION_STATUS_CHANGES.labels(
        from_status=from_status, to_status=to_status
    ).inc()


def record_payment_failure(retry_count: int) -> None:
    """Record payment failure.

    Args:
        retry_count: Current retry count
    """
    PAYMENT_FAILURES.labels(retry_count=str(retry_count)).inc()


def record_grace_period_entry() -> None:
    """Record subscription entering grace period."""
    GRACE_PERIOD_ENTRIES.inc()


def record_tier_downgrade() -> None:
    """Record tier downgrade due to grace expiration."""
    TIER_DOWNGRADES.inc()


def record_credit_purchase(status: str, amount: int = 0) -> None:
    """Record credit purchase operation.

    Args:
        status: Purchase status (success, limit_exceeded, not_pro)
        amount: Credits purchased (0 on failure)
    """
    CREDIT_PURCHASES.labels(status=status).inc()
    if amount > 0:
        CREDIT_PURCHASE_AMOUNT.observe(amount)


def update_credit_balance(
    daily: int = 0,
    subscription: int = 0,
    purchased: int = 0,
    kickstart: int = 0,
) -> None:
    """Update current credit balance gauge.

    Args:
        daily: Current daily credits
        subscription: Current subscription credits
        purchased: Current purchased credits
        kickstart: Current kickstart credits
    """
    CREDIT_BALANCE.labels(credit_type="daily").set(daily)
    CREDIT_BALANCE.labels(credit_type="subscription").set(subscription)
    CREDIT_BALANCE.labels(credit_type="purchased").set(purchased)
    CREDIT_BALANCE.labels(credit_type="kickstart").set(kickstart)


# =============================================================================
# RECOVERY METRICS (T347)
# =============================================================================

# Recovery operations counter
RECOVERY_OPERATIONS = Counter(
    "recovery_operations_total",
    "Total recovery operations",
    labelnames=["operation", "status"],
)

# Recovery latency (time from request to restored task)
RECOVERY_LATENCY = Histogram(
    "recovery_latency_seconds",
    "Time to recover a task from tombstone",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)


# =============================================================================
# RECOVERY METRICS HELPERS (T347)
# =============================================================================


def record_recovery_operation(operation: str, status: str) -> None:
    """Record recovery operation.

    T347: Add recovery metrics (SC-010)

    Args:
        operation: The operation type (recover, list_tombstones)
        status: Operation status (success, not_found, collision, expired)
    """
    RECOVERY_OPERATIONS.labels(operation=operation, status=status).inc()


def record_recovery_latency(duration_seconds: float) -> None:
    """Record recovery latency.

    T347: SC-010 requires recovery < 30 seconds.

    Args:
        duration_seconds: Time taken to recover the task
    """
    RECOVERY_LATENCY.observe(duration_seconds)
