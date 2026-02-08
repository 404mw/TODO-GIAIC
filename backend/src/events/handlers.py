"""Event handlers for core domain events.

T148: Implement completion handler that triggers generation
T200: Implement activity log handler for all events (FR-052)
"""

import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.events.bus import get_event_bus, subscribe
from src.events.types import (
    AchievementUnlockedEvent,
    AIChatEvent,
    AISubtasksGeneratedEvent,
    NoteConvertedEvent,
    NoteCreatedEvent,
    NoteDeletedEvent,
    RecurringInstanceGeneratedEvent,
    ReminderFiredEvent,
    SubtaskCompletedEvent,
    SubtaskCreatedEvent,
    SubtaskDeletedEvent,
    SubscriptionCancelledEvent,
    SubscriptionCreatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)
from src.models.activity import ActivityLog
from src.models.task import TaskInstance, TaskTemplate
from src.schemas.enums import ActivitySource, EntityType


logger = logging.getLogger(__name__)


# =============================================================================
# ACTIVITY LOG HANDLER (T200, FR-052)
# =============================================================================


def _map_event_to_activity(event: object) -> tuple[EntityType, str, dict] | None:
    """Map an event to activity log parameters.

    Args:
        event: The domain event

    Returns:
        Tuple of (entity_type, action, metadata) or None if not loggable
    """
    # Task events
    if isinstance(event, TaskCreatedEvent):
        return (
            EntityType.TASK,
            "task_created",
            {"title": event.title, "source": event.source.value},
        )
    if isinstance(event, TaskCompletedEvent):
        return (
            EntityType.TASK,
            "task_completed",
            {
                "completed_by": event.completed_by.value,
                "template_id": str(event.template_id) if event.template_id else None,
            },
        )
    if isinstance(event, TaskDeletedEvent):
        return (
            EntityType.TASK,
            "task_deleted",
            {
                "hard_delete": event.hard_delete,
                "tombstone_id": str(event.tombstone_id) if event.tombstone_id else None,
            },
        )
    if isinstance(event, TaskUpdatedEvent):
        return (
            EntityType.TASK,
            "task_updated",
            {"changes": list(event.changes.keys())},
        )

    # Subtask events
    if isinstance(event, SubtaskCreatedEvent):
        return (
            EntityType.SUBTASK,
            "subtask_created",
            {"task_id": str(event.task_id), "title": event.title},
        )
    if isinstance(event, SubtaskCompletedEvent):
        return (
            EntityType.SUBTASK,
            "subtask_completed",
            {"task_id": str(event.task_id)},
        )
    if isinstance(event, SubtaskDeletedEvent):
        return (
            EntityType.SUBTASK,
            "subtask_deleted",
            {"task_id": str(event.task_id)},
        )

    # Note events
    if isinstance(event, NoteCreatedEvent):
        return (
            EntityType.NOTE,
            "note_created",
            {"has_voice": event.has_voice},
        )
    if isinstance(event, NoteConvertedEvent):
        return (
            EntityType.NOTE,
            "note_converted",
            {"task_id": str(event.task_id)},
        )
    if isinstance(event, NoteDeletedEvent):
        return (
            EntityType.NOTE,
            "note_deleted",
            {},
        )

    # AI events
    if isinstance(event, AIChatEvent):
        return (
            EntityType.AI_CHAT,
            "ai_chat",
            {
                "credits_used": event.credits_used,
                "task_id": str(event.task_id) if event.task_id else None,
            },
        )
    if isinstance(event, AISubtasksGeneratedEvent):
        return (
            EntityType.TASK,
            "ai_subtask_generation",
            {
                "count": event.count,
                "credits_used": event.credits_used,
            },
        )

    # Subscription events
    if isinstance(event, SubscriptionCreatedEvent):
        return (
            EntityType.SUBSCRIPTION,
            "subscription_created",
            {"tier": event.tier},
        )
    if isinstance(event, SubscriptionCancelledEvent):
        return (
            EntityType.SUBSCRIPTION,
            "subscription_cancelled",
            {
                "effective_date": (
                    event.effective_date.isoformat() if event.effective_date else None
                )
            },
        )

    # Achievement events
    if isinstance(event, AchievementUnlockedEvent):
        return (
            EntityType.ACHIEVEMENT,
            "achievement_unlocked",
            {
                "achievement_name": event.achievement_name,
                "perk_type": event.perk_type,
                "perk_value": event.perk_value,
            },
        )

    # Reminder events
    if isinstance(event, ReminderFiredEvent):
        return (
            EntityType.REMINDER,
            "reminder_fired",
            {"task_id": str(event.task_id)},
        )

    return None


def _get_entity_id(event: object) -> UUID:
    """Extract the primary entity ID from an event."""
    if hasattr(event, "task_id"):
        return event.task_id
    if hasattr(event, "subtask_id"):
        return event.subtask_id
    if hasattr(event, "note_id"):
        return event.note_id
    if hasattr(event, "reminder_id"):
        return event.reminder_id
    if hasattr(event, "achievement_id"):
        # Achievement IDs are strings, create a deterministic UUID
        return uuid4()  # Use random for now
    if hasattr(event, "user_id"):
        return event.user_id  # Fallback to user_id for subscription events
    raise ValueError(f"Cannot extract entity_id from {type(event).__name__}")


