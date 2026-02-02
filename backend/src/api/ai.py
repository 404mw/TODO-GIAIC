"""AI API endpoints.

Phase 10: User Story 6 - AI Chat Widget (Priority: P3)

T235: POST /api/v1/ai/chat with SSE streaming per api-specification.md Section 7.1
T236: POST /api/v1/ai/confirm-action per api-specification.md Section 7.3
T237: GET /api/v1/ai/credits per api-specification.md Section 7.5
T238: Apply 20 req/min rate limit to AI endpoints (FR-061)
"""

import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import Settings
from src.dependencies import get_current_user, get_db_session, get_settings
from src.models.user import User
from src.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ConfirmActionRequest,
    CreditBalanceResponse,
    CreditBalance,
    SubtaskGenerationRequest,
    SubtaskGenerationResponse,
    SuggestedAction,
)
from src.services.ai_service import (
    AIService,
    AIServiceError,
    InsufficientCreditsError,
    AITaskLimitExceededError,
    AIServiceUnavailableError,
    TierRequiredError,
    AudioDurationExceededError,
    get_ai_service,
)
from src.schemas.ai import TranscribeRequest, TranscriptionResponse

logger = logging.getLogger(__name__)


# =============================================================================
# ROUTER & RATE LIMITER
# =============================================================================

router = APIRouter(prefix="/ai", tags=["AI"])


def get_user_id_for_rate_limit(request: Request) -> str:
    """Get user ID from request state for rate limiting."""
    if hasattr(request.state, "user"):
        return str(request.state.user.id)
    return get_remote_address(request)


# T238: 20 req/min rate limit for AI endpoints
limiter = Limiter(key_func=get_user_id_for_rate_limit)


# =============================================================================
# DEPENDENCIES
# =============================================================================


