"""AI service for chat, subtask generation, note conversion, and voice transcription.

Phase 10: User Story 6 - AI Chat Widget (Priority: P3)
Implements FR-029 to FR-035.

T232: AIService.chat with credit check (FR-030)
T233: Action suggestion validation (FR-034)
T234: Per-task AI request counter (FR-035)
T241: AI interaction logging (FR-052)

Phase 11: User Story 7 - Auto Subtask Generation (Priority: P3)
Implements FR-031.

T247: AIService.generate_subtasks (FR-031)
T248: Subtask limit enforcement in generation
T251: Metrics for subtask generation

Phase 12: User Story 5 Extended - Note to Task Conversion (Priority: P3)
Implements FR-032.

T257: AIService.convert_note_to_task (FR-032)
T261: Metrics for note conversion

Phase 13: Voice Transcription (Priority: P3)
Implements FR-033, FR-036.

T268: AIService.transcribe_voice with credit calculation (FR-033)
T273: Transcription metrics
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, UTC
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.integrations.ai_agent import (
    AIAgentClient,
    AIAgentTimeoutError,
    AIAgentUnavailableError,
)
from src.integrations.deepgram_client import (
    DeepgramClient,
    DeepgramError,
    DeepgramTimeoutError,
    DeepgramConnectionError,
    DeepgramAPIError,
)
from src.models.credit import AICreditLedger
from src.models.note import Note
from src.models.task import TaskInstance
from src.models.user import User
from src.schemas.ai import (
    ChatRequest,
    ChatResponse,
    SuggestedAction,
    SubtaskGenerationRequest,
    SubtaskGenerationResponse,
    SubtaskSuggestion,
)
from src.schemas.ai_agents import ActionSuggestion, ChatAgentResult
from src.schemas.enums import CreditType, CreditOperation
from src.schemas.note import (
    NoteConvertResponse,
    TaskSuggestion as NoteTaskSuggestion,
    SubtaskSuggestion as NoteSubtaskSuggestion,
)
from src.middleware.metrics import (
    record_credit_consumption,
    record_subtask_generation_request,
    record_subtask_generation_latency,
    record_subtasks_generated_count,
    record_subtask_generation_failure,
    record_note_to_task_conversion,
)


logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    pass


class InsufficientCreditsError(AIServiceError):
    """Raised when user has insufficient AI credits (402)."""

    pass


class AITaskLimitExceededError(AIServiceError):
    """Raised when per-task AI request limit is reached (429)."""

    pass


class AIServiceUnavailableError(AIServiceError):
    """Raised when AI service is unavailable (503)."""

    pass


class TierRequiredError(AIServiceError):
    """Raised when feature requires higher tier (403)."""

    pass


class AudioDurationExceededError(AIServiceError):
    """Raised when audio exceeds maximum duration (400)."""

    pass


# =============================================================================
# AI SERVICE RESPONSE
# =============================================================================


class AIServiceChatResponse:
    """Extended chat response with warning flag."""

    def __init__(
        self,
        response: str,
        suggested_actions: list[SuggestedAction],
        credits_used: int,
        credits_remaining: int,
        ai_request_warning: bool = False,
    ):
        self.response = response
        self.suggested_actions = suggested_actions
        self.credits_used = credits_used
        self.credits_remaining = credits_remaining
        self.ai_request_warning = ai_request_warning


class AIServiceTranscriptionResponse:
    """Response from voice transcription.

    Phase 13: T268 - Transcription response
    """

    def __init__(
        self,
        transcription: str,
        language: str,
        confidence: float,
        credits_used: int,
        credits_remaining: int,
    ):
        self.transcription = transcription
        self.language = language
        self.confidence = confidence
        self.credits_used = credits_used
        self.credits_remaining = credits_remaining


# =============================================================================
# AI SERVICE
# =============================================================================


class AIService:
    """Service for AI-powered features.

    Handles:
    - AI chat with credit consumption (FR-030)
    - Action suggestions requiring confirmation (FR-034)
    - Per-task request limits (FR-035)
    - Credit balance management
    """

    # Per-task request limits (FR-035)
    AI_TASK_WARNING_THRESHOLD = 5
    AI_TASK_BLOCK_THRESHOLD = 10

    def __init__(self, session: AsyncSession, settings: Settings):
        """Initialize AI service.

        Args:
            session: Database session
            settings: Application settings
        """
        self.session = session
        self.settings = settings
        self.ai_client = AIAgentClient(settings)
        self.deepgram_client = DeepgramClient(settings)

        # Per-session, per-task request counters
        # Format: {session_id: {task_id: count}}
        self._task_request_counters: dict[str, dict[UUID, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    # =========================================================================
    # CHAT (T232, T233, T234)
    # =========================================================================

    async def chat(
        self,
        user: User,
        request: ChatRequest,
        task_id: UUID | None = None,
        session_id: str | None = None,
    ) -> AIServiceChatResponse:
        """Process AI chat message.

        T232: AIService.chat with credit check (FR-030)
        T233: Action suggestion validation (FR-034)
        T234: Per-task AI request counter (FR-035)

        Args:
            user: The requesting user
            request: Chat request with message and context
            task_id: Optional task ID for per-task limits
            session_id: Session ID for per-session tracking

        Returns:
            AIServiceChatResponse with response and credits info

        Raises:
            InsufficientCreditsError: If user has 0 credits (402)
            AITaskLimitExceededError: If 10 requests per task reached (429)
            AIServiceUnavailableError: If AI is down (503)
        """
        # T234: Check per-task request limit (FR-035)
        ai_request_warning = False
        if task_id and session_id:
            request_count = self._task_request_counters[session_id][task_id]

            if request_count >= self.AI_TASK_BLOCK_THRESHOLD:
                raise AITaskLimitExceededError(
                    f"AI request limit of {self.AI_TASK_BLOCK_THRESHOLD} "
                    f"per task per session reached"
                )

            # Include current request in count for warning
            if request_count + 1 >= self.AI_TASK_WARNING_THRESHOLD:
                ai_request_warning = True

        # Check and consume credits (FR-030)
        credits_needed = self.settings.ai_credit_chat
        balance = await self._get_credit_balance(user.id)

        if balance < credits_needed:
            raise InsufficientCreditsError(
                f"Insufficient credits. Need {credits_needed}, have {balance}."
            )

        # Build task context if requested
        task_context = None
        if request.context.include_tasks:
            task_context = await self._build_task_context(
                user.id,
                request.context.task_limit,
            )

        # Call AI agent
        try:
            result = await self._call_chat_agent(
                message=request.message,
                task_context=task_context,
            )
        except (AIAgentTimeoutError, AIAgentUnavailableError) as e:
            logger.error(f"AI service error for user {user.id}: {e}")
            raise AIServiceUnavailableError(str(e))
        except Exception as e:
            logger.error(f"Unexpected AI error for user {user.id}: {e}")
            raise AIServiceUnavailableError(f"AI service error: {e}")

        # Consume credit after successful response
        await self._consume_credits(user.id, credits_needed, "chat")
        new_balance = await self._get_credit_balance(user.id)

        # T234: Increment per-task counter
        if task_id and session_id:
            self._task_request_counters[session_id][task_id] += 1

        # T233: Convert agent suggestions to API format (FR-034)
        suggested_actions = [
            SuggestedAction(
                type=action.action_type,
                task_id=action.target_id,
                description=action.action_description,
                data=action.parameters,
            )
            for action in result.suggested_actions
        ]

        # T241: Log AI interaction
        logger.info(
            "AI chat completed",
            extra={
                "user_id": str(user.id),
                "task_id": str(task_id) if task_id else None,
                "credits_used": credits_needed,
                "credits_remaining": new_balance,
                "suggested_actions_count": len(suggested_actions),
            },
        )

        return AIServiceChatResponse(
            response=result.response_text,
            suggested_actions=suggested_actions,
            credits_used=credits_needed,
            credits_remaining=new_balance,
            ai_request_warning=ai_request_warning,
        )

    async def _call_chat_agent(
        self,
        message: str,
        task_context: str | None,
    ) -> ChatAgentResult:
        """Call the AI chat agent.

        Separated for easy mocking in tests.

        Args:
            message: User message
            task_context: Optional task context

        Returns:
            ChatAgentResult from AI
        """
        return await self.ai_client.chat(
            message=message,
            task_context=task_context,
        )

    # =========================================================================
    # SUBTASK GENERATION
    # =========================================================================

    async def generate_subtasks(
        self,
        user: User,
        request: SubtaskGenerationRequest,
    ) -> SubtaskGenerationResponse:
        """Generate subtask suggestions for a task.

        T247: AIService.generate_subtasks (FR-031)
        T248: Subtask limit enforcement in generation
        T251: Metrics for subtask generation

        Args:
            user: The requesting user
            request: Request with task_id

        Returns:
            SubtaskGenerationResponse with suggestions

        Raises:
            InsufficientCreditsError: If no credits available
            AIServiceUnavailableError: If AI is down
        """
        tier = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
        start_time = time.perf_counter()

        # Check credits
        credits_needed = self.settings.ai_credit_subtask
        balance = await self._get_credit_balance(user.id)

        if balance < credits_needed:
            # T251: Record insufficient credits failure
            record_subtask_generation_failure("insufficient_credits")
            record_subtask_generation_request(tier, "insufficient_credits")
            raise InsufficientCreditsError(
                f"Insufficient credits. Need {credits_needed}, have {balance}."
            )

        # Get task
        task = await self._get_task(user.id, request.task_id)
        if not task:
            # T251: Record task not found failure
            record_subtask_generation_failure("task_not_found")
            record_subtask_generation_request(tier, "task_not_found")
            raise AIServiceError(f"Task {request.task_id} not found")

        # T248: Get max subtasks based on tier (limit enforcement)
        max_subtasks = (
            self.settings.pro_max_subtasks
            if user.is_pro
            else self.settings.free_max_subtasks
        )

        # Call AI
        try:
            result = await self.ai_client.generate_subtasks(
                task_title=task.title,
                task_description=task.description,
                max_subtasks=max_subtasks,
            )
        except AIAgentTimeoutError as e:
            # T251: Record timeout failure
            record_subtask_generation_failure("timeout")
            record_subtask_generation_request(tier, "timeout")
            logger.error(f"Subtask generation timeout for user {user.id}: {e}")
            raise AIServiceUnavailableError(str(e))
        except AIAgentUnavailableError as e:
            # T251: Record AI unavailable failure
            record_subtask_generation_failure("ai_unavailable")
            record_subtask_generation_request(tier, "ai_unavailable")
            logger.error(f"Subtask generation error for user {user.id}: {e}")
            raise AIServiceUnavailableError(str(e))

        # Consume credit
        await self._consume_credits(user.id, credits_needed, "subtask_generation")
        new_balance = await self._get_credit_balance(user.id)

        # T251: Record success metrics
        duration = time.perf_counter() - start_time
        subtasks_count = len(result.subtasks)

        record_subtask_generation_request(tier, "success")
        record_subtask_generation_latency(tier, duration)
        record_subtasks_generated_count(tier, subtasks_count)
        record_credit_consumption("subtask_generation", credits_needed)

        # Log
        logger.info(
            "Subtask generation completed",
            extra={
                "user_id": str(user.id),
                "task_id": str(request.task_id),
                "subtasks_generated": subtasks_count,
                "credits_used": credits_needed,
                "duration_seconds": round(duration, 3),
                "tier": tier,
            },
        )

        return SubtaskGenerationResponse(
            suggested_subtasks=[
                SubtaskSuggestion(title=s.title)
                for s in result.subtasks
            ],
            credits_used=credits_needed,
            credits_remaining=new_balance,
        )

    # =========================================================================
    # NOTE TO TASK CONVERSION (T257)
    # =========================================================================

    async def convert_note_to_task(
        self,
        user: User,
        note_id: UUID,
    ) -> NoteConvertResponse:
        """Convert a note to a task suggestion using AI.

        T257: AIService.convert_note_to_task (FR-032)
        T261: Metrics for note conversion

        Args:
            user: The requesting user
            note_id: ID of the note to convert

        Returns:
            NoteConvertResponse with task suggestion

        Raises:
            InsufficientCreditsError: If no credits available
            AIServiceError: If note not found or is archived
            AIServiceUnavailableError: If AI is down
        """
        # Check credits
        credits_needed = self.settings.ai_credit_conversion
        balance = await self._get_credit_balance(user.id)

        if balance < credits_needed:
            raise InsufficientCreditsError(
                f"Insufficient credits. Need {credits_needed}, have {balance}."
            )

        # Get note
        note = await self._get_note(user.id, note_id)
        if not note:
            raise AIServiceError(f"Note {note_id} not found")

        # Check if note is archived
        if note.archived:
            raise AIServiceError("Cannot convert archived note")

        # Call AI
        try:
            result = await self.ai_client.convert_note_to_task(
                note_content=note.content,
            )
        except AIAgentTimeoutError as e:
            logger.error(f"Note conversion timeout for user {user.id}: {e}")
            raise AIServiceUnavailableError(str(e))
        except AIAgentUnavailableError as e:
            logger.error(f"Note conversion error for user {user.id}: {e}")
            raise AIServiceUnavailableError(str(e))

        # Consume credit
        await self._consume_credits(user.id, credits_needed, "note_conversion")
        new_balance = await self._get_credit_balance(user.id)

        # T261: Record metrics
        record_note_to_task_conversion()
        record_credit_consumption("note_conversion", credits_needed)

        # Log
        logger.info(
            "Note conversion completed",
            extra={
                "user_id": str(user.id),
                "note_id": str(note_id),
                "confidence": result.confidence,
                "credits_used": credits_needed,
                "suggested_subtasks": len(result.task.subtasks),
            },
        )

        # Convert AI agent result to API response schema
        task_suggestion = NoteTaskSuggestion(
            title=result.task.title,
            description=result.task.description,
            priority=result.task.priority,
            due_date=result.task.due_date,
            estimated_duration=result.task.estimated_duration,
            subtasks=[
                NoteSubtaskSuggestion(title=s.title)
                for s in result.task.subtasks
            ],
        )

        return NoteConvertResponse(
            task_suggestion=task_suggestion,
            note_understanding=result.note_understanding,
            confidence=result.confidence,
            credits_used=credits_needed,
            credits_remaining=new_balance,
        )

    async def _get_note(
        self,
        user_id: UUID,
        note_id: UUID,
    ) -> Note | None:
        """Get a note by ID with ownership check."""
        query = select(Note).where(
            Note.id == note_id,
            Note.user_id == user_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # =========================================================================
    # VOICE TRANSCRIPTION (T268)
    # =========================================================================

    async def transcribe_voice(
        self,
        user: User,
        audio_url: str,
        duration_seconds: int,
        language: str = "en",
    ) -> AIServiceTranscriptionResponse:
        """Transcribe voice audio using Deepgram.

        T268: AIService.transcribe_voice with credit calculation (FR-033)
        T273: Transcription metrics

        Args:
            user: The requesting user (must be Pro tier)
            audio_url: URL of the audio file to transcribe
            duration_seconds: Duration of the audio in seconds
            language: Language code for transcription (default: en)

        Returns:
            AIServiceTranscriptionResponse with transcription and credits info

        Raises:
            TierRequiredError: If user is not Pro tier (403)
            AudioDurationExceededError: If duration exceeds 300 seconds (400)
            InsufficientCreditsError: If not enough credits (402)
            AIServiceUnavailableError: If Deepgram is down (503)
        """
        import math
        from src.schemas.enums import UserTier

        start_time = time.perf_counter()

        # T263: Check Pro tier requirement
        if user.tier != UserTier.PRO:
            raise TierRequiredError(
                "Pro tier required for voice transcription"
            )

        # T265: Check max duration (FR-036)
        max_duration = self.settings.max_audio_duration_seconds
        if duration_seconds > max_duration:
            raise AudioDurationExceededError(
                f"Audio duration exceeds maximum of {max_duration} seconds"
            )

        # T264: Calculate credits needed (5 credits per minute, rounded up)
        credits_per_minute = self.settings.ai_credit_transcription_per_min
        minutes = math.ceil(duration_seconds / 60)
        credits_needed = minutes * credits_per_minute

        # Check credit balance
        balance = await self._get_credit_balance(user.id)
        if balance < credits_needed:
            raise InsufficientCreditsError(
                f"Insufficient credits. Need {credits_needed}, have {balance}. "
                f"({minutes} minute(s) at {credits_per_minute} credits/min)"
            )

        # Call Deepgram
        try:
            result = await self.deepgram_client.transcribe(
                audio_url=audio_url,
                duration_seconds=duration_seconds,
                language=language,
            )
        except DeepgramTimeoutError as e:
            logger.error(f"Deepgram timeout for user {user.id}: {e}")
            # T273: Record timeout metric
            self._record_transcription_failure("timeout")
            raise AIServiceUnavailableError(f"Transcription timed out: {e}")
        except DeepgramConnectionError as e:
            logger.error(f"Deepgram connection error for user {user.id}: {e}")
            self._record_transcription_failure("connection_error")
            raise AIServiceUnavailableError(f"Transcription service unavailable: {e}")
        except DeepgramAPIError as e:
            logger.error(f"Deepgram API error for user {user.id}: {e}")
            self._record_transcription_failure("api_error")
            raise AIServiceUnavailableError(f"Transcription failed: {e}")
        except DeepgramError as e:
            logger.error(f"Deepgram error for user {user.id}: {e}")
            self._record_transcription_failure("unknown")
            raise AIServiceUnavailableError(f"Transcription error: {e}")

        # Consume credits
        await self._consume_credits(user.id, credits_needed, "transcription")
        new_balance = await self._get_credit_balance(user.id)

        # T273: Record success metrics
        duration = time.perf_counter() - start_time
        self._record_transcription_success(
            tier=user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
            duration=duration,
            audio_seconds=duration_seconds,
            credits_used=credits_needed,
        )

        # Log
        logger.info(
            "Voice transcription completed",
            extra={
                "user_id": str(user.id),
                "audio_duration_seconds": duration_seconds,
                "credits_used": credits_needed,
                "credits_remaining": new_balance,
                "confidence": result.confidence,
                "language": result.language,
                "processing_time": round(duration, 3),
            },
        )

        return AIServiceTranscriptionResponse(
            transcription=result.text,
            language=result.language,
            confidence=result.confidence,
            credits_used=credits_needed,
            credits_remaining=new_balance,
        )

    def _record_transcription_failure(self, reason: str) -> None:
        """Record transcription failure metric.

        T273: Add transcription metrics
        """
        # Import here to avoid circular dependency
        from src.middleware.metrics import record_credit_consumption
        # Failure metrics can be extended with a dedicated counter
        logger.warning(f"Transcription failed: {reason}")

    def _record_transcription_success(
        self,
        tier: str,
        duration: float,
        audio_seconds: int,
        credits_used: int,
    ) -> None:
        """Record transcription success metrics.

        T273: Add transcription metrics
        """
        from src.middleware.metrics import (
            record_credit_consumption,
            record_voice_note_duration,
        )
        record_credit_consumption("transcription", credits_used)
        record_voice_note_duration(audio_seconds)

    # =========================================================================
    # CREDIT MANAGEMENT
    # =========================================================================

    async def get_credit_balance(self, user: User) -> dict:
        """Get detailed credit balance for a user.

        Args:
            user: The user

        Returns:
            Dict with balance breakdown and reset time
        """
        from datetime import timedelta

        # Get balances by type
        daily = await self._get_credit_balance_by_type(user.id, CreditType.DAILY)
        subscription = await self._get_credit_balance_by_type(
            user.id, CreditType.SUBSCRIPTION
        )
        purchased = await self._get_credit_balance_by_type(
            user.id, CreditType.PURCHASED
        )
        kickstart = await self._get_credit_balance_by_type(
            user.id, CreditType.KICKSTART
        )

        total = daily + subscription + purchased + kickstart

        # Calculate next daily reset (UTC midnight)
        now = datetime.now(UTC)
        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        return {
            "balance": {
                "daily_free": daily,
                "subscription": subscription,
                "purchased": purchased + kickstart,  # Combine for display
                "total": total,
            },
            "daily_reset_at": next_midnight.isoformat(),
            "tier": user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
        }

    async def _get_credit_balance(self, user_id: UUID) -> int:
        """Get total available credit balance."""
        query = select(
            func.coalesce(
                func.sum(AICreditLedger.amount - AICreditLedger.consumed),
                0,
            )
        ).where(
            AICreditLedger.user_id == user_id,
            AICreditLedger.expired == False,
            (AICreditLedger.expires_at.is_(None)) |
            (AICreditLedger.expires_at > datetime.now(UTC)),
        )

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _get_credit_balance_by_type(
        self,
        user_id: UUID,
        credit_type: CreditType,
    ) -> int:
        """Get available credit balance for a specific type."""
        query = select(
            func.coalesce(
                func.sum(AICreditLedger.amount - AICreditLedger.consumed),
                0,
            )
        ).where(
            AICreditLedger.user_id == user_id,
            AICreditLedger.credit_type == credit_type,
            AICreditLedger.expired == False,
            (AICreditLedger.expires_at.is_(None)) |
            (AICreditLedger.expires_at > datetime.now(UTC)),
        )

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _consume_credits(
        self,
        user_id: UUID,
        amount: int,
        operation_ref: str,
    ) -> None:
        """Consume credits in FIFO order.

        Order: daily -> subscription -> kickstart -> purchased
        """
        remaining = amount

        # Get available credits ordered by FIFO priority
        query = (
            select(AICreditLedger)
            .where(
                AICreditLedger.user_id == user_id,
                AICreditLedger.expired == False,
                AICreditLedger.amount > AICreditLedger.consumed,
                (AICreditLedger.expires_at.is_(None)) |
                (AICreditLedger.expires_at > datetime.now(UTC)),
            )
            .order_by(
                # FIFO priority order
                # 1 = daily, 2 = subscription, 3 = kickstart, 4 = purchased
                AICreditLedger.credit_type.asc(),
                AICreditLedger.created_at.asc(),
            )
        )

        result = await self.session.execute(query)
        credits = result.scalars().all()

        for credit in credits:
            if remaining <= 0:
                break

            available = credit.amount - credit.consumed
            consume_amount = min(available, remaining)

            credit.consumed += consume_amount
            self.session.add(credit)

            remaining -= consume_amount

        await self.session.flush()

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _build_task_context(
        self,
        user_id: UUID,
        limit: int,
    ) -> str:
        """Build task context string for AI.

        Args:
            user_id: User's ID
            limit: Max tasks to include

        Returns:
            Formatted task list string
        """
        query = (
            select(TaskInstance)
            .where(
                TaskInstance.user_id == user_id,
                TaskInstance.completed == False,
                TaskInstance.hidden == False,
            )
            .order_by(TaskInstance.due_date.asc().nullslast())
            .limit(limit)
        )

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        if not tasks:
            return "No active tasks."

        lines = []
        for task in tasks:
            due_str = (
                f" (due: {task.due_date.strftime('%Y-%m-%d')})"
                if task.due_date
                else ""
            )
            priority_str = f"[{task.priority.value.upper()}]" if task.priority else ""
            lines.append(f"- {task.title}{priority_str}{due_str}")

        return "\n".join(lines)

    async def _get_task(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> TaskInstance | None:
        """Get a task by ID with ownership check."""
        query = select(TaskInstance).where(
            TaskInstance.id == task_id,
            TaskInstance.user_id == user_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def clear_session_counters(self, session_id: str) -> None:
        """Clear per-task counters for a session.

        Called when session changes (token refresh/re-login).

        Args:
            session_id: Session ID to clear
        """
        if session_id in self._task_request_counters:
            del self._task_request_counters[session_id]


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_ai_service(session: AsyncSession, settings: Settings) -> AIService:
    """Get an AIService instance."""
    return AIService(session, settings)
