"""Activity logs and deletion tombstones

Revision ID: 005
Revises: 004
Create Date: 2026-01-21

Creates tables for:
- activity_logs: Audit trail of user and system actions
- deletion_tombstones: Serialized deleted entities for recovery
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # ACTIVITY LOGS TABLE
    # ==========================================================================
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "entity_type",
            sa.Enum(
                "task",
                "subtask",
                "note",
                "reminder",
                "achievement",
                "subscription",
                "credit",
                name="entity_type",
            ),
            nullable=False,
        ),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column(
            "source",
            sa.Enum("user", "ai", "system", name="action_source"),
            nullable=False,
        ),
        sa.Column("metadata", sa.JSON(), nullable=True, server_default="{}"),
        sa.Column("request_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index(
        "idx_activity_logs_entity",
        "activity_logs",
        ["entity_type", "entity_id"],
    )
    op.create_index(
        "idx_activity_logs_created_at", "activity_logs", ["created_at"]
    )
    op.create_index(
        "idx_activity_logs_user_created",
        "activity_logs",
        ["user_id", "created_at"],
    )

    # ==========================================================================
    # DELETION TOMBSTONES TABLE
    # ==========================================================================
    op.create_table(
        "deletion_tombstones",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "entity_type",
            sa.Enum("task", "note", name="tombstone_entity_type"),
            nullable=False,
        ),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("entity_data", sa.JSON(), nullable=False),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_deletion_tombstones_user_id", "deletion_tombstones", ["user_id"])
    op.create_index(
        "idx_deletion_tombstones_user_deleted",
        "deletion_tombstones",
        ["user_id", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_table("deletion_tombstones")
    op.drop_table("activity_logs")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS tombstone_entity_type")
    op.execute("DROP TYPE IF EXISTS action_source")
    op.execute("DROP TYPE IF EXISTS entity_type")
