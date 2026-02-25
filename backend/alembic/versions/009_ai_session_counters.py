"""AI session counters + focus session goal duration

Revision ID: 009
Revises: 008
Create Date: 2026-02-24

Creates:
- ai_session_counters table (Task 4.3a): DB-backed AI rate-limit counters
  for multi-process safety (replaces in-memory _task_request_counters dict)

Modifies:
- focus_sessions table: adds goal_duration_minutes column (Task 5.5)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # AI SESSION COUNTERS (Task 4.3a)
    # ==========================================================================

    op.create_table(
        "ai_session_counters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Composite unique constraint enabling ON CONFLICT DO UPDATE upsert
    op.create_index(
        "uq_ai_session_task",
        "ai_session_counters",
        ["session_id", "task_id"],
        unique=True,
    )

    # Individual indexes for fast lookups
    op.create_index(
        "ix_ai_session_counters_session_id",
        "ai_session_counters",
        ["session_id"],
    )
    op.create_index(
        "ix_ai_session_counters_expires_at",
        "ai_session_counters",
        ["expires_at"],
    )

    # ==========================================================================
    # FOCUS SESSIONS — ADD GOAL DURATION (Task 5.5)
    # ==========================================================================

    op.add_column(
        "focus_sessions",
        sa.Column(
            "goal_duration_minutes",
            sa.Integer(),
            nullable=True,
            comment="User-set focus goal in minutes (stored only; does not trigger auto-stop)",
        ),
    )


def downgrade() -> None:
    # Remove focus_sessions column
    op.drop_column("focus_sessions", "goal_duration_minutes")

    # Drop ai_session_counters table
    op.drop_index("ix_ai_session_counters_expires_at", table_name="ai_session_counters")
    op.drop_index("ix_ai_session_counters_session_id", table_name="ai_session_counters")
    op.drop_index("uq_ai_session_task", table_name="ai_session_counters")
    op.drop_table("ai_session_counters")
