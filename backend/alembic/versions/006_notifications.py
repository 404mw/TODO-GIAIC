"""Notifications and push subscriptions

Revision ID: 006
Revises: 005
Create Date: 2026-01-21

Creates tables for:
- notifications: In-app and push notification records
- push_subscriptions: Browser push notification subscriptions
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # NOTIFICATIONS TABLE
    # ==========================================================================
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "reminder",
                "achievement",
                "subscription",
                "system",
                name="notification_type",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("body", sa.String(500), nullable=False),
        sa.Column("action_url", sa.String(255), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "idx_notifications_user_unread",
        "notifications",
        ["user_id"],
        postgresql_where=sa.text("read = false"),
    )
    op.create_index(
        "idx_notifications_user_created",
        "notifications",
        ["user_id", "created_at"],
    )

    # ==========================================================================
    # PUSH SUBSCRIPTIONS TABLE (FR-028a/FR-028b)
    # ==========================================================================
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("endpoint", sa.String(2048), nullable=False),
        sa.Column("p256dh_key", sa.String(255), nullable=False),
        sa.Column("auth_key", sa.String(255), nullable=False),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.UniqueConstraint("endpoint"),
    )
    op.create_index("idx_push_subscriptions_user_id", "push_subscriptions", ["user_id"])
    op.create_index(
        "idx_push_subscriptions_active",
        "push_subscriptions",
        ["user_id"],
        postgresql_where=sa.text("active = true"),
    )


def downgrade() -> None:
    op.drop_table("push_subscriptions")
    op.drop_table("notifications")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS notification_type")
