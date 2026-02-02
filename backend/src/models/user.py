"""User model for authentication and profile management.

T030: User model per data-model.md Entity 1
"""

from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import UserTier

if TYPE_CHECKING:
    from src.models.achievement import UserAchievementState
    from src.models.activity import ActivityLog
    from src.models.auth import RefreshToken
    from src.models.credit import AICreditLedger
    from src.models.note import Note
    from src.models.notification import Notification, PushSubscription
    from src.models.reminder import Reminder
    from src.models.subscription import Subscription
    from src.models.task import TaskInstance, TaskTemplate
    from src.models.tombstone import DeletionTombstone


class UserBase(SQLModel):
    """Base fields for User model."""

    google_id: str = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Google OAuth subject ID",
    )
    email: EmailStr = Field(
        unique=True,
        index=True,
        nullable=False,
        description="User email from Google profile",
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        nullable=False,
        description="Display name from Google profile",
    )
    avatar_url: str | None = Field(
        default=None,
        description="Google profile picture URL",
    )
    timezone: str = Field(
        default="UTC",
        description="User's preferred timezone (IANA format)",
    )
    tier: UserTier = Field(
        default=UserTier.FREE,
        nullable=False,
        description="Subscription tier",
    )


class User(UserBase, BaseModel, table=True):
    """User database model.

    Represents an authenticated account with profile, preferences,
    subscription status, and timezone.

    Per data-model.md Entity 1.
    """

    __tablename__ = "users"

    # Relationships
    task_instances: list["TaskInstance"] = Relationship(back_populates="user")
    task_templates: list["TaskTemplate"] = Relationship(back_populates="user")
    notes: list["Note"] = Relationship(back_populates="user")
    reminders: list["Reminder"] = Relationship(back_populates="user")
    notifications: list["Notification"] = Relationship(back_populates="user")
    push_subscriptions: list["PushSubscription"] = Relationship(back_populates="user")
    achievement_state: Optional["UserAchievementState"] = Relationship(back_populates="user")
    subscription: Optional["Subscription"] = Relationship(back_populates="user")
    credit_entries: list["AICreditLedger"] = Relationship(back_populates="user")
    tombstones: list["DeletionTombstone"] = Relationship(back_populates="user")
    activity_logs: list["ActivityLog"] = Relationship(back_populates="user")
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")

    @property
    def is_pro(self) -> bool:
        """Check if user has Pro tier."""
        return self.tier == UserTier.PRO


class UserCreate(UserBase):
    """Schema for creating a new user from OAuth."""

    pass


class UserUpdate(SQLModel):
    """Schema for updating user profile (FR-070).

    PATCH semantics: omitted fields are unchanged, null explicitly clears.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    timezone: str | None = Field(default=None)


class UserRead(UserBase):
    """Schema for reading user data in API responses."""

    id: str  # UUID as string for JSON serialization

    class Config:
        from_attributes = True


class UserPublic(SQLModel):
    """Public user profile visible to others."""

    id: str
    name: str
    avatar_url: str | None = None
