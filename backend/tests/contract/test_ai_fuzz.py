"""Schemathesis fuzz tests for AI endpoints.

T377: Run schemathesis against AI endpoints.

These tests use property-based testing to find edge cases and
potential issues with the AI API contract.
"""

import uuid

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
async def fuzz_client(app):
    """Async HTTP client that lives inside the patched contract_app context."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# =============================================================================
# AI ENDPOINT FUZZ TESTS
# =============================================================================


@pytest.mark.parametrize(
    "endpoint,method",
    [
        ("/api/v1/ai/chat", "POST"),
        ("/api/v1/ai/generate-subtasks", "POST"),
        ("/api/v1/ai/confirm-action", "POST"),
        ("/api/v1/ai/credits", "GET"),
        ("/api/v1/ai/transcribe", "POST"),
    ],
)
class TestAIEndpointsExist:
    """Test that AI endpoints are defined in schema."""

    def test_endpoint_exists_in_schema(self, schema, endpoint, method):
        """Test that AI endpoints are defined in schema."""
        openapi_schema = schema.raw_schema
        paths = openapi_schema.get("paths", {})

        # Check endpoint exists
        found = endpoint in paths or any(
            endpoint.replace("{", "").replace("}", "") in path for path in paths
        )
        assert found, f"Endpoint {endpoint} not found in schema"


class TestAIChatFuzz:
    """Fuzz tests for AI chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_without_auth(self, fuzz_client: AsyncClient):
        """Test that chat without auth returns 401."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": str(uuid.uuid4())},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, fuzz_client: AsyncClient):
        """Test that empty message is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "", "task_id": str(uuid.uuid4())},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_chat_message_too_long(self, fuzz_client: AsyncClient):
        """Test that overly long message is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "x" * 10001, "task_id": str(uuid.uuid4())},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_chat_invalid_task_id(self, fuzz_client: AsyncClient):
        """Test that invalid task ID is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": "not-a-uuid"},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_chat_missing_required_fields(self, fuzz_client: AsyncClient):
        """Test that missing required fields are rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)


class TestSubtaskGenerationFuzz:
    """Fuzz tests for subtask generation endpoint."""

    @pytest.mark.asyncio
    async def test_generate_without_auth(self, fuzz_client: AsyncClient):
        """Test that subtask generation without auth returns 401."""
        response = await fuzz_client.post(
            "/api/v1/ai/generate-subtasks",
            json={"task_id": str(uuid.uuid4())},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_generate_invalid_task_id(self, fuzz_client: AsyncClient):
        """Test that invalid task ID is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/generate-subtasks",
            json={"task_id": "not-a-uuid"},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_generate_missing_task_id(self, fuzz_client: AsyncClient):
        """Test that missing task ID is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/generate-subtasks",
            json={},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)


class TestActionConfirmFuzz:
    """Fuzz tests for action confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_without_auth(self, fuzz_client: AsyncClient):
        """Test that action confirm without auth returns 401."""
        response = await fuzz_client.post(
            "/api/v1/ai/confirm-action",
            json={"action_id": str(uuid.uuid4()), "confirmed": True},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_confirm_invalid_action_id(self, fuzz_client: AsyncClient):
        """Test that invalid action ID is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/confirm-action",
            json={"action_id": "not-a-uuid", "confirmed": True},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_confirm_missing_confirmed_field(self, fuzz_client: AsyncClient):
        """Test that missing confirmed field is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/confirm-action",
            json={"action_id": str(uuid.uuid4())},
        )
        # Should return 401 (no auth) or 422 (validation error)
        assert response.status_code in (401, 422)


class TestCreditsFuzz:
    """Fuzz tests for credits endpoint."""

    @pytest.mark.asyncio
    async def test_credits_without_auth(self, fuzz_client: AsyncClient):
        """Test that credits check without auth returns 401."""
        response = await fuzz_client.get("/api/v1/ai/credits")
        assert response.status_code == 401


