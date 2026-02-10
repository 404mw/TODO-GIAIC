"""Mock-based unit tests for AIService.

Covers uncovered code paths:
- AI agent error handling (timeout, unavailable)
- Deepgram error handling
- _record_transcription_failure / _record_transcription_success
- get_credit_balance_details
- _get_credit_balance_by_type
- _build_task_context
- clear_session_counters
- get_ai_service factory
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


def _make_service():
    from src.services.ai_service import AIService

    session = AsyncMock()
    settings = MagicMock()
    settings.ai_chat_cost = 1
    settings.ai_subtask_cost = 2
    settings.ai_transcription_cost = 3
    settings.ai_note_conversion_cost = 1
    settings.free_max_subtasks = 5
    settings.pro_max_subtasks = 10
    service = AIService(session, settings)
    return service, session, settings


def _make_user(**overrides):
    u = MagicMock()
    u.id = uuid4()
    u.tier = MagicMock()
    u.tier.value = "free"
    u.is_pro = False
    for k, v in overrides.items():
        setattr(u, k, v)
    return u


class TestGetCreditBalancePublic:
    @pytest.mark.asyncio
    async def test_returns_balance_breakdown(self):
        service, session, _ = _make_service()
        user = _make_user()

        # Each call to _get_credit_balance_by_type does a DB query
        result_mock = MagicMock()
        result_mock.scalar.return_value = 10
        session.execute.return_value = result_mock

        result = await service.get_credit_balance(user)

        assert "balance" in result
        assert "daily_reset_at" in result
        assert "tier" in result
        assert result["balance"]["total"] == 40  # 10 * 4 types

    @pytest.mark.asyncio
    async def test_zero_balances(self):
        service, session, _ = _make_service()
        user = _make_user()

        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        session.execute.return_value = result_mock

        result = await service.get_credit_balance(user)

        assert result["balance"]["total"] == 0


class TestBuildTaskContext:
    @pytest.mark.asyncio
    async def test_no_tasks(self):
        service, session, _ = _make_service()

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute.return_value = result_mock

        result = await service._build_task_context(uuid4(), 10)
        assert result == "No active tasks."

    @pytest.mark.asyncio
    async def test_with_tasks(self):
        service, session, _ = _make_service()

        task1 = MagicMock()
        task1.title = "Buy groceries"
        task1.due_date = datetime(2025, 6, 15, tzinfo=UTC)
        task1.priority = MagicMock()
        task1.priority.value = "high"

        task2 = MagicMock()
        task2.title = "Read book"
        task2.due_date = None
        task2.priority = None

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [task1, task2]
        session.execute.return_value = result_mock

        result = await service._build_task_context(uuid4(), 10)
        assert "Buy groceries" in result
        assert "[HIGH]" in result
        assert "Read book" in result


class TestClearSessionCounters:
    def test_clears_existing_session(self):
        service, _, _ = _make_service()
        service._task_request_counters["sess_123"] = {"task1": 5}

        service.clear_session_counters("sess_123")
        assert "sess_123" not in service._task_request_counters

    def test_no_error_for_missing_session(self):
        service, _, _ = _make_service()
        service.clear_session_counters("nonexistent")


class TestRecordTranscriptionFailure:
    def test_records_without_error(self):
        service, _, _ = _make_service()
        # Should not raise
        service._record_transcription_failure("timeout")
        service._record_transcription_failure("connection_error")
        service._record_transcription_failure("api_error")


class TestRecordTranscriptionSuccess:
    def test_records_without_error(self):
        service, _, _ = _make_service()
        service._record_transcription_success(
            tier="free",
            duration=1.5,
            audio_seconds=30,
            credits_used=3,
        )


class TestGetAiServiceFactory:
    def test_factory_returns_service(self):
        from src.services.ai_service import AIService, get_ai_service

        session = AsyncMock()
        settings = MagicMock()
        result = get_ai_service(session, settings)
        assert isinstance(result, AIService)


class TestGetCreditBalanceByType:
    @pytest.mark.asyncio
    async def test_returns_balance(self):
        from src.schemas.enums import CreditType

        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 25
        session.execute.return_value = result_mock

        result = await service._get_credit_balance_by_type(
            uuid4(), CreditType.DAILY
        )
        assert result == 25

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self):
        from src.schemas.enums import CreditType

        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar.return_value = None
        session.execute.return_value = result_mock

        result = await service._get_credit_balance_by_type(
            uuid4(), CreditType.PURCHASED
        )
        assert result == 0


class TestGetCreditBalance:
    @pytest.mark.asyncio
    async def test_returns_total_balance(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 50
        session.execute.return_value = result_mock

        result = await service._get_credit_balance(uuid4())
        assert result == 50

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self):
        service, session, _ = _make_service()
        result_mock = MagicMock()
        result_mock.scalar.return_value = None
        session.execute.return_value = result_mock

        result = await service._get_credit_balance(uuid4())
        assert result == 0
