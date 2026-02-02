"""Integration tests for subtask ordering persistence after reorder.

T132: [P] [US4] Integration test: Subtask ordering persistence after reorder

Tests verify:
- Reordering persists correctly to database
- Order indices remain gapless after reorder
- Multiple reorder operations work correctly
- Ordering persists after server "restart" (session refresh)
- Edge cases: reverse order, single item, no change
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.models.user import User


class TestSubtaskOrderingPersistence:
    """Integration tests for subtask ordering persistence (FR-020)."""

    @pytest.mark.asyncio
    async def test_reorder_persists_to_database(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        idempotency_key: str,
    ):
        """Verify reordered subtasks persist correctly."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Ordering persistence test"},
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )
        task_id = task_response.json()["data"]["id"]

        # Create subtasks: A, B, C
        subtask_ids = []
        for title in ["A", "B", "C"]:
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": title},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Verify initial order: A=0, B=1, C=2
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        subtasks_sorted = sorted(subtasks, key=lambda s: s["order_index"])
        assert [s["title"] for s in subtasks_sorted] == ["A", "B", "C"]

        # Reorder to: C, A, B
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_ids[2], subtask_ids[0], subtask_ids[1]]},
            headers=auth_headers,
        )
        assert reorder_response.status_code == 200

        # Verify order persisted by fetching task again
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        subtasks_sorted = sorted(subtasks, key=lambda s: s["order_index"])
        assert [s["title"] for s in subtasks_sorted] == ["C", "A", "B"]

    @pytest.mark.asyncio
    async def test_reorder_maintains_gapless_indices(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify order indices are gapless (0, 1, 2, ...) after reorder."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Gapless indices test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        # Create 5 subtasks
        subtask_ids = []
        for i in range(5):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i}"},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Reverse the order
        reversed_ids = list(reversed(subtask_ids))
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": reversed_ids},
            headers=auth_headers,
        )
        assert reorder_response.status_code == 200

        # Verify indices are 0, 1, 2, 3, 4 (gapless)
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        indices = sorted([s["order_index"] for s in subtasks])
        assert indices == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_multiple_reorder_operations(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify multiple sequential reorder operations work correctly."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Multiple reorder test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        # Create subtasks
        subtask_ids = []
        for title in ["First", "Second", "Third"]:
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": title},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # First reorder: Second, First, Third
        await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_ids[1], subtask_ids[0], subtask_ids[2]]},
            headers=auth_headers,
        )

        # Second reorder: Third, Second, First
        await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_ids[2], subtask_ids[1], subtask_ids[0]]},
            headers=auth_headers,
        )

        # Verify final order
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        subtasks_sorted = sorted(subtasks, key=lambda s: s["order_index"])
        assert [s["title"] for s in subtasks_sorted] == ["Third", "Second", "First"]

    @pytest.mark.asyncio
    async def test_reorder_same_order_is_idempotent(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify reordering to same order doesn't change anything."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Idempotent reorder test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        # Create subtasks
        subtask_ids = []
        for title in ["A", "B", "C"]:
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": title},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Reorder with same order
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": subtask_ids},  # Same order
            headers=auth_headers,
        )
        assert reorder_response.status_code == 200

        # Verify order unchanged
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        subtasks_sorted = sorted(subtasks, key=lambda s: s["order_index"])
        assert [s["title"] for s in subtasks_sorted] == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_reorder_with_single_subtask(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify reordering with single subtask works."""
        # Create task with one subtask
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Single subtask reorder"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        subtask_resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Only subtask"},
            headers=auth_headers,
        )
        subtask_id = subtask_resp.json()["data"]["id"]

        # Reorder with single subtask
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_id]},
            headers=auth_headers,
        )
        assert reorder_response.status_code == 200

        # Verify order
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        assert len(subtasks) == 1
        assert subtasks[0]["order_index"] == 0

    @pytest.mark.asyncio
    async def test_reorder_with_invalid_subtask_id_fails(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify reordering with invalid subtask ID fails."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Invalid ID test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        subtask_resp = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Real subtask"},
            headers=auth_headers,
        )
        real_id = subtask_resp.json()["data"]["id"]

        # Try to reorder with non-existent ID
        fake_id = str(uuid4())
        reorder_response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [real_id, fake_id]},
            headers=auth_headers,
        )
        assert reorder_response.status_code == 404

    @pytest.mark.asyncio
    async def test_reorder_preserves_completion_status(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify reordering preserves subtask completion status."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Completion status test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        # Create subtasks
        subtask_ids = []
        for title in ["A", "B", "C"]:
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": title},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Complete subtask B
        await client.patch(
            f"/api/v1/subtasks/{subtask_ids[1]}",
            json={"completed": True},
            headers=auth_headers,
        )

        # Reorder to: C, A, B
        await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": [subtask_ids[2], subtask_ids[0], subtask_ids[1]]},
            headers=auth_headers,
        )

        # Verify B is still completed
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        b_subtask = next(s for s in subtasks if s["id"] == subtask_ids[1])
        assert b_subtask["completed"] is True

    @pytest.mark.asyncio
    async def test_order_persists_after_delete_and_reorder(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Verify order remains gapless after delete followed by reorder."""
        # Create task with subtasks
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Delete then reorder test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = task_response.json()["data"]["id"]

        # Create subtasks: A, B, C, D
        subtask_ids = []
        for title in ["A", "B", "C", "D"]:
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": title},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Delete B (index 1)
        await client.delete(
            f"/api/v1/subtasks/{subtask_ids[1]}",
            headers=auth_headers,
        )

        # Verify indices are gapless after delete: A=0, C=1, D=2
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        indices = sorted([s["order_index"] for s in subtasks])
        assert indices == [0, 1, 2]

        # Reorder remaining: D, A, C
        remaining_ids = [subtask_ids[3], subtask_ids[0], subtask_ids[2]]
        await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": remaining_ids},
            headers=auth_headers,
        )

        # Verify final order
        task_detail = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        subtasks = task_detail.json()["data"]["subtasks"]
        subtasks_sorted = sorted(subtasks, key=lambda s: s["order_index"])
        assert [s["title"] for s in subtasks_sorted] == ["D", "A", "C"]
        # Verify still gapless
        assert [s["order_index"] for s in subtasks_sorted] == [0, 1, 2]
