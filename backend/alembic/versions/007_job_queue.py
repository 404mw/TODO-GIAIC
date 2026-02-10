"""Job queue and idempotency keys

Revision ID: 007
Revises: 006
Create Date: 2026-01-21

Creates tables for:
- job_queue: Background job processing with SKIP LOCKED pattern
- idempotency_keys: Request idempotency for POST/PATCH operations
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # JOB QUEUE TABLE
    # ==========================================================================
    op.create_table(
        "job_queue",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "completed",
                "failed",
                "dead",
                name="job_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Partial index for pending jobs (optimizes FOR UPDATE SKIP LOCKED queries)
    op.create_index(
        "idx_job_queue_pending",
        "job_queue",
        ["scheduled_at", "priority"],
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index("idx_job_queue_status", "job_queue", ["status"])
    op.create_index("idx_job_queue_job_type", "job_queue", ["job_type"])
    op.create_index(
        "idx_job_queue_failed",
        "job_queue",
        ["job_type", "failed_at"],
        postgresql_where=sa.text("status = 'failed'"),
    )

    # ==========================================================================
    # IDEMPOTENCY KEYS TABLE (FR-059)
    # ==========================================================================
    op.create_table(
        "idempotency_keys",
        sa.Column("key", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("request_path", sa.String(255), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP + INTERVAL '24 hours'"),
        ),
        sa.PrimaryKeyConstraint("key"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_idempotency_keys_user_id", "idempotency_keys", ["user_id"])
    op.create_index(
        "idx_idempotency_keys_cleanup",
        "idempotency_keys",
        ["expires_at"],
        postgresql_where=sa.text("response_status IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
    op.drop_table("job_queue")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS job_status")
