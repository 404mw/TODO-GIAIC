"""Integration tests for task recovery lifecycle.

T346: Full recovery lifecycle test (FR-062 to FR-064)

Tests the complete flow: delete task -> verify tombstone -> recover task -> verify state
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subtask import Subtask
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.enums import SubtaskSource, TaskPriority


# =============================================================================
# HELPERS
# =============================================================================


async def _create_task_with_subtasks(
    client: AsyncClient,
    auth_headers: dict,
    idempotency_key: str,
) -> dict:
    """Create a task with subtasks via API and return the full response data."""
    # Create task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task to Delete and Recover",
            "description": "This task will be deleted and recovered",
            "priority": "high",
            "estimated_duration": 60,
        },
        headers={**auth_headers, "Idempotency-Key": idempotency_key},
    )
    assert create_response.status_code == 201
    task_data = create_response.json()["data"]
    task_id = task_data["id"]

    # Add subtasks
    for i, title in enumerate(["Step 1", "Step 2"]):
        sub_response = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": title},
            headers=auth_headers,
        )
        assert sub_response.status_code == 201

    return task_data


# =============================================================================
# T346: Integration test for recovery lifecycle
# =============================================================================


@pytest.mark.asyncio
async def test_full_recovery_lifecycle(
    client: AsyncClient,
    auth_headers: dict,
    test_user: User,
) -> None:
    """T346: Complete recovery lifecycle - create, delete, list tombstones, recover.

    FR-062: Delete creates tombstone with serialized data
    FR-063: Recovery restores original ID and timestamps
    FR-064: Recovered tasks do not trigger achievements or streaks
    """
    # 1. Create a task
    task_data = await _create_task_with_subtasks(
        client, auth_headers, str(uuid4())
    )
    task_id = task_data["id"]

    # 2. Delete the task (creates tombstone)
    delete_response = await client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200
    delete_data = delete_response.json()["data"]
    tombstone_id = delete_data["tombstone_id"]
    assert "recoverable_until" in delete_data

    # 3. Verify task is gone
    get_response = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404

    # 4. List tombstones
    tombstones_response = await client.get(
        "/api/v1/tombstones",
        headers=auth_headers,
    )
    assert tombstones_response.status_code == 200
    tombstones = tombstones_response.json()["data"]
    assert len(tombstones) >= 1
    tombstone_ids = [t["id"] for t in tombstones]
    assert tombstone_id in tombstone_ids

    # 5. Recover the task
    recover_response = await client.post(
        f"/api/v1/tasks/recover/{tombstone_id}",
        headers=auth_headers,
    )
    assert recover_response.status_code == 200
    recovered_data = recover_response.json()["data"]

    # 6. Verify recovered task has original ID
    assert recovered_data["id"] == task_id
    assert recovered_data["title"] == "Task to Delete and Recover"
    assert recovered_data["priority"] == "high"

    # 7. Verify task is accessible again
    get_recovered = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )
    assert get_recovered.status_code == 200

    # 8. Verify tombstone is gone
    tombstones_after = await client.get(
        "/api/v1/tombstones",
        headers=auth_headers,
    )
    tombstone_ids_after = [t["id"] for t in tombstones_after.json()["data"]]
    assert tombstone_id not in tombstone_ids_after


@pytest.mark.asyncio
async def test_recover_nonexistent_tombstone_returns_404(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Recovering a nonexistent tombstone returns 404."""
    fake_id = str(uuid4())
    response = await client.post(
        f"/api/v1/tasks/recover/{fake_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_recover_task_id_collision_returns_409(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Recovering a task when original ID already exists returns 409."""
    # Create and delete a task
    task_data = await _create_task_with_subtasks(
        client, auth_headers, str(uuid4())
    )
    task_id = task_data["id"]

    # Delete task
    delete_resp = await client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )
    assert delete_resp.status_code == 200
    tombstone_id = delete_resp.json()["data"]["tombstone_id"]

    # Create a new task that occupies the same ID
    # (this simulates an ID collision scenario)
    from uuid import UUID
    collision_task = TaskInstance(
        id=UUID(task_id),
        user_id=test_user.id,
        title="Collision Task",
        priority=TaskPriority.LOW,
    )
    db_session.add(collision_task)
    await db_session.commit()

    # Try to recover - should get 409
    recover_resp = await client.post(
        f"/api/v1/tasks/recover/{tombstone_id}",
        headers=auth_headers,
    )
    assert recover_resp.status_code == 409


@pytest.mark.asyncio
async def test_tombstone_fifo_limit(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    """FR-062: Max 3 tombstones per user with FIFO eviction."""
    task_ids = []
    # Create and delete 4 tasks
    for i in range(4):
        create_resp = await client.post(
            "/api/v1/tasks",
            json={"title": f"Task {i + 1}"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert create_resp.status_code == 201
        task_ids.append(create_resp.json()["data"]["id"])

    # Delete all 4
    tombstone_ids = []
    for tid in task_ids:
        del_resp = await client.delete(
            f"/api/v1/tasks/{tid}",
            headers=auth_headers,
        )
        assert del_resp.status_code == 200
        tombstone_ids.append(del_resp.json()["data"]["tombstone_id"])

    # List tombstones - should have at most 3
    tombstones_resp = await client.get(
        "/api/v1/tombstones",
        headers=auth_headers,
    )
    assert tombstones_resp.status_code == 200
    tombstones = tombstones_resp.json()["data"]
    assert len(tombstones) <= 3

    # First tombstone should have been evicted (FIFO)
    current_ids = [t["id"] for t in tombstones]
    assert tombstone_ids[0] not in current_ids
