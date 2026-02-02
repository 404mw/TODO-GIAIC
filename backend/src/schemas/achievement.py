"""Achievement schemas for gamification system.

T052: Achievement schemas per api-specification.md Section 9
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.enums import PerkType


class AchievementPerk(BaseModel):
    """Perk granted by an achievement."""

    type: PerkType = Field(description="Perk type")
    value: int = Field(description="Perk value")


class UnlockedAchievement(BaseModel):
    """Achievement that has been unlocked."""

    id: str = Field(description="Achievement ID (e.g., 'tasks_25')")
    name: str = Field(description="Achievement name")
    description: str = Field(description="How to unlock")
    unlocked_at: datetime = Field(description="When achievement was unlocked")
    perk: AchievementPerk | None = Field(
        default=None,
        description="Perk granted by achievement",
    )


class AchievementProgress(BaseModel):
    """Progress toward an achievement."""

    id: str = Field(description="Achievement ID")
    name: str = Field(description="Achievement name")
    current: int = Field(description="Current progress value")
    threshold: int = Field(description="Required value to unlock")
    unlocked: bool = Field(description="Whether achievement is unlocked")


class UserStats(BaseModel):
    """User statistics for achievement tracking."""

    lifetime_tasks_completed: int = Field(description="Total tasks completed")
    current_streak: int = Field(description="Current daily streak")
    longest_streak: int = Field(description="Best streak achieved")
    focus_completions: int = Field(description="Tasks with 50%+ focus time")
    notes_converted: int = Field(description="Notes converted to tasks")


class EffectiveLimits(BaseModel):
    """User's effective limits after applying achievement perks.

    Per FR-046.
    """

    max_tasks: int = Field(description="Maximum tasks allowed")
    max_notes: int = Field(description="Maximum notes allowed")
    daily_ai_credits: int = Field(description="Daily AI credits")


class AchievementResponse(BaseModel):
    """Full achievement response.

    Per api-specification.md Section 9.1.
    """

    stats: UserStats = Field(description="User statistics")
    unlocked: list[UnlockedAchievement] = Field(
        description="Unlocked achievements"
    )
    progress: list[AchievementProgress] = Field(
        description="Progress toward all achievements",
    )
    effective_limits: EffectiveLimits = Field(
        description="User's effective limits",
    )


class UserStatsResponse(BaseModel):
    """Response containing just user stats."""

    stats: UserStats = Field(description="User statistics")


class EffectiveLimitsResponse(BaseModel):
    """Response containing just effective limits."""

    effective_limits: EffectiveLimits = Field(
        description="User's effective limits",
    )
