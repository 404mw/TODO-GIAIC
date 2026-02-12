"""Main API router aggregating all sub-routers.

T367: Create main API router aggregating all sub-routers
T368: Configure /api/v1 prefix for all routes (FR-068)
T369: Apply rate limiting per endpoint category (FR-061)

This module centralizes all API route configuration and applies
consistent rate limiting based on endpoint category.
"""

from fastapi import APIRouter

# =============================================================================
# API V1 ROUTER
# =============================================================================

api_v1_router = APIRouter(prefix="/api/v1")

# =============================================================================
# HEALTH CHECK ROUTES (No rate limiting - needs to be always accessible)
# =============================================================================
# Health routes are mounted separately at root level (not under /api/v1)

# =============================================================================
# AUTHENTICATION ROUTES (10 req/min per IP - FR-061)
# =============================================================================

from src.api.auth import router as auth_router

api_v1_router.include_router(auth_router)

# =============================================================================
# USER ROUTES (100 req/min per user)
# =============================================================================

from src.api.users import router as users_router

api_v1_router.include_router(users_router)

# =============================================================================
# TASK MANAGEMENT ROUTES (100 req/min per user)
# =============================================================================

from src.api.tasks import router as tasks_router
from src.api.subtasks import router as subtasks_router
from src.api.subtasks import tasks_router as subtasks_tasks_router
from src.api.templates import router as templates_router

api_v1_router.include_router(tasks_router)
api_v1_router.include_router(subtasks_router, prefix="/subtasks")
api_v1_router.include_router(subtasks_tasks_router)
api_v1_router.include_router(templates_router)

# =============================================================================
# NOTES ROUTES (100 req/min per user)
# =============================================================================

from src.api.notes import router as notes_router

api_v1_router.include_router(notes_router)

# =============================================================================
# REMINDERS ROUTES (100 req/min per user)
# =============================================================================

from src.api.reminders import router as reminders_router
from src.api.reminders import tasks_router as reminders_tasks_router

api_v1_router.include_router(reminders_router, prefix="/reminders")
api_v1_router.include_router(reminders_tasks_router)

# =============================================================================
# AI ROUTES (20 req/min per user - FR-061)
# =============================================================================

from src.api.ai import router as ai_router

api_v1_router.include_router(ai_router)

# =============================================================================
# CREDITS ROUTES (100 req/min per user)
# =============================================================================

from src.api.credits import router as credits_router

api_v1_router.include_router(credits_router)

# =============================================================================
# ACHIEVEMENTS ROUTES (100 req/min per user)
# =============================================================================

from src.api.achievements import router as achievements_router

api_v1_router.include_router(achievements_router)

# =============================================================================
# FOCUS MODE ROUTES (100 req/min per user)
# =============================================================================

from src.api.focus import router as focus_router

api_v1_router.include_router(focus_router)

# =============================================================================
# SUBSCRIPTION ROUTES (100 req/min per user)
# =============================================================================

from src.api.subscription import router as subscription_router

api_v1_router.include_router(subscription_router)

# =============================================================================
# RECOVERY ROUTES (100 req/min per user)
# =============================================================================

from src.api.recovery import router as recovery_router
from src.api.recovery import tasks_router as recovery_tasks_router

api_v1_router.include_router(recovery_router)
api_v1_router.include_router(recovery_tasks_router)

# =============================================================================
# NOTIFICATION ROUTES (100 req/min per user)
# =============================================================================

from src.api.notifications import router as notifications_router

api_v1_router.include_router(notifications_router)

# =============================================================================
# ACTIVITY LOG ROUTES (100 req/min per user)
# =============================================================================

from src.api.activity import router as activity_router

api_v1_router.include_router(activity_router)


# =============================================================================
# RATE LIMITING CATEGORIES
# =============================================================================
# Rate limits are applied at the individual endpoint level using decorators:
# - @rate_limit_auth: 10 req/min per IP (auth endpoints)
# - @rate_limit_ai: 20 req/min per user (AI endpoints)
# - @rate_limit_general: 100 req/min per user (all other endpoints)
#
# See src/middleware/rate_limit.py for decorator implementations.
# Individual routers apply these decorators to their endpoints.


def get_api_router() -> APIRouter:
    """Get the main API v1 router.

    Returns:
        Configured APIRouter with all sub-routers included
    """
    return api_v1_router


__all__ = ["api_v1_router", "get_api_router"]
