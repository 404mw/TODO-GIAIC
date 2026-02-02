"""Integration tests for subtask limit enforcement across tiers.

T131: [P] [US4] Integration test: Subtask limit enforcement across tiers

Tests verify:
- Free tier: Max 4 subtasks per task
- Pro tier: Max 10 subtasks per task
- Limit enforcement happens at API layer
- Proper error responses when limits exceeded
- Limits apply per-task, not globally
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.models.user import User


class TestSubtaskLimitEnforcementAcrossTiers:
    """Comprehensive integration tests for tier-based subtask limits (FR-019)."""

    @pytest.mark.asyncio
    async def test_free_user_limited_to_4_subtasks(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
        idempotency_key: str,
    ):
        """Free tier: Verify 4 subtask limit is enforced."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Free tier subtask limit test"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Add 4 subtasks (should all succeed)
        for i in range(4):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Free Subtask {i + 1}"},
                headers=auth_headers,
            )
            assert resp.status_code == 201, f"Failed to create subtask {i + 1}"

        # Verify all 4 subtasks exist
        task_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert len(task_response.json()["data"]["subtasks"]) == 4

        # 5th subtask should fail with 409
        resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Exceeds limit"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "limit" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_pro_user_limited_to_10_subtasks(
        self,
        client: AsyncClient,
        pro_auth_headers: dict[str, str],  # Pro user
    ):
        """Pro tier: Verify 10 subtask limit is enforced."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Pro tier subtask limit test"},
            headers={**pro_auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Add 10 subtasks (should all succeed)
        for i in range(10):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Pro Subtask {i + 1}"},
                headers=pro_auth_headers,
            )
            assert resp.status_code == 201, f"Failed to create subtask {i + 1}"

        # Verify all 10 subtasks exist
        task_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=pro_auth_headers,
        )
        assert len(task_response.json()["data"]["subtasks"]) == 10

        # 11th subtask should fail with 409
        resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Exceeds limit"},
            headers=pro_auth_headers,
        )
        assert resp.status_code == 409
        assert "limit" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_subtask_limits_per_task_not_global(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
    ):
        """Verify subtask limits apply per-task, not globally across all tasks."""
        # Create first task and fill to limit
        task1_response = await client.post(
            "/api/v1/tasks",
            json={"title": "First Task"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task1_id = task1_response.json()["data"]["id"]

        for i in range(4):
            await client.post(
                f"/api/v1/tasks/{task1_id}/subtasks",
                json={"title": f"Task1 Subtask {i + 1}"},
                headers=auth_headers,
            )

        # Create second task - should be able to add subtasks
        task2_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Second Task"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task2_id = task2_response.json()["data"]["id"]

        # Should succeed - limits are per-task
        resp = await client.post(
            f"/api/v1/tasks/{task2_id}/subtasks",
            json={"title": "Task2 Subtask 1"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_pro_can_add_more_subtasks_than_free(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
        pro_auth_headers: dict[str, str],  # Pro user
    ):
        """Verify Pro users have higher limit than Free users."""
        # Free user task
        free_task = await client.post(
            "/api/v1/tasks",
            json={"title": "Free task"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        free_task_id = free_task.json()["data"]["id"]

        # Pro user task
        pro_task = await client.post(
            "/api/v1/tasks",
            json={"title": "Pro task"},
            headers={**pro_auth_headers, "Idempotency-Key": str(uuid4())},
        )
        pro_task_id = pro_task.json()["data"]["id"]

        # Free user: 5th subtask fails
        for i in range(4):
            await client.post(
                f"/api/v1/tasks/{free_task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=auth_headers,
            )

        free_5th = await client.post(
            f"/api/v1/tasks/{free_task_id}/subtasks",
            json={"title": "5th subtask"},
            headers=auth_headers,
        )
        assert free_5th.status_code == 409

        # Pro user: 5th subtask succeeds
        for i in range(5):
            resp = await client.post(
                f"/api/v1/tasks/{pro_task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=pro_auth_headers,
            )
            assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_deleting_subtask_allows_new_subtask(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
    ):
        """Verify that deleting a subtask allows creating a new one."""
        # Create task and fill to limit
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Delete and add test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        subtask_ids = []
        for i in range(4):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Verify we're at limit
        limit_check = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Over limit"},
            headers=auth_headers,
        )
        assert limit_check.status_code == 409

        # Delete one subtask
        delete_resp = await client.delete(
            f"/api/v1/subtasks/{subtask_ids[0]}",
            headers=auth_headers,
        )
        assert delete_resp.status_code == 200

        # Now we should be able to add a new subtask
        new_subtask = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Replacement subtask"},
            headers=auth_headers,
        )
        assert new_subtask.status_code == 201

    @pytest.mark.asyncio
    async def test_limit_error_includes_tier_info(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
    ):
        """Verify error response includes tier-specific limit information."""
        # Create task and fill to limit
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Error info test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        for i in range(4):
            await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=auth_headers,
            )

        # Exceed limit and check error details
        resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Over limit"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        error = resp.json()
        assert "detail" in error
        # Error should mention the limit number
        assert "4" in error["detail"] or "free" in error["detail"].lower()
