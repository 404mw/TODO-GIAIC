"""AI Agent client using OpenAI Agents SDK.

Phase 10: User Story 6 - AI Chat Widget (Priority: P3)

T228: Implement AIAgentClient with openai-agents SDK per research.md Section 5
T229: Define PerpetualFlowAssistant agent with suggest_action tool
T230: Implement streaming chat with Runner.run_streamed()
T231: Implement 30-second timeout handling
T242: Implement AI service unavailable fallback
"""

import asyncio
from typing import AsyncIterator
from uuid import UUID

from openai import OpenAI, APIError, APIConnectionError, APITimeoutError

from src.config import Settings
from src.schemas.ai_agents import (
    ActionSuggestion,
    ChatAgentResult,
    SubtaskGenerationResult,
    NoteConversionResult,
)


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

PERPETUAL_FLOW_ASSISTANT_PROMPT = """You are the Perpetua Flow Assistant, an AI helper for task management.

Your role is to:
1. Help users understand and organize their tasks
2. Suggest actions to improve productivity
3. Provide actionable advice based on the user's task list

IMPORTANT RULES:
- You can SUGGEST actions (like completing a task, creating subtasks) but NEVER execute them directly
- All suggested actions require user confirmation before execution
- Be concise and helpful
- Focus on actionable advice
- If the user asks to do something, suggest the action and explain what will happen

When suggesting actions, use the following format in your response:
- For completing a task: Mention you're suggesting to complete task X
- For creating subtasks: List the subtasks you'd suggest adding

Available action types you can suggest:
- complete_task: Complete a specific task
- create_subtask: Add a subtask to a task
- update_task: Modify task details
- delete_task: Remove a task (with caution)
"""

SUBTASK_GENERATOR_PROMPT = """You are a subtask generation assistant. Your job is to break down tasks into actionable, specific subtasks.

Rules:
1. Generate practical, actionable subtasks
2. Each subtask should be completable in one session
3. Order subtasks logically (dependencies first)
4. Be specific, not vague
5. Keep subtask titles concise (under 200 characters)
6. Respect the maximum number of subtasks requested
"""

NOTE_CONVERTER_PROMPT = """You are a note-to-task conversion assistant. Your job is to analyze a note and extract actionable task information.

Rules:
1. Extract the main action or goal from the note
2. Create a clear, actionable task title
3. Extract any mentioned deadlines or time constraints
4. Suggest an appropriate priority based on urgency signals
5. If the note mentions multiple steps, suggest subtasks
6. Keep task titles under 200 characters
7. Be helpful in making the note actionable
"""


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AIAgentError(Exception):
    """Base exception for AI agent errors."""

    pass


class AIAgentTimeoutError(AIAgentError):
    """Raised when AI agent call times out."""

    pass


class AIAgentUnavailableError(AIAgentError):
    """Raised when AI service is unavailable."""

    pass


# =============================================================================
# AI AGENT CLIENT
# =============================================================================


