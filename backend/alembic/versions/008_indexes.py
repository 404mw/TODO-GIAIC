"""Additional performance indexes

Revision ID: 008
Revises: 007
Create Date: 2026-01-21

Creates additional indexes for query optimization:
- Composite indexes for common query patterns
- Partial indexes for filtering conditions
- Covering indexes for frequently accessed data
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # TASK INSTANCES INDEXES
    # ==========================================================================

    # Active tasks for a user (not hidden, not archived)
    op.create_index(
        "idx_task_instances_user_active",
        "task_instances",
        ["user_id", "created_at"],
        postgresql_where=sa.text("hidden = false AND archived = false"),
    )

    # Overdue tasks (due_date in past, not completed)
    op.create_index(
        "idx_task_instances_overdue",
        "task_instances",
        ["user_id", "due_date"],
        postgresql_where=sa.text("completed = false AND due_date IS NOT NULL"),
    )

    # Tasks by priority for sorting
    op.create_index(
        "idx_task_instances_user_priority",
        "task_instances",
        ["user_id", "priority", "due_date"],
        postgresql_where=sa.text("hidden = false AND archived = false"),
    )

    # ==========================================================================
    # SUBTASKS INDEXES
    # ==========================================================================

    # Incomplete subtasks for a task (for auto-completion check)
    op.create_index(
        "idx_subtasks_incomplete",
        "subtasks",
        ["task_id"],
        postgresql_where=sa.text("completed = false"),
    )

    # ==========================================================================
    # REMINDERS INDEXES
    # ==========================================================================

    # Upcoming reminders (for scheduler)
    op.create_index(
        "idx_reminders_upcoming",
        "reminders",
        ["scheduled_at"],
        postgresql_where=sa.text("fired = false"),
    )

    # ==========================================================================
    # NOTES INDEXES
    # ==========================================================================

    # Active notes (not archived)
    op.create_index(
        "idx_notes_user_active",
        "notes",
        ["user_id", "created_at"],
        postgresql_where=sa.text("archived = false"),
    )

    # ==========================================================================
    # CREDIT LEDGER INDEXES
    # ==========================================================================

    # Available credits (for FIFO consumption)
    op.create_index(
        "idx_ai_credit_available",
        "ai_credit_ledger",
        ["user_id", "credit_type", "created_at"],
        postgresql_where=sa.text(
            "amount > 0 AND operation = 'grant' AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)"
        ),
    )

    # ==========================================================================
    # ACTIVITY LOGS INDEXES
    # ==========================================================================

    # Recent activity by action type
    op.create_index(
        "idx_activity_logs_action",
        "activity_logs",
        ["action", "created_at"],
    )

    # ==========================================================================
    # DELETION TOMBSTONES INDEXES
    # ==========================================================================

    # User's recoverable items ordered by deletion time
    op.create_index(
        "idx_deletion_tombstones_recoverable",
        "deletion_tombstones",
        ["user_id", "deleted_at"],
    )


def downgrade() -> None:
    # Drop all indexes created in this migration
    op.drop_index("idx_deletion_tombstones_recoverable", table_name="deletion_tombstones")
    op.drop_index("idx_activity_logs_action", table_name="activity_logs")
    op.drop_index("idx_ai_credit_available", table_name="ai_credit_ledger")
    op.drop_index("idx_notes_user_active", table_name="notes")
    op.drop_index("idx_reminders_upcoming", table_name="reminders")
    op.drop_index("idx_subtasks_incomplete", table_name="subtasks")
    op.drop_index("idx_task_instances_user_priority", table_name="task_instances")
    op.drop_index("idx_task_instances_overdue", table_name="task_instances")
    op.drop_index("idx_task_instances_user_active", table_name="task_instances")
