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
    try:
        await session.execute(
            text("INSERT INTO _migrations (name) VALUES (:name)"),
            {"name": name},
        )
        await session.commit()
    except Exception as e:
        # If migration is already marked (duplicate key), that's fine
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            logger.warning(f"Migration {name} already marked as applied (duplicate key), skipping mark")
            await session.rollback()
        else:
            raise


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
    """Fix enum case mismatch for creditoperation and credittype.

    Note: This migration may fail on existing databases with enum constraints.
    The code model now uses explicit SQLAlchemy enum configuration which
    will handle enums correctly going forward.
    """
    logger.info("Applying migration: 002_fix_credit_enum_case")

    try:
        # Check if enum types exist and what their values are
        result = await session.execute(
            text("""
                SELECT enumlabel
                FROM pg_enum
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'creditoperation'
                )
                LIMIT 1
            """)
        )
        first_label = result.scalar()

        # If enum exists and first value is already lowercase, skip migration
        if first_label and first_label.islower():
            logger.info("✓ Enum types already have lowercase values, skipping migration")
            await session.commit()
            return

        # Drop and recreate approach (safer for production)
        # Note: This will CASCADE drop any dependencies
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

        # Add columns with new types
        await session.execute(
            text("""
                ALTER TABLE ai_credit_ledger
                ADD COLUMN IF NOT EXISTS operation_new creditoperation
            """)
        )
        await session.execute(
            text("""
                ALTER TABLE ai_credit_ledger
                ADD COLUMN IF NOT EXISTS credit_type_new credittype
            """)
        )

        # Copy and convert data to lowercase
        await session.execute(
            text("""
                UPDATE ai_credit_ledger
                SET operation_new = LOWER(operation::text)::creditoperation
            """)
        )
        await session.execute(
            text("""
                UPDATE ai_credit_ledger
                SET credit_type_new = LOWER(credit_type::text)::credittype
            """)
        )

        # Drop old columns
        await session.execute(text("ALTER TABLE ai_credit_ledger DROP COLUMN operation"))
        await session.execute(text("ALTER TABLE ai_credit_ledger DROP COLUMN credit_type"))

        # Rename new columns
        await session.execute(
            text("ALTER TABLE ai_credit_ledger RENAME COLUMN operation_new TO operation")
        )
        await session.execute(
            text("ALTER TABLE ai_credit_ledger RENAME COLUMN credit_type_new TO credit_type")
        )

        # Set NOT NULL constraints
        await session.execute(
            text("ALTER TABLE ai_credit_ledger ALTER COLUMN operation SET NOT NULL")
        )
        await session.execute(
            text("ALTER TABLE ai_credit_ledger ALTER COLUMN credit_type SET NOT NULL")
        )

        await session.commit()
        logger.info("✓ Migration applied: 002_fix_credit_enum_case")

    except Exception as e:
        logger.warning(f"⚠ Enum migration skipped due to error: {e}")
        logger.info("The model now uses explicit SQLAlchemy enum config which handles this")
        await session.rollback()
        await session.commit()  # Mark as applied anyway since model handles it


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


