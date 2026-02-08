"""Tier-based limit calculations with achievement perks.

T135: [US4] Extract subtask limit logic to dedicated utility in src/lib/limits.py
T133: [US4] Add effective_subtask_limit calculation with achievement perks

This module provides centralized limit calculations for:
- Subtasks per task (FR-019)
- Tasks per user
- Notes per user
- AI credits

All limit calculations consider:
1. Base tier limits (Free vs Pro)
2. Achievement perks (from UserAchievementState)
"""

from typing import TYPE_CHECKING

from src.schemas.enums import PerkType, UserTier

if TYPE_CHECKING:
    from src.models.achievement import UserAchievementState


# =============================================================================
# BASE LIMITS BY TIER
# =============================================================================

# Subtask limits (FR-019)
FREE_TIER_SUBTASK_LIMIT = 4
PRO_TIER_SUBTASK_LIMIT = 10

# Task limits (per data-model.md)
FREE_TIER_TASK_LIMIT = 50
PRO_TIER_TASK_LIMIT = 200

# Note limits (per data-model.md)
FREE_TIER_NOTE_LIMIT = 10
PRO_TIER_NOTE_LIMIT = 25

# Description limits
FREE_TIER_DESCRIPTION_LIMIT = 1000
PRO_TIER_DESCRIPTION_LIMIT = 2000

# AI Credits
FREE_TIER_DAILY_CREDITS = 0
PRO_TIER_DAILY_CREDITS = 10


# =============================================================================
# EFFECTIVE LIMIT CALCULATIONS
# =============================================================================


def get_base_subtask_limit(tier: UserTier) -> int:
    """Get base subtask limit for a tier.

    Args:
        tier: User's subscription tier

    Returns:
        Maximum subtasks allowed per task for the tier
    """
    return PRO_TIER_SUBTASK_LIMIT if tier == UserTier.PRO else FREE_TIER_SUBTASK_LIMIT


def get_effective_subtask_limit(
    tier: UserTier,
    achievement_state: "UserAchievementState | None" = None,
) -> int:
    """Calculate effective subtask limit including achievement perks.

    T133: Add effective_subtask_limit calculation with achievement perks

    Currently, no achievements grant subtask limit perks, but this function
    is designed for future extensibility.

    Args:
        tier: User's subscription tier
        achievement_state: User's achievement state (optional)

    Returns:
        Effective maximum subtasks allowed per task

    Note:
        Per data-model.md, current achievement perks affect:
        - MAX_TASKS: +15/+25/+50 (tasks_5, tasks_25, tasks_100)
        - MAX_NOTES: +5/+5 (focus_10, notes_10)
        - DAILY_CREDITS: +2/+5 (streak_7, streak_30)

        No achievements currently grant MAX_SUBTASKS perks.
        This function is prepared for future extensibility.
    """
    base_limit = get_base_subtask_limit(tier)

    # Currently no achievements grant subtask perks
    # This is prepared for future extensibility
    perk_bonus = 0

    if achievement_state:
        # Future: Sum up any MAX_SUBTASKS perks from achievements
        # For now, subtask limits are tier-based only
        # Note: PerkType.MAX_SUBTASKS doesn't exist yet - prepared for extensibility
        pass

    return base_limit + perk_bonus


def get_base_task_limit(tier: UserTier) -> int:
    """Get base task limit for a tier.

    Args:
        tier: User's subscription tier

    Returns:
        Maximum tasks allowed for the tier
    """
    return PRO_TIER_TASK_LIMIT if tier == UserTier.PRO else FREE_TIER_TASK_LIMIT


def get_effective_task_limit(
    tier: UserTier,
    achievement_state: "UserAchievementState | None" = None,
) -> int:
    """Calculate effective task limit including achievement perks.

    Args:
        tier: User's subscription tier
        achievement_state: User's achievement state (optional)

    Returns:
        Effective maximum tasks allowed
    """
    base_limit = get_base_task_limit(tier)

    perk_bonus = 0
    if achievement_state:
        perk_bonus = _calculate_perk_bonus(achievement_state, PerkType.MAX_TASKS)

    return base_limit + perk_bonus


def get_base_note_limit(tier: UserTier) -> int:
    """Get base note limit for a tier.

    Args:
        tier: User's subscription tier

    Returns:
        Maximum notes allowed for the tier
    """
    return PRO_TIER_NOTE_LIMIT if tier == UserTier.PRO else FREE_TIER_NOTE_LIMIT


