"""
Integration Tests: Performance Validation
SC-001: OAuth sign-in completes within 10 seconds
SC-003: 95% of API responses < 500ms

T385: OAuth sign-in performance test (SC-001)
T388: 95% of API responses < 500ms (SC-003)
"""
import statistics
import time
from collections import defaultdict
from typing import List, Tuple

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# =============================================================================
# T385: SC-001 – OAuth Sign-in Performance
# =============================================================================


class TestOAuthSignInPerformance:
    """
    SC-001: OAuth Sign-in Performance
    Target: Backend OAuth processing < 2s (end-to-end < 10s)
    """

    @pytest.mark.asyncio
    async def test_oauth_signin_backend_under_2_seconds(self, client: AsyncClient):
        """Backend OAuth processing completes in under 2 seconds (SC-001)."""
        mock_google_payload = {
            "sub": "google-perf-001",
            "email": "perf001@example.com",
            "name": "Perf User",
            "picture": "https://example.com/avatar.jpg",
            "email_verified": True,
        }

        with patch(
            "src.integrations.google_oauth.GoogleOAuthClient.verify_id_token",
            new_callable=AsyncMock,
            return_value=mock_google_payload,
        ):
            start_time = time.perf_counter()

            response = await client.post(
                "/api/v1/auth/google/callback",
                json={"id_token": "mock_google_id_token"},
            )

            elapsed = time.perf_counter() - start_time

            assert response.status_code == 200, f"OAuth callback failed: {response.text}"
            assert elapsed < 2.0, (
                f"OAuth sign-in took {elapsed:.3f}s, exceeds 2s target (SC-001)"
            )

            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_oauth_signin_multiple_iterations(self, client: AsyncClient):
        """OAuth sign-in p95 consistently under 2s across 10 iterations (SC-001)."""
        times: List[float] = []

        for i in range(10):
            mock_payload = {
                "sub": f"google-perf-iter-{i}",
                "email": f"perf-iter-{i}@example.com",
                "name": f"Perf Iter {i}",
                "picture": "https://example.com/avatar.jpg",
                "email_verified": True,
            }

            with patch(
                "src.integrations.google_oauth.GoogleOAuthClient.verify_id_token",
                new_callable=AsyncMock,
                return_value=mock_payload,
            ):
                start = time.perf_counter()
                response = await client.post(
                    "/api/v1/auth/google/callback",
                    json={"id_token": f"mock_token_{i}"},
                )
                elapsed = time.perf_counter() - start
                times.append(elapsed)
                # Accept rate limiting (429) in rapid fire test
                assert response.status_code in (200, 429), (
                    f"Unexpected status {response.status_code}: {response.text}"
                )
                if response.status_code == 429:
                    # Skip timing for rate-limited requests
                    times.pop()

        if not times:
            pytest.skip("All requests were rate-limited")

        p95 = sorted(times)[int(len(times) * 0.95)]
        avg = statistics.mean(times)

        assert max(times) < 2.0, f"Max OAuth time {max(times):.3f}s exceeds 2s"
        assert avg < 1.5, f"Avg OAuth time {avg:.3f}s too close to 2s"


# =============================================================================
# T388: SC-003 – API Response Latency
# =============================================================================


class TestAPIResponseLatency:
    """
    SC-003: API Response Latency
    Target: 95% of API responses < 500ms
    """

    @pytest.mark.asyncio
    async def test_api_responses_p95_under_500ms(
        self, client: AsyncClient, auth_headers: dict
    ):
        """95% of non-AI API responses complete in under 500ms (SC-003)."""
        times: List[Tuple[str, float]] = []

        endpoints = [
            "/api/v1/tasks",
            "/api/v1/notes",
            "/api/v1/achievements",
            "/api/v1/notifications",
        ]

        for endpoint in endpoints:
            for _ in range(20):
                start = time.perf_counter()
                await client.get(endpoint, headers=auth_headers)
                elapsed = time.perf_counter() - start
                times.append((endpoint, elapsed))

        all_times = [t[1] for t in times]
        sorted_times = sorted(all_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[p95_idx] if sorted_times else 0

        assert p95 < 0.5, (
            f"API p95 latency {p95 * 1000:.1f}ms exceeds 500ms (SC-003)"
        )

    @pytest.mark.asyncio
    async def test_task_crud_latency(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Task CRUD p95 latency < 500ms (SC-003)."""
        times: List[Tuple[str, float]] = []
        task_ids: List[str] = []

        # Create
        for i in range(10):
            start = time.perf_counter()
            resp = await client.post(
                "/api/v1/tasks",
                json={"title": f"Perf Task {i}", "priority": "medium"},
                headers=auth_headers,
            )
            elapsed = time.perf_counter() - start
            times.append(("POST /tasks", elapsed))
            if resp.status_code in (200, 201):
                resp_data = resp.json()
                task_ids.append(resp_data.get("data", resp_data)["id"])

        # Read
        for tid in task_ids[:5]:
            start = time.perf_counter()
            await client.get(f"/api/v1/tasks/{tid}", headers=auth_headers)
            elapsed = time.perf_counter() - start
            times.append(("GET /tasks/:id", elapsed))

        # Update
        for tid in task_ids[:5]:
            start = time.perf_counter()
            await client.patch(
                f"/api/v1/tasks/{tid}",
                json={"title": "Updated Perf Task"},
                headers=auth_headers,
            )
            elapsed = time.perf_counter() - start
            times.append(("PATCH /tasks/:id", elapsed))

        # Delete
        for tid in task_ids:
            start = time.perf_counter()
            await client.delete(f"/api/v1/tasks/{tid}", headers=auth_headers)
            elapsed = time.perf_counter() - start
            times.append(("DELETE /tasks/:id", elapsed))

        all_times = [t[1] for t in times]
        sorted_times = sorted(all_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[p95_idx] if sorted_times else 0

        assert p95 < 0.5, (
            f"Task CRUD p95 {p95 * 1000:.1f}ms exceeds 500ms (SC-003)"
        )


class TestHealthEndpointLatency:
    """Health probe latency validation."""

    @pytest.mark.asyncio
    async def test_liveness_probe_fast(self, client: AsyncClient):
        """Liveness probe p95 < 100ms."""
        times = []
        for _ in range(50):
            start = time.perf_counter()
            resp = await client.get("/health/live")
            times.append(time.perf_counter() - start)

        p95 = sorted(times)[int(len(times) * 0.95)]
        assert p95 < 0.1, f"Liveness p95 {p95 * 1000:.1f}ms exceeds 100ms"

    @pytest.mark.asyncio
    async def test_readiness_probe_fast(self, client: AsyncClient):
        """Readiness probe p95 < 200ms."""
        times = []
        for _ in range(20):
            start = time.perf_counter()
            await client.get("/health/ready")
            times.append(time.perf_counter() - start)

        p95 = sorted(times)[int(len(times) * 0.95)]
        assert p95 < 0.2, f"Readiness p95 {p95 * 1000:.1f}ms exceeds 200ms"
