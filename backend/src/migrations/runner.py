"""Database migration runner.

Automatically applies pending migrations on application startup.
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def create_migrations_table(session: AsyncSession) -> None:
    """Create migrations tracking table if it doesn't exist."""
    await session.execute(
        text("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    )
    await session.commit()


async def is_migration_applied(session: AsyncSession, name: str) -> bool:
    """Check if a migration has already been applied."""
    result = await session.execute(
        text("SELECT COUNT(*) FROM _migrations WHERE name = :name"),
        {"name": name},
    )
    count = result.scalar()
    return count > 0


async def mark_migration_applied(session: AsyncSession, name: str) -> None:
    """Mark a migration as applied."""
    await session.execute(
        text("INSERT INTO _migrations (name) VALUES (:name)"),
        {"name": name},
    )
    await session.commit()


async def apply_migration_001_user_achievement_states_created_at(
    session: AsyncSession,
) -> None:
    """Add created_at column to user_achievement_states table."""
    logger.info("Applying migration: 001_user_achievement_states_created_at")

    # Add created_at column
    await session.execute(
        text("""
            ALTER TABLE user_achievement_states
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """)
    )

    # Backfill existing rows
    await session.execute(
        text("""
            UPDATE user_achievement_states
            SET created_at = updated_at
            WHERE created_at = NOW()
        """)
    )

    await session.commit()
    logger.info("✓ Migration applied: 001_user_achievement_states_created_at")


async def apply_migration_002_fix_credit_enum_case(session: AsyncSession) -> None:
    """Fix enum case mismatch for creditoperation and credittype."""
    logger.info("Applying migration: 002_fix_credit_enum_case")

    # Convert columns to text (need explicit cast from enum)
    await session.execute(
        text("ALTER TABLE ai_credit_ledger ALTER COLUMN operation TYPE TEXT USING operation::text")
    )
    await session.execute(
        text("ALTER TABLE ai_credit_ledger ALTER COLUMN credit_type TYPE TEXT USING credit_type::text")
    )

    # Drop old enum types
    await session.execute(text("DROP TYPE IF EXISTS creditoperation CASCADE"))
    await session.execute(text("DROP TYPE IF EXISTS credittype CASCADE"))

    # Create new enum types with lowercase values
    await session.execute(
        text(
            "CREATE TYPE creditoperation AS ENUM "
            "('grant', 'consume', 'expire', 'carryover')"
        )
    )
    await session.execute(
        text(
            "CREATE TYPE credittype AS ENUM "
            "('kickstart', 'daily', 'subscription', 'purchased')"
        )
    )

    # Update data to lowercase
    await session.execute(
        text("UPDATE ai_credit_ledger SET operation = LOWER(operation)")
    )
    await session.execute(
        text("UPDATE ai_credit_ledger SET credit_type = LOWER(credit_type)")
    )

    # Convert back to enum types
    await session.execute(
        text(
            "ALTER TABLE ai_credit_ledger "
            "ALTER COLUMN operation TYPE creditoperation "
            "USING operation::creditoperation"
        )
    )
    await session.execute(
        text(
            "ALTER TABLE ai_credit_ledger "
            "ALTER COLUMN credit_type TYPE credittype "
            "USING credit_type::credittype"
        )
    )

    await session.commit()
    logger.info("✓ Migration applied: 002_fix_credit_enum_case")


async def apply_migration_003_add_subscription_columns(session: AsyncSession) -> None:
    """Add missing payment tracking columns to subscriptions table."""
    logger.info("Applying migration: 003_add_subscription_columns")

    # Add retry_count
    await session.execute(
        text("""
            ALTER TABLE subscriptions
            ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0
        """)
    )

    # Add last_retry_at
    await session.execute(
        text("""
            ALTER TABLE subscriptions
            ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMPTZ
        """)
    )

    # Add last_payment_at
    await session.execute(
        text("""
            ALTER TABLE subscriptions
            ADD COLUMN IF NOT EXISTS last_payment_at TIMESTAMPTZ
        """)
    )

    # Add grace_warning_sent
    await session.execute(
        text("""
            ALTER TABLE subscriptions
            ADD COLUMN IF NOT EXISTS grace_warning_sent BOOLEAN NOT NULL DEFAULT false
        """)
    )

    await session.commit()
    logger.info("✓ Migration applied: 003_add_subscription_columns")


# List of all migrations in order
MIGRATIONS = [
    ("001_user_achievement_states_created_at", apply_migration_001_user_achievement_states_created_at),
    ("002_fix_credit_enum_case", apply_migration_002_fix_credit_enum_case),
    ("003_add_subscription_columns", apply_migration_003_add_subscription_columns),
]


async def run_migrations(session: AsyncSession) -> None:
    """Run all pending migrations."""
    logger.info("Checking for pending migrations...")

    # Create migrations tracking table
    await create_migrations_table(session)

    # Apply pending migrations
    applied_count = 0
    for name, migration_func in MIGRATIONS:
        if not await is_migration_applied(session, name):
            try:
                await migration_func(session)
                await mark_migration_applied(session, name)
                applied_count += 1
            except Exception as e:
                logger.error(f"✗ Migration failed: {name}")
                logger.error(f"Error: {e}")
                raise

    if applied_count == 0:
        logger.info("✓ All migrations up to date")
    else:
        logger.info(f"✓ Applied {applied_count} migration(s)")
