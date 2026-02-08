"""Mock-based unit tests for NoteService.

Covers uncovered code paths:
- set_transcription_pending
- set_transcription_completed
- set_transcription_failed
- _update_transcription_status
- get_note_service factory
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.schemas.enums import TranscriptionStatus


def _make_service():
    from src.services.note_service import NoteService

    session = AsyncMock()
    settings = MagicMock()
    settings.free_max_notes = 50
    settings.pro_max_notes = 500
    service = NoteService(session, settings)
    return service, session, settings


def _make_user(**overrides):
    u = MagicMock()
    u.id = uuid4()
    u.tier = "free"
    u.is_pro = False
    for k, v in overrides.items():
        setattr(u, k, v)
    return u


def _make_note(**overrides):
    n = MagicMock()
    n.id = uuid4()
    n.user_id = uuid4()
    n.content = "Test note"
    n.archived = False
    n.voice_url = None
    n.transcription_status = None
    n.created_at = datetime.now(UTC)
    n.updated_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(n, k, v)
    return n


class TestSetTranscriptionPending:
    @pytest.mark.asyncio
    async def test_sets_pending_status(self):
        service, session, _ = _make_service()
        user = _make_user()
        note = _make_note(user_id=user.id)

        # get_note query
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = note
        session.execute.return_value = result_mock

        result = await service.set_transcription_pending(
            user=user, note_id=note.id,
        )

        assert note.transcription_status == TranscriptionStatus.PENDING


class TestSetTranscriptionCompleted:
    @pytest.mark.asyncio
    @patch("src.services.note_service.record_voice_note_operation")
    async def test_sets_completed_and_updates_content(self, mock_record):
        service, session, _ = _make_service()
        user = _make_user()
        note = _make_note(user_id=user.id, content="old content")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = note
        session.execute.return_value = result_mock

        result = await service.set_transcription_completed(
            user=user, note_id=note.id,
            transcription_text="Hello from voice",
        )

        assert note.transcription_status == TranscriptionStatus.COMPLETED
        assert note.content == "Hello from voice"
        mock_record.assert_called_once_with("transcribe")

    @pytest.mark.asyncio
    @patch("src.services.note_service.record_voice_note_operation")
    async def test_empty_transcription_preserves_content(self, mock_record):
        service, session, _ = _make_service()
        user = _make_user()
        note = _make_note(user_id=user.id, content="original")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = note
        session.execute.return_value = result_mock

        result = await service.set_transcription_completed(
            user=user, note_id=note.id,
            transcription_text="",
        )

        assert note.transcription_status == TranscriptionStatus.COMPLETED
        assert note.content == "original"


class TestSetTranscriptionFailed:
    @pytest.mark.asyncio
    async def test_sets_failed_status(self):
        service, session, _ = _make_service()
        user = _make_user()
        note = _make_note(user_id=user.id)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = note
        session.execute.return_value = result_mock

        result = await service.set_transcription_failed(
            user=user, note_id=note.id,
        )

        assert note.transcription_status == TranscriptionStatus.FAILED


class TestGetNoteServiceFactory:
    def test_returns_service_instance(self):
        from src.services.note_service import NoteService, get_note_service

        session = AsyncMock()
        settings = MagicMock()
        result = get_note_service(session, settings)
        assert isinstance(result, NoteService)
