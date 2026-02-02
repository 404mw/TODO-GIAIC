"""Event system for domain events.

This module provides:
- Event bus for in-process synchronous event dispatch (AD-003)
- Event type definitions for all domain events
- Event handlers for cross-cutting concerns (activity logging, etc.)
"""

# Event bus
from src.events.bus import (
    EventBus,
    dispatch,
    get_event_bus,
    reset_event_bus,
    subscribe,
)

# Event types
from src.events.types import (
    AchievementUnlockedEvent,
    AIChatEvent,
    AISubtasksGeneratedEvent,
    BaseEvent,
    Event,
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

# Event handlers
from src.events.handlers import (
    activity_log_handler,
    create_task_completed_event,
    handle_recurring_task_completed,
    handle_subtask_completed_for_auto_complete,
    register_all_handlers,
)

# Legacy subtask handlers (for backwards compatibility)
from src.events.subtask_handlers import (
    check_auto_complete_eligibility,
    handle_subtask_completed,
)

__all__ = [
    # Event bus
    "EventBus",
    "get_event_bus",
    "reset_event_bus",
    "dispatch",
    "subscribe",
    # Event types
    "BaseEvent",
    "Event",
    "TaskCreatedEvent",
    "TaskCompletedEvent",
    "TaskDeletedEvent",
    "TaskUpdatedEvent",
    "SubtaskCreatedEvent",
    "SubtaskCompletedEvent",
    "SubtaskDeletedEvent",
    "NoteCreatedEvent",
    "NoteConvertedEvent",
    "NoteDeletedEvent",
    "AIChatEvent",
    "AISubtasksGeneratedEvent",
    "SubscriptionCreatedEvent",
    "SubscriptionCancelledEvent",
    "AchievementUnlockedEvent",
    "RecurringInstanceGeneratedEvent",
    "ReminderFiredEvent",
    # Handlers
    "activity_log_handler",
    "create_task_completed_event",
    "handle_recurring_task_completed",
    "handle_subtask_completed_for_auto_complete",
    "register_all_handlers",
    # Legacy
    "check_auto_complete_eligibility",
    "handle_subtask_completed",
]
