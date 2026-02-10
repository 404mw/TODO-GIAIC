"""Integration tests for note lifecycle.

T175: Integration test for note lifecycle
Tests the complete note workflow from creation to deletion.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.note import Note
from src.models.user import User


class TestNoteLifecycle:
    """Integration tests for complete note lifecycle."""

    @pytest.mark.asyncio
    async def test_create_list_get_update_delete_note(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test full note lifecycle: create -> list -> get -> update -> delete."""
        # 1. CREATE NOTE
        create_response = await client.post(
            "/api/v1/notes",
            json={"content": "Initial note content"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert create_response.status_code == 201
        created_note = create_response.json()["data"]
        note_id = created_note["id"]
        assert created_note["content"] == "Initial note content"
        assert created_note["archived"] is False

        # 2. LIST NOTES - verify note appears
        list_response = await client.get(
            "/api/v1/notes",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["pagination"]["total"] >= 1
        note_ids = [n["id"] for n in list_data["data"]]
        assert note_id in note_ids

        # 3. GET NOTE - retrieve specific note
        get_response = await client.get(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        retrieved_note = get_response.json()["data"]
        assert retrieved_note["id"] == note_id
        assert retrieved_note["content"] == "Initial note content"

        # 4. UPDATE NOTE
        update_response = await client.patch(
            f"/api/v1/notes/{note_id}",
            json={"content": "Updated note content"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert update_response.status_code == 200
        updated_note = update_response.json()["data"]
        assert updated_note["content"] == "Updated note content"

        # 5. DELETE NOTE
        delete_response = await client.delete(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # 6. VERIFY DELETION
        get_deleted_response = await client.get(
            f"/api/v1/notes/{note_id}",
            headers=auth_headers,
        )
        assert get_deleted_response.status_code == 404

    @pytest.mark.asyncio
    async def test_note_isolation_between_users(
        self,
        client: AsyncClient,
        auth_headers: dict,
        pro_auth_headers: dict,
        test_user: User,
        pro_user: User,
    ):
        """Notes are isolated between users."""
        # Create note as test_user
        create_response = await client.post(
            "/api/v1/notes",
            json={"content": "Private note"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        note_id = create_response.json()["data"]["id"]

        # pro_user should not be able to access it
        get_response = await client.get(
            f"/api/v1/notes/{note_id}",
            headers=pro_auth_headers,
        )
        assert get_response.status_code == 404

        # pro_user's note list should not include it
        list_response = await client.get(
            "/api/v1/notes",
            headers=pro_auth_headers,
        )
        note_ids = [n["id"] for n in list_response.json()["data"]]
        assert note_id not in note_ids

    @pytest.mark.asyncio
    async def test_voice_note_lifecycle_pro_user(
        self,
        client: AsyncClient,
        pro_auth_headers: dict,
        pro_user: User,
    ):
        """Pro user can create and manage voice notes."""
        # Create voice note
        create_response = await client.post(
            "/api/v1/notes",
            json={
                "content": "Voice note transcription",
                "voice_url": "https://storage.example.com/voice/test.webm",
                "voice_duration_seconds": 60,
            },
            headers={**pro_auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert create_response.status_code == 201
        note = create_response.json()["data"]
        assert note["voice_url"] == "https://storage.example.com/voice/test.webm"
        assert note["voice_duration_seconds"] == 60

        # Verify in list
        list_response = await client.get(
            "/api/v1/notes",
            headers=pro_auth_headers,
        )
        notes = list_response.json()["data"]
        voice_notes = [n for n in notes if n["voice_url"] is not None]
        assert len(voice_notes) >= 1

    @pytest.mark.asyncio
    async def test_voice_note_blocked_for_free_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Free user cannot create voice notes."""
        response = await client.post(
            "/api/v1/notes",
            json={
                "content": "Voice note attempt",
                "voice_url": "https://storage.example.com/voice/test.webm",
                "voice_duration_seconds": 30,
            },
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "TIER_REQUIRED"

    @pytest.mark.asyncio
    async def test_note_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test pagination of notes."""
        # Create 5 notes
        for i in range(5):
            await client.post(
                "/api/v1/notes",
                json={"content": f"Pagination test note {i}"},
                headers={**auth_headers, "Idempotency-Key": str(uuid4())},
            )

        # Get first page with limit 2
        page1_response = await client.get(
            "/api/v1/notes?limit=2&offset=0",
            headers=auth_headers,
        )
        page1 = page1_response.json()
        assert len(page1["data"]) == 2
        assert page1["pagination"]["has_more"] is True
        assert page1["pagination"]["total"] >= 5

        # Get second page
        page2_response = await client.get(
            "/api/v1/notes?limit=2&offset=2",
            headers=auth_headers,
        )
        page2 = page2_response.json()
        assert len(page2["data"]) == 2

        # Verify no overlap
        page1_ids = {n["id"] for n in page1["data"]}
        page2_ids = {n["id"] for n in page2["data"]}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_archived_notes_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test archived notes filtering."""
        # Create archived note directly in DB
        archived_note = Note(
            id=uuid4(),
            user_id=test_user.id,
            content="Archived note",
            archived=True,
        )
        db_session.add(archived_note)
        await db_session.commit()

        # Create regular note via API
        await client.post(
            "/api/v1/notes",
            json={"content": "Regular note"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )

        # List without archived (default)
        list_response = await client.get(
            "/api/v1/notes",
            headers=auth_headers,
        )
        notes = list_response.json()["data"]
        archived_in_list = [n for n in notes if n["content"] == "Archived note"]
        assert len(archived_in_list) == 0

        # List with archived
        list_archived_response = await client.get(
            "/api/v1/notes?archived=true",
            headers=auth_headers,
        )
        all_notes = list_archived_response.json()["data"]
        archived_in_all = [n for n in all_notes if n["content"] == "Archived note"]
        assert len(archived_in_all) == 1

    @pytest.mark.asyncio
    async def test_note_limit_enforcement(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test that note limits are enforced."""
        # Create 9 notes (almost at free limit of 10)
        for i in range(9):
            db_session.add(
                Note(id=uuid4(), user_id=test_user.id, content=f"Note {i}")
            )
        await db_session.commit()

        # 10th note should work
        response_10 = await client.post(
            "/api/v1/notes",
            json={"content": "10th note"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response_10.status_code == 201

        # 11th note should fail
        response_11 = await client.post(
            "/api/v1/notes",
            json={"content": "11th note"},
            headers={**auth_headers, "Idempotency-Key": str(uuid4())},
        )
        assert response_11.status_code == 409
        assert response_11.json()["error"]["code"] == "LIMIT_EXCEEDED"
