"""Achievement models for gamification system.

T036: AchievementDefinition model per data-model.md Entity 7
T037: UserAchievementState model per data-model.md Entity 8
"""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON, Enum as SQLAEnum

from src.models.base import BaseModel, TimestampMixin
from src.schemas.enums import AchievementCategory, PerkType

if TYPE_CHECKING:
    from src.models.user import User


class AchievementDefinition(SQLModel, table=True):
    """Achievement Definition database model.

    Static definition of achievable milestones and their rewards.
    This table is seeded with predefined achievements.

    Per data-model.md Entity 7.
    """

    __tablename__ = "achievement_definitions"

    # Primary key is the achievement code (e.g., "tasks_5")
    id: str = Field(
        primary_key=True,
        nullable=False,
        description="Achievement code (e.g., 'tasks_5')",
    )

    name: str = Field(
        nullable=False,
        description="Display name",
    )
    description: str = Field(
        nullable=False,
        description="How to unlock",
    )
    category: AchievementCategory = Field(
        sa_column=Column(
            SQLAEnum(AchievementCategory, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
        description="Achievement category",
    )
    threshold: int = Field(
        gt=0,
        nullable=False,
        description="Required count/value to unlock",
    )

    # Perk granted on unlock (optional)
    perk_type: PerkType | None = Field(
        default=None,
        sa_column=Column(
            SQLAEnum(PerkType, values_callable=lambda x: [e.value for e in x]),
            nullable=True,
        ),
        description="Type of perk granted",
    )
    perk_value: int | None = Field(
        default=None,
        gt=0,
        description="Perk amount",
    )

    @property
    def perk(self) -> dict | None:
        """Get perk as dictionary if defined."""
        if self.perk_type and self.perk_value:
            return {"type": self.perk_type, "value": self.perk_value}
        return None


# Predefined achievements to seed the database
ACHIEVEMENT_SEED_DATA = [
    {
        "id": "tasks_5",
        "name": "Task Starter",
        "description": "Complete 5 tasks",
        "category": AchievementCategory.TASKS,
        "threshold": 5,
        "perk_type": PerkType.MAX_TASKS,
        "perk_value": 15,
    },
    {
        "id": "tasks_25",
        "name": "Task Master",
        "description": "Complete 25 tasks",
        "category": AchievementCategory.TASKS,
        "threshold": 25,
        "perk_type": PerkType.MAX_TASKS,
        "perk_value": 25,
    },
    {
        "id": "tasks_100",
        "name": "Centurion",
        "description": "Complete 100 tasks",
        "category": AchievementCategory.TASKS,
        "threshold": 100,
        "perk_type": PerkType.MAX_TASKS,
        "perk_value": 50,
    },
    {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "category": AchievementCategory.STREAKS,
        "threshold": 7,
        "perk_type": PerkType.DAILY_CREDITS,
        "perk_value": 2,
    },
    {
        "id": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day streak",
        "category": AchievementCategory.STREAKS,
        "threshold": 30,
        "perk_type": PerkType.DAILY_CREDITS,
        "perk_value": 5,
    },
    {
        "id": "focus_10",
        "name": "Focus Initiate",
        "description": "Complete 10 focus sessions (50%+ of estimated time)",
        "category": AchievementCategory.FOCUS,
        "threshold": 10,
        "perk_type": PerkType.MAX_NOTES,
        "perk_value": 5,
    },
    {
        "id": "notes_10",
        "name": "Note Taker",
        "description": "Convert 10 notes to tasks",
        "category": AchievementCategory.NOTES,
        "threshold": 10,
        "perk_type": PerkType.MAX_NOTES,
        "perk_value": 5,
    },
]


class UserAchievementState(TimestampMixin, table=True):
    """User Achievement State database model.

    Current progress toward achievements and effective limits for a user.

    Per data-model.md Entity 8.
    """

    __tablename__ = "user_achievement_states"

    id: UUID = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="State record ID",
    )

    # Foreign key (one-to-one with User)
    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        nullable=False,
        index=True,
        description="User reference",
    )

    # Lifetime statistics
    lifetime_tasks_completed: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Total tasks ever completed",
    )

    # Streak tracking (FR-043)
    current_streak: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Current daily streak",
    )
    longest_streak: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Best streak achieved",
    )
    last_completion_date: date | None = Field(
        default=None,
        description="Last task completion day (UTC date)",
    )

    # Focus tracking (FR-045)
    focus_completions: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Tasks with 50%+ focus time",
    )

    # Notes tracking
    notes_converted: int = Field(
        default=0,
        ge=0,
        nullable=False,
        description="Notes converted to tasks",
    )

    # Unlocked achievements (array of achievement IDs)
    unlocked_achievements: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, default=list, nullable=False),
        description="Earned achievement IDs",
    )

    # Relationships
    user: "User" = Relationship(back_populates="achievement_state")

    def has_achievement(self, achievement_id: str) -> bool:
        """Check if user has unlocked a specific achievement."""
        return achievement_id in self.unlocked_achievements

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement. Returns True if newly unlocked."""
        if achievement_id not in self.unlocked_achievements:
            self.unlocked_achievements = [*self.unlocked_achievements, achievement_id]
            return True
        return False
