"""AI Agent schemas for OpenAI Agents SDK output_type.

T056: SubtaskSuggestion and SubtaskGenerationResult schemas
T057: ActionSuggestion schema for chat agent
T058: TaskSuggestion schema for note conversion agent

Per research.md Section 5 - these are used as output_type
for structured agent responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.enums import TaskPriority


class SubtaskSuggestionAgent(BaseModel):
    """Individual subtask suggestion from AI agent.

    Used in SubtaskGenerator agent output.
    """

    title: str = Field(
        max_length=200,
        description="Suggested subtask title (1-200 chars)",
    )
    rationale: str | None = Field(
        default=None,
        max_length=500,
        description="Brief explanation of why this subtask is helpful",
    )


class SubtaskGenerationResult(BaseModel):
    """Structured output from SubtaskGenerator agent.

    Per research.md Section 5 - used as output_type for
    openai-agents Runner.run() call.
    """

    subtasks: list[SubtaskSuggestionAgent] = Field(
        max_length=10,
        description="List of suggested subtasks (max 10)",
    )
    task_understanding: str = Field(
        max_length=500,
        description="Brief summary of how AI understood the task",
    )


class ActionSuggestion(BaseModel):
    """Suggested action from chat agent for user confirmation.

    Per FR-034 - all AI actions require user confirmation.
    This schema defines the structure of suggested actions.
    """

    action_type: str = Field(
        description="Type of action (complete_task, create_subtask, etc.)",
    )
    target_id: UUID | None = Field(
        default=None,
        description="ID of the target entity (task, subtask, etc.)",
    )
    action_description: str = Field(
        max_length=200,
        description="Human-readable description of the action",
    )
    parameters: dict | None = Field(
        default=None,
        description="Action-specific parameters",
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="AI confidence in this suggestion (0-1)",
    )


class ChatAgentResult(BaseModel):
    """Structured output from PerpetualFlowAssistant chat agent.

    Per research.md Section 5 - used as output_type for
    chat agent responses.
    """

    response_text: str = Field(
        max_length=2000,
        description="Natural language response to user",
    )
    suggested_actions: list[ActionSuggestion] = Field(
        default_factory=list,
        max_length=5,
        description="Actions suggested by AI (max 5)",
    )
    reasoning: str | None = Field(
        default=None,
        max_length=500,
        description="Brief explanation of AI reasoning (not shown to user)",
    )


class TaskSuggestion(BaseModel):
    """Task suggestion from note conversion agent.

    Per research.md Section 5 - used as output_type for
    NoteConverter agent.
    """

    title: str = Field(
        max_length=200,
        description="Suggested task title (1-200 chars)",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Suggested task description",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Suggested task priority",
    )
    due_date: datetime | None = Field(
        default=None,
        description="Suggested due date (if extractable from note)",
    )
    estimated_duration: int | None = Field(
        default=None,
        ge=1,
        le=720,
        description="Suggested duration in minutes (if extractable)",
    )
    subtasks: list[SubtaskSuggestionAgent] = Field(
        default_factory=list,
        max_length=4,
        description="Suggested subtasks (max 4 for free tier default)",
    )


class NoteConversionResult(BaseModel):
    """Structured output from NoteConverter agent.

    Per research.md Section 5 - used as output_type for
    note-to-task conversion.
    """

    task: TaskSuggestion = Field(
        description="Suggested task details",
    )
    note_understanding: str = Field(
        max_length=500,
        description="Brief summary of how AI understood the note",
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="AI confidence in this conversion (0-1)",
    )


class TranscriptionResult(BaseModel):
    """Result from Deepgram voice transcription.

    Phase 13: Voice Transcription (T267)
    Per research.md Section 6 - Deepgram NOVA2 transcription result.
    """

    text: str = Field(
        description="Transcribed text from audio",
    )
    language: str = Field(
        default="en",
        description="Detected language code (ISO 639-1)",
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Transcription confidence score (0-1)",
    )
    words: list[dict] | None = Field(
        default=None,
        description="Word-level timing (optional)",
    )
    duration_seconds: float | None = Field(
        default=None,
        description="Audio duration in seconds",
    )
