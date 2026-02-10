"""Background job for streak calculation.

T208: Implement streak_calculate job (UTC 00:00 daily) per FR-043

This job runs daily at UTC 00:00 to:
- Calculate streaks for all users with activity
- Update current_streak and longest_streak
- Reset broken streaks
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlmodel import select

from src.config import Settings
from src.models.achievement import UserAchievementState
from src.models.task import TaskInstance


logger = logging.getLogger(__name__)


async def handle_streak_calculate(
    payload: dict[str, Any],
    session: AsyncSession,
    settings: Settings,
) -> dict[str, Any]:
    """Calculate daily streaks for all users.

    T208: Streak calculation job

    SC-007: UTC boundary accuracy - streaks calculated at UTC midnight

    A streak is maintained when a user completes at least one task
    on consecutive calendar days (UTC).

    Args:
        payload: Job payload (usually empty for this job)
        session: Database session
        settings: Application settings

    Returns:
        Result dictionary with calculation summary
    """
    now = datetime.now(UTC)
    today = now.date()
    yesterday = today - timedelta(days=1)

    logger.info(f"Starting streak calculation for {today}")

    try:
        # Get all users with achievement states
        query = select(UserAchievementState)
        result = await session.execute(query)
        achievement_states = result.scalars().all()

        if not achievement_states:
            logger.info("No users with achievement states to process")
            return {
                "status": "success",
                "users_processed": 0,
                "streaks_incremented": 0,
                "streaks_reset": 0,
            }

        streaks_incremented = 0
        streaks_reset = 0
        streaks_maintained = 0

        for state in achievement_states:
            # Check if user completed any task yesterday
            completed_yesterday = await _user_completed_task_on_date(
                session, state.user_id, yesterday
            )

            if completed_yesterday:
                # Increment streak
                state.current_streak += 1

                # Update longest streak if needed
                if state.current_streak > state.longest_streak:
                    state.longest_streak = state.current_streak

                state.last_completion_date = yesterday
                session.add(state)
                streaks_incremented += 1

                logger.debug(
                    f"User {state.user_id} streak incremented to {state.current_streak}"
                )

            else:
                # Check if streak should be reset
                # Only reset if they had a streak and didn't complete anything yesterday
                if state.current_streak > 0:
                    # Check when their last activity was
                    last_activity = state.last_completion_date

                    if last_activity:
                        last_activity_date = last_activity
                        days_since = (yesterday - last_activity_date).days

                        if days_since > 0:
                            # Streak is broken
                            old_streak = state.current_streak
                            state.current_streak = 0
                            session.add(state)
                            streaks_reset += 1

                            logger.debug(
                                f"User {state.user_id} streak reset (was {old_streak})"
                            )
                        else:
                            # Last activity was yesterday, streak maintained
                            streaks_maintained += 1
                    else:
                        # No last activity date, reset
                        state.current_streak = 0
                        session.add(state)
                        streaks_reset += 1

        await session.commit()

        users_processed = len(achievement_states)

        logger.info(
            f"Streak calculation complete: {users_processed} users, "
            f"{streaks_incremented} incremented, {streaks_reset} reset, "
            f"{streaks_maintained} maintained"
        )

        return {
            "status": "success",
            "date": str(today),
            "users_processed": users_processed,
            "streaks_incremented": streaks_incremented,
            "streaks_reset": streaks_reset,
            "streaks_maintained": streaks_maintained,
        }

    except Exception as e:
        logger.error(f"Streak calculation failed: {e}", exc_info=True)
        return {
            "status": "retry",
            "error": str(e),
        }


async def _user_completed_task_on_date(
    session: AsyncSession,
    user_id: UUID,
    date: Any,
) -> bool:
    """Check if user completed any task on a specific date.

    Args:
        session: Database session
        user_id: User ID
        date: Date to check (date object)

    Returns:
        True if user completed at least one task on that date
    """
    start_of_day = datetime.combine(date, datetime.min.time()).replace(tzinfo=UTC)
    end_of_day = start_of_day + timedelta(days=1)

    query = select(TaskInstance.id).where(
        TaskInstance.user_id == user_id,
        TaskInstance.completed == True,
        TaskInstance.completed_at >= start_of_day,
        TaskInstance.completed_at < end_of_day,
    ).limit(1)

    result = await session.execute(query)
    return result.scalar_one_or_none() is not None


async def calculate_user_streak(
    session: AsyncSession,
    user_id: UUID,
) -> tuple[int, int]:
    """Calculate current and longest streak for a specific user.

    This is a utility function that can be called on-demand
    to recalculate streaks.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Tuple of (current_streak, longest_streak)
    """
    today = datetime.now(UTC).date()

    # Find all completion dates for this user
    query = text("""
        SELECT DISTINCT DATE(completed_at AT TIME ZONE 'UTC') as completion_date
        FROM task_instances
        WHERE user_id = :user_id
          AND completed = true
          AND completed_at IS NOT NULL
        ORDER BY completion_date DESC
    """)

    result = await session.execute(query, {"user_id": str(user_id)})
    dates = [row[0] for row in result.fetchall()]

    if not dates:
        return 0, 0

    # Calculate current streak
    current_streak = 0
    expected_date = today

    for completion_date in dates:
        # Allow for today or yesterday as starting point
        if expected_date == today and completion_date == today - timedelta(days=1):
            expected_date = today - timedelta(days=1)

        if completion_date == expected_date:
            current_streak += 1
            expected_date = expected_date - timedelta(days=1)
        elif completion_date < expected_date:
            break

    # Calculate longest streak
    longest_streak = 0
    streak = 0
    prev_date = None

    for completion_date in reversed(dates):
        if prev_date is None or completion_date == prev_date + timedelta(days=1):
            streak += 1
        else:
            streak = 1
        prev_date = completion_date
        longest_streak = max(longest_streak, streak)

    return current_streak, longest_streak
