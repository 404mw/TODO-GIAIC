"""User API endpoints.

T078a: GET /api/v1/users/me per api-specification.md Section 3.1
T078b: PATCH /api/v1/users/me per api-specification.md Section 3.2 (FR-070)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import CurrentUser, DBSession
from src.middleware.error_handler import ValidationError
from src.middleware.rate_limit import get_limiter
from src.models.user import User, UserRead, UserUpdate
from src.services.user_service import (
    InvalidNameError,
    InvalidTimezoneError,
    UserService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

limiter = get_limiter()


class UserProfileResponse(BaseModel):
    """Response wrapper for user profile."""

    data: UserRead


class UserUpdateRequest(BaseModel):
    """Request body for updating user profile.

    Per api-specification.md Section 3.2:
    - name: string, max 100 chars
    - timezone: string, valid IANA timezone
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Display name (1-100 characters)",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="Timezone in IANA format (e.g., 'America/New_York')",
    )


# =============================================================================
# T078a: GET /api/v1/users/me
# =============================================================================


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the authenticated user's profile information.",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Authentication required"},
    },
)
@limiter.limit("100/minute")
async def get_current_user_profile(
    request: Request,
    current_user: CurrentUser,
) -> UserProfileResponse:
    """Get the authenticated user's profile.

    Returns the current user's profile including:
    - Basic info (id, email, name, avatar)
    - Subscription tier
    - Timezone preference
    - Account timestamps
    """
    return UserProfileResponse(
        data=UserRead(
            id=str(current_user.id),
            google_id=current_user.google_id,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
            timezone=current_user.timezone,
            tier=current_user.tier,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat(),
        )
    )


# =============================================================================
# T078b: PATCH /api/v1/users/me
# =============================================================================


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the authenticated user's profile (FR-070).",
    responses={
        200: {"description": "Profile updated successfully"},
        400: {"description": "Invalid timezone or name too long"},
        401: {"description": "Authentication required"},
    },
)
@limiter.limit("100/minute")
async def update_current_user_profile(
    request: Request,
    body: UserUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: Settings = Depends(get_settings),
) -> UserProfileResponse:
    """Update the authenticated user's profile.

    PATCH semantics:
    - Omitted fields remain unchanged
    - Only name and timezone can be updated

    Validation:
    - name: 1-100 characters
    - timezone: Valid IANA timezone
    """
    try:
        user_service = UserService(db, settings)

        updated_user = await user_service.update_profile(
            user=current_user,
            name=body.name,
            timezone=body.timezone,
        )

        logger.info(
            "User profile updated",
            extra={
                "user_id": str(updated_user.id),
                "action": "profile_update",
            },
        )

        return UserProfileResponse(
            data=UserRead(
                id=str(updated_user.id),
                google_id=updated_user.google_id,
                email=updated_user.email,
                name=updated_user.name,
                avatar_url=updated_user.avatar_url,
                timezone=updated_user.timezone,
                tier=updated_user.tier,
                created_at=updated_user.created_at.isoformat(),
                updated_at=updated_user.updated_at.isoformat(),
            )
        )

    except InvalidTimezoneError as e:
        raise ValidationError(
            message=str(e),
            details=[{"field": "timezone", "message": str(e)}],
        )
    except InvalidNameError as e:
        raise ValidationError(
            message=str(e),
            details=[{"field": "name", "message": str(e)}],
        )
