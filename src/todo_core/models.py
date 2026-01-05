"""Task data model for TODO application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def validate_title(title: str) -> str:
    """Validate and normalize task title.

    Args:
        title: Raw title input

    Returns:
        Trimmed, validated title

    Raises:
        ValueError: If validation fails
    """
    trimmed = title.strip()
    if not trimmed:
        raise ValueError("Title cannot be empty or whitespace-only")
    if len(trimmed) > 200:
        raise ValueError(
            f"Title exceeds maximum length of 200 characters (got {len(trimmed)})"
        )
    return trimmed


def validate_description(description: Optional[str]) -> Optional[str]:
    """Validate and normalize task description.

    Args:
        description: Raw description input or None

    Returns:
        Trimmed description or None if empty

    Raises:
        ValueError: If description exceeds 1000 characters
    """
    if description is None:
        return None

    trimmed = description.strip()
    if not trimmed:
        return None

    if len(trimmed) > 1000:
        raise ValueError(
            f"Description exceeds maximum length of 1000 characters (got {len(trimmed)})"
        )

    return trimmed


@dataclass(slots=True)
class Task:
    """Task model for TODO application.

    Attributes:
        id: Unique sequential identifier (auto-generated)
        title: Task title (1-200 chars after trim)
        description: Optional description (max 1000 chars)
        status: "incomplete" or "complete"
        created_at: Creation timestamp (ISO 8601: YYYY-MM-DD HH:MM:SS)
        completed_at: Completion timestamp (ISO 8601, None if incomplete)
    """

    id: int
    title: str
    description: Optional[str] = None
    status: str = "incomplete"
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    completed_at: Optional[str] = None

    def mark_complete(self) -> None:
        """Mark task as complete with current timestamp.

        Sets status to 'complete' and records completion timestamp.
        Idempotent - safe to call multiple times.
        """
        if self.status != "complete":
            self.status = "complete"
            self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_title(self, new_title: str) -> None:
        """Update task title.

        Args:
            new_title: New title (will be trimmed)

        Raises:
            ValueError: If title is empty after trimming or exceeds 200 chars
        """
        title = new_title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        self.title = title

    def update_description(self, new_description: Optional[str]) -> None:
        """Update task description.

        Args:
            new_description: New description (will be trimmed) or None

        Raises:
            ValueError: If description exceeds 1000 chars
        """
        if new_description is None:
            self.description = None
        else:
            desc = new_description.strip()
            if len(desc) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
            self.description = desc if desc else None
