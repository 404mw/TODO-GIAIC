"""Achievement API endpoints.

Phase 15: User Story 9 - Achievement System

T303: Implement GET /api/v1/achievements per api-specification.md Section 8.1
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import get_current_user, get_db_session as get_db
from src.models.user import User
from src.schemas.achievement import (
    AchievementResponse,
    EffectiveLimitsResponse,
    UserStatsResponse,
)
from src.services.achievement_service import get_achievement_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get(
    "",
    response_model=AchievementResponse,
    summary="Get user achievements",
    description="""
    Retrieve the authenticated user's achievement data including:
    - User stats (lifetime tasks, streak, focus completions, notes converted)
    - List of unlocked achievements with perks
    - Progress toward all achievements
    - Effective limits based on tier and achievement perks

    Per api-specification.md Section 8.1.
    """,
)
async def get_achievements(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AchievementResponse:
    """Get user achievements, stats, progress, and effective limits.

    T303: GET /api/v1/achievements

    Returns:
        AchievementResponse with stats, unlocked, progress, effective_limits
    """
    service = get_achievement_service(session, settings)

    response = await service.get_achievement_response(
        user_id=current_user.id,
        tier=current_user.tier,
    )

    logger.debug(
        f"Retrieved achievements for user {current_user.id}: "
        f"{len(response.unlocked)} unlocked, streak={response.stats.current_streak}"
    )

    return response


@router.get(
    "/me",
    response_model=AchievementResponse,
    summary="Get current user's achievements",
    description="""
    Alias for GET /achievements - retrieves the authenticated user's achievement data.

    Returns same data as the root achievements endpoint.
    Per API.md documentation.
    """,
)
async def get_my_achievements(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AchievementResponse:
    """Get current user's achievements (alias endpoint).

    Returns:
        AchievementResponse with stats, unlocked, progress, effective_limits
    """
    service = get_achievement_service(session, settings)

    response = await service.get_achievement_response(
        user_id=current_user.id,
        tier=current_user.tier,
    )

    logger.debug(
        f"Retrieved achievements via /me for user {current_user.id}: "
        f"{len(response.unlocked)} unlocked, streak={response.stats.current_streak}"
    )

    return response


@router.get(
    "/stats",
    response_model=UserStatsResponse,
    summary="Get user stats",
    description="Retrieve just the user's achievement statistics.",
)
async def get_user_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserStatsResponse:
    """Get user achievement stats only.

    Returns:
        UserStatsResponse with stats
    """
    service = get_achievement_service(session, settings)

    response = await service.get_achievement_response(
        user_id=current_user.id,
        tier=current_user.tier,
    )

    return UserStatsResponse(stats=response.stats)


@router.get(
    "/limits",
    response_model=EffectiveLimitsResponse,
    summary="Get effective limits",
    description="""
    Retrieve the user's effective limits based on their tier and achievement perks.

    Per FR-046: Effective limits = base tier limits + achievement perks.
    """,
)
async def get_effective_limits(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> EffectiveLimitsResponse:
    """Get user's effective limits.

    Returns:
        EffectiveLimitsResponse with effective_limits
    """
    service = get_achievement_service(session, settings)

    state = await service.get_or_create_achievement_state(current_user.id)
    limits = await service.calculate_effective_limits(current_user.tier, state)

    return EffectiveLimitsResponse(effective_limits=limits)