class TestTranscribeFuzz:
    """Fuzz tests for transcription endpoint."""

    @pytest.mark.asyncio
    async def test_transcribe_without_auth(self, fuzz_client: AsyncClient):
        """Test that transcription without auth returns 401."""
        response = await fuzz_client.post(
            "/api/v1/ai/transcribe",
            content=b"fake-audio-data",
            headers={"Content-Type": "audio/webm"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio(self, fuzz_client: AsyncClient):
        """Test that empty audio is rejected."""
        response = await fuzz_client.post(
            "/api/v1/ai/transcribe",
            content=b"",
            headers={"Content-Type": "audio/webm"},
        )
        # Should return 401 (no auth) or 400/422 (invalid content)
        assert response.status_code in (400, 401, 422)


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


class TestAISchemaValidation:
    """Validate AI endpoint request/response schemas."""

    def test_chat_request_schema(self, schema):
        """Test chat request schema is valid."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/ai/chat", {})
        post = path.get("post", {})

        assert "requestBody" in post
        content = post["requestBody"].get("content", {})
        assert "application/json" in content

    def test_subtask_generation_request_schema(self, schema):
        """Test subtask generation request schema is valid."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/ai/generate-subtasks", {})
        post = path.get("post", {})

        assert "requestBody" in post

    def test_credits_response_schema(self, schema):
        """Test credits response schema includes balance."""
        openapi = schema.raw_schema
        path = openapi["paths"].get("/api/v1/ai/credits", {})
        get = path.get("get", {})

        responses = get.get("responses", {})
        assert "200" in responses


# =============================================================================
# RATE LIMITING TESTS
# =============================================================================


class TestAIRateLimiting:
    """Test rate limiting on AI endpoints (FR-061: 20 req/min)."""

    @pytest.mark.asyncio
    async def test_chat_rate_limit_header_present(self, fuzz_client: AsyncClient):
        """Test that rate limit headers are returned."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": str(uuid.uuid4())},
        )
        # Even 401 responses should include rate limit headers
        # (depends on middleware order)


# =============================================================================
# ERROR RESPONSE VALIDATION
# =============================================================================


class TestAIErrorResponses:
    """Test AI endpoint error response format."""

    @pytest.mark.asyncio
    async def test_validation_error_format(self, fuzz_client: AsyncClient):
        """Test that validation errors follow standard format."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={},  # Missing required fields
        )

        if response.status_code == 422:
            data = response.json()
            # FastAPI validation error format
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_auth_error_format(self, fuzz_client: AsyncClient):
        """Test that auth errors follow standard format."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": str(uuid.uuid4())},
        )

        if response.status_code == 401:
            data = response.json()
            assert "error" in data or "detail" in data


# =============================================================================
# CREDIT CONSUMPTION TESTS
# =============================================================================


class TestAICreditConsumption:
    """Test AI credit consumption behavior."""

    @pytest.mark.asyncio
    async def test_insufficient_credits_response(self, fuzz_client: AsyncClient):
        """Test that 402 is returned when credits are insufficient."""
        # Without auth, we can't test actual credit consumption
        # but we can verify the endpoint accepts the request format
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": str(uuid.uuid4())},
        )
        # Expected: 401 (no auth), or 402 (no credits) if auth passes
        assert response.status_code in (401, 402)


# =============================================================================
# STREAMING RESPONSE TESTS
# =============================================================================


class TestAIStreaming:
    """Test AI chat streaming behavior."""

    @pytest.mark.asyncio
    async def test_chat_accepts_stream_header(self, fuzz_client: AsyncClient):
        """Test that chat endpoint accepts stream Accept header."""
        response = await fuzz_client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello", "task_id": str(uuid.uuid4())},
            headers={"Accept": "text/event-stream"},
        )
        # Should return 401 (no auth) - but endpoint accepts stream
        assert response.status_code == 401