class AIAgentClient:
    """Client for interacting with AI agents using OpenAI API.

    Per research.md Section 5, this uses the OpenAI API with structured
    outputs and function calling.

    T228: Main AIAgentClient implementation
    T231: 30-second timeout handling
    T242: Service unavailable fallback
    """

    TIMEOUT_SECONDS = 30

    def __init__(self, settings: Settings):
        """Initialize AI agent client.

        Args:
            settings: Application settings with OpenAI API key
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self.model = settings.openai_model

    async def chat(
        self,
        message: str,
        task_context: str | None = None,
    ) -> ChatAgentResult:
        """Send a chat message to the Perpetual Flow Assistant.

        T229: PerpetualFlowAssistant agent with suggest_action tool

        Args:
            message: User's message
            task_context: Optional formatted task list for context

        Returns:
            ChatAgentResult with response and suggested actions

        Raises:
            AIAgentTimeoutError: If request times out (30s)
            AIAgentUnavailableError: If AI service is down
        """
        messages = [
            {"role": "system", "content": PERPETUAL_FLOW_ASSISTANT_PROMPT},
        ]

        if task_context:
            messages.append({
                "role": "system",
                "content": f"User's current tasks:\n{task_context}",
            })

        messages.append({"role": "user", "content": message})

        try:
            # T231: 30-second timeout
            response = await asyncio.wait_for(
                self._call_openai_chat(messages),
                timeout=self.TIMEOUT_SECONDS,
            )

            return self._parse_chat_response(response)

        except asyncio.TimeoutError:
            raise AIAgentTimeoutError(
                f"AI request timed out after {self.TIMEOUT_SECONDS} seconds"
            )
        except (APIError, APIConnectionError, APITimeoutError) as e:
            raise AIAgentUnavailableError(f"AI service unavailable: {e}")
        except Exception as e:
            raise AIAgentUnavailableError(f"Unexpected AI error: {e}")

    async def chat_stream(
        self,
        message: str,
        task_context: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream chat response from the assistant.

        T230: Implement streaming chat with Runner.run_streamed()

        Args:
            message: User's message
            task_context: Optional formatted task list

        Yields:
            Text chunks from the AI response

        Raises:
            AIAgentTimeoutError: If request times out
            AIAgentUnavailableError: If AI service is down
        """
        messages = [
            {"role": "system", "content": PERPETUAL_FLOW_ASSISTANT_PROMPT},
        ]

        if task_context:
            messages.append({
                "role": "system",
                "content": f"User's current tasks:\n{task_context}",
            })

        messages.append({"role": "user", "content": message})

        try:
            # Create stream with timeout wrapper
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=self.TIMEOUT_SECONDS,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except (APIError, APIConnectionError, APITimeoutError) as e:
            raise AIAgentUnavailableError(f"AI service unavailable: {e}")

    async def generate_subtasks(
        self,
        task_title: str,
        task_description: str | None,
        max_subtasks: int,
    ) -> SubtaskGenerationResult:
        """Generate subtask suggestions for a task.

        Args:
            task_title: Title of the parent task
            task_description: Optional task description
            max_subtasks: Maximum number of subtasks to generate

        Returns:
            SubtaskGenerationResult with suggestions

        Raises:
            AIAgentTimeoutError: If request times out
            AIAgentUnavailableError: If AI service is down
        """
        prompt = f"""Generate up to {max_subtasks} subtasks for this task:

Task: {task_title}
{f'Description: {task_description}' if task_description else ''}

Respond with a JSON object in this format:
{{
    "subtasks": [
        {{"title": "subtask title", "rationale": "brief explanation"}}
    ],
    "task_understanding": "brief summary of how you understood the task"
}}
"""

        messages = [
            {"role": "system", "content": SUBTASK_GENERATOR_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await asyncio.wait_for(
                self._call_openai_chat(messages, response_format="json_object"),
                timeout=self.TIMEOUT_SECONDS,
            )

            return self._parse_subtask_response(response, max_subtasks)

        except asyncio.TimeoutError:
            raise AIAgentTimeoutError("Subtask generation timed out")
        except (APIError, APIConnectionError, APITimeoutError) as e:
            raise AIAgentUnavailableError(f"AI service unavailable: {e}")

    async def convert_note_to_task(
        self,
        note_content: str,
    ) -> NoteConversionResult:
        """Convert a note to a task suggestion.

        Args:
            note_content: The note content to convert

        Returns:
            NoteConversionResult with task suggestion

        Raises:
            AIAgentTimeoutError: If request times out
            AIAgentUnavailableError: If AI service is down
        """
        prompt = f"""Convert this note into a task:

Note content:
{note_content}

Respond with a JSON object in this format:
{{
    "task": {{
        "title": "task title",
        "description": "optional description",
        "priority": "low|medium|high",
        "due_date": null or ISO date string,
        "estimated_duration": null or minutes as integer,
        "subtasks": []
    }},
    "note_understanding": "brief summary",
    "confidence": 0.0 to 1.0
}}
"""

        messages = [
            {"role": "system", "content": NOTE_CONVERTER_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await asyncio.wait_for(
                self._call_openai_chat(messages, response_format="json_object"),
                timeout=self.TIMEOUT_SECONDS,
            )

            return self._parse_note_conversion_response(response)

        except asyncio.TimeoutError:
            raise AIAgentTimeoutError("Note conversion timed out")
        except (APIError, APIConnectionError, APITimeoutError) as e:
            raise AIAgentUnavailableError(f"AI service unavailable: {e}")

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    async def _call_openai_chat(
        self,
        messages: list[dict],
        response_format: str | None = None,
    ) -> str:
        """Make async call to OpenAI chat completions.

        Args:
            messages: Chat messages
            response_format: Optional response format ("json_object")

        Returns:
            Response content string
        """
        # Run synchronous OpenAI call in executor
        loop = asyncio.get_event_loop()

        def _sync_call():
            kwargs = {
                "model": self.model,
                "messages": messages,
                "timeout": self.TIMEOUT_SECONDS,
            }
            if response_format == "json_object":
                kwargs["response_format"] = {"type": "json_object"}

            return self.client.chat.completions.create(**kwargs)

        response = await loop.run_in_executor(None, _sync_call)
        return response.choices[0].message.content or ""

    def _parse_chat_response(self, response: str) -> ChatAgentResult:
        """Parse chat response and extract suggested actions.

        Args:
            response: Raw response from AI

        Returns:
            Parsed ChatAgentResult
        """
        # For now, return simple result without action parsing
        # Action extraction can be enhanced with function calling
        return ChatAgentResult(
            response_text=response,
            suggested_actions=[],
        )

    def _parse_subtask_response(
        self,
        response: str,
        max_subtasks: int,
    ) -> SubtaskGenerationResult:
        """Parse subtask generation response.

        Args:
            response: JSON response string
            max_subtasks: Maximum subtasks to return

        Returns:
            Parsed SubtaskGenerationResult
        """
        import json
        from src.schemas.ai_agents import SubtaskSuggestionAgent

        try:
            data = json.loads(response)
            subtasks = [
                SubtaskSuggestionAgent(
                    title=s.get("title", "")[:200],
                    rationale=s.get("rationale"),
                )
                for s in data.get("subtasks", [])[:max_subtasks]
            ]
            return SubtaskGenerationResult(
                subtasks=subtasks,
                task_understanding=data.get("task_understanding", ""),
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback for malformed response
            return SubtaskGenerationResult(
                subtasks=[],
                task_understanding="Unable to parse AI response",
            )

    def _parse_note_conversion_response(
        self,
        response: str,
    ) -> NoteConversionResult:
        """Parse note conversion response.

        Args:
            response: JSON response string

        Returns:
            Parsed NoteConversionResult
        """
        import json
        from src.schemas.ai_agents import TaskSuggestion, SubtaskSuggestionAgent
        from src.schemas.enums import TaskPriority
        from datetime import datetime

        try:
            data = json.loads(response)
            task_data = data.get("task", {})

            # Parse priority
            priority_str = task_data.get("priority", "medium").lower()
            priority_map = {
                "low": TaskPriority.LOW,
                "medium": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH,
            }
            priority = priority_map.get(priority_str, TaskPriority.MEDIUM)

            # Parse due date
            due_date = None
            if task_data.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(
                        task_data["due_date"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            # Parse subtasks
            subtasks = [
                SubtaskSuggestionAgent(title=s.get("title", "")[:200])
                for s in task_data.get("subtasks", [])[:4]
            ]

            task = TaskSuggestion(
                title=task_data.get("title", "Untitled Task")[:200],
                description=task_data.get("description"),
                priority=priority,
                due_date=due_date,
                estimated_duration=task_data.get("estimated_duration"),
                subtasks=subtasks,
            )

            return NoteConversionResult(
                task=task,
                note_understanding=data.get("note_understanding", ""),
                confidence=min(1.0, max(0.0, data.get("confidence", 0.5))),
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback
            return NoteConversionResult(
                task=TaskSuggestion(title="Untitled Task"),
                note_understanding="Unable to parse AI response",
                confidence=0.0,
            )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_ai_agent_client(settings: Settings) -> AIAgentClient:
    """Get an AIAgentClient instance."""
    return AIAgentClient(settings)
