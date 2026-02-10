"""Unit tests for AI service.

Phase 10: User Story 6 - AI Chat Widget (Priority: P3)
Tests for FR-029 to FR-035.

T221: AI chat deducts 1 credit (FR-030)
T222: AI chat returns 402 when 0 credits
T223: AI action suggestion requires confirmation (FR-034)
T224: AI request warning at 5 requests per task (FR-035)
T225: AI request blocked at 10 requests per task (FR-035)
T226: AI service unavailable returns 503

Phase 11: User Story 7 - Auto Subtask Generation (Priority: P3)
Tests for FR-031.

T243: Subtask generation deducts 1 credit (flat)
T244: Generated subtasks respect user tier limit
T245: SubtaskGenerator agent returns structured output
"""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.credit import AICreditLedger
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.ai import ChatRequest, ChatContext, SubtaskGenerationRequest
from src.schemas.ai_agents import (
    ActionSuggestion,
    ChatAgentResult,
    SubtaskGenerationResult,
    SubtaskSuggestionAgent,
)
from src.schemas.enums import CreditType, CreditOperation, UserTier


# =============================================================================
# TEST: T221 - AI chat deducts 1 credit (FR-030)
# =============================================================================


@pytest.mark.asyncio
async def test_ai_chat_deducts_one_credit(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T221: AI chat deducts exactly 1 credit per message (FR-030)."""
    from src.services.ai_service import AIService

    # Grant test user some credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    # Create AI service with mocked agent
    service = AIService(session=db_session, settings=settings)

    # Mock the AI agent response
    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="Test AI response",
            suggested_actions=[],
        )

        # Call chat
        request = ChatRequest(message="Hello, AI!")
        result = await service.chat(user=test_user, request=request)

    # Verify credit was deducted
    assert result.credits_used == 1
    assert result.credits_remaining == 9


# =============================================================================
# TEST: T222 - AI chat returns 402 when 0 credits
# =============================================================================


@pytest.mark.asyncio
async def test_ai_chat_returns_402_when_no_credits(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T222: AI chat returns 402 INSUFFICIENT_CREDITS when user has 0 credits."""
    from src.services.ai_service import AIService, InsufficientCreditsError

    # User has no credits
    service = AIService(session=db_session, settings=settings)

    request = ChatRequest(message="Hello, AI!")

    with pytest.raises(InsufficientCreditsError) as exc_info:
        await service.chat(user=test_user, request=request)

    assert "Insufficient credits" in str(exc_info.value)


# =============================================================================
# TEST: T223 - AI action suggestion requires confirmation (FR-034)
# =============================================================================


@pytest.mark.asyncio
async def test_ai_action_suggestion_requires_confirmation(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T223: AI actions are returned as suggestions requiring user confirmation (FR-034)."""
    from src.services.ai_service import AIService

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI agent returning an action suggestion
    task_id = uuid4()
    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="I suggest completing this task.",
            suggested_actions=[
                ActionSuggestion(
                    action_type="complete_task",
                    target_id=task_id,
                    action_description="Complete the quarterly report task",
                    confidence=0.9,
                )
            ],
        )

        request = ChatRequest(message="What should I do next?")
        result = await service.chat(user=test_user, request=request)

    # Verify action is returned as suggestion (not executed)
    assert len(result.suggested_actions) == 1
    assert result.suggested_actions[0].type == "complete_task"
    # Action should NOT be executed - only suggested
    assert result.suggested_actions[0].task_id == task_id


# =============================================================================
# TEST: T224 - AI request warning at 5 requests per task (FR-035)
# =============================================================================


@pytest.mark.asyncio
async def test_ai_request_warning_at_5_per_task(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T224: System warns at 5 AI requests per task (FR-035)."""
    from src.services.ai_service import AIService

    # Grant enough credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=20,
        balance_after=20,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Create a task to track requests
    task_id = uuid4()

    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="Test response",
            suggested_actions=[],
        )

        # Simulate session ID for per-session tracking
        session_id = str(uuid4())

        # Make 5 requests for the same task
        for i in range(5):
            request = ChatRequest(message="Help me with this task")
            result = await service.chat(
                user=test_user,
                request=request,
                task_id=task_id,
                session_id=session_id,
            )

        # 5th request should include warning
        assert result.ai_request_warning is True


# =============================================================================
# TEST: T225 - AI request blocked at 10 requests per task (FR-035)
# =============================================================================


@pytest.mark.asyncio
async def test_ai_request_blocked_at_10_per_task(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T225: AI requests blocked at 10 per task per session (FR-035)."""
    from src.services.ai_service import AIService, AITaskLimitExceededError

    # Grant enough credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=50,
        balance_after=50,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)
    task_id = uuid4()
    session_id = str(uuid4())

    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="Test response",
            suggested_actions=[],
        )

        # Make 10 requests
        for i in range(10):
            request = ChatRequest(message="Help me")
            await service.chat(
                user=test_user,
                request=request,
                task_id=task_id,
                session_id=session_id,
            )

        # 11th request should be blocked
        with pytest.raises(AITaskLimitExceededError):
            request = ChatRequest(message="One more")
            await service.chat(
                user=test_user,
                request=request,
                task_id=task_id,
                session_id=session_id,
            )


# =============================================================================
# TEST: T226 - AI service unavailable returns 503
# =============================================================================


@pytest.mark.asyncio
async def test_ai_service_unavailable_returns_503(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T226: When AI service is unavailable, return 503 error."""
    from src.services.ai_service import AIService, AIServiceUnavailableError

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI agent to raise exception
    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.side_effect = Exception("OpenAI API is down")

        request = ChatRequest(message="Hello!")

        with pytest.raises(AIServiceUnavailableError):
            await service.chat(user=test_user, request=request)


# =============================================================================
# TEST: Credit consumption is FIFO order
# =============================================================================


@pytest.mark.asyncio
async def test_ai_credit_consumption_fifo_order(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """Credits consumed in FIFO order: daily -> subscription -> purchased."""
    from src.services.ai_service import AIService

    # Grant different credit types
    daily_credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.DAILY,
        amount=5,
        balance_after=5,
        operation=CreditOperation.GRANT,
        consumed=0,
        expires_at=datetime.now(UTC).replace(hour=23, minute=59, second=59),
    )
    purchased_credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.PURCHASED,
        amount=10,
        balance_after=15,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(daily_credit)
    db_session.add(purchased_credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="Response",
            suggested_actions=[],
        )

        # Use 1 credit
        request = ChatRequest(message="Test")
        await service.chat(user=test_user, request=request)

    # Refresh credits from DB
    await db_session.refresh(daily_credit)
    await db_session.refresh(purchased_credit)

    # Daily credit should be consumed first
    assert daily_credit.consumed == 1
    assert purchased_credit.consumed == 0


# =============================================================================
# TEST: Session reset clears per-task counters
# =============================================================================


@pytest.mark.asyncio
async def test_session_change_resets_task_counters(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """New session resets per-task AI request counters (FR-035)."""
    from src.services.ai_service import AIService

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=50,
        balance_after=50,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)
    task_id = uuid4()

    with patch.object(service, '_call_chat_agent') as mock_agent:
        mock_agent.return_value = ChatAgentResult(
            response_text="Response",
            suggested_actions=[],
        )

        # Use session 1 - make 8 requests
        session_1 = str(uuid4())
        for _ in range(8):
            request = ChatRequest(message="Test")
            await service.chat(
                user=test_user,
                request=request,
                task_id=task_id,
                session_id=session_1,
            )

        # New session - counter should reset
        session_2 = str(uuid4())
        request = ChatRequest(message="Test")
        result = await service.chat(
            user=test_user,
            request=request,
            task_id=task_id,
            session_id=session_2,
        )

        # Should not have warning (only 1 request in new session)
        assert result.ai_request_warning is False


# =============================================================================
# PHASE 11: SUBTASK GENERATION TESTS (T243-T245)
# =============================================================================


# TEST: T243 - Subtask generation deducts 1 credit (flat) (FR-031)
# =============================================================================


@pytest.mark.asyncio
async def test_subtask_generation_deducts_one_credit(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T243: Subtask generation deducts exactly 1 credit (flat rate) per generation (FR-031)."""
    from src.services.ai_service import AIService

    # Grant test user some credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create a task to generate subtasks for
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Plan project launch",
        description="Launch the product by Q2",
    )
    db_session.add(task)
    await db_session.commit()

    # Create AI service
    service = AIService(session=db_session, settings=settings)

    # Mock the AI agent subtask generation
    with patch.object(service.ai_client, 'generate_subtasks') as mock_gen:
        mock_gen.return_value = SubtaskGenerationResult(
            subtasks=[
                SubtaskSuggestionAgent(title="Research market", rationale="Understand competition"),
                SubtaskSuggestionAgent(title="Draft timeline", rationale="Plan phases"),
            ],
            task_understanding="Planning a product launch",
        )

        # Generate subtasks
        request = SubtaskGenerationRequest(task_id=task.id)
        result = await service.generate_subtasks(user=test_user, request=request)

    # Verify credit was deducted - flat rate of 1 credit
    assert result.credits_used == 1
    assert result.credits_remaining == 9


@pytest.mark.asyncio
async def test_subtask_generation_no_credits_returns_402(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T243 (edge): Subtask generation returns 402 when no credits available."""
    from src.services.ai_service import AIService, InsufficientCreditsError

    # Create a task but no credits
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Test task",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)
    request = SubtaskGenerationRequest(task_id=task.id)

    with pytest.raises(InsufficientCreditsError) as exc_info:
        await service.generate_subtasks(user=test_user, request=request)

    assert "Insufficient credits" in str(exc_info.value)


# =============================================================================
# TEST: T244 - Generated subtasks respect user tier limit
# =============================================================================


@pytest.mark.asyncio
async def test_subtask_generation_respects_free_tier_limit(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T244: Free user subtask generation limited to 4 subtasks (free tier max)."""
    from src.services.ai_service import AIService

    # Ensure user is free tier
    test_user.tier = UserTier.FREE
    db_session.add(test_user)

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create task
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Complex project",
        description="A very complex project",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Track the max_subtasks parameter passed to AI
    captured_max = None

    async def capture_max_subtasks(task_title, task_description, max_subtasks):
        nonlocal captured_max
        captured_max = max_subtasks
        return SubtaskGenerationResult(
            subtasks=[SubtaskSuggestionAgent(title=f"Subtask {i}") for i in range(max_subtasks)],
            task_understanding="Complex project",
        )

    with patch.object(service.ai_client, 'generate_subtasks', side_effect=capture_max_subtasks):
        request = SubtaskGenerationRequest(task_id=task.id)
        result = await service.generate_subtasks(user=test_user, request=request)

    # Verify max_subtasks was limited to free tier limit (4)
    assert captured_max == settings.free_max_subtasks
    assert len(result.suggested_subtasks) <= settings.free_max_subtasks


@pytest.mark.asyncio
async def test_subtask_generation_respects_pro_tier_limit(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T244: Pro user subtask generation allows up to 10 subtasks."""
    from src.services.ai_service import AIService

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create task
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Enterprise project",
        description="Large enterprise project",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Track the max_subtasks parameter passed to AI
    captured_max = None

    async def capture_max_subtasks(task_title, task_description, max_subtasks):
        nonlocal captured_max
        captured_max = max_subtasks
        return SubtaskGenerationResult(
            subtasks=[SubtaskSuggestionAgent(title=f"Subtask {i}") for i in range(max_subtasks)],
            task_understanding="Enterprise project",
        )

    with patch.object(service.ai_client, 'generate_subtasks', side_effect=capture_max_subtasks):
        request = SubtaskGenerationRequest(task_id=task.id)
        result = await service.generate_subtasks(user=test_user, request=request)

    # Verify max_subtasks was set to pro tier limit (10)
    assert captured_max == settings.pro_max_subtasks
    assert len(result.suggested_subtasks) <= settings.pro_max_subtasks


# =============================================================================
# TEST: T245 - SubtaskGenerator agent returns structured output
# =============================================================================


@pytest.mark.asyncio
async def test_subtask_generator_returns_structured_output(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T245: SubtaskGenerator agent returns properly structured SubtaskGenerationResult."""
    from src.services.ai_service import AIService

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create task
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Write report",
        description="Quarterly sales report",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI with structured response
    with patch.object(service.ai_client, 'generate_subtasks') as mock_gen:
        mock_gen.return_value = SubtaskGenerationResult(
            subtasks=[
                SubtaskSuggestionAgent(
                    title="Gather sales data",
                    rationale="Need raw data before analysis",
                ),
                SubtaskSuggestionAgent(
                    title="Create charts",
                    rationale="Visual representation of trends",
                ),
                SubtaskSuggestionAgent(
                    title="Write summary",
                    rationale="Executive overview",
                ),
            ],
            task_understanding="Creating a quarterly sales report with data analysis",
        )

        request = SubtaskGenerationRequest(task_id=task.id)
        result = await service.generate_subtasks(user=test_user, request=request)

    # Verify structured output
    assert len(result.suggested_subtasks) == 3
    assert result.suggested_subtasks[0].title == "Gather sales data"
    assert result.suggested_subtasks[1].title == "Create charts"
    assert result.suggested_subtasks[2].title == "Write summary"

    # Verify response schema matches SubtaskGenerationResponse
    assert hasattr(result, 'suggested_subtasks')
    assert hasattr(result, 'credits_used')
    assert hasattr(result, 'credits_remaining')


@pytest.mark.asyncio
async def test_subtask_generator_handles_empty_response(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T245 (edge): SubtaskGenerator handles empty subtask list gracefully."""
    from src.services.ai_service import AIService

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create task
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Simple task",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI returning empty subtasks (task is too simple to break down)
    with patch.object(service.ai_client, 'generate_subtasks') as mock_gen:
        mock_gen.return_value = SubtaskGenerationResult(
            subtasks=[],
            task_understanding="Task is already atomic, no breakdown needed",
        )

        request = SubtaskGenerationRequest(task_id=task.id)
        result = await service.generate_subtasks(user=test_user, request=request)

    # Verify empty response is handled
    assert len(result.suggested_subtasks) == 0
    assert result.credits_used == 1  # Credit still deducted


@pytest.mark.asyncio
async def test_subtask_generation_task_not_found(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T245 (edge): Subtask generation raises error for non-existent task."""
    from src.services.ai_service import AIService, AIServiceError

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Try to generate subtasks for non-existent task
    fake_task_id = uuid4()
    request = SubtaskGenerationRequest(task_id=fake_task_id)

    with pytest.raises(AIServiceError) as exc_info:
        await service.generate_subtasks(user=test_user, request=request)

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_subtask_generation_service_unavailable(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T245 (edge): Subtask generation returns 503 when AI service is unavailable."""
    from src.services.ai_service import AIService, AIServiceUnavailableError
    from src.integrations.ai_agent import AIAgentUnavailableError

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create task
    task = TaskInstance(
        id=uuid4(),
        user_id=test_user.id,
        title="Test task",
    )
    db_session.add(task)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI service failure
    with patch.object(service.ai_client, 'generate_subtasks') as mock_gen:
        mock_gen.side_effect = AIAgentUnavailableError("OpenAI is down")

        request = SubtaskGenerationRequest(task_id=task.id)

        with pytest.raises(AIServiceUnavailableError):
            await service.generate_subtasks(user=test_user, request=request)


# =============================================================================
# PHASE 12: NOTE TO TASK CONVERSION TESTS (T253-T255)
# =============================================================================


# TEST: T253 - Note conversion deducts 1 credit (FR-032)
# =============================================================================


@pytest.mark.asyncio
async def test_note_conversion_deducts_one_credit(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T253: Note conversion deducts exactly 1 credit per conversion (FR-032)."""
    from src.services.ai_service import AIService
    from src.models.note import Note
    from src.schemas.ai_agents import NoteConversionResult, TaskSuggestion

    # Grant test user some credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create a note to convert
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Need to review Q4 sales report by Friday and send summary to team",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    # Create AI service
    service = AIService(session=db_session, settings=settings)

    # Mock the AI agent note conversion
    with patch.object(service.ai_client, 'convert_note_to_task') as mock_convert:
        mock_convert.return_value = NoteConversionResult(
            task=TaskSuggestion(
                title="Review Q4 sales report",
                description="Review and send summary to team",
            ),
            note_understanding="User needs to review a sales report and send summary",
            confidence=0.9,
        )

        # Convert note
        result = await service.convert_note_to_task(user=test_user, note_id=note.id)

    # Verify credit was deducted - flat rate of 1 credit
    assert result.credits_used == 1
    assert result.credits_remaining == 9


@pytest.mark.asyncio
async def test_note_conversion_no_credits_returns_402(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T253 (edge): Note conversion returns 402 when no credits available."""
    from src.services.ai_service import AIService, InsufficientCreditsError
    from src.models.note import Note

    # Create a note but no credits
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="This note should fail to convert",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    with pytest.raises(InsufficientCreditsError) as exc_info:
        await service.convert_note_to_task(user=test_user, note_id=note.id)

    assert "Insufficient credits" in str(exc_info.value)


# =============================================================================
# TEST: T254 - NoteConverter agent returns TaskSuggestion
# =============================================================================


@pytest.mark.asyncio
async def test_note_converter_returns_task_suggestion(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T254: NoteConverter agent returns properly structured TaskSuggestion."""
    from src.services.ai_service import AIService
    from src.models.note import Note
    from src.schemas.ai_agents import (
        NoteConversionResult,
        TaskSuggestion,
        SubtaskSuggestionAgent,
    )
    from src.schemas.enums import TaskPriority
    from datetime import datetime, timedelta

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create note
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Plan birthday party: buy cake, send invites, book venue by next week",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI with structured response including subtasks
    due_date = datetime.now() + timedelta(days=7)
    with patch.object(service.ai_client, 'convert_note_to_task') as mock_convert:
        mock_convert.return_value = NoteConversionResult(
            task=TaskSuggestion(
                title="Plan birthday party",
                description="Organize all party details",
                priority=TaskPriority.HIGH,
                due_date=due_date,
                estimated_duration=120,
                subtasks=[
                    SubtaskSuggestionAgent(title="Buy cake"),
                    SubtaskSuggestionAgent(title="Send invites"),
                    SubtaskSuggestionAgent(title="Book venue"),
                ],
            ),
            note_understanding="User needs to plan a birthday party with multiple tasks by next week",
            confidence=0.95,
        )

        result = await service.convert_note_to_task(user=test_user, note_id=note.id)

    # Verify structured output
    assert result.task_suggestion.title == "Plan birthday party"
    assert result.task_suggestion.description == "Organize all party details"
    assert result.task_suggestion.priority == TaskPriority.HIGH
    assert len(result.task_suggestion.subtasks) == 3
    assert result.task_suggestion.subtasks[0].title == "Buy cake"
    assert result.confidence == 0.95
    assert "birthday party" in result.note_understanding


@pytest.mark.asyncio
async def test_note_converter_handles_minimal_output(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T254 (edge): NoteConverter handles minimal response gracefully."""
    from src.services.ai_service import AIService
    from src.models.note import Note
    from src.schemas.ai_agents import NoteConversionResult, TaskSuggestion

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create simple note
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Call mom",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI returning minimal response (no subtasks, no due date)
    with patch.object(service.ai_client, 'convert_note_to_task') as mock_convert:
        mock_convert.return_value = NoteConversionResult(
            task=TaskSuggestion(title="Call mom"),
            note_understanding="Simple reminder to call mother",
            confidence=0.8,
        )

        result = await service.convert_note_to_task(user=test_user, note_id=note.id)

    # Verify minimal response is handled
    assert result.task_suggestion.title == "Call mom"
    assert result.task_suggestion.subtasks == []
    assert result.credits_used == 1


# =============================================================================
# TEST: T255 - Note archived after conversion confirmation
# =============================================================================


@pytest.mark.asyncio
async def test_note_archived_after_conversion_confirmation(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T255: Note is archived after user confirms the conversion."""
    from src.services.ai_service import AIService
    from src.services.note_service import NoteService
    from src.models.note import Note
    from src.schemas.ai_agents import NoteConversionResult, TaskSuggestion

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create note
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Important meeting notes to convert",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    # Verify note is not archived initially
    assert note.archived is False

    ai_service = AIService(session=db_session, settings=settings)
    note_service = NoteService(session=db_session, settings=settings)

    # Mock conversion
    with patch.object(ai_service.ai_client, 'convert_note_to_task') as mock_convert:
        mock_convert.return_value = NoteConversionResult(
            task=TaskSuggestion(title="Follow up on meeting"),
            note_understanding="Meeting notes to follow up on",
            confidence=0.9,
        )

        # Get conversion suggestion (note NOT archived yet)
        result = await ai_service.convert_note_to_task(
            user=test_user,
            note_id=note.id,
        )

    # Refresh note from DB
    await db_session.refresh(note)

    # Note should still NOT be archived after getting suggestion
    # (archiving happens only when user confirms and creates the task)
    assert note.archived is False

    # Now confirm conversion by archiving the note
    archived_note = await note_service.archive_note(user=test_user, note_id=note.id)

    # Verify note is now archived
    assert archived_note.archived is True

    # Refresh from DB to confirm persistence
    await db_session.refresh(note)
    assert note.archived is True


@pytest.mark.asyncio
async def test_note_not_found_returns_error(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T255 (edge): Converting non-existent note raises error."""
    from src.services.ai_service import AIService, AIServiceError

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Try to convert non-existent note
    fake_note_id = uuid4()

    with pytest.raises(AIServiceError) as exc_info:
        await service.convert_note_to_task(user=test_user, note_id=fake_note_id)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_archived_note_cannot_be_converted(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T255 (edge): Already archived notes cannot be converted."""
    from src.services.ai_service import AIService, AIServiceError
    from src.models.note import Note

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create archived note
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Already archived note",
        archived=True,  # Already archived
    )
    db_session.add(note)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    with pytest.raises(AIServiceError) as exc_info:
        await service.convert_note_to_task(user=test_user, note_id=note.id)

    assert "archived" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_note_conversion_service_unavailable(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T254 (edge): Note conversion returns 503 when AI service is unavailable."""
    from src.services.ai_service import AIService, AIServiceUnavailableError
    from src.integrations.ai_agent import AIAgentUnavailableError
    from src.models.note import Note

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=10,
        balance_after=10,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)

    # Create note
    note = Note(
        id=uuid4(),
        user_id=test_user.id,
        content="Note to convert",
        archived=False,
    )
    db_session.add(note)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock AI service failure
    with patch.object(service.ai_client, 'convert_note_to_task') as mock_convert:
        mock_convert.side_effect = AIAgentUnavailableError("OpenAI is down")

        with pytest.raises(AIServiceUnavailableError):
            await service.convert_note_to_task(user=test_user, note_id=note.id)


# =============================================================================
# PHASE 13: VOICE TRANSCRIPTION TESTS (T263-T265)
# =============================================================================


# TEST: T263 - Voice transcription requires Pro tier
# =============================================================================


@pytest.mark.asyncio
async def test_voice_transcription_requires_pro_tier(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T263: Voice transcription requires Pro tier - free users get 403."""
    from src.services.ai_service import AIService, TierRequiredError

    # Ensure user is free tier
    test_user.tier = UserTier.FREE
    db_session.add(test_user)

    # Grant credits (free user still has credits but can't use voice features)
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.KICKSTART,
        amount=50,
        balance_after=50,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Try to transcribe as free user
    with pytest.raises(TierRequiredError) as exc_info:
        await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    assert "Pro tier required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_voice_transcription_allowed_for_pro_tier(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T263 (positive): Pro users can use voice transcription."""
    from src.services.ai_service import AIService
    from src.schemas.ai_agents import TranscriptionResult

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock Deepgram client
    with patch.object(service, 'deepgram_client') as mock_deepgram:
        mock_deepgram.transcribe = AsyncMock(return_value=TranscriptionResult(
            text="This is a test transcription",
            language="en",
            confidence=0.95,
        ))

        # Transcribe as Pro user - should succeed
        result = await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    assert result.transcription == "This is a test transcription"
    assert result.language == "en"


# =============================================================================
# TEST: T264 - Transcription costs 5 credits per minute (FR-033)
# =============================================================================


@pytest.mark.asyncio
async def test_transcription_costs_5_credits_per_minute(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T264: Transcription costs 5 credits per minute, rounded up (FR-033)."""
    from src.services.ai_service import AIService
    from src.schemas.ai_agents import TranscriptionResult

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock Deepgram client
    with patch.object(service, 'deepgram_client') as mock_deepgram:
        mock_deepgram.transcribe = AsyncMock(return_value=TranscriptionResult(
            text="Test transcription",
            language="en",
            confidence=0.95,
        ))

        # Transcribe 45 seconds of audio (should cost 5 credits for 1 minute, rounded up)
        result = await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=45,
        )

    # 45 seconds = 0.75 minutes, rounded up to 1 minute = 5 credits
    assert result.credits_used == 5
    assert result.credits_remaining == 95


@pytest.mark.asyncio
async def test_transcription_costs_10_credits_for_90_seconds(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T264: 90 seconds of audio costs 10 credits (2 minutes rounded up)."""
    from src.services.ai_service import AIService
    from src.schemas.ai_agents import TranscriptionResult

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock Deepgram client
    with patch.object(service, 'deepgram_client') as mock_deepgram:
        mock_deepgram.transcribe = AsyncMock(return_value=TranscriptionResult(
            text="Test transcription",
            language="en",
            confidence=0.95,
        ))

        # Transcribe 90 seconds = 1.5 minutes = 2 minutes (rounded up) = 10 credits
        result = await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=90,
        )

    assert result.credits_used == 10
    assert result.credits_remaining == 90


@pytest.mark.asyncio
async def test_transcription_insufficient_credits(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T264 (edge): Transcription fails when insufficient credits for duration."""
    from src.services.ai_service import AIService, InsufficientCreditsError

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant only 3 credits (not enough for 1 minute = 5 credits)
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=3,
        balance_after=3,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Try to transcribe 30 seconds (needs 5 credits, only have 3)
    with pytest.raises(InsufficientCreditsError) as exc_info:
        await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    assert "Insufficient credits" in str(exc_info.value)


# =============================================================================
# TEST: T265 - Max 300 seconds audio enforced (FR-036)
# =============================================================================


@pytest.mark.asyncio
async def test_max_300_seconds_audio_enforced(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T265: Audio duration cannot exceed 300 seconds (5 minutes) (FR-036)."""
    from src.services.ai_service import AIService, AudioDurationExceededError

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant plenty of credits
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=500,
        balance_after=500,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Try to transcribe 301 seconds (exceeds 300 second limit)
    with pytest.raises(AudioDurationExceededError) as exc_info:
        await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/long.webm",
            duration_seconds=301,
        )

    assert "300 seconds" in str(exc_info.value)


@pytest.mark.asyncio
async def test_exactly_300_seconds_allowed(
    db_session: AsyncSession,
    test_user: User,
    settings: Settings,
):
    """T265 (boundary): Exactly 300 seconds is allowed."""
    from src.services.ai_service import AIService
    from src.schemas.ai_agents import TranscriptionResult

    # Set user to Pro tier
    test_user.tier = UserTier.PRO
    db_session.add(test_user)

    # Grant plenty of credits (300 seconds = 5 minutes = 25 credits)
    credit = AICreditLedger(
        id=uuid4(),
        user_id=test_user.id,
        credit_type=CreditType.SUBSCRIPTION,
        amount=100,
        balance_after=100,
        operation=CreditOperation.GRANT,
        consumed=0,
    )
    db_session.add(credit)
    await db_session.commit()

    service = AIService(session=db_session, settings=settings)

    # Mock Deepgram client
    with patch.object(service, 'deepgram_client') as mock_deepgram:
        mock_deepgram.transcribe = AsyncMock(return_value=TranscriptionResult(
            text="Long transcription text",
            language="en",
            confidence=0.92,
        ))

        # Transcribe exactly 300 seconds (should succeed)
        result = await service.transcribe_voice(
            user=test_user,
            audio_url="https://storage.example.com/audio/max.webm",
            duration_seconds=300,
        )

    # 300 seconds = 5 minutes = 25 credits
    assert result.credits_used == 25
    assert result.credits_remaining == 75
