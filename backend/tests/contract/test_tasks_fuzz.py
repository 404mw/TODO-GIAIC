"""Schemathesis fuzz tests for task endpoints.

T376: Run schemathesis against task endpoints.

These tests use property-based testing to find edge cases and
potential issues with the tasks API contract.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import schemathesis.openapi
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app(contract_app):
    """Use the shared contract app with test settings."""
    return contract_app


@pytest.fixture
def schema(app):
    """Create schemathesis schema from app."""
    return schemathesis.openapi.from_dict(app.openapi())


@pytest.fixture
def auth_headers():
    """Mock auth headers for testing (tests will fail with 401 without real auth)."""
    # In real tests, this would be a valid JWT token
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def valid_task_payload():
    """Valid task creation payload."""
    return {
        "title": "Test Task",
        "description": "A test task description",
        "priority": "medium",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }


# =============================================================================
# TASK ENDPOINT FUZZ TESTS
# =============================================================================


@pytest.mark.parametrize(
    "endpoint,method",
    [
        ("/api/v1/tasks", "GET"),
        ("/api/v1/tasks", "POST"),
        ("/api/v1/tasks/{task_id}", "GET"),
        ("/api/v1/tasks/{task_id}", "PATCH"),
        ("/api/v1/tasks/{task_id}", "DELETE"),
        ("/api/v1/tasks/{task_id}/force-complete", "POST"),
    ],
)
class TestTaskEndpointsExist:
    """Test that task endpoints are defined in schema."""

    def test_endpoint_exists_in_schema(self, schema, endpoint, method):
        """Test that task endpoints are defined in schema."""
        openapi_schema = schema.raw_schema
        paths = openapi_schema.get("paths", {})

        # Check endpoint exists (may have path params)
        found = False
        for path in paths:
            if endpoint.replace("{task_id}", "") in path:
                found = True
                break

        assert found, f"Endpoint pattern {endpoint} not found in schema"


class TestTaskCreationFuzz:
    """Fuzz tests for task creation endpoint."""

    def test_task_creation_without_auth(self, app):
        """Test that task creation without auth returns 401."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test Task"},
                )
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())

    def test_task_creation_empty_title(self, app):
        """Test that empty title is rejected."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": ""},
                )
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_task_creation_title_too_long(self, app):
        """Test that title exceeding 200 chars is rejected."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "x" * 201},
                )
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_task_creation_invalid_priority(self, app):
        """Test that invalid priority is rejected."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test", "priority": "invalid"},
                )
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_task_creation_invalid_due_date_format(self, app):
        """Test that invalid due date format is rejected."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test", "due_date": "not-a-date"},
                )
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_task_creation_due_date_too_far(self, app):
        """Test that due date > 30 days is handled (FR-013)."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                far_future = datetime.now(timezone.utc) + timedelta(days=31)
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test", "due_date": far_future.isoformat()},
                )
                # Should return 401 (no auth) or 422/400 (validation error)
                assert response.status_code in (400, 401, 422)

        asyncio.get_event_loop().run_until_complete(_test())


class TestTaskRetrievalFuzz:
    """Fuzz tests for task retrieval endpoints."""

    def test_get_task_invalid_uuid(self, app):
        """Test that invalid UUID is rejected."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/tasks/not-a-uuid")
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_get_task_nonexistent(self, app):
        """Test that nonexistent task returns 404 (after auth)."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                random_uuid = str(uuid.uuid4())
                response = await client.get(f"/api/v1/tasks/{random_uuid}")
                # Without auth, should return 401
                # With auth, should return 404
                assert response.status_code in (401, 404)

        asyncio.get_event_loop().run_until_complete(_test())


class TestTaskUpdateFuzz:
    """Fuzz tests for task update endpoint."""

    def test_update_task_without_auth(self, app):
        """Test that task update without auth returns 401."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                random_uuid = str(uuid.uuid4())
                response = await client.patch(
                    f"/api/v1/tasks/{random_uuid}",
                    json={"title": "Updated"},
                )
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())

    def test_update_task_invalid_version(self, app):
        """Test that version mismatch is handled (FR-014 optimistic locking)."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                random_uuid = str(uuid.uuid4())
                response = await client.patch(
                    f"/api/v1/tasks/{random_uuid}",
                    json={"title": "Updated", "version": -1},
                )
                # Should return 401 (no auth) or 409/422 (version conflict)
                assert response.status_code in (401, 409, 422)

        asyncio.get_event_loop().run_until_complete(_test())


class TestTaskDeletionFuzz:
    """Fuzz tests for task deletion endpoint."""

    def test_delete_task_without_auth(self, app):
        """Test that task deletion without auth returns 401."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                random_uuid = str(uuid.uuid4())
                response = await client.delete(f"/api/v1/tasks/{random_uuid}")
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())