def _get_user_id(event: object) -> UUID:
    """Extract the user ID from an event."""
    if hasattr(event, "user_id"):
        return event.user_id
    raise ValueError(f"Cannot extract user_id from {type(event).__name__}")


def _get_source(event: object) -> ActivitySource:
    """Extract the activity source from an event."""
    if hasattr(event, "source"):
        return event.source
    # Default sources based on event type
    if isinstance(event, (AIChatEvent, AISubtasksGeneratedEvent)):
        return ActivitySource.AI
    if isinstance(event, RecurringInstanceGeneratedEvent):
        return ActivitySource.SYSTEM
    return ActivitySource.USER


async def activity_log_handler(
    event: object,
    session: AsyncSession,
    settings: Settings,
) -> None:
    """Log all domain events to the activity log.

    T200: Activity log handler for all events (FR-052)

    This handler creates an immutable audit trail of all significant
    actions in the system.

    Args:
        event: The domain event
        session: Database session
        settings: Application settings
    """
    mapping = _map_event_to_activity(event)
    if mapping is None:
        logger.debug(f"No activity log mapping for {type(event).__name__}")
        return

    entity_type, action, metadata = mapping

    try:
        activity = ActivityLog(
            id=uuid4(),
            user_id=_get_user_id(event),
            entity_type=entity_type,
            entity_id=_get_entity_id(event),
            action=action,
            source=_get_source(event),
            extra_data=metadata,
            created_at=datetime.utcnow(),
        )

        session.add(activity)
        await session.flush()

        logger.debug(
            f"Logged activity: {action} for {entity_type.value} "
            f"(user={activity.user_id})"
        )
    except Exception as e:
        logger.error(f"Failed to log activity for {type(event).__name__}: {e}")
        # Don't raise - activity logging should not block the main operation


# =============================================================================
# RECURRING TASK COMPLETION HANDLER (T148)
# =============================================================================


async def handle_recurring_task_completed(
    event: TaskCompletedEvent,
    session: AsyncSession,
    settings: Settings,
) -> RecurringInstanceGeneratedEvent | None:
    """Handle task completion for recurring tasks.

    T148: Completion handler that triggers generation

    When a task that belongs to a recurring template is completed,
    this handler generates the next instance.

    Args:
        event: The task completed event
        session: Database session
        settings: Application settings

    Returns:
        RecurringInstanceGeneratedEvent if a new instance was generated, None otherwise
    """
    from src.services.recurring_service import get_recurring_service

    # Only process if task has a template
    if event.template_id is None:
        return None

    # Get the template
    query = select(TaskTemplate).where(TaskTemplate.id == event.template_id)
    result = await session.execute(query)
    template = result.scalar_one_or_none()

    if template is None:
        return None

    # Don't generate if template is inactive
    if not template.active:
        return None

    # Generate next instance
    service = get_recurring_service(session, settings)

    try:
        next_instance = await service.generate_next_instance(template)

        if next_instance is not None:
            return RecurringInstanceGeneratedEvent(
                template_id=template.id,
                instance_id=next_instance.id,
                user_id=next_instance.user_id,
                due_date=next_instance.due_date,
            )
    except Exception as e:
        # FR-017: Don't fail on generation error
        logger.error(f"Failed to generate recurring instance: {e}")

    return None


# =============================================================================
# SUBTASK AUTO-COMPLETE HANDLER
# =============================================================================


async def handle_subtask_completed_for_auto_complete(
    event: SubtaskCompletedEvent,
    session: AsyncSession,
    settings: Settings,
) -> None:
    """Check if task should be auto-completed when subtask is completed.

    FR-009: Auto-complete task when all subtasks are complete.

    Args:
        event: The subtask completed event
        session: Database session
        settings: Application settings
    """
    from src.events.subtask_handlers import check_auto_complete_eligibility

    try:
        # Check if parent task should be auto-completed
        should_complete = await check_auto_complete_eligibility(
            session, event.task_id
        )

        if should_complete:
            from src.services.task_service import get_task_service
            from src.schemas.enums import CompletedBy

            service = get_task_service(session, settings)
            task = await service.get_task(event.task_id, event.user_id)

            if task and not task.completed:
                await service.complete_task(
                    task_id=event.task_id,
                    user_id=event.user_id,
                    completed_by=CompletedBy.AUTO,
                )
                logger.info(
                    f"Auto-completed task {event.task_id} after subtask completion"
                )
    except Exception as e:
        logger.error(f"Failed to check auto-complete for task {event.task_id}: {e}")


# =============================================================================
# ACHIEVEMENT UNLOCK HANDLER (T301, FR-044)
# =============================================================================