async def get_ai_service_dep(
    session=Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AIService:
    """Dependency to get AI service."""
    return get_ai_service(session, settings)


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/chat",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="AI Chat",
    description="Send message to AI assistant. Costs 1 credit per message.",
)
@limiter.limit("20/minute")
async def ai_chat(
    request: Request,
    body: ChatRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
    settings: Settings = Depends(get_settings),
):
    """T235: POST /api/v1/ai/chat endpoint.

    Per api-specification.md Section 7.1.

    Request Headers:
        - Authorization: Bearer <access_token>
        - Idempotency-Key: <uuid>

    Request Body:
        {
            "message": "What tasks should I focus on today?",
            "context": {
                "include_tasks": true,
                "task_limit": 10
            }
        }

    Response 200:
        {
            "data": {
                "response": "...",
                "suggested_actions": [...],
                "credits_used": 1,
                "credits_remaining": 14
            }
        }

    Errors:
        - 402: INSUFFICIENT_CREDITS
        - 429: RATE_LIMIT_EXCEEDED or AI_TASK_LIMIT_REACHED
        - 503: AI_SERVICE_UNAVAILABLE
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Idempotency-Key header is required",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    # Get optional task_id and session_id from headers
    task_id = None
    task_id_header = request.headers.get("X-Task-Id")
    if task_id_header:
        try:
            task_id = UUID(task_id_header)
        except ValueError:
            pass

    # Use JWT jti as session_id for per-session tracking
    session_id = getattr(request.state, "session_id", None)

    try:
        result = await ai_service.chat(
            user=user,
            request=body,
            task_id=task_id,
            session_id=session_id,
        )

        response_data = {
            "data": {
                "response": result.response,
                "suggested_actions": [
                    {
                        "type": action.type,
                        "task_id": str(action.task_id) if action.task_id else None,
                        "description": action.description,
                        "data": action.data,
                    }
                    for action in result.suggested_actions
                ],
                "credits_used": result.credits_used,
                "credits_remaining": result.credits_remaining,
            }
        }

        # Add warning flag if approaching limit
        if result.ai_request_warning:
            response_data["data"]["ai_request_warning"] = True

        return response_data

    except InsufficientCreditsError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": {
                    "code": "INSUFFICIENT_CREDITS",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AITaskLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "AI_TASK_LIMIT_REACHED",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AIServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "AI_SERVICE_UNAVAILABLE",
                    "message": "AI service is temporarily unavailable",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )


@router.post(
    "/chat/stream",
    status_code=status.HTTP_200_OK,
    summary="AI Chat (Streaming)",
    description="Send message to AI with SSE streaming response.",
)
@limiter.limit("20/minute")
async def ai_chat_stream(
    request: Request,
    body: ChatRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
):
    """Stream AI chat response via Server-Sent Events.

    Per research.md Section 8 - SSE streaming.

    Response format:
        data: {"text": "partial response..."}
        data: {"text": "more text..."}
        data: [DONE]
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Idempotency-Key required"}},
        )

    # Check credits before streaming
    balance = await ai_service.get_credit_balance(user)
    if balance["balance"]["total"] < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"error": {"code": "INSUFFICIENT_CREDITS", "message": "No credits available"}},
        )

    async def generate():
        """Generate SSE events."""
        try:
            async for chunk in ai_service.ai_client.chat_stream(
                message=body.message,
                task_context=None,  # TODO: Add task context support
            ):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': 'AI service error'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/generate-subtasks",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Generate Subtasks (AI)",
    description="""AI generates subtask suggestions for a task using the SubtaskGenerator agent.

**Behavior (FR-031):**
- Costs 1 credit per generation (flat rate)
- Respects tier-based subtask limits:
  - Free tier: Up to 4 subtasks suggested
  - Pro tier: Up to 10 subtasks suggested
- Requires Idempotency-Key header for request deduplication

**Rate Limits:**
- 20 requests per minute per user (FR-061)

**Credit Consumption:**
- 1 credit deducted per successful generation
- No credit deducted on failure

**Errors:**
- 400: VALIDATION_ERROR - Invalid request or missing Idempotency-Key
- 402: INSUFFICIENT_CREDITS - User has 0 credits
- 404: TASK_NOT_FOUND - Task doesn't exist or belongs to another user
- 429: RATE_LIMIT_EXCEEDED - Too many requests
- 503: AI_SERVICE_UNAVAILABLE - AI service is temporarily unavailable
""",
    responses={
        200: {
            "description": "Subtasks generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "suggested_subtasks": [
                                {"title": "Research market trends"},
                                {"title": "Draft project timeline"},
                                {"title": "Assign team resources"},
                            ],
                            "credits_used": 1,
                            "credits_remaining": 9,
                        }
                    }
                }
            },
        },
        402: {"description": "Insufficient credits"},
        503: {"description": "AI service unavailable"},
    },
)
@limiter.limit("20/minute")
async def generate_subtasks(
    request: Request,
    body: SubtaskGenerationRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
):
    """T249: POST /api/v1/ai/generate-subtasks endpoint.

    Phase 11: User Story 7 - Auto Subtask Generation (Priority: P3)
    Implements FR-031.

    Uses the SubtaskGenerator AI agent to break down a task into
    actionable subtasks based on the task's title and description.

    Per api-specification.md Section 7.2.

    Request Headers:
        - Authorization: Bearer <access_token>
        - Idempotency-Key: <uuid>

    Request Body:
        { "task_id": "<uuid>" }

    Response 200:
        {
            "data": {
                "suggested_subtasks": [
                    { "title": "Research market trends" },
                    { "title": "Draft project timeline" }
                ],
                "credits_used": 1,
                "credits_remaining": 9
            }
        }

    Tier Limits:
        - Free tier: Max 4 subtasks suggested
        - Pro tier: Max 10 subtasks suggested
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Idempotency-Key required"}},
        )

    try:
        result = await ai_service.generate_subtasks(user=user, request=body)

        return {
            "data": {
                "suggested_subtasks": [
                    {"title": s.title}
                    for s in result.suggested_subtasks
                ],
                "credits_used": result.credits_used,
                "credits_remaining": result.credits_remaining,
            }
        }

    except InsufficientCreditsError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": {
                    "code": "INSUFFICIENT_CREDITS",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AIServiceError as e:
        # Handle task not found and other service errors
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": str(e),
                        "request_id": getattr(request.state, "request_id", None),
                    }
                },
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "AI_SERVICE_ERROR",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AIServiceUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "AI_SERVICE_UNAVAILABLE",
                    "message": "AI service is temporarily unavailable",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )


@router.post(
    "/transcribe",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Transcribe Voice Audio (Pro Only)",
    description="""Transcribe voice audio using Deepgram NOVA2 model.

**Requirements:**
- Pro tier subscription required (FR-033)
- Maximum audio duration: 300 seconds (FR-036)

**Credit Cost (FR-033):**
- 5 credits per minute of audio (rounded up)
- Example: 45 seconds = 1 minute = 5 credits
- Example: 90 seconds = 2 minutes = 10 credits

**Rate Limits:**
- 20 requests per minute per user (FR-061)

