"""Event type definitions for the in-process event system.

T198: Define event types (task.created, task.completed, task.deleted, etc.)
Per plan.md Event Types section.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from src.schemas.enums import ActivitySource, CompletedBy


# =============================================================================
# BASE EVENT
# =============================================================================


@dataclass
class BaseEvent:
    """Base class for all domain events."""

    event_type: str = field(init=False)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow(), kw_only=True)

    def __post_init__(self) -> None:
        """Set event_type from class name."""
        # Convert CamelCase to snake_case with dots
        # TaskCreatedEvent -> task.created
        name = self.__class__.__name__.replace("Event", "")
        parts = []
        current = []
        for char in name:
            if char.isupper() and current:
                parts.append("".join(current).lower())
                current = [char]
            else:
                current.append(char)
        if current:
            parts.append("".join(current).lower())

        # Join with dots (e.g., ["Task", "Created"] -> "task.created")
        if len(parts) >= 2:
            self.event_type = f"{parts[0]}.{'_'.join(parts[1:])}"
        else:
            self.event_type = parts[0] if parts else "unknown"


# =============================================================================
# TASK EVENTS
# =============================================================================


@dataclass
class TaskCreatedEvent(BaseEvent):
    """Event emitted when a task is created.

    Per plan.md Event Types: task.created
    """

    task_id: UUID
    user_id: UUID
    title: str
    source: ActivitySource = ActivitySource.USER


@dataclass
class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is completed.

    Per plan.md Event Types: task.completed
    """

    task_id: UUID
    user_id: UUID
    completed_by: CompletedBy
    template_id: UUID | None = None
    completed_at: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class TaskDeletedEvent(BaseEvent):
    """Event emitted when a task is deleted.

    Per plan.md Event Types: task.deleted
    """

    task_id: UUID
    user_id: UUID
    tombstone_id: UUID | None = None
    hard_delete: bool = False


@dataclass
class TaskUpdatedEvent(BaseEvent):
    """Event emitted when a task is updated."""

    task_id: UUID
    user_id: UUID
    changes: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# SUBTASK EVENTS
# =============================================================================


@dataclass
class SubtaskCreatedEvent(BaseEvent):
    """Event emitted when a subtask is created."""

    subtask_id: UUID
    task_id: UUID
    user_id: UUID
    title: str
    source: ActivitySource = ActivitySource.USER


@dataclass
class SubtaskCompletedEvent(BaseEvent):
    """Event emitted when a subtask is completed.

    Per plan.md Event Types: subtask.completed
    """

    subtask_id: UUID
    task_id: UUID
    user_id: UUID


@dataclass
class SubtaskDeletedEvent(BaseEvent):
    """Event emitted when a subtask is deleted."""

    subtask_id: UUID
    task_id: UUID
    user_id: UUID


# =============================================================================
# NOTE EVENTS
# =============================================================================


@dataclass
class NoteCreatedEvent(BaseEvent):
    """Event emitted when a note is created."""

    note_id: UUID
    user_id: UUID
    has_voice: bool = False


@dataclass
class NoteConvertedEvent(BaseEvent):
    """Event emitted when a note is converted to a task.

    Per plan.md Event Types: note.converted
    """

    note_id: UUID
    task_id: UUID
    user_id: UUID


@dataclass
class NoteDeletedEvent(BaseEvent):
    """Event emitted when a note is deleted."""

    note_id: UUID
    user_id: UUID


# =============================================================================
# AI EVENTS
# =============================================================================


@dataclass
class AIChatEvent(BaseEvent):
    """Event emitted when AI chat is used.

    Per plan.md Event Types: ai.chat
    """

    user_id: UUID
    task_id: UUID | None
    credits_used: int
    message_preview: str = ""


@dataclass
class AISubtasksGeneratedEvent(BaseEvent):
    """Event emitted when AI generates subtasks.

    Per plan.md Event Types: ai.subtasks_generated
    """

    task_id: UUID
    user_id: UUID
    count: int
    credits_used: int


# =============================================================================
# SUBSCRIPTION EVENTS
# =============================================================================


@dataclass
class SubscriptionCreatedEvent(BaseEvent):
    """Event emitted when a subscription is created/activated.

    Per plan.md Event Types: subscription.created
    """

    user_id: UUID
    tier: str  # "pro"


@dataclass
class SubscriptionCancelledEvent(BaseEvent):
    """Event emitted when a subscription is cancelled.

    Per plan.md Event Types: subscription.cancelled
    """

    user_id: UUID
    effective_date: datetime | None = None


# =============================================================================
# ACHIEVEMENT EVENTS
# =============================================================================


@dataclass
class AchievementUnlockedEvent(BaseEvent):
    """Event emitted when an achievement is unlocked.

    Per plan.md Event Types: achievement.unlocked
    """

    user_id: UUID
    achievement_id: str
    achievement_name: str
    perk_type: str | None = None
    perk_value: int | None = None


# =============================================================================
# RECURRING TASK EVENTS
# =============================================================================


@dataclass
class RecurringInstanceGeneratedEvent(BaseEvent):
    """Event emitted when a recurring task instance is generated."""

    template_id: UUID
    instance_id: UUID
    user_id: UUID
    due_date: datetime | None = None


# =============================================================================
# REMINDER EVENTS
# =============================================================================


@dataclass
class ReminderFiredEvent(BaseEvent):
    """Event emitted when a reminder is fired."""

    reminder_id: UUID
    task_id: UUID
    user_id: UUID


# =============================================================================
# TYPE UNION
# =============================================================================

# All event types for type hints
Event = (
    TaskCreatedEvent
    | TaskCompletedEvent
    | TaskDeletedEvent
    | TaskUpdatedEvent
    | SubtaskCreatedEvent
    | SubtaskCompletedEvent
    | SubtaskDeletedEvent
    | NoteCreatedEvent
    | NoteConvertedEvent
    | NoteDeletedEvent
    | AIChatEvent
    | AISubtasksGeneratedEvent
    | SubscriptionCreatedEvent
    | SubscriptionCancelledEvent
    | AchievementUnlockedEvent
    | RecurringInstanceGeneratedEvent
    | ReminderFiredEvent
)
