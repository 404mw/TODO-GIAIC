"""Contract tests for Note API endpoints.

T164: Contract test: Note CRUD endpoints
Validates request/response schemas match api-specification.md Section 6.

Tests verify:
- Request body schemas for POST/PATCH
- Response schemas for all endpoints
- Error response formats
- Pagination format
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


# =============================================================================
# NOTE ENDPOINT CONTRACT TESTS
# =============================================================================


class TestNoteContractSchemas:
    """Contract tests for Note endpoints."""

    @pytest.mark.asyncio
    async def test_list_notes_response_schema(
        self, client: AsyncClient, auth_headers: dict, test_user
    ):
        """GET /api/v1/notes response matches contract."""
        response = await client.get("/api/v1/notes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # Verify pagination structure
        pagination = data["pagination"]
        assert "offset" in pagination
        assert "limit" in pagination
        assert "total" in pagination
        assert "has_more" in pagination

    @pytest.mark.asyncio
    async def test_create_note_request_schema(
        self, client: AsyncClient, auth_headers: dict, idempotency_key: str
    ):
        """POST /api/v1/notes request schema validation."""
        # Valid request
        valid_payload = {"content": "Test note content"}

        response = await client.post(
            "/api/v1/notes",
            json=valid_payload,
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "data" in data
        note = data["data"]
        assert "id" in note
        assert "content" in note
        assert "archived" in note
        assert "voice_url" in note
        assert "voice_duration_seconds" in note
        assert "transcription_status" in note
        assert "created_at" in note
        assert "updated_at" in note

    @pytest.mark.asyncio
    async def test_create_note_with_voice_request_schema(
        self, client: AsyncClient, pro_auth_headers: dict, idempotency_key: str
    ):
        """POST /api/v1/notes with voice fields request schema (Pro)."""
        valid_payload = {
            "content": "Voice note content",
            "voice_url": "https://storage.example.com/voice/abc123.webm",
            "voice_duration_seconds": 45,
        }

        response = await client.post(
            "/api/v1/notes",
            json=valid_payload,
            headers={**pro_auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 201
        data = response.json()
        note = data["data"]

        assert note["voice_url"] == "https://storage.example.com/voice/abc123.webm"
        assert note["voice_duration_seconds"] == 45

    @pytest.mark.asyncio
    async def test_create_note_invalid_content_rejected(
        self, client: AsyncClient, auth_headers: dict, idempotency_key: str
    ):
        """POST /api/v1/notes rejects invalid content."""
        # Empty content
        invalid_payload = {"content": ""}

        response = await client.post(
            "/api/v1/notes",
            json=invalid_payload,
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_update_note_request_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        idempotency_key: str,
    ):
        """PATCH /api/v1/notes/:id request schema validation."""
        # First create a note
        create_response = await client.post(
            "/api/v1/notes",
            json={"content": "Original content"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        note_id = create_response.json()["data"]["id"]

        # Update the note
        update_payload = {"content": "Updated content"}

        response = await client.patch(
            f"/api/v1/notes/{note_id}",
            json=update_payload,
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert data["data"]["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_get_note_not_found_error_schema(
        self, client: AsyncClient, auth_headers: dict
    ):
        """GET /api/v1/notes/:id returns proper error for not found."""
        fake_id = str(uuid4())

        response = await client.get(
            f"/api/v1/notes/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()

        # Verify error structure per api-specification.md Section 11
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_note_response_schema(
        self, client: AsyncClient, auth_headers: dict, idempotency_key: str
    ):
        """DELETE /api/v1/notes/:id response schema."""
        # First create a note
        create_response = await client.post(
            "/api/v1/notes",
            json={"content": "To be deleted"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        note_id = create_response.json()["data"]["id"]

        # Delete the note
        response = await client.delete(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_voice_note_free_tier_error_schema(
        self, client: AsyncClient, auth_headers: dict, idempotency_key: str
    ):
        """POST /api/v1/notes voice note returns 403 for free tier."""
        payload = {
            "content": "Voice note",
            "voice_url": "https://storage.example.com/voice/abc.webm",
            "voice_duration_seconds": 30,
        }

        response = await client.post(
            "/api/v1/notes",
            json=payload,
            headers={**auth_headers, "Idempotency-Key": idempotency_key},
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "TIER_REQUIRED"

    @pytest.mark.asyncio
    async def test_note_limit_exceeded_error_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        db_session,
    ):
        """POST /api/v1/notes returns 409 when limit exceeded."""
        from src.models.note import Note

        # Create 10 notes (free tier limit)
        for i in range(10):
            db_session.add(
                Note(id=uuid4(), user_id=test_user.id, content=f"Note {i}")
            )
        await db_session.commit()

        # Try to create 11th note
        response = await client.post(
            "/api/v1/notes",
            json={"content": "11th note"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )

        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "LIMIT_EXCEEDED"
