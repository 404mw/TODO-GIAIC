"""In-memory task storage with sequential ID generation."""

from typing import List, Optional
from todo_core.models import Task, validate_title, validate_description


class TaskStore:
    """In-memory task storage with sequential ID generation.

    Attributes:
        tasks: List of all tasks in creation order
        _next_id: Class-level counter for sequential IDs
    """

    _next_id: int = 1  # Sequential ID counter

    def __init__(self):
        """Initialize empty task store."""
        self.tasks: List[Task] = []

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """Create and store a new task.

        Validates input, generates sequential ID, and adds task to storage.

        Args:
            title: Task title (will be validated and trimmed)
            description: Optional description (will be validated and trimmed)

        Returns:
            Created task with auto-generated ID and timestamps

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        validated_title = validate_title(title)
        validated_desc = validate_description(description)

        # Create task with sequential ID
        task = Task(id=TaskStore._next_id, title=validated_title, description=validated_desc)

        # Increment ID counter and store task
        TaskStore._next_id += 1
        self.tasks.append(task)

        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task if found, None otherwise
        """
        return next((t for t in self.tasks if t.id == task_id), None)

    def list_all_tasks(self) -> List[Task]:
        """List all tasks in creation order.

        Returns:
            Shallow copy of all tasks (prevents external modification)
        """
        return self.tasks.copy()

    def list_by_status(self, status: str) -> List[Task]:
        """List tasks filtered by status.

        Args:
            status: "incomplete" or "complete"

        Returns:
            List of tasks matching the status
        """
        return [t for t in self.tasks if t.status == status]

    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID.

        Args:
            task_id: Task identifier

        Returns:
            True if task was deleted, False if not found
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    @classmethod
    def reset_id_counter(cls) -> None:
        """Reset ID counter to 1 (for testing only)."""
        cls._next_id = 1
