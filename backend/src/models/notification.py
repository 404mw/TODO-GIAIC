"""Notification models for alerts and push notifications.

T042: Notification model per data-model.md Entity 13
T358a: PushSubscription model per FR-028a
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import BaseModel
from src.schemas.enums import NotificationType

if TYPE_CHECKING:
    from src.models.user import User


class Notification(BaseModel, table=True):
    """Notification database model.

    In-app or push message for user alerts.

    Per data-model.md Entity 13.
    """

    __tablename__ = "notifications"

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Recipient",
    )

    # Notification content
    type: NotificationType = Field(
        nullable=False,
        description="Notification category",
    )
    title: str = Field(
        max_length=100,
        nullable=False,
        description="Notification title (max 100 chars)",
    )
    body: str = Field(
        max_length=500,
        nullable=False,
        description="Notification content (max 500 chars)",
    )
    action_url: str | None = Field(
        default=None,
        description="Deep link target (URL path)",
    )

    # Read status (FR-057)
    read: bool = Field(
        default=False,
        nullable=False,
        description="Read status",
    )
    read_at: datetime | None = Field(
        default=None,
        description="When read (UTC)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="notifications")


class PushSubscription(SQLModel, table=True):
    """Push Subscription database model.

    WebPush subscription for push notifications.

    Per FR-028a.
    """

    __tablename__ = "push_subscriptions"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Subscription ID",
    )

    # Foreign key
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Subscriber",
    )

    # WebPush fields
    endpoint: str = Field(
        nullable=False,
        unique=True,
        description="Push service endpoint URL",
    )
    p256dh_key: str = Field(
        nullable=False,
        description="Client public key (base64)",
    )
    auth_key: str = Field(
        nullable=False,
        description="Authentication secret (base64)",
    )

    # Status
    active: bool = Field(
        default=True,
        nullable=False,
        description="Whether subscription is active",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Subscription created (UTC)",
    )
    last_used_at: datetime | None = Field(
        default=None,
        description="Last successful push (UTC)",
    )

    # Relationships
    user: "User" = Relationship(back_populates="push_subscriptions")
