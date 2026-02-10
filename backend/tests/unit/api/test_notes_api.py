"""Unit tests for Note API endpoints.

Tests all note CRUD and conversion endpoint functions with mocked dependencies.
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.api.notes import (
    list_notes,
    create_note,
    get_note,
    update_note,
    delete_note,
    convert_note_to_task,
)
from src.services.note_service import (
    NoteArchivedError,
    NoteLimitExceededError,
    NoteNotFoundError,
    VoiceNoteProRequiredError,
)
from src.services.ai_service import (
    AIServiceError,
    AIServiceUnavailableError,
    InsufficientCreditsError,
)
from src.middleware.error_handler import (
    ConflictError,
    ForbiddenError,
    LimitExceededError,
    NotFoundError,
    InsufficientCreditsError as HTTPInsufficientCreditsError,
    AIServiceUnavailableError as HTTPAIUnavailableError,
)


def _make_note(**overrides):
    """Create a mock note with proper typed attributes."""
    note = MagicMock()
    note.id = uuid4()
    note.user_id = uuid4()
    note.content = "Test note content"
    note.archived = False
    note.voice_url = None
    note.voice_duration_seconds = None
    note.transcription_status = None
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(note, k, v)
    return note


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.tier = "free"
    user.is_pro = False
    return user


@pytest.fixture
def mock_note_service():
    return AsyncMock()


@pytest.fixture
def mock_ai_service():
    return AsyncMock()


# =============================================================================
# LIST NOTES
# =============================================================================


class TestListNotes:
    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_note_service):
        note = _make_note()
        mock_note_service.list_notes.return_value = ([note], 1)
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await list_notes(
            current_user=mock_user, note_service=mock_note_service,
            archived=False, offset=0, limit=25,
        )

        assert result.pagination.total == 1

    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_empty(self, mock_resp_cls, mock_user, mock_note_service):
        mock_note_service.list_notes.return_value = ([], 0)

        result = await list_notes(
            current_user=mock_user, note_service=mock_note_service,
            archived=False, offset=0, limit=25,
        )

        assert result.pagination.total == 0
        assert result.data == []

    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_has_more(self, mock_resp_cls, mock_user, mock_note_service):
        notes = [_make_note() for _ in range(25)]
        mock_note_service.list_notes.return_value = (notes, 50)
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await list_notes(
            current_user=mock_user, note_service=mock_note_service,
            archived=False, offset=0, limit=25,
        )

        assert result.pagination.has_more is True


# =============================================================================
# CREATE NOTE
# =============================================================================


class TestCreateNote:
    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_note_service):
        note = _make_note()
        mock_note_service.create_note.return_value = note
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await create_note(
            data=MagicMock(), current_user=mock_user,
            note_service=mock_note_service, idempotency_key="key-1",
        )

        assert result.data is not None

    @pytest.mark.asyncio
    async def test_voice_pro_required(self, mock_user, mock_note_service):
        mock_note_service.create_note.side_effect = VoiceNoteProRequiredError("Pro only")

        with pytest.raises(ForbiddenError):
            await create_note(
                data=MagicMock(), current_user=mock_user,
                note_service=mock_note_service, idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_limit_exceeded(self, mock_user, mock_note_service):
        mock_note_service.create_note.side_effect = NoteLimitExceededError("Limit")

        with pytest.raises(LimitExceededError):
            await create_note(
                data=MagicMock(), current_user=mock_user,
                note_service=mock_note_service, idempotency_key="key-1",
            )


# =============================================================================
# GET NOTE
# =============================================================================


class TestGetNote:
    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_note_service):
        note = _make_note()
        mock_note_service.get_note.return_value = note
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await get_note(
            note_id=note.id, current_user=mock_user,
            note_service=mock_note_service,
        )

        assert result.data is not None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_note_service):
        mock_note_service.get_note.side_effect = NoteNotFoundError("Not found")

        with pytest.raises(NotFoundError):
            await get_note(
                note_id=uuid4(), current_user=mock_user,
                note_service=mock_note_service,
            )


# =============================================================================
# UPDATE NOTE
# =============================================================================


class TestUpdateNote:
    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_success(self, mock_resp_cls, mock_user, mock_note_service):
        note = _make_note()
        mock_note_service.update_note.return_value = note
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await update_note(
            note_id=note.id, data=MagicMock(),
            current_user=mock_user, note_service=mock_note_service,
            idempotency_key="key-1",
        )

        assert result.data is not None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_note_service):
        mock_note_service.update_note.side_effect = NoteNotFoundError("Not found")

        with pytest.raises(NotFoundError):
            await update_note(
                note_id=uuid4(), data=MagicMock(),
                current_user=mock_user, note_service=mock_note_service,
                idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_archived(self, mock_user, mock_note_service):
        mock_note_service.update_note.side_effect = NoteArchivedError("Archived")

        with pytest.raises(ConflictError):
            await update_note(
                note_id=uuid4(), data=MagicMock(),
                current_user=mock_user, note_service=mock_note_service,
                idempotency_key="key-1",
            )


# =============================================================================
# DELETE NOTE
# =============================================================================


class TestDeleteNote:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_note_service):
        mock_note_service.delete_note.return_value = None

        # delete_note returns None (204 No Content)
        result = await delete_note(
            note_id=uuid4(), current_user=mock_user,
            note_service=mock_note_service,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_user, mock_note_service):
        mock_note_service.delete_note.side_effect = NoteNotFoundError("Not found")

        with pytest.raises(NotFoundError):
            await delete_note(
                note_id=uuid4(), current_user=mock_user,
                note_service=mock_note_service,
            )


# =============================================================================
# CONVERT NOTE TO TASK
# =============================================================================


class TestConvertNoteToTask:
    @pytest.mark.asyncio
    async def test_success(self, mock_user, mock_ai_service):
        mock_result = MagicMock()
        mock_ai_service.convert_note_to_task.return_value = mock_result

        result = await convert_note_to_task(
            note_id=uuid4(), current_user=mock_user,
            ai_service=mock_ai_service, idempotency_key="key-1",
        )

        assert result.data == mock_result

    @pytest.mark.asyncio
    async def test_insufficient_credits(self, mock_user, mock_ai_service):
        mock_ai_service.convert_note_to_task.side_effect = InsufficientCreditsError("No credits")

        with pytest.raises(HTTPInsufficientCreditsError):
            await convert_note_to_task(
                note_id=uuid4(), current_user=mock_user,
                ai_service=mock_ai_service, idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_ai_error_not_found(self, mock_user, mock_ai_service):
        mock_ai_service.convert_note_to_task.side_effect = AIServiceError("Note not found")

        with pytest.raises(NotFoundError):
            await convert_note_to_task(
                note_id=uuid4(), current_user=mock_user,
                ai_service=mock_ai_service, idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_ai_error_archived(self, mock_user, mock_ai_service):
        mock_ai_service.convert_note_to_task.side_effect = AIServiceError("Note is archived")

        with pytest.raises(ConflictError):
            await convert_note_to_task(
                note_id=uuid4(), current_user=mock_user,
                ai_service=mock_ai_service, idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_ai_error_generic(self, mock_user, mock_ai_service):
        mock_ai_service.convert_note_to_task.side_effect = AIServiceError("Some AI error")

        with pytest.raises(HTTPAIUnavailableError):
            await convert_note_to_task(
                note_id=uuid4(), current_user=mock_user,
                ai_service=mock_ai_service, idempotency_key="key-1",
            )

    @pytest.mark.asyncio
    async def test_ai_unavailable(self, mock_user, mock_ai_service):
        mock_ai_service.convert_note_to_task.side_effect = AIServiceUnavailableError("Down")

        with pytest.raises(HTTPAIUnavailableError):
            await convert_note_to_task(
                note_id=uuid4(), current_user=mock_user,
                ai_service=mock_ai_service, idempotency_key="key-1",
            )
