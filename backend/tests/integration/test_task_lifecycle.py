"""Integration tests for the full task lifecycle.

T129: Integration test for full task lifecycle
Tests the complete flow: create -> update -> subtasks -> complete -> delete -> recover
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.models.user import User
from src.schemas.enums import TaskPriority


class TestTaskLifecycle:
    """Integration tests for complete task CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_task_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_user: User,
        idempotency_key: str,
    ):
        """Test complete task lifecycle: create -> update -> complete -> delete."""
        # =====================================================================
        # 1. CREATE TASK
        # =====================================================================
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Integration test task",
                "description": "Testing full lifecycle",
                "priority": "high",
                "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
            },
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert create_response.status_code == 201
        task_data = create_response.json()["data"]
        task_id = task_data["id"]

        assert task_data["title"] == "Integration test task"
        assert task_data["priority"] == "high"
        assert task_data["completed"] is False
        assert task_data["version"] == 1

        # =====================================================================
        # 2. GET TASK
        # =====================================================================
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        get_data = get_response.json()["data"]
        assert get_data["id"] == task_id
        assert get_data["title"] == "Integration test task"

        # =====================================================================
        # 3. UPDATE TASK WITH OPTIMISTIC LOCKING
        # =====================================================================
        update_response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated task title",
                "version": 1,
            },
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )

        assert update_response.status_code == 200
        update_data = update_response.json()["data"]
        assert update_data["title"] == "Updated task title"
        assert update_data["version"] == 2

        # =====================================================================
        # 4. ADD SUBTASKS
        # =====================================================================
        subtask1_response = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 1"},
            headers=auth_headers,
        )

        assert subtask1_response.status_code == 201
        subtask1_id = subtask1_response.json()["data"]["id"]
        assert subtask1_response.json()["data"]["order_index"] == 0

        subtask2_response = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 2"},
            headers=auth_headers,
        )

        assert subtask2_response.status_code == 201
        subtask2_id = subtask2_response.json()["data"]["id"]
        assert subtask2_response.json()["data"]["order_index"] == 1

        # =====================================================================
        # 5. COMPLETE SUBTASKS TO TRIGGER AUTO-COMPLETION
        # =====================================================================
        # Complete subtask 1
        await client.patch(
            f"/api/v1/subtasks/{subtask1_id}",
            json={"completed": True},
            headers=auth_headers,
        )

        # Verify task is not yet auto-completed
        task_check = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert task_check.json()["data"]["completed"] is False

        # Complete subtask 2
        await client.patch(
            f"/api/v1/subtasks/{subtask2_id}",
            json={"completed": True},
            headers=auth_headers,
        )

        # Verify task is now auto-completed
        task_completed = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        completed_data = task_completed.json()["data"]
        assert completed_data["completed"] is True
        assert completed_data["completed_by"] == "auto"

        # =====================================================================
        # 6. DELETE TASK (creates tombstone)
        # =====================================================================
        delete_response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert delete_response.status_code == 200
        delete_data = delete_response.json()["data"]
        assert "tombstone_id" in delete_data
        assert "recoverable_until" in delete_data

        # Verify task is no longer accessible
        get_deleted = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_deleted.status_code == 404

    @pytest.mark.asyncio
    async def test_version_conflict_on_stale_update(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        idempotency_key: str,
    ):
        """Test that stale updates return 409 conflict."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Version test task"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        task_id = create_response.json()["data"]["id"]

        # First update (should succeed)
        update1 = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"title": "First update", "version": 1},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert update1.status_code == 200
        assert update1.json()["data"]["version"] == 2

        # Second update with stale version (should fail)
        update2 = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Stale update", "version": 1},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert update2.status_code == 409

    @pytest.mark.asyncio
    async def test_force_complete_task_with_subtasks(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        idempotency_key: str,
    ):
        """Test that force-complete marks all subtasks as completed."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Force complete test"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        task_data = create_response.json()["data"]
        task_id = task_data["id"]
        version = task_data["version"]

        # Add subtasks
        await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 1"},
            headers=auth_headers,
        )
        await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 2"},
            headers=auth_headers,
        )

        # Force complete
        force_response = await client.post(
            f"/api/v1/tasks/{task_id}/force-complete",
            json={"version": version},
            headers=auth_headers,
        )

        assert force_response.status_code == 200
        force_data = force_response.json()["data"]
        assert force_data["completed"] is True
        assert force_data["completed_by"] == "force"

        # Verify subtasks are completed
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        assert all(s["completed"] for s in subtasks)

    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test task listing with pagination and filters."""
        # Create multiple tasks
        for i in range(5):
            await client.post(
                "/api/v1/tasks",
                json={
                    "title": f"List test task {i}",
                    "priority": "high" if i % 2 == 0 else "low",
                },
                headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            )

        # List all tasks
        list_response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data["data"]) >= 5
        assert "pagination" in data

        # List with priority filter
        filtered = await client.get(
            "/api/v1/tasks?priority=high",
            headers=auth_headers,
        )
        assert filtered.status_code == 200
        high_tasks = filtered.json()["data"]
        assert all(t["priority"] == "high" for t in high_tasks)

    @pytest.mark.asyncio
    async def test_subtask_reorder(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        idempotency_key: str,
    ):
        """Test subtask reordering maintains gapless indices."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Reorder test"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        task_id = create_response.json()["data"]["id"]

        # Add subtasks
        subtask_ids = []
        for i in range(3):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i}"},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Reorder: [2, 0, 1]
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_ids[2], subtask_ids[0], subtask_ids[1]]},
            headers=auth_headers,
        )

        assert reorder_response.status_code == 200
        reordered = reorder_response.json()["data"]
        assert reordered[0]["id"] == subtask_ids[2]
        assert reordered[0]["order_index"] == 0
        assert reordered[1]["id"] == subtask_ids[0]
        assert reordered[1]["order_index"] == 1
        assert reordered[2]["id"] == subtask_ids[1]
        assert reordered[2]["order_index"] == 2


class TestSubtaskLimits:
    """Integration tests for tier-based subtask limits (FR-019)."""

    @pytest.mark.asyncio
    async def test_free_user_subtask_limit(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],  # Free user
        idempotency_key: str,
    ):
        """Test that free users are limited to 4 subtasks per task."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Free tier limit test"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        task_id = create_response.json()["data"]["id"]

        # Add 4 subtasks (should succeed)
        for i in range(4):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=auth_headers,
            )
            assert resp.status_code == 201

        # 5th subtask should fail
        resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 5"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_pro_user_subtask_limit(
        self,
        client: AsyncClient,
        pro_auth_headers: dict[str, str],  # Pro user
    ):
        """Test that Pro users are limited to 10 subtasks per task."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Pro tier limit test"},
            headers={**pro_auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_response.json()["data"]["id"]

        # Add 10 subtasks (should succeed)
        for i in range(10):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i + 1}"},
                headers=pro_auth_headers,
            )
            assert resp.status_code == 201

        # 11th subtask should fail
        resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask 11"},
            headers=pro_auth_headers,
        )
        assert resp.status_code == 409