def get_effective_note_limit(
    tier: UserTier,
    achievement_state: "UserAchievementState | None" = None,
) -> int:
    """Calculate effective note limit including achievement perks.

    Args:
        tier: User's subscription tier
        achievement_state: User's achievement state (optional)

    Returns:
        Effective maximum notes allowed
    """
    base_limit = get_base_note_limit(tier)

    perk_bonus = 0
    if achievement_state:
        perk_bonus = _calculate_perk_bonus(achievement_state, PerkType.MAX_NOTES)

    return base_limit + perk_bonus


def get_base_daily_credits(tier: UserTier) -> int:
    """Get base daily AI credits for a tier.

    Args:
        tier: User's subscription tier

    Returns:
        Daily AI credits for the tier
    """
    return PRO_TIER_DAILY_CREDITS if tier == UserTier.PRO else FREE_TIER_DAILY_CREDITS


def get_effective_daily_credits(
    tier: UserTier,
    achievement_state: "UserAchievementState | None" = None,
) -> int:
    """Calculate effective daily AI credits including achievement perks.

    Args:
        tier: User's subscription tier
        achievement_state: User's achievement state (optional)

    Returns:
        Effective daily AI credits
    """
    base_credits = get_base_daily_credits(tier)

    perk_bonus = 0
    if achievement_state:
        perk_bonus = _calculate_perk_bonus(achievement_state, PerkType.DAILY_CREDITS)

    return base_credits + perk_bonus


def get_description_limit(tier: UserTier) -> int:
    """Get description character limit for a tier.

    Args:
        tier: User's subscription tier

    Returns:
        Maximum description length in characters
    """
    return PRO_TIER_DESCRIPTION_LIMIT if tier == UserTier.PRO else FREE_TIER_DESCRIPTION_LIMIT


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _calculate_perk_bonus(
    achievement_state: "UserAchievementState",
    perk_type: PerkType | None,
) -> int:
    """Calculate total perk bonus for a specific perk type.

    Sums up all perks of the given type from unlocked achievements.

    Args:
        achievement_state: User's achievement state
        perk_type: Type of perk to sum

    Returns:
        Total bonus from all matching perks
    """
    if perk_type is None:
        return 0

    from src.models.achievement import ACHIEVEMENT_SEED_DATA

    bonus = 0
    for achievement in ACHIEVEMENT_SEED_DATA:
        if achievement["id"] in achievement_state.unlocked_achievements:
            if achievement.get("perk_type") == perk_type:
                bonus += achievement.get("perk_value", 0)

    return bonus


# =============================================================================
# EFFECTIVE LIMITS DATA CLASS
# =============================================================================


class EffectiveLimits:
    """Container for all effective limits for a user.

    Provides a convenient way to access all limits at once.
    """

    def __init__(
        self,
        tier: UserTier,
        achievement_state: "UserAchievementState | None" = None,
    ):
        """Initialize effective limits.

        Args:
            tier: User's subscription tier
            achievement_state: User's achievement state (optional)
        """
        self.tier = tier
        self.achievement_state = achievement_state

    @property
    def subtasks_per_task(self) -> int:
        """Effective subtask limit per task."""
        return get_effective_subtask_limit(self.tier, self.achievement_state)

    @property
    def max_tasks(self) -> int:
        """Effective maximum tasks."""
        return get_effective_task_limit(self.tier, self.achievement_state)

    @property
    def max_notes(self) -> int:
        """Effective maximum notes."""
        return get_effective_note_limit(self.tier, self.achievement_state)

    @property
    def daily_credits(self) -> int:
        """Effective daily AI credits."""
        return get_effective_daily_credits(self.tier, self.achievement_state)

    @property
    def description_length(self) -> int:
        """Effective description character limit."""
        return get_description_limit(self.tier)

    def to_dict(self) -> dict:
        """Convert limits to dictionary.

        Returns:
            Dictionary with all effective limits
        """
        return {
            "tier": self.tier.value,
            "subtasks_per_task": self.subtasks_per_task,
            "max_tasks": self.max_tasks,
            "max_notes": self.max_notes,
            "daily_credits": self.daily_credits,
            "description_length": self.description_length,
        }
