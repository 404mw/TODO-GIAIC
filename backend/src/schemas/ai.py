"""AI schemas for chat, subtask generation, and transcription.

T051: AI schemas per api-specification.md Section 8
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.enums import UserTier


class ChatContext(BaseModel):
    """Context options for AI chat."""

    include_tasks: bool = Field(
        default=False,
        description="Include user's tasks in context",
    )
    task_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Max tasks to include",
    )


class ChatRequest(BaseModel):
    """Request body for AI chat.

    Per api-specification.md Section 8.1.
    """

    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User message to AI assistant",
    )
    context: ChatContext = Field(
        default_factory=ChatContext,
        description="Optional context settings",
    )


class SuggestedAction(BaseModel):
    """AI-suggested action for user confirmation.

    Per api-specification.md Section 8.1 and FR-034.
    """

    type: str = Field(
        description="Action type (e.g., 'complete_task', 'create_subtask')",
    )
    task_id: UUID | None = Field(
        default=None,
        description="Related task ID",
    )
    description: str = Field(
        description="Human-readable action description",
    )
    data: dict | None = Field(
        default=None,
        description="Action-specific data",
    )


class ChatResponse(BaseModel):
    """Response from AI chat.

    Per api-specification.md Section 8.1.
    """

    response: str = Field(description="AI assistant response")
    suggested_actions: list[SuggestedAction] = Field(
        default_factory=list,
        description="Suggested actions requiring user confirmation",
    )
    credits_used: int = Field(description="Credits consumed")
    credits_remaining: int = Field(description="Remaining credits")


class SubtaskGenerationRequest(BaseModel):
    """Request body for subtask generation.

    Per api-specification.md Section 8.2.
    """

    task_id: UUID = Field(description="Task to generate subtasks for")


class SubtaskSuggestion(BaseModel):
    """AI-suggested subtask."""

    title: str = Field(
        max_length=200,
        description="Suggested subtask title",
    )


class SubtaskGenerationResponse(BaseModel):
    """Response from subtask generation.

    Per api-specification.md Section 8.2.
    """

    suggested_subtasks: list[SubtaskSuggestion] = Field(
        description="AI-suggested subtasks",
    )
    credits_used: int = Field(description="Credits consumed")
    credits_remaining: int = Field(description="Remaining credits")


class ConfirmActionRequest(BaseModel):
    """Request body for confirming AI action.

    Per api-specification.md Section 8.3.
    """

    action_type: str = Field(
        description="Type of action to execute",
    )
    action_data: dict = Field(
        description="Action-specific data",
    )


class TranscribeRequest(BaseModel):
    """Request body for voice transcription.

    Per api-specification.md Section 8.4.
    """

    audio_url: str = Field(
        description="URL of audio file to transcribe",
    )
    duration_seconds: int = Field(
        ge=1,
        le=300,
        description="Audio duration in seconds (max 300)",
    )


class TranscriptionResponse(BaseModel):
    """Response from voice transcription.

    Per api-specification.md Section 8.4.
    """

    transcription: str = Field(description="Transcribed text")
    language: str = Field(description="Detected language code")
    confidence: float = Field(
        ge=0,
        le=1,
        description="Transcription confidence (0-1)",
    )
    credits_used: int = Field(description="Credits consumed")
    credits_remaining: int = Field(description="Remaining credits")


class CreditBalance(BaseModel):
    """Credit balance breakdown."""

    daily_free: int = Field(description="Daily free credits remaining")
    subscription: int = Field(description="Subscription credits remaining")
    purchased: int = Field(description="Purchased credits remaining")
    total: int = Field(description="Total credits available")


class CreditBalanceResponse(BaseModel):
    """Response for credit balance query.

    Per api-specification.md Section 8.5.
    """

    balance: CreditBalance = Field(description="Credit breakdown")
    daily_reset_at: datetime = Field(description="Next daily credit reset (UTC)")
    tier: UserTier = Field(description="User's subscription tier")