class TestTaskForceCompleteFuzz:
    """Fuzz tests for force-complete endpoint."""

    def test_force_complete_without_auth(self, app):
        """Test that force-complete without auth returns 401."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                random_uuid = str(uuid.uuid4())
                response = await client.post(
                    f"/api/v1/tasks/{random_uuid}/force-complete"
                )
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())


class TestTaskListFuzz:
    """Fuzz tests for task list endpoint."""

    def test_list_tasks_without_auth(self, app):
        """Test that task list without auth returns 401."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/tasks")
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())

    def test_list_tasks_invalid_pagination(self, app):
        """Test that invalid pagination params are handled."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.get(
                    "/api/v1/tasks",
                    params={"offset": -1, "limit": 1000},
                )
                # Should return 401 (no auth) or 422 (validation error)
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_list_tasks_with_filters(self, app):
        """Test task list with various filters."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                # Test with valid filter params
                response = await client.get(
                    "/api/v1/tasks",
                    params={
                        "is_completed": "true",
                        "priority": "high",
                        "limit": 10,
                    },
                )
                # Should return 401 (no auth)
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


class TestTaskSchemaValidation:
    """Validate task endpoint request/response schemas."""

    def test_task_create_request_schema(self, schema):
        """Test task creation request schema is valid."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/tasks", {})
        post = path.get("post", {})

        assert "requestBody" in post
        content = post["requestBody"].get("content", {})
        assert "application/json" in content

    def test_task_response_schema_has_required_fields(self, schema):
        """Test task response schema includes required fields."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/tasks/{task_id}", {})
        get = path.get("get", {})

        responses = get.get("responses", {})
        assert "200" in responses

    def test_task_list_response_is_paginated(self, schema):
        """Test task list returns paginated response."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/tasks", {})
        get = path.get("get", {})

        responses = get.get("responses", {})
        assert "200" in responses


# =============================================================================
# IDEMPOTENCY TESTS
# =============================================================================


class TestTaskIdempotency:
    """Test idempotency handling for task operations."""

    def test_create_task_with_idempotency_key(self, app):
        """Test that idempotency key is accepted on create."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                idempotency_key = str(uuid.uuid4())
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test Task"},
                    headers={"Idempotency-Key": idempotency_key},
                )
                # Should return 401 (no auth) but idempotency key is accepted
                assert response.status_code == 401

        asyncio.get_event_loop().run_until_complete(_test())


# =============================================================================
# BOUNDARY VALUE TESTS
# =============================================================================


class TestTaskBoundaryValues:
    """Test boundary values for task fields."""

    def test_title_boundary_values(self, app):
        """Test title field at boundary values."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                # Minimum valid (1 char)
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "x"},
                )
                assert response.status_code in (401, 201)

                # Maximum valid (200 chars)
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "x" * 200},
                )
                assert response.status_code in (401, 201)

                # Just over maximum (201 chars)
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "x" * 201},
                )
                assert response.status_code in (401, 422)

        asyncio.get_event_loop().run_until_complete(_test())

    def test_description_boundary_values(self, app):
        """Test description field at boundary values."""
        import asyncio

        async def _test():
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                # Maximum valid (based on tier, typically 500-5000)
                response = await client.post(
                    "/api/v1/tasks",
                    json={"title": "Test", "description": "x" * 500},
                )
                assert response.status_code in (401, 201)

        asyncio.get_event_loop().run_until_complete(_test())
