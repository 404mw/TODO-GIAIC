"""Notification API endpoints.

Phase 19: Notifications (FR-055 to FR-057)

T355: Implement GET /api/v1/notifications per api-specification.md Section 10.1
T356: Implement PATCH /api/v1/notifications/:id/read per api-specification.md Section 10.2
T357: Implement POST /api/v1/notifications/read-all per api-specification.md Section 10.3
T358b: Implement POST /api/v1/notifications/push-subscription (FR-028a)
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.dependencies import (
    CurrentUser,
    DBSession,
    get_settings,
)
from src.schemas.common import DataResponse
from src.schemas.notification import (
    MarkAllReadResponse,
    NotificationListResponse,
    NotificationResponse,
    PushSubscriptionRequest,
    PushSubscriptionResponse,
)
from src.services.notification_service import (
    NotificationNotFoundError,
    NotificationService,
)


router = APIRouter(prefix="/notifications", tags=["notifications"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_notification_service(
    db: DBSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> NotificationService:
    """Get NotificationService instance."""
    return NotificationService(db, settings)


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]


# =============================================================================
# T355: GET /api/v1/notifications
# =============================================================================


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications",
    description="List user notifications with optional unread filter.",
)
async def list_notifications(
    user: CurrentUser,
    service: NotificationServiceDep,
    unread_only: bool = Query(default=False, description="Filter unread only"),
    limit: int = Query(default=50, ge=1, le=100, description="Max notifications"),
):
    """List notifications for the authenticated user.

    Per api-specification.md Section 10.1.
    """
    notifications, unread_count = await service.list_notifications(
        user=user,
        unread_only=unread_only,
        limit=limit,
    )

    return NotificationListResponse(
        data=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
    )


# =============================================================================
# T356: PATCH /api/v1/notifications/:id/read
# =============================================================================


@router.patch(
    "/{notification_id}/read",
    response_model=DataResponse,
    summary="Mark notification read",
    description="Mark a specific notification as read.",
)
async def mark_notification_read(
    notification_id: UUID,
    user: CurrentUser,
    service: NotificationServiceDep,
):
    """Mark a notification as read.

    Per api-specification.md Section 10.2.
    """
    try:
        notification = await service.mark_notification_read(
            user=user,
            notification_id=notification_id,
        )
    except NotificationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return DataResponse(
        data=NotificationResponse.model_validate(notification),
    )


# =============================================================================
# T357: POST /api/v1/notifications/read-all
# =============================================================================


@router.post(
    "/read-all",
    response_model=DataResponse,
    summary="Mark all notifications read",
    description="Mark all unread notifications as read.",
)
async def mark_all_read(
    user: CurrentUser,
    service: NotificationServiceDep,
):
    """Mark all notifications as read.

    Per api-specification.md Section 10.3.
    """
    count = await service.mark_all_notifications_read(user=user)

    return DataResponse(
        data=MarkAllReadResponse(marked_count=count),
    )


# =============================================================================
# T358b: POST /api/v1/notifications/push-subscription (FR-028a)
# =============================================================================


@router.post(
    "/push-subscription",
    response_model=DataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register push subscription",
    description="Register a WebPush subscription for push notifications.",
)
async def register_push_subscription(
    request: PushSubscriptionRequest,
    user: CurrentUser,
    service: NotificationServiceDep,
):
    """Register a push notification subscription.

    Per FR-028a: Frontend registers WebPush subscriptions,
    backend stores tokens for push delivery.
    """
    subscription = await service.register_push_subscription(
        user=user,
        endpoint=request.endpoint,
        p256dh_key=request.p256dh_key,
        auth_key=request.auth_key,
    )

    return DataResponse(
        data=PushSubscriptionResponse.model_validate(subscription),
    )


@router.delete(
    "/push-subscription",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister push subscription",
    description="Unregister a WebPush subscription.",
)
async def unregister_push_subscription(
    user: CurrentUser,
    service: NotificationServiceDep,
    endpoint: str = Query(description="Push service endpoint URL to unregister"),
):
    """Unregister a push notification subscription."""
    found = await service.unregister_push_subscription(
        user=user,
        endpoint=endpoint,
    )

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Push subscription not found",
        )
