"""
Integration Tests: AI Chat Performance Validation
T391: AI chat p95 < 5 seconds (SC-005)

Tests AI endpoint performance under mocked conditions.
"""
import statistics
import time
from typing import List

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# =============================================================================
# T391: SC-005 – AI Chat Response Time
# =============================================================================


class TestAIChatPerformance:
    """
    SC-005: AI Chat Response Time
    Target: p95 < 5 seconds for AI chat responses
    """

    @pytest.mark.asyncio
    async def test_ai_chat_p95_under_5_seconds(
        self, client: AsyncClient, pro_auth_headers: dict, mock_openai
    ):
        """AI chat endpoint p95 response time < 5 seconds (SC-005).

        Uses mocked OpenAI to measure backend processing overhead.
        Real-world latency depends on OpenAI API but backend should
        add minimal overhead.
        """
        times: List[float] = []
        iterations = 20

        for i in range(iterations):
            start = time.perf_counter()

            response = await client.post(
                "/api/v1/ai/chat",
                json={
                    "message": f"Help me organize my tasks for today (iteration {i})",
                    "task_id": None,
                },
                headers=pro_auth_headers,
            )

            elapsed = time.perf_counter() - start
            times.append(elapsed)

        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[p95_idx]
        avg = statistics.mean(times)

        # SC-005: p95 < 5 seconds
        assert p95 < 5.0, (
            f"AI chat p95 {p95:.3f}s exceeds 5s target (SC-005)"
        )

    @pytest.mark.asyncio
    async def test_ai_subtask_generation_latency(
        self, client: AsyncClient, pro_auth_headers: dict, mock_openai_subtasks
    ):
        """AI subtask generation responds within acceptable time."""
        times: List[float] = []

        # Create a task first
        task_resp = await client.post(
            "/api/v1/tasks",
            json={"title": "Task for AI subtask generation", "priority": "high"},
            headers=pro_auth_headers,
        )

        if task_resp.status_code not in (200, 201):
            pytest.skip("Could not create test task")

        task_id = task_resp.json()["id"]

        for _ in range(10):
            start = time.perf_counter()

            response = await client.post(
                "/api/v1/ai/generate-subtasks",
                json={"task_id": task_id},
                headers=pro_auth_headers,
            )

            elapsed = time.perf_counter() - start
            times.append(elapsed)

        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[p95_idx]

        # Subtask generation should also be < 5s
        assert p95 < 5.0, (
            f"Subtask generation p95 {p95:.3f}s exceeds 5s target"
        )

    @pytest.mark.asyncio
    async def test_ai_credits_endpoint_fast(
        self, client: AsyncClient, pro_auth_headers: dict
    ):
        """AI credits balance check should be fast (< 200ms p95)."""
        times: List[float] = []

        for _ in range(20):
            start = time.perf_counter()
            response = await client.get(
                "/api/v1/ai/credits",
                headers=pro_auth_headers,
            )
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[p95_idx]

        assert p95 < 0.2, (
            f"AI credits p95 {p95 * 1000:.1f}ms exceeds 200ms"
        )

    @pytest.mark.asyncio
    async def test_ai_service_unavailable_fast_failure(
        self, client: AsyncClient, pro_auth_headers: dict, mock_openai_error
    ):
        """When AI service is unavailable, response should fail fast (< 2s)."""
        start = time.perf_counter()

        response = await client.post(
            "/api/v1/ai/chat",
            json={"message": "Test service unavailable"},
            headers=pro_auth_headers,
        )

        elapsed = time.perf_counter() - start

        # Should return 503 quickly, not hang
        assert elapsed < 2.0, (
            f"AI unavailable took {elapsed:.3f}s, should fail fast"
        )
        # Accept 503 or 402 (no credits) or similar error codes
        assert response.status_code in (402, 500, 503)