async def handle_task_completed_for_achievements(
    event: TaskCompletedEvent,
    session: AsyncSession,
    settings: Settings,
) -> list[AchievementUnlockedEvent]:
    """Handle task completion for achievement tracking.

    T301: Implement achievement unlock event handler (FR-044)

    Updates streak, increments lifetime tasks, checks for focus completion,
    and unlocks any eligible achievements.

    Args:
        event: The task completed event
        session: Database session
        settings: Application settings

    Returns:
        List of AchievementUnlockedEvent for any newly unlocked achievements
    """
    from src.services.achievement_service import get_achievement_service

    unlocked_events = []

    try:
        service = get_achievement_service(session, settings)

        # Get or create achievement state
        state = await service.get_or_create_achievement_state(event.user_id)

        # Update streak
        await service.update_streak(state, event.completed_at)

        # Increment lifetime tasks
        await service.increment_lifetime_tasks(state)

        # Check for focus completion (need to get task for this)
        try:
            query = select(TaskInstance).where(TaskInstance.id == event.task_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if task and service.is_focus_completion(task):
                await service.increment_focus_completions(state)
                logger.info(
                    f"Focus completion recorded for task {event.task_id}"
                )
        except Exception as e:
            logger.warning(f"Failed to check focus completion: {e}")

        # Check and unlock achievements
        newly_unlocked = await service.check_and_unlock(state)

        # Create events for newly unlocked achievements
        for achievement in newly_unlocked:
            unlock_event = AchievementUnlockedEvent(
                user_id=event.user_id,
                achievement_id=achievement["id"],
                achievement_name=achievement["name"],
                perk_type=achievement["perk"]["type"].value if achievement.get("perk") else None,
                perk_value=achievement["perk"]["value"] if achievement.get("perk") else None,
            )
            unlocked_events.append(unlock_event)

            logger.info(
                f"Achievement unlocked: {achievement['id']} for user {event.user_id}"
            )

    except Exception as e:
        logger.error(f"Failed to process achievements for task completion: {e}")

    return unlocked_events


async def handle_note_converted_for_achievements(
    event: NoteConvertedEvent,
    session: AsyncSession,
    settings: Settings,
) -> list[AchievementUnlockedEvent]:
    """Handle note conversion for achievement tracking.

    Increments notes_converted counter and checks for note achievements.

    Args:
        event: The note converted event
        session: Database session
        settings: Application settings

    Returns:
        List of AchievementUnlockedEvent for any newly unlocked achievements
    """
    from src.services.achievement_service import get_achievement_service

    unlocked_events = []

    try:
        service = get_achievement_service(session, settings)

        # Get or create achievement state
        state = await service.get_or_create_achievement_state(event.user_id)

        # Increment notes converted
        await service.increment_notes_converted(state)

        # Check and unlock achievements
        newly_unlocked = await service.check_and_unlock(state)

        # Create events for newly unlocked achievements
        for achievement in newly_unlocked:
            unlock_event = AchievementUnlockedEvent(
                user_id=event.user_id,
                achievement_id=achievement["id"],
                achievement_name=achievement["name"],
                perk_type=achievement["perk"]["type"].value if achievement.get("perk") else None,
                perk_value=achievement["perk"]["value"] if achievement.get("perk") else None,
            )
            unlocked_events.append(unlock_event)

    except Exception as e:
        logger.error(f"Failed to process achievements for note conversion: {e}")

    return unlocked_events


# =============================================================================
# EVENT HANDLER REGISTRATION
# =============================================================================


def register_all_handlers() -> None:
    """Register all event handlers with the global event bus.

    This function should be called during application startup.
    """
    bus = get_event_bus()

    # Activity log handler for all event types
    event_types = [
        TaskCreatedEvent,
        TaskCompletedEvent,
        TaskDeletedEvent,
        TaskUpdatedEvent,
        SubtaskCreatedEvent,
        SubtaskCompletedEvent,
        SubtaskDeletedEvent,
        NoteCreatedEvent,
        NoteConvertedEvent,
        NoteDeletedEvent,
        AIChatEvent,
        AISubtasksGeneratedEvent,
        SubscriptionCreatedEvent,
        SubscriptionCancelledEvent,
        AchievementUnlockedEvent,
        ReminderFiredEvent,
    ]

    for event_type in event_types:
        bus.register(event_type, activity_log_handler)

    # Specific handlers
    bus.register(TaskCompletedEvent, handle_recurring_task_completed)
    bus.register(SubtaskCompletedEvent, handle_subtask_completed_for_auto_complete)

    # Achievement handlers (T301)
    bus.register(TaskCompletedEvent, handle_task_completed_for_achievements)
    bus.register(NoteConvertedEvent, handle_note_converted_for_achievements)

    logger.info(f"Registered handlers for {len(event_types)} event types")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_task_completed_event(task: TaskInstance) -> TaskCompletedEvent:
    """Create a TaskCompletedEvent from a TaskInstance.

    Args:
        task: The completed task

    Returns:
        TaskCompletedEvent
    """
    from src.schemas.enums import CompletedBy

    return TaskCompletedEvent(
        task_id=task.id,
        user_id=task.user_id,
        template_id=task.template_id,
        completed_by=task.completed_by or CompletedBy.MANUAL,
        completed_at=task.completed_at or datetime.utcnow(),
    )
