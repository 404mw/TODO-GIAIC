"""SQLModel database models for Perpetua Flow Backend.

T060: Export all models in src/models/__init__.py

All models use SQLModel which combines Pydantic validation with SQLAlchemy ORM.
"""

from src.models.base import BaseModel, TimestampMixin, VersionedModel
from src.models.user import User, UserBase, UserCreate, UserPublic, UserRead, UserUpdate
from src.models.task import TaskInstance, TaskInstanceBase, TaskTemplate
from src.models.subtask import Subtask, SubtaskBase
from src.models.note import Note, NoteBase
from src.models.reminder import Reminder, ReminderBase
from src.models.achievement import (
    AchievementDefinition,
    UserAchievementState,
    ACHIEVEMENT_SEED_DATA,
)
from src.models.credit import AICreditLedger
from src.models.subscription import Subscription
from src.models.activity import ActivityLog
from src.models.tombstone import DeletionTombstone
from src.models.notification import Notification, PushSubscription
from src.models.job_queue import JobQueue
from src.models.auth import RefreshToken
from src.models.idempotency import IdempotencyKey
from src.models.focus import FocusSession

__all__ = [
    # Base models
    "BaseModel",
    "TimestampMixin",
    "VersionedModel",
    # User
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserPublic",
    # Task
    "TaskInstance",
    "TaskInstanceBase",
    "TaskTemplate",
    # Subtask
    "Subtask",
    "SubtaskBase",
    # Note
    "Note",
    "NoteBase",
    # Reminder
    "Reminder",
    "ReminderBase",
    # Achievement
    "AchievementDefinition",
    "UserAchievementState",
    "ACHIEVEMENT_SEED_DATA",
    # Credit
    "AICreditLedger",
    # Subscription
    "Subscription",
    # Activity
    "ActivityLog",
    # Tombstone
    "DeletionTombstone",
    # Notification
    "Notification",
    "PushSubscription",
    # Job Queue
    "JobQueue",
    # Auth
    "RefreshToken",
    # Idempotency
    "IdempotencyKey",
    # Focus
    "FocusSession",
]
