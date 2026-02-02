"""AI credit ledger and subscriptions

Revision ID: 004
Revises: 003
Create Date: 2026-01-21

Creates tables for:
- ai_credit_ledger: Transaction history for credit consumption
- subscriptions: Pro subscription management
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # AI CREDIT LEDGER TABLE
    # ==========================================================================
    op.create_table(
        "ai_credit_ledger",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "credit_type",
            sa.Enum(
                "kickstart", "daily", "subscription", "purchased", name="credit_type"
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column(
            "operation",
            sa.Enum("grant", "consume", "expire", "carryover", name="credit_operation"),
            nullable=False,
        ),
        sa.Column("operation_ref", sa.String(255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_ai_credit_ledger_user_id", "ai_credit_ledger", ["user_id"])
    op.create_index(
        "idx_ai_credit_ledger_user_created",
        "ai_credit_ledger",
        ["user_id", "created_at"],
    )
    op.create_index(
        "idx_ai_credit_ledger_expires_at",
        "ai_credit_ledger",
        ["expires_at"],
        postgresql_where=sa.text("expires_at IS NOT NULL"),
    )

    # ==========================================================================
    # SUBSCRIPTIONS TABLE
    # ==========================================================================
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("checkout_subscription_id", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "past_due",
                "grace",
                "cancelled",
                "expired",
                name="subscription_status",
            ),
            nullable=False,
        ),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("grace_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "failed_payment_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("checkout_subscription_id"),
    )
    op.create_index("idx_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index(
        "idx_subscriptions_checkout_id",
        "subscriptions",
        ["checkout_subscription_id"],
    )
    op.create_index("idx_subscriptions_status", "subscriptions", ["status"])


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("ai_credit_ledger")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS subscription_status")
    op.execute("DROP TYPE IF EXISTS credit_operation")
    op.execute("DROP TYPE IF EXISTS credit_type")