**Errors:**
- 400: VALIDATION_ERROR - Invalid request or audio exceeds 300 seconds
- 402: INSUFFICIENT_CREDITS - Not enough credits for transcription
- 403: PRO_TIER_REQUIRED - Voice transcription requires Pro subscription
- 429: RATE_LIMIT_EXCEEDED - Too many requests
- 503: TRANSCRIPTION_SERVICE_UNAVAILABLE - Deepgram service unavailable
""",
    responses={
        200: {
            "description": "Transcription completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "transcription": "This is the transcribed text from your voice recording.",
                            "language": "en",
                            "confidence": 0.95,
                            "credits_used": 5,
                            "credits_remaining": 45,
                        }
                    }
                }
            },
        },
        402: {"description": "Insufficient credits"},
        403: {"description": "Pro tier required"},
        503: {"description": "Transcription service unavailable"},
    },
)
@limiter.limit("20/minute")
async def transcribe_voice(
    request: Request,
    body: TranscribeRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
):
    """T270: POST /api/v1/ai/transcribe endpoint.

    Phase 13: Voice Transcription (Priority: P3)
    Implements FR-033, FR-036.

    Per api-specification.md Section 7.4.

    Request Headers:
        - Authorization: Bearer <access_token>
        - Idempotency-Key: <uuid>

    Request Body:
        {
            "audio_url": "https://storage.example.com/audio/recording.webm",
            "duration_seconds": 45
        }

    Response 200:
        {
            "data": {
                "transcription": "Transcribed text...",
                "language": "en",
                "confidence": 0.95,
                "credits_used": 5,
                "credits_remaining": 45
            }
        }

    Credit Calculation:
        - 5 credits per minute (rounded up)
        - 45 seconds -> 1 minute -> 5 credits
        - 90 seconds -> 2 minutes -> 10 credits
        - 300 seconds -> 5 minutes -> 25 credits
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Idempotency-Key header is required",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    try:
        result = await ai_service.transcribe_voice(
            user=user,
            audio_url=body.audio_url,
            duration_seconds=body.duration_seconds,
        )

        return {
            "data": {
                "transcription": result.transcription,
                "language": result.language,
                "confidence": result.confidence,
                "credits_used": result.credits_used,
                "credits_remaining": result.credits_remaining,
            }
        }

    except TierRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "PRO_TIER_REQUIRED",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AudioDurationExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "AUDIO_DURATION_EXCEEDED",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except InsufficientCreditsError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": {
                    "code": "INSUFFICIENT_CREDITS",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    except AIServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "TRANSCRIPTION_SERVICE_UNAVAILABLE",
                    "message": "Transcription service is temporarily unavailable",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )


@router.post(
    "/confirm-action",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Confirm AI Action",
    description="Execute an AI-suggested action after user confirmation.",
)
@limiter.limit("20/minute")
async def confirm_action(
    request: Request,
    body: ConfirmActionRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
    session=Depends(get_db_session),
):
    """T236: POST /api/v1/ai/confirm-action endpoint.

    Per api-specification.md Section 7.3.

    Executes AI-suggested actions (FR-034: requires confirmation).

    Supported action_types:
        - complete_task
        - create_subtasks
        - update_task

    Request Body:
        {
            "action_type": "create_subtasks",
            "action_data": {
                "task_id": "<uuid>",
                "subtasks": [
                    { "title": "..." }
                ]
            }
        }
    """
    # Check idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Idempotency-Key required"}},
        )

    action_type = body.action_type
    action_data = body.action_data

    # Import services as needed
    from src.services.task_service import TaskService, get_task_service

    task_service = get_task_service(session, ai_service.settings)

    if action_type == "complete_task":
        task_id = UUID(action_data.get("task_id"))
        from src.schemas.task import TaskUpdate
        result = await task_service.complete_task(user=user, task_id=task_id)
        return {"data": {"task": {"id": str(result.id), "completed": True}}}

    elif action_type == "create_subtasks":
        task_id = UUID(action_data.get("task_id"))
        subtasks_data = action_data.get("subtasks", [])
        from src.schemas.subtask import SubtaskCreate

        created = []
        for s in subtasks_data:
            subtask = await task_service.create_subtask(
                user=user,
                task_id=task_id,
                data=SubtaskCreate(title=s.get("title")),
            )
            created.append({"id": str(subtask.id), "title": subtask.title})

        return {"data": {"subtasks": created}}

    elif action_type == "update_task":
        task_id = UUID(action_data.get("task_id"))
        from src.schemas.task import TaskUpdate
        update_data = {k: v for k, v in action_data.items() if k != "task_id"}
        result = await task_service.update_task(
            user=user,
            task_id=task_id,
            data=TaskUpdate(**update_data),
        )
        return {"data": {"task": {"id": str(result.id)}}}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ACTION", "message": f"Unknown action: {action_type}"}},
        )


@router.get(
    "/credits",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get Credit Balance",
    description="Get AI credit balance breakdown.",
)
async def get_credits(
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service_dep),
):
    """T237: GET /api/v1/ai/credits endpoint.

    Per api-specification.md Section 7.5.

    Response 200:
        {
            "data": {
                "balance": {
                    "daily_free": 8,
                    "subscription": 45,
                    "purchased": 20,
                    "total": 73
                },
                "daily_reset_at": "2026-01-20T00:00:00.000Z",
                "tier": "pro"
            }
        }
    """
    result = await ai_service.get_credit_balance(user)

    return {"data": result}


# =============================================================================
# ROUTER EXPORT
# =============================================================================

# Router is exported and should be included in main router
__all__ = ["router"]
