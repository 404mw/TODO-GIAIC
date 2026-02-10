"""Achievement definitions and user achievement states

Revision ID: 003
Revises: 002
Create Date: 2026-01-21

Creates tables for:
- achievement_definitions: Static achievement definitions with rewards
- user_achievement_states: User progress and unlocked achievements
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # ACHIEVEMENT DEFINITIONS TABLE (seed data)
    # ==========================================================================
    op.create_table(
        "achievement_definitions",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column(
            "category",
            sa.Enum("tasks", "streaks", "focus", "notes", name="achievement_category"),
            nullable=False,
        ),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column(
            "perk_type",
            sa.Enum("max_tasks", "max_notes", "daily_credits", name="perk_type"),
            nullable=True,
        ),
        sa.Column("perk_value", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Insert seed data for achievement definitions
    op.execute(
        """
        INSERT INTO achievement_definitions (id, name, description, category, threshold, perk_type, perk_value)
        VALUES
            ('tasks_5', 'Task Starter', 'Complete 5 tasks', 'tasks', 5, 'max_tasks', 15),
            ('tasks_25', 'Task Master', 'Complete 25 tasks', 'tasks', 25, 'max_tasks', 25),
            ('tasks_100', 'Centurion', 'Complete 100 tasks', 'tasks', 100, 'max_tasks', 50),
            ('streak_7', 'Week Warrior', 'Maintain a 7-day streak', 'streaks', 7, 'daily_credits', 2),
            ('streak_30', 'Monthly Master', 'Maintain a 30-day streak', 'streaks', 30, 'daily_credits', 5),
            ('focus_10', 'Focus Initiate', 'Complete 10 focus sessions', 'focus', 10, 'max_notes', 5),
            ('notes_10', 'Note Taker', 'Convert 10 notes to tasks', 'notes', 10, 'max_notes', 5)
        """
    )

    # ==========================================================================
    # USER ACHIEVEMENT STATES TABLE
    # ==========================================================================
    op.create_table(
        "user_achievement_states",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "lifetime_tasks_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_completion_date", sa.Date(), nullable=True),
        sa.Column("focus_completions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes_converted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unlocked_achievements", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "idx_user_achievement_states_user_id", "user_achievement_states", ["user_id"]
    )


def downgrade() -> None:
    op.drop_table("user_achievement_states")
    op.drop_table("achievement_definitions")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS perk_type")
    op.execute("DROP TYPE IF EXISTS achievement_category")
