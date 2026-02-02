"""Achievement service for gamification system.

Phase 15: User Story 9 - Achievement System (FR-043 to FR-046)

T298: Implement AchievementService.check_and_unlock with all achievement types
T299: Implement AchievementService.update_streak on task completion (FR-043)
T300: Implement AchievementService.calculate_effective_limits (FR-046)
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import Settings
from src.lib.limits import (
    get_effective_daily_credits,
    get_effective_note_limit,
    get_effective_task_limit,
)
from src.models.achievement import (
    AchievementDefinition,
    ACHIEVEMENT_SEED_DATA,
    UserAchievementState,
)
from src.schemas.achievement import (
    AchievementPerk,
    AchievementProgress,
    AchievementResponse,
    EffectiveLimits,
    UnlockedAchievement,
    UserStats,
)
from src.schemas.enums import AchievementCategory, PerkType, UserTier

if TYPE_CHECKING:
    from src.models.task import TaskInstance


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AchievementServiceError(Exception):
    """Base exception for achievement service errors."""

    pass


class AchievementStateNotFoundError(AchievementServiceError):
    """Raised when user's achievement state is not found."""

    pass


# =============================================================================
# ACHIEVEMENT SERVICE
# =============================================================================


class AchievementService:
    """Service for achievement and streak operations.

    Handles:
    - Streak tracking and calculation (FR-043)
    - Achievement unlock checking (FR-044)
    - Focus completion tracking (FR-045)
    - Effective limits calculation (FR-046)
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    # =========================================================================
    # STREAK MANAGEMENT (T299, FR-043)
    # =========================================================================

    async def update_streak(
        self,
        achievement_state: UserAchievementState,
        completion_time: datetime,
    ) -> UserAchievementState:
        """Update streak on task completion.

        T299: Implement AchievementService.update_streak

        FR-043: Streak calculation uses UTC calendar days with ≥1 task completed.

        Args:
            achievement_state: User's current achievement state
            completion_time: When the task was completed

        Returns:
            Updated UserAchievementState
        """
        # Normalize to UTC date
        if completion_time.tzinfo is None:
            # Treat naive datetime as UTC
            completion_date = completion_time.date()
        else:
            # Convert to UTC and get date
            utc_time = completion_time.astimezone(timezone.utc)
            completion_date = utc_time.date()

        last_date = achievement_state.last_completion_date

        if last_date is None:
            # First ever completion - start streak
            achievement_state.current_streak = 1
            achievement_state.longest_streak = max(
                achievement_state.longest_streak, 1
            )
        elif completion_date == last_date:
            # Same day - no change to streak
            pass
        elif completion_date == last_date + timedelta(days=1):
            # Consecutive day - increment streak
            achievement_state.current_streak += 1
            achievement_state.longest_streak = max(
                achievement_state.longest_streak,
                achievement_state.current_streak,
            )
        else:
            # Missed at least one day - reset streak
            logger.info(
                f"Streak reset: last completion {last_date}, "
                f"new completion {completion_date}"
            )
            achievement_state.current_streak = 1

        # Update last completion date
        achievement_state.last_completion_date = completion_date

        self.session.add(achievement_state)
        await self.session.flush()

        return achievement_state

    # =========================================================================
    # ACHIEVEMENT UNLOCKING (T298, FR-044)
    # =========================================================================

    async def check_and_unlock(
        self,
        achievement_state: UserAchievementState,
    ) -> list[dict]:
        """Check and unlock any achievements the user qualifies for.

        T298: Implement AchievementService.check_and_unlock

        FR-044: Achievement unlock is permanent - perks are never revoked.

        Args:
            achievement_state: User's current achievement state

        Returns:
            List of newly unlocked achievements with their details
        """
        newly_unlocked = []

        for achievement_data in ACHIEVEMENT_SEED_DATA:
            achievement_id = achievement_data["id"]

            # Skip if already unlocked
            if achievement_id in achievement_state.unlocked_achievements:
                continue

            # Check if user qualifies
            qualifies = self._check_qualification(
                achievement_state, achievement_data
            )

            if qualifies:
                # Unlock the achievement
                achievement_state.unlock_achievement(achievement_id)

                newly_unlocked.append({
                    "id": achievement_id,
                    "name": achievement_data["name"],
                    "description": achievement_data["description"],
                    "perk": {
                        "type": achievement_data.get("perk_type"),
                        "value": achievement_data.get("perk_value"),
                    }
                    if achievement_data.get("perk_type")
                    else None,
                })

                logger.info(
                    f"Achievement unlocked: {achievement_id} for user "
                    f"{achievement_state.user_id}"
                )

        if newly_unlocked:
            self.session.add(achievement_state)
            await self.session.flush()

        return newly_unlocked

    def _check_qualification(
        self,
        state: UserAchievementState,
        achievement_data: dict,
    ) -> bool:
        """Check if user qualifies for an achievement.

        Args:
            state: User's achievement state
            achievement_data: Achievement definition data

        Returns:
            True if user qualifies, False otherwise
        """
        category = achievement_data["category"]
        threshold = achievement_data["threshold"]

        if category == AchievementCategory.TASKS:
            return state.lifetime_tasks_completed >= threshold
        elif category == AchievementCategory.STREAKS:
            # Check against longest streak (not current, as current resets)
            return state.longest_streak >= threshold
        elif category == AchievementCategory.FOCUS:
            return state.focus_completions >= threshold
        elif category == AchievementCategory.NOTES:
            return state.notes_converted >= threshold

        return False

    async def increment_lifetime_tasks(
        self,
        achievement_state: UserAchievementState,
    ) -> UserAchievementState:
        """Increment lifetime tasks completed counter.

        Args:
            achievement_state: User's achievement state

        Returns:
            Updated achievement state
        """
        achievement_state.lifetime_tasks_completed += 1
        self.session.add(achievement_state)
        await self.session.flush()
        return achievement_state

    async def increment_focus_completions(
        self,
        achievement_state: UserAchievementState,
    ) -> UserAchievementState:
        """Increment focus completions counter.

        Args:
            achievement_state: User's achievement state

        Returns:
            Updated achievement state
        """
        achievement_state.focus_completions += 1
        self.session.add(achievement_state)
        await self.session.flush()
        return achievement_state

    async def increment_notes_converted(
        self,
        achievement_state: UserAchievementState,
    ) -> UserAchievementState:
        """Increment notes converted counter.

        Args:
            achievement_state: User's achievement state

        Returns:
            Updated achievement state
        """
        achievement_state.notes_converted += 1
        self.session.add(achievement_state)
        await self.session.flush()
        return achievement_state

    # =========================================================================
    # FOCUS COMPLETION TRACKING (FR-045)
    # =========================================================================

    def is_focus_completion(self, task: "TaskInstance") -> bool:
        """Check if a completed task qualifies as a focus completion.

        FR-045: Track focus mode completion (≥50% of estimated duration in focus).

        A task is a focus completion if:
        - It has an estimated duration
        - User spent ≥50% of the estimated time in focus mode

        Args:
            task: The completed task

        Returns:
            True if task qualifies as focus completion
        """
        if task.estimated_duration is None:
            return False

        if task.focus_time_seconds is None or task.focus_time_seconds == 0:
            return False

        # Convert estimated duration (minutes) to seconds
        estimated_seconds = task.estimated_duration * 60

        # Calculate percentage
        focus_percentage = task.focus_time_seconds / estimated_seconds

        return focus_percentage >= 0.5

    # =========================================================================
    # EFFECTIVE LIMITS CALCULATION (T300, FR-046)
    # =========================================================================

    async def calculate_effective_limits(
        self,
        tier: UserTier,
        achievement_state: UserAchievementState | None,
    ) -> EffectiveLimits:
        """Calculate effective limits for a user based on tier and achievements.

        T300: Implement AchievementService.calculate_effective_limits

        FR-046: Effective limits = base tier limits + achievement perks.

        Args:
            tier: User's subscription tier
            achievement_state: User's achievement state (optional)

        Returns:
            EffectiveLimits with max_tasks, max_notes, daily_ai_credits
        """
        return EffectiveLimits(
            max_tasks=get_effective_task_limit(tier, achievement_state),
            max_notes=get_effective_note_limit(tier, achievement_state),
            daily_ai_credits=get_effective_daily_credits(tier, achievement_state),
        )

    # =========================================================================
    # ACHIEVEMENT STATE MANAGEMENT
    # =========================================================================

    async def get_or_create_achievement_state(
        self,
        user_id: UUID,
    ) -> UserAchievementState:
        """Get or create achievement state for a user.

        Args:
            user_id: The user's ID

        Returns:
            UserAchievementState
        """
        query = select(UserAchievementState).where(
            UserAchievementState.user_id == user_id
        )
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if state is None:
            state = UserAchievementState(
                id=uuid4(),
                user_id=user_id,
                lifetime_tasks_completed=0,
                current_streak=0,
                longest_streak=0,
                last_completion_date=None,
                focus_completions=0,
                notes_converted=0,
                unlocked_achievements=[],
            )
            self.session.add(state)
            await self.session.flush()
            await self.session.refresh(state)

        return state

    async def get_achievement_state(
        self,
        user_id: UUID,
    ) -> UserAchievementState:
        """Get achievement state for a user.

        Args:
            user_id: The user's ID

        Returns:
            UserAchievementState

        Raises:
            AchievementStateNotFoundError: If state not found
        """
        query = select(UserAchievementState).where(
            UserAchievementState.user_id == user_id
        )
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if state is None:
            raise AchievementStateNotFoundError(
                f"Achievement state not found for user {user_id}"
            )

        return state

    # =========================================================================
    # FULL ACHIEVEMENT RESPONSE
    # =========================================================================

    async def get_achievement_response(
        self,
        user_id: UUID,
        tier: UserTier,
    ) -> AchievementResponse:
        """Get full achievement response for API endpoint.

        Args:
            user_id: The user's ID
            tier: User's subscription tier

        Returns:
            AchievementResponse with stats, unlocked, progress, effective_limits
        """
        state = await self.get_or_create_achievement_state(user_id)

        # Build stats
        stats = UserStats(
            lifetime_tasks_completed=state.lifetime_tasks_completed,
            current_streak=state.current_streak,
            longest_streak=state.longest_streak,
            focus_completions=state.focus_completions,
            notes_converted=state.notes_converted,
        )

        # Build unlocked achievements list
        unlocked = []
        for achievement_data in ACHIEVEMENT_SEED_DATA:
            if achievement_data["id"] in state.unlocked_achievements:
                perk = None
                if achievement_data.get("perk_type"):
                    perk = AchievementPerk(
                        type=achievement_data["perk_type"],
                        value=achievement_data["perk_value"],
                    )

                unlocked.append(
                    UnlockedAchievement(
                        id=achievement_data["id"],
                        name=achievement_data["name"],
                        description=achievement_data["description"],
                        unlocked_at=state.updated_at,  # Approximation
                        perk=perk,
                    )
                )

        # Build progress for all achievements
        progress = []
        for achievement_data in ACHIEVEMENT_SEED_DATA:
            current = self._get_progress_value(state, achievement_data)
            progress.append(
                AchievementProgress(
                    id=achievement_data["id"],
                    name=achievement_data["name"],
                    current=current,
                    threshold=achievement_data["threshold"],
                    unlocked=achievement_data["id"] in state.unlocked_achievements,
                )
            )

        # Calculate effective limits
        effective_limits = await self.calculate_effective_limits(tier, state)

        return AchievementResponse(
            stats=stats,
            unlocked=unlocked,
            progress=progress,
            effective_limits=effective_limits,
        )

    def _get_progress_value(
        self,
        state: UserAchievementState,
        achievement_data: dict,
    ) -> int:
        """Get current progress value for an achievement.

        Args:
            state: User's achievement state
            achievement_data: Achievement definition

        Returns:
            Current progress value
        """
        category = achievement_data["category"]

        if category == AchievementCategory.TASKS:
            return state.lifetime_tasks_completed
        elif category == AchievementCategory.STREAKS:
            return state.longest_streak
        elif category == AchievementCategory.FOCUS:
            return state.focus_completions
        elif category == AchievementCategory.NOTES:
            return state.notes_converted

        return 0


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_achievement_service(
    session: AsyncSession,
    settings: Settings,
) -> AchievementService:
    """Get an AchievementService instance."""
    return AchievementService(session, settings)
