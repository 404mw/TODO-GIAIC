"""Notification schemas for alerts and push notifications.

T054: Notification schemas per api-specification.md Section 11
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.enums import NotificationType


class NotificationResponse(BaseModel):
    """Notification response.

    Per api-specification.md Section 11.1.
    """

    id: UUID = Field(description="Notification ID")
    type: NotificationType = Field(description="Notification type")
    title: str = Field(description="Notification title")
    body: str = Field(description="Notification content")
    action_url: str | None = Field(description="Deep link target")
    read: bool = Field(description="Read status")
    read_at: datetime | None = Field(description="When read")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response for notification list with unread count.

    Per api-specification.md Section 11.1.
    """

    data: list[NotificationResponse] = Field(description="Notifications")
    unread_count: int = Field(description="Total unread count")


class NotificationListFilters(BaseModel):
    """Query parameters for listing notifications."""

    unread_only: bool = Field(
        default=False,
        description="Filter unread only",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Max notifications to return",
    )


class MarkAllReadResponse(BaseModel):
    """Response for mark all read operation.

    Per api-specification.md Section 11.3.
    """

    marked_count: int = Field(description="Number of notifications marked read")


class PushSubscriptionRequest(BaseModel):
    """Request to register push subscription.

    Per FR-028a.
    """

    endpoint: str = Field(description="Push service endpoint URL")
    p256dh_key: str = Field(description="Client public key (base64)")
    auth_key: str = Field(description="Authentication secret (base64)")


class PushSubscriptionResponse(BaseModel):
    """Response for push subscription registration."""

    id: UUID = Field(description="Subscription ID")
    endpoint: str = Field(description="Push service endpoint URL")
    created_at: datetime = Field(description="Subscription created time")

    class Config:
        from_attributes = True
