"""Contract tests for Task CRUD endpoints.

T100: Contract test for Task CRUD endpoints schema validation
Validates API contracts against OpenAPI specification.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.models.user import User


class TestTaskContractValidation:
    """Contract tests for task API schema validation."""

    @pytest.mark.asyncio
    async def test_create_task_request_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        idempotency_key: str,
    ):
        """Validate task creation request and response schemas."""
        # Valid request
        valid_request = {
            "title": "Test task",
            "description": "Test description",
            "priority": "high",
            "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
            "estimated_duration": 60,
        }

        response = await client.post(
            "/api/v1/tasks",
            json=valid_request,
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 201

        # Validate response schema
        data = response.json()
        assert "data" in data

        task = data["data"]
        required_fields = [
            "id", "title", "description", "priority", "due_date",
            "estimated_duration", "focus_time_seconds", "completed",
            "completed_at", "completed_by", "hidden", "archived",
            "template_id", "subtask_count", "subtask_completed_count",
            "version", "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in task, f"Missing field: {field}"

        # Validate types
        assert isinstance(task["id"], str)  # UUID as string
        assert isinstance(task["title"], str)
        assert isinstance(task["completed"], bool)
        assert isinstance(task["version"], int)

    @pytest.mark.asyncio
    async def test_create_task_validation_errors(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate task creation validation error responses."""
        # Missing required field (title)
        response = await client.post(
            "/api/v1/tasks",
            json={"description": "Missing title"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 422

        # Empty title
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "   "},  # Whitespace only
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 422

        # Title too long
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "A" * 201},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 422

        # Invalid priority enum
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test", "priority": "invalid"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_task_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate task detail response schema."""
        # Create task first
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Schema test task"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_response.json()["data"]["id"]

        # Add a subtask
        await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask for schema test"},
            headers=auth_headers,
        )

        # Get task detail
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

        task = data["data"]
        # Detail response should have subtasks array
        assert "subtasks" in task
        assert isinstance(task["subtasks"], list)
        assert len(task["subtasks"]) > 0

        # Validate subtask schema
        subtask = task["subtasks"][0]
        assert "id" in subtask
        assert "title" in subtask
        assert "completed" in subtask
        assert "order_index" in subtask
        assert "source" in subtask

    @pytest.mark.asyncio
    async def test_list_tasks_pagination_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate task list pagination response schema."""
        response = await client.get(
            "/api/v1/tasks?offset=0&limit=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Must have data and pagination
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # Validate pagination schema
        pagination = data["pagination"]
        assert "offset" in pagination
        assert "limit" in pagination
        assert "total" in pagination
        assert "has_more" in pagination

        assert isinstance(pagination["offset"], int)
        assert isinstance(pagination["limit"], int)
        assert isinstance(pagination["total"], int)
        assert isinstance(pagination["has_more"], bool)

    @pytest.mark.asyncio
    async def test_update_task_version_required(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate that version is required for task updates."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Version test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_response.json()["data"]["id"]

        # Update without version should fail
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated without version"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_task_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate delete response schema with tombstone."""
        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Delete schema test"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_response.json()["data"]["id"]

        # Delete task
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

        delete_data = data["data"]
        assert "tombstone_id" in delete_data
        assert "recoverable_until" in delete_data

        # Validate UUID format
        assert isinstance(delete_data["tombstone_id"], str)
        # Validate ISO timestamp format
        assert isinstance(delete_data["recoverable_until"], str)

    @pytest.mark.asyncio
    async def test_error_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate error response schema format."""
        # Request non-existent task
        response = await client.get(
            f"/api/v1/tasks/{uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()

        # Error response should have detail
        assert "detail" in data
        detail = data["detail"]
        assert "code" in detail
        assert "message" in detail


class TestSubtaskContractValidation:
    """Contract tests for subtask API schema validation."""

    @pytest.mark.asyncio
    async def test_create_subtask_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate subtask creation response schema."""
        # Create task
        create_task = await client.post(
            "/api/v1/tasks",
            json={"title": "Parent task"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_task.json()["data"]["id"]

        # Create subtask
        response = await client.post(
            f"/api/v1/tasks/{task_id}/subtasks",
            json={"title": "Subtask schema test"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "data" in data

        subtask = data["data"]
        required_fields = [
            "id", "task_id", "title", "completed", "completed_at",
            "order_index", "source", "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in subtask, f"Missing field: {field}"

        assert subtask["source"] in ["user", "ai"]
        assert isinstance(subtask["order_index"], int)

    @pytest.mark.asyncio
    async def test_reorder_subtasks_response_schema(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Validate subtask reorder response schema."""
        # Create task with subtasks
        create_task = await client.post(
            "/api/v1/tasks",
            json={"title": "Reorder parent"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        task_id = create_task.json()["data"]["id"]

        subtask_ids = []
        for i in range(2):
            resp = await client.post(
                f"/api/v1/tasks/{task_id}/subtasks",
                json={"title": f"Subtask {i}"},
                headers=auth_headers,
            )
            subtask_ids.append(resp.json()["data"]["id"])

        # Reorder
        response = await client.put(
            f"/api/v1/tasks/{task_id}/subtasks/reorder",
            json={"subtask_ids": list(reversed(subtask_ids))},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        for item in data["data"]:
            assert "id" in item
            assert "order_index" in item
            assert isinstance(item["order_index"], int)
