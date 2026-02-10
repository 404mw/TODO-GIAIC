"""Initial schema - Users, task_instances, task_templates, subtasks

Revision ID: 001
Revises: None
Create Date: 2026-01-21

Creates the core tables for:
- users: User accounts with Google OAuth integration
- task_instances: Concrete task occurrences
- task_templates: Recurring task definitions
- subtasks: Child items of tasks
- refresh_tokens: JWT refresh token storage
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # USERS TABLE
    # ==========================================================================
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("google_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column(
            "tier",
            sa.Enum("free", "pro", name="user_tier"),
            nullable=False,
            server_default="free",
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
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_users_google_id", "users", ["google_id"], unique=True)
    op.create_index("idx_users_email", "users", ["email"], unique=True)

    # ==========================================================================
    # TASK TEMPLATES TABLE (for recurring tasks)
    # ==========================================================================
    op.create_table(
        "task_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True, server_default=""),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="task_priority"),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("estimated_duration", sa.Integer(), nullable=True),
        sa.Column("rrule", sa.String(500), nullable=False),
        sa.Column("next_due", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
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
    op.create_index("idx_task_templates_user_id", "task_templates", ["user_id"])

    # ==========================================================================
    # TASK INSTANCES TABLE
    # ==========================================================================
    op.create_table(
        "task_instances",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True, server_default=""),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="task_priority", create_type=False),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_duration", sa.Integer(), nullable=True),
        sa.Column("focus_time_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "completed_by",
            sa.Enum("manual", "auto", "force", name="completed_by"),
            nullable=True,
        ),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
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
        sa.ForeignKeyConstraint(
            ["template_id"], ["task_templates.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("idx_task_instances_user_id", "task_instances", ["user_id"])
    op.create_index(
        "idx_task_instances_user_completed",
        "task_instances",
        ["user_id", "completed"],
    )
    op.create_index("idx_task_instances_template_id", "task_instances", ["template_id"])
    op.create_index("idx_task_instances_due_date", "task_instances", ["due_date"])

    # ==========================================================================
    # SUBTASKS TABLE
    # ==========================================================================
    op.create_table(
        "subtasks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "source",
            sa.Enum("user", "ai", name="subtask_source"),
            nullable=False,
            server_default="user",
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
        sa.ForeignKeyConstraint(["task_id"], ["task_instances.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_subtasks_task_id", "subtasks", ["task_id"])
    op.create_index("idx_subtasks_task_order", "subtasks", ["task_id", "order_index"])

    # ==========================================================================
    # REFRESH TOKENS TABLE
    # ==========================================================================
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("subtasks")
    op.drop_table("task_instances")
    op.drop_table("task_templates")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS subtask_source")
    op.execute("DROP TYPE IF EXISTS completed_by")
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS user_tier")
