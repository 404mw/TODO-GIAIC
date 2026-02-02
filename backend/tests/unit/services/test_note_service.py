"""Unit tests for NoteService.

Phase 7: User Story 5 - Notes with Voice Recording (Priority: P2)
Tests for FR-022 to FR-024.

T159: Test: Create text note with content validation (FR-023)
T160: Test: Free user limited to 10 notes (FR-022)
T161: Test: Pro user limited to 25 notes (FR-022)
T162: Test: Voice note requires Pro tier (FR-024)
T163: Test: Voice recording max 300 seconds (FR-036)
"""

from datetime import datetime, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.note import Note
from src.models.user import User
from src.schemas.enums import UserTier
from src.schemas.note import NoteCreate, NoteUpdate


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def note_service(db_session: AsyncSession, settings):
    """Create NoteService instance."""
    from src.services.note_service import NoteService

    return NoteService(db_session, settings)


@pytest.fixture
async def existing_notes_for_free_user(db_session: AsyncSession, test_user: User):
    """Create 10 notes for free user (at limit)."""
    notes = []
    for i in range(10):
        note = Note(
            id=uuid4(),
            user_id=test_user.id,
            content=f"Note {i + 1}",
        )
        db_session.add(note)
        notes.append(note)
    await db_session.commit()
    return notes


@pytest.fixture
async def existing_notes_for_pro_user(db_session: AsyncSession, pro_user: User):
    """Create 25 notes for pro user (at limit)."""
    notes = []
    for i in range(25):
        note = Note(
            id=uuid4(),
            user_id=pro_user.id,
            content=f"Pro Note {i + 1}",
        )
        db_session.add(note)
        notes.append(note)
    await db_session.commit()
    return notes


# =============================================================================
# T159: TEXT NOTE CREATION WITH CONTENT VALIDATION (FR-023)
# =============================================================================


