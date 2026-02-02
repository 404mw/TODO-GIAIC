"""Notes and reminders tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-21

Creates tables for:
- notes: Quick-capture text or voice recordings
- reminders: Scheduled notifications for tasks
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # NOTES TABLE
    # ==========================================================================
    op.create_table(
        "notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.String(2000), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("voice_url", sa.String(2048), nullable=True),
        sa.Column("voice_duration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "transcription_status",
            sa.Enum("pending", "completed", "failed", name="transcription_status"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_notes_user_id", "notes", ["user_id"])
    op.create_index("idx_notes_user_archived", "notes", ["user_id", "archived"])

    # ==========================================================================
    # REMINDERS TABLE
    # ==========================================================================
    op.create_table(
        "reminders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("before", "after", "absolute", name="reminder_type"),
            nullable=False,
        ),
        sa.Column("offset_minutes", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "method",
            sa.Enum("push", "in_app", name="reminder_method"),
            nullable=False,
            server_default="in_app",
        ),
        sa.Column("fired", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("fired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["task_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_reminders_task_id", "reminders", ["task_id"])
    op.create_index("idx_reminders_user_id", "reminders", ["user_id"])
    op.create_index("idx_reminders_scheduled_at", "reminders", ["scheduled_at"])
    op.create_index(
        "idx_reminders_pending",
        "reminders",
        ["scheduled_at"],
        postgresql_where=sa.text("fired = false"),
    )


def downgrade() -> None:
    op.drop_table("reminders")
    op.drop_table("notes")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS reminder_method")
    op.execute("DROP TYPE IF EXISTS reminder_type")
    op.execute("DROP TYPE IF EXISTS transcription_status")
