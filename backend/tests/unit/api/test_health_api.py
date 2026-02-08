"""Unit tests for health check API endpoints.

Tests for:
- GET /health/live - Liveness probe
- GET /health/ready - Readiness probe
- GET /metrics - Prometheus metrics
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# LIVENESS TESTS
# =============================================================================


class TestLivenessEndpoint:
    """Test liveness probe endpoint."""

    @pytest.mark.asyncio
    async def test_liveness_returns_200(self, client):
        """GET /health/live should always return 200."""
        response = await client.get("/health/live")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_liveness_returns_ok_status(self, client):
        """GET /health/live should return status ok."""
        response = await client.get("/health/live")
        data = response.json()
        assert data["status"] == "ok"


# =============================================================================
# READINESS TESTS
# =============================================================================


class TestReadinessEndpoint:
    """Test readiness probe endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_returns_200_when_healthy(self, client):
        """GET /health/ready should return 200 when all checks pass."""
        response = await client.get("/health/ready")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_readiness_includes_check_details(self, client):
        """GET /health/ready response should include check details."""
        response = await client.get("/health/ready")
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert "configuration" in data["checks"]
