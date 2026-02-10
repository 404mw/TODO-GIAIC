"""Health check endpoints for liveness and readiness probes (FR-067).

Provides:
- GET /health/live - Liveness probe (is the service running?)
- GET /health/ready - Readiness probe (is the service ready to handle requests?)
- GET /metrics - Prometheus metrics endpoint
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import get_db_session
from src.middleware.metrics import metrics_endpoint

router = APIRouter(tags=["Health"])


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class LivenessResponse(BaseModel):
    """Response schema for liveness probe."""

    status: str = "ok"


class ReadinessCheck(BaseModel):
    """Individual readiness check result."""

    status: str  # "ok" or "error"
    message: str | None = None


class ReadinessResponse(BaseModel):
    """Response schema for readiness probe."""

    status: str  # "ok" or "degraded" or "error"
    checks: dict[str, ReadinessCheck]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Liveness probe",
    description="Check if the service is alive. Always returns 200 if the service is running.",
)
async def liveness() -> LivenessResponse:
    """Liveness probe - checks if the service is running.

    This endpoint should return 200 as long as the process is alive.
    It does NOT check dependencies (use /health/ready for that).
    """
    return LivenessResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    description="Check if the service is ready to handle requests. Checks database connectivity.",
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service is not ready - dependencies unavailable"},
    },
)
async def readiness(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReadinessResponse:
    """Readiness probe - checks if the service is ready to handle requests.

    Verifies:
    - Database connectivity
    - Essential configuration is loaded

    Returns 503 if any critical check fails.
    """
    checks: dict[str, ReadinessCheck] = {}
    overall_status = "ok"

    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = ReadinessCheck(status="ok")
    except Exception as e:
        checks["database"] = ReadinessCheck(status="error", message=str(e))
        overall_status = "error"

    # Check essential configuration
    try:
        # Verify critical settings are loaded
        assert settings.database_url is not None
        assert settings.get_jwt_public_key()  # Supports both file and inline
        assert settings.google_client_id is not None
        checks["configuration"] = ReadinessCheck(status="ok")
    except Exception as e:
        checks["configuration"] = ReadinessCheck(status="error", message=str(e))
        if overall_status == "ok":
            overall_status = "degraded"

    # Return appropriate response
    response = ReadinessResponse(status=overall_status, checks=checks)

    if overall_status == "error":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )

    return response


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Expose Prometheus-compatible metrics for monitoring.",
    include_in_schema=False,  # Hide from OpenAPI docs
)
async def metrics():
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    return metrics_endpoint()