class TestCreateTextNote:
    """Tests for text note creation with content validation."""

    @pytest.mark.asyncio
    async def test_create_text_note_success(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """T159: Create text note with valid content."""
        data = NoteCreate(content="Remember to buy groceries")

        note = await note_service.create_note(user=test_user, data=data)

        assert note is not None
        assert note.id is not None
        assert note.content == "Remember to buy groceries"
        assert note.user_id == test_user.id
        assert note.archived is False
        assert note.voice_url is None
        assert note.voice_duration_seconds is None
        assert note.transcription_status is None
        assert note.created_at is not None

    @pytest.mark.asyncio
    async def test_create_text_note_strips_whitespace(
        self, note_service, test_user: User
    ):
        """T159: Note content whitespace is trimmed."""
        data = NoteCreate(content="  Important note  ")

        note = await note_service.create_note(user=test_user, data=data)

        assert note.content == "Important note"

    @pytest.mark.asyncio
    async def test_create_text_note_max_content_length(
        self, note_service, test_user: User
    ):
        """T159: Note content can be up to 2000 characters (FR-023)."""
        data = NoteCreate(content="x" * 2000)

        note = await note_service.create_note(user=test_user, data=data)

        assert len(note.content) == 2000

    @pytest.mark.asyncio
    async def test_create_text_note_exceeds_max_length_rejected(
        self, note_service, test_user: User
    ):
        """T159: Content exceeding 2000 chars is rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(content="x" * 2001)

    @pytest.mark.asyncio
    async def test_create_text_note_empty_content_rejected(
        self, note_service, test_user: User
    ):
        """T159: Empty content is rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(content="")

    @pytest.mark.asyncio
    async def test_create_text_note_whitespace_only_rejected(
        self, note_service, test_user: User
    ):
        """T159: Whitespace-only content is rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(content="   ")


# =============================================================================
# T160: FREE USER NOTE LIMIT (FR-022)
# =============================================================================


class TestFreeUserNoteLimit:
    """Tests for free user note limit of 10."""

    @pytest.mark.asyncio
    async def test_free_user_can_create_up_to_10_notes(
        self, note_service, test_user: User
    ):
        """T160: Free user can create notes up to limit."""
        notes = []
        for i in range(10):
            data = NoteCreate(content=f"Note {i + 1}")
            note = await note_service.create_note(user=test_user, data=data)
            notes.append(note)

        assert len(notes) == 10

    @pytest.mark.asyncio
    async def test_free_user_exceeds_10_notes_rejected(
        self, note_service, test_user: User, existing_notes_for_free_user
    ):
        """T160: Free user blocked at 10 notes (FR-022)."""
        from src.services.note_service import NoteLimitExceededError

        data = NoteCreate(content="11th note")

        with pytest.raises(NoteLimitExceededError) as exc_info:
            await note_service.create_note(user=test_user, data=data)

        assert "10" in str(exc_info.value)  # Limit mentioned in error


# =============================================================================
# T161: PRO USER NOTE LIMIT (FR-022)
# =============================================================================


class TestProUserNoteLimit:
    """Tests for pro user note limit of 25."""

    @pytest.mark.asyncio
    async def test_pro_user_can_create_up_to_25_notes(
        self, note_service, pro_user: User
    ):
        """T161: Pro user can create notes up to limit."""
        notes = []
        for i in range(25):
            data = NoteCreate(content=f"Pro Note {i + 1}")
            note = await note_service.create_note(user=pro_user, data=data)
            notes.append(note)

        assert len(notes) == 25

    @pytest.mark.asyncio
    async def test_pro_user_exceeds_25_notes_rejected(
        self, note_service, pro_user: User, existing_notes_for_pro_user
    ):
        """T161: Pro user blocked at 25 notes (FR-022)."""
        from src.services.note_service import NoteLimitExceededError

        data = NoteCreate(content="26th note")

        with pytest.raises(NoteLimitExceededError) as exc_info:
            await note_service.create_note(user=pro_user, data=data)

        assert "25" in str(exc_info.value)  # Limit mentioned in error


# =============================================================================
# T162: VOICE NOTE REQUIRES PRO TIER (FR-024)
# =============================================================================


class TestVoiceNoteProTierRequired:
    """Tests for voice note Pro tier requirement."""

    @pytest.mark.asyncio
    async def test_voice_note_rejected_for_free_user(
        self, note_service, test_user: User
    ):
        """T162: Voice notes require Pro tier (FR-024)."""
        from src.services.note_service import VoiceNoteProRequiredError

        data = NoteCreate(
            content="Voice note content",
            voice_url="https://storage.example.com/audio.webm",
            voice_duration_seconds=45,
        )

        with pytest.raises(VoiceNoteProRequiredError):
            await note_service.create_note(user=test_user, data=data)

    @pytest.mark.asyncio
    async def test_voice_note_allowed_for_pro_user(
        self, note_service, pro_user: User
    ):
        """T162: Pro user can create voice notes (FR-024)."""
        data = NoteCreate(
            content="Voice note content",
            voice_url="https://storage.example.com/audio.webm",
            voice_duration_seconds=45,
        )

        note = await note_service.create_note(user=pro_user, data=data)

        assert note.voice_url == "https://storage.example.com/audio.webm"
        assert note.voice_duration_seconds == 45


# =============================================================================
# T163: VOICE RECORDING MAX 300 SECONDS (FR-036)
# =============================================================================


class TestVoiceRecordingMaxDuration:
    """Tests for voice recording duration limit."""

    @pytest.mark.asyncio
    async def test_voice_recording_at_max_duration_allowed(
        self, note_service, pro_user: User
    ):
        """T163: Voice recording exactly at 300 seconds allowed (FR-036)."""
        data = NoteCreate(
            content="Long voice note",
            voice_url="https://storage.example.com/audio.webm",
            voice_duration_seconds=300,
        )

        note = await note_service.create_note(user=pro_user, data=data)

        assert note.voice_duration_seconds == 300

    @pytest.mark.asyncio
    async def test_voice_recording_exceeds_max_duration_rejected(
        self, note_service, pro_user: User
    ):
        """T163: Voice recording exceeding 300 seconds rejected (FR-036)."""
        from pydantic import ValidationError

        # This should be caught at schema validation level
        with pytest.raises(ValidationError):
            NoteCreate(
                content="Too long voice note",
                voice_url="https://storage.example.com/audio.webm",
                voice_duration_seconds=301,
            )

    @pytest.mark.asyncio
    async def test_voice_recording_min_duration_validation(
        self, note_service, pro_user: User
    ):
        """T163: Voice recording must be at least 1 second."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(
                content="Too short voice note",
                voice_url="https://storage.example.com/audio.webm",
                voice_duration_seconds=0,
            )


# =============================================================================
# ADDITIONAL TESTS FOR NOTE SERVICE METHODS
# =============================================================================


