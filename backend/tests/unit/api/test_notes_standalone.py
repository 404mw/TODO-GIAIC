"""Unit tests for standalone notes API — Task 7.1 remaining items.

Covers:
- Standalone note creation without task context (FR-012 v1.2)
- ?archived=true/false filter on note list endpoint
- Note convert returns suggestion without auto-archiving; records notes_converted metric
- 402 LIMIT_EXCEEDED (not 409 NOTE_LIMIT_EXCEEDED) when note limit reached
- 410 ENDPOINT_GONE for deprecated POST/GET /tasks/{task_id}/notes
"""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks, HTTPException

from src.api.notes import create_note, list_notes, convert_note_to_task
from src.api.tasks import create_task_note_gone, list_task_notes_gone
from src.middleware.error_handler import LimitExceededError
from src.services.note_service import NoteLimitExceededError
from src.services.ai_service import InsufficientCreditsError


# =============================================================================
# FIXTURES
# =============================================================================


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


def _make_note(**overrides):
    note = MagicMock()
    note.id = uuid4()
    note.user_id = uuid4()
    note.content = "Test note"
    note.archived = False
    note.voice_url = None
    note.voice_duration_seconds = None
    note.transcription_status = None
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    for k, v in overrides.items():
        setattr(note, k, v)
    return note


# =============================================================================
# TEST 1: STANDALONE NOTE CREATION WITHOUT TASK CONTEXT (FR-012 v1.2)
# =============================================================================


class TestStandaloneNoteCreation:
    """Verify notes can be created without any task relationship (FR-012 v1.2)."""

    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_create_note_without_task_id(
        self, mock_resp_cls, mock_user, mock_note_service
    ):
        """Task 7.1: Standalone POST /api/v1/notes does not require task_id.

        The NoteCreate schema has no task_id field since v1.2.
        Notes are standalone user-owned entities.
        """
        from src.schemas.note import NoteCreate

        # Verify NoteCreate schema does not have task_id field
        fields = NoteCreate.model_fields
        assert "task_id" not in fields, (
            "NoteCreate must not have a task_id field (FR-012 v1.2: notes are standalone)"
        )

        # Verify note can be created with only content
        data = NoteCreate(content="My standalone note")
        assert data.content == "My standalone note"

        # Verify API endpoint works without task context
        note = _make_note()
        mock_note_service.create_note.return_value = note
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await create_note(
            data=MagicMock(),
            background_tasks=BackgroundTasks(),
            current_user=mock_user,
            note_service=mock_note_service,
            idempotency_key="key-1",
        )

        assert result.data is not None
        # create_note called without task_id context
        mock_note_service.create_note.assert_called_once()


# =============================================================================
# TEST 2: ?archived=true/false FILTER ON NOTE LIST ENDPOINT
# =============================================================================


class TestArchivedFilter:
    """Verify the ?archived=bool filter is correctly passed through the API layer."""

    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_list_notes_archived_false_excludes_archived(
        self, mock_resp_cls, mock_user, mock_note_service
    ):
        """Task 7.1: ?archived=false returns only active notes."""
        active_note = _make_note(archived=False)
        mock_note_service.list_notes.return_value = ([active_note], 1)
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await list_notes(
            current_user=mock_user,
            note_service=mock_note_service,
            archived=False,
            offset=0,
            limit=25,
        )

        # Service called with archived=False
        mock_note_service.list_notes.assert_called_once()
        call_kwargs = mock_note_service.list_notes.call_args.kwargs
        assert call_kwargs.get("archived") is False or (
            len(mock_note_service.list_notes.call_args.args) > 2
            and mock_note_service.list_notes.call_args.args[2] is False
        )
        assert result.pagination.total == 1

    @pytest.mark.asyncio
    @patch("src.api.notes.NoteResponse")
    async def test_list_notes_archived_true_includes_archived(
        self, mock_resp_cls, mock_user, mock_note_service
    ):
        """Task 7.1: ?archived=true returns both active and archived notes."""
        active = _make_note(archived=False)
        archived = _make_note(archived=True)
        mock_note_service.list_notes.return_value = ([active, archived], 2)
        mock_resp_cls.model_validate.return_value = MagicMock()

        result = await list_notes(
            current_user=mock_user,
            note_service=mock_note_service,
            archived=True,
            offset=0,
            limit=25,
        )

        # Service called with archived=True
        mock_note_service.list_notes.assert_called_once()
        call_kwargs = mock_note_service.list_notes.call_args.kwargs
        assert call_kwargs.get("archived") is True or (
            len(mock_note_service.list_notes.call_args.args) > 2
            and mock_note_service.list_notes.call_args.args[2] is True
        )
        assert result.pagination.total == 2


# =============================================================================
# TEST 3: NOTE CONVERT — NO AUTO-ARCHIVE + notes_converted METRIC
# =============================================================================


