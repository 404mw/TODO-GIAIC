"""Integration tests for health check endpoints.

T012a: Readiness probe returns 503 when DB unavailable (FR-067)
"""

import pytest
from unittest.mock import AsyncMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db_session


# =============================================================================
# T012a: Readiness probe returns 503 when DB unavailable
# =============================================================================


@pytest.mark.asyncio
async def test_liveness_probe_returns_200(client: AsyncClient):
    """Liveness probe should always return 200 if the service is running."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_probe_returns_200_when_healthy(client: AsyncClient):
    """Readiness probe returns 200 when database is available."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["database"]["status"] == "ok"
    assert data["checks"]["configuration"]["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_probe_returns_503_when_db_unavailable(
    app,
    settings,
):
    """T012a: Readiness probe returns 503 when DB is unavailable (FR-067).

    When the database connection fails, the /health/ready endpoint
    should return HTTP 503 Service Unavailable with error details.
    """
    from httpx import ASGITransport, AsyncClient

    # Create a mock session that raises on execute (simulating DB down)
    broken_session = AsyncMock(spec=AsyncSession)
    broken_session.execute.side_effect = ConnectionError(
        "could not connect to server"
    )

    # Override the DB session dependency with the broken one
    app.dependency_overrides[get_db_session] = lambda: broken_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        # Error middleware wraps HTTPException detail in error.message
        data = body.get("error", {}).get("message", body.get("detail", body))
        assert data["status"] == "error"
        assert data["checks"]["database"]["status"] == "error"
        assert data["checks"]["database"]["message"] is not None
        assert "connect" in data["checks"]["database"]["message"].lower()
    finally:
        # Restore original override
        app.dependency_overrides.pop(get_db_session, None)