class TestGetNote:
    """Tests for getting a note."""

    @pytest.mark.asyncio
    async def test_get_note_success(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Get note by ID with ownership check."""
        # Create a note first
        note = Note(
            id=uuid4(),
            user_id=test_user.id,
            content="Test note",
        )
        db_session.add(note)
        await db_session.commit()

        # Get the note
        retrieved = await note_service.get_note(user=test_user, note_id=note.id)

        assert retrieved.id == note.id
        assert retrieved.content == "Test note"

    @pytest.mark.asyncio
    async def test_get_note_not_found(self, note_service, test_user: User):
        """Get non-existent note raises error."""
        from src.services.note_service import NoteNotFoundError

        with pytest.raises(NoteNotFoundError):
            await note_service.get_note(user=test_user, note_id=uuid4())

    @pytest.mark.asyncio
    async def test_get_note_wrong_user_rejected(
        self, note_service, test_user: User, pro_user: User, db_session: AsyncSession
    ):
        """User cannot access another user's note."""
        from src.services.note_service import NoteNotFoundError

        # Create a note for test_user
        note = Note(
            id=uuid4(),
            user_id=test_user.id,
            content="Private note",
        )
        db_session.add(note)
        await db_session.commit()

        # pro_user tries to access it
        with pytest.raises(NoteNotFoundError):
            await note_service.get_note(user=pro_user, note_id=note.id)


class TestListNotes:
    """Tests for listing notes with pagination."""

    @pytest.mark.asyncio
    async def test_list_notes_with_pagination(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """List notes with pagination."""
        # Create 5 notes
        for i in range(5):
            db_session.add(Note(id=uuid4(), user_id=test_user.id, content=f"Note {i}"))
        await db_session.commit()

        # Get first page
        notes, total = await note_service.list_notes(
            user=test_user, offset=0, limit=3
        )

        assert len(notes) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_list_notes_excludes_archived_by_default(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Archived notes excluded by default."""
        # Create regular and archived notes
        db_session.add(Note(id=uuid4(), user_id=test_user.id, content="Regular note"))
        db_session.add(
            Note(id=uuid4(), user_id=test_user.id, content="Archived note", archived=True)
        )
        await db_session.commit()

        notes, total = await note_service.list_notes(user=test_user, archived=False)

        assert total == 1
        assert notes[0].content == "Regular note"

    @pytest.mark.asyncio
    async def test_list_notes_includes_archived_when_requested(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Archived notes included when requested."""
        # Create regular and archived notes
        db_session.add(Note(id=uuid4(), user_id=test_user.id, content="Regular note"))
        db_session.add(
            Note(id=uuid4(), user_id=test_user.id, content="Archived note", archived=True)
        )
        await db_session.commit()

        notes, total = await note_service.list_notes(user=test_user, archived=True)

        assert total == 2


class TestUpdateNote:
    """Tests for updating notes."""

    @pytest.mark.asyncio
    async def test_update_note_content(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Update note content."""
        note = Note(id=uuid4(), user_id=test_user.id, content="Original content")
        db_session.add(note)
        await db_session.commit()

        data = NoteUpdate(content="Updated content")
        updated = await note_service.update_note(
            user=test_user, note_id=note.id, data=data
        )

        assert updated.content == "Updated content"

    @pytest.mark.asyncio
    async def test_update_archived_note_rejected(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Cannot update archived note."""
        from src.services.note_service import NoteArchivedError

        note = Note(
            id=uuid4(), user_id=test_user.id, content="Archived note", archived=True
        )
        db_session.add(note)
        await db_session.commit()

        data = NoteUpdate(content="New content")
        with pytest.raises(NoteArchivedError):
            await note_service.update_note(user=test_user, note_id=note.id, data=data)


class TestDeleteNote:
    """Tests for deleting notes."""

    @pytest.mark.asyncio
    async def test_delete_note_success(
        self, note_service, test_user: User, db_session: AsyncSession
    ):
        """Delete note successfully."""
        note = Note(id=uuid4(), user_id=test_user.id, content="To be deleted")
        db_session.add(note)
        await db_session.commit()
        note_id = note.id

        await note_service.delete_note(user=test_user, note_id=note_id)

        from src.services.note_service import NoteNotFoundError

        with pytest.raises(NoteNotFoundError):
            await note_service.get_note(user=test_user, note_id=note_id)

    @pytest.mark.asyncio
    async def test_delete_note_not_found(self, note_service, test_user: User):
        """Delete non-existent note raises error."""
        from src.services.note_service import NoteNotFoundError

        with pytest.raises(NoteNotFoundError):
            await note_service.delete_note(user=test_user, note_id=uuid4())