class TestNoteConvertBehavior:
    """Verify note convert returns AI suggestion without auto-archiving the note."""

    @pytest.mark.asyncio
    @patch("src.services.ai_service.record_note_to_task_conversion")
    async def test_convert_records_notes_converted_metric(
        self, mock_record_metric
    ):
        """Task 7.1 / FR-012 v1.2: convert_note_to_task records notes_converted metric."""
        from src.services.ai_service import AIService

        session = AsyncMock()
        settings = MagicMock()
        settings.ai_credit_conversion = 1
        settings.ai_task_warning_threshold = 5
        settings.ai_task_block_threshold = 10
        service = AIService(session, settings)

        user = MagicMock()
        user.id = uuid4()
        note_id = uuid4()

        # Mock credit balance (enough credits)
        balance_result = MagicMock()
        balance_result.scalar.return_value = 5

        # Mock note query (non-archived note)
        note_mock = MagicMock()
        note_mock.archived = False
        note_mock.content = "Buy groceries and clean house"
        note_scalar = MagicMock()
        note_scalar.scalar_one_or_none.return_value = note_mock

        # Mock session counter query (no counter yet)
        counter_scalar = MagicMock()
        counter_scalar.scalar_one_or_none.return_value = None

        # Mock AI client
        ai_result = MagicMock()
        ai_result.task.title = "Buy groceries"
        ai_result.task.description = "Get milk, eggs, bread"
        ai_result.task.priority = "medium"
        ai_result.task.due_date = None
        ai_result.task.estimated_duration = 30
        ai_result.task.subtasks = []
        ai_result.note_understanding = "Shopping and cleaning tasks"
        ai_result.confidence = 0.9

        service.ai_client = AsyncMock()
        service.ai_client.convert_note_to_task.return_value = ai_result

        # DB execute: first for balance, then note, then counter, then consume
        session.execute.side_effect = [
            balance_result,  # _get_credit_balance
            note_scalar,     # _get_note
            counter_scalar,  # _get_session_counter (if called)
            balance_result,  # consume_credits
            balance_result,  # _get_credit_balance after consume
        ]
        session.flush = AsyncMock()

        await service.convert_note_to_task(user=user, note_id=note_id)

        # notes_converted metric must be recorded
        mock_record_metric.assert_called_once()

    @pytest.mark.asyncio
    async def test_convert_api_endpoint_does_not_call_archive_note(
        self, mock_user, mock_ai_service
    ):
        """Task 7.1 / FR-012 v1.2: convert endpoint does NOT auto-archive note.

        The API endpoint only calls ai_service.convert_note_to_task().
        It has no note_service dependency — archive_note is never called.
        """
        mock_result = MagicMock()
        mock_ai_service.convert_note_to_task.return_value = mock_result

        result = await convert_note_to_task(
            note_id=uuid4(),
            current_user=mock_user,
            ai_service=mock_ai_service,
            idempotency_key="key-1",
        )

        # Only convert was called — no archive
        mock_ai_service.convert_note_to_task.assert_called_once()
        mock_ai_service.archive_note.assert_not_called()
        assert result.data == mock_result


# =============================================================================
# TEST 4: 402 LIMIT_EXCEEDED (not 409) WHEN NOTE LIMIT REACHED
# =============================================================================


class TestNoteLimitExceededReturns402:
    """Verify NoteLimitExceededError maps to HTTP 402 LimitExceededError (not 409)."""

    @pytest.mark.asyncio
    async def test_note_limit_exceeded_raises_limit_exceeded_error_402(
        self, mock_user, mock_note_service
    ):
        """Task 7.1: NoteLimitExceededError → LimitExceededError (HTTP 402).

        Per FR-012 v1.2: error code changed from 409 NOTE_LIMIT_EXCEEDED
        to 402 LIMIT_EXCEEDED.
        """
        mock_note_service.create_note.side_effect = NoteLimitExceededError(
            "Note limit of 10 reached for Free tier"
        )

        with pytest.raises(LimitExceededError) as exc_info:
            await create_note(
                data=MagicMock(),
                background_tasks=BackgroundTasks(),
                current_user=mock_user,
                note_service=mock_note_service,
                idempotency_key="key-1",
            )

        # LimitExceededError must report HTTP 402 (FR-012 v1.2)
        err = exc_info.value
        assert err is not None
        assert err.status_code == 402
        assert err.code == "LIMIT_EXCEEDED"


# =============================================================================
# TEST 5: 410 ENDPOINT_GONE FOR DEPRECATED TASK-SCOPED NOTE ENDPOINTS
# =============================================================================


class TestDeprecatedTaskNoteEndpointsReturn410:
    """Verify deprecated POST/GET /tasks/{task_id}/notes return 410 ENDPOINT_GONE."""

    @pytest.mark.asyncio
    async def test_deprecated_post_tasks_notes_returns_410(self):
        """Task 7.1: POST /tasks/{task_id}/notes → 410 ENDPOINT_GONE."""
        with pytest.raises(HTTPException) as exc_info:
            await create_task_note_gone(task_id=uuid4())

        exc = exc_info.value
        assert exc.status_code == 410
        assert exc.detail["code"] == "ENDPOINT_GONE"
        assert "POST /api/v1/notes" in exc.detail["message"]

    @pytest.mark.asyncio
    async def test_deprecated_get_tasks_notes_returns_410(self):
        """Task 7.1: GET /tasks/{task_id}/notes → 410 ENDPOINT_GONE."""
        with pytest.raises(HTTPException) as exc_info:
            await list_task_notes_gone(task_id=uuid4())

        exc = exc_info.value
        assert exc.status_code == 410
        assert exc.detail["code"] == "ENDPOINT_GONE"
        assert "GET /api/v1/notes" in exc.detail["message"]