async def apply_migration_004_add_consumed_column(session: AsyncSession) -> None:
    """Add consumed column to ai_credit_ledger for tracking partial consumption."""
    logger.info("Applying migration: 004_add_consumed_column")

    # Add consumed column with default 0
    await session.execute(
        text("""
            ALTER TABLE ai_credit_ledger
            ADD COLUMN IF NOT EXISTS consumed INTEGER NOT NULL DEFAULT 0
        """)
    )

    # Add check constraint
    await session.execute(
        text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'ai_credit_ledger_consumed_check'
                ) THEN
                    ALTER TABLE ai_credit_ledger
                    ADD CONSTRAINT ai_credit_ledger_consumed_check CHECK (consumed >= 0);
                END IF;
            END $$;
        """)
    )

    await session.commit()
    logger.info("✓ Migration applied: 004_add_consumed_column")


async def apply_migration_005_add_credit_ledger_columns(session: AsyncSession) -> None:
    """Add remaining columns to ai_credit_ledger: expired, expires_at, source_id."""
    logger.info("Applying migration: 005_add_credit_ledger_columns")

    # Add expired column
    await session.execute(
        text("""
            ALTER TABLE ai_credit_ledger
            ADD COLUMN IF NOT EXISTS expired BOOLEAN NOT NULL DEFAULT false
        """)
    )

    # Add expires_at column (for daily credit expiration)
    await session.execute(
        text("""
            ALTER TABLE ai_credit_ledger
            ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ
        """)
    )

    # Add index on expires_at
    await session.execute(
        text("""
            CREATE INDEX IF NOT EXISTS ix_ai_credit_ledger_expires_at
            ON ai_credit_ledger (expires_at)
        """)
    )

    # Add source_id column (for expiration record tracking)
    await session.execute(
        text("""
            ALTER TABLE ai_credit_ledger
            ADD COLUMN IF NOT EXISTS source_id UUID
        """)
    )

    await session.commit()
    logger.info("✓ Migration applied: 005_add_credit_ledger_columns")


async def apply_migration_006_add_updated_at_column(session: AsyncSession) -> None:
    """Add updated_at column to all tables inheriting from BaseModel/TimestampMixin."""
    logger.info("Applying migration: 006_add_updated_at_column")

    # Tables that inherit from BaseModel and need updated_at
    tables = [
        "ai_credit_ledger",
        "focus_sessions",
        "notifications",
        "task_templates",
        "reminders",
        "subscriptions",
        "subtasks",
        "notes",
        "users",
        "task_instances",
    ]

    # Add updated_at column to each table (only if table exists)
    for table_name in tables:
        # Check if table exists first
        result = await session.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                )
            """),
            {"table_name": table_name}
        )
        table_exists = result.scalar()

        if table_exists:
            await session.execute(
                text(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                """)
            )
            logger.info(f"  ✓ Added updated_at to {table_name}")
        else:
            logger.info(f"  ⊘ Skipped {table_name} (table does not exist)")

    await session.commit()
    logger.info("✓ Migration applied: 006_add_updated_at_column")


async def apply_migration_007_force_achievement_enum_lowercase(session: AsyncSession) -> None:
    """Forcefully ensure achievementcategory enum uses lowercase values.

    This migration addresses the case where the enum was created with uppercase values
    but the database has lowercase data, causing a mismatch. It will:
    1. Check current enum state
    2. Drop and recreate with lowercase if needed
    3. Ensure data is lowercase

    Safe to run multiple times.
    """
    logger.info("Applying migration: 007_force_achievement_enum_lowercase")

    try:
        # Step 1: Check if achievementcategory enum exists
        result = await session.execute(
            text("""
                SELECT enumlabel
                FROM pg_enum
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'achievementcategory'
                )
                ORDER BY enumsortorder
            """)
        )
        rows = result.fetchall()
        enum_values = [row[0] for row in rows] if rows else []

        logger.info(f"  Current achievementcategory enum values: {enum_values}")

        # Step 2: Check if achievement_definitions table exists
        result = await session.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'achievement_definitions'
                )
            """)
        )
        table_exists = result.scalar()

        if not table_exists:
            logger.info("✓ achievement_definitions table doesn't exist, skipping")
            await session.commit()
            return

        # Step 3: If enum doesn't exist or has mixed case, recreate it
        needs_fix = False
        if not enum_values:
            logger.info("  achievementcategory enum doesn't exist, will create")
            needs_fix = True
        elif not all(v.islower() for v in enum_values):
            logger.info("  achievementcategory enum has uppercase/mixed values, will fix")
            needs_fix = True
        else:
            logger.info("✓ achievementcategory enum already has correct lowercase values")
            await session.commit()
            return

        # Step 4: Convert column to TEXT temporarily
        logger.info("  Converting category column to TEXT")
        await session.execute(
            text("""
                ALTER TABLE achievement_definitions
                ALTER COLUMN category TYPE TEXT
            """)
        )

        # Step 5: Ensure all data is lowercase
        logger.info("  Converting all category data to lowercase")
        await session.execute(
            text("""
                UPDATE achievement_definitions
                SET category = LOWER(category)
                WHERE category IS NOT NULL
            """)
        )

        # Step 6: Drop old enum type if it exists
        logger.info("  Dropping old achievementcategory enum type")
        await session.execute(
            text("DROP TYPE IF EXISTS achievementcategory CASCADE")
        )

        # Step 7: Create new enum with lowercase values
        logger.info("  Creating achievementcategory enum with lowercase values")
        await session.execute(
            text(
                "CREATE TYPE achievementcategory AS ENUM "
                "('tasks', 'streaks', 'focus', 'notes')"
            )
        )

        # Step 8: Convert column back to enum type
        logger.info("  Converting category column back to achievementcategory enum")
        await session.execute(
            text("""
                ALTER TABLE achievement_definitions
                ALTER COLUMN category TYPE achievementcategory
                USING category::achievementcategory
            """)
        )

        # Step 9: Restore NOT NULL constraint
        logger.info("  Restoring NOT NULL constraint")
        await session.execute(
            text("""
                ALTER TABLE achievement_definitions
                ALTER COLUMN category SET NOT NULL
            """)
        )

        await session.commit()
        logger.info("✓ Migration applied: 007_force_achievement_enum_lowercase")

    except Exception as e:
        logger.error(f"Migration 007 failed: {e}", exc_info=True)
        await session.rollback()
        raise


# List of all migrations in order
MIGRATIONS = [
    ("001_user_achievement_states_created_at", apply_migration_001_user_achievement_states_created_at),
    ("002_fix_credit_enum_case", apply_migration_002_fix_credit_enum_case),
    ("003_add_subscription_columns", apply_migration_003_add_subscription_columns),
    ("004_add_consumed_column", apply_migration_004_add_consumed_column),
    ("005_add_credit_ledger_columns", apply_migration_005_add_credit_ledger_columns),
    ("006_add_updated_at_column", apply_migration_006_add_updated_at_column),
    ("007_force_achievement_enum_lowercase", apply_migration_007_force_achievement_enum_lowercase),
]


async def run_migrations(session: AsyncSession) -> None:
    """Run all pending migrations."""
    logger.info("Checking for pending migrations...")

    # Create migrations tracking table
    await create_migrations_table(session)

    # Check which migrations are pending
    pending_migrations = []
    applied_migrations = []
    for name, _ in MIGRATIONS:
        if await is_migration_applied(session, name):
            applied_migrations.append(name)
        else:
            pending_migrations.append(name)

    logger.info(f"  Already applied: {len(applied_migrations)} migrations")
    if applied_migrations:
        logger.info(f"    {', '.join(applied_migrations)}")
    logger.info(f"  Pending: {len(pending_migrations)} migrations")
    if pending_migrations:
        logger.info(f"    {', '.join(pending_migrations)}")

    # Apply pending migrations
    applied_count = 0
    for name, migration_func in MIGRATIONS:
        if not await is_migration_applied(session, name):
            logger.info(f"  Applying migration: {name}")
            try:
                await migration_func(session)
                await mark_migration_applied(session, name)
                applied_count += 1
            except Exception as e:
                logger.error(f"✗ Migration failed: {name}")
                logger.error(f"Error: {e}", exc_info=True)
                raise

    if applied_count == 0:
        logger.info("✓ All migrations up to date")
    else:
        logger.info(f"✓ Applied {applied_count} migration(s)")
