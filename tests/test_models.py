"""Tests for Task data model."""

import pytest
from datetime import datetime
from todo_core.models import Task, validate_title, validate_description


class TestValidateTitle:
    """Test title validation function."""

    def test_valid_title(self):
        """Test that valid titles are accepted."""
        assert validate_title("Buy groceries") == "Buy groceries"
        assert validate_title("  Trim whitespace  ") == "Trim whitespace"

    def test_empty_title_raises_error(self):
        """Test that empty titles are rejected."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("")
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("   ")

    def test_title_length_limit(self):
        """Test that titles exceeding 200 chars are rejected."""
        valid_title = "A" * 200
        assert validate_title(valid_title) == valid_title

        invalid_title = "A" * 201
        with pytest.raises(ValueError, match="exceeds maximum length of 200"):
            validate_title(invalid_title)


class TestValidateDescription:
    """Test description validation function."""

    def test_none_description(self):
        """Test that None description is handled correctly."""
        assert validate_description(None) is None

    def test_empty_description_normalized_to_none(self):
        """Test that empty descriptions are normalized to None."""
        assert validate_description("") is None
        assert validate_description("   ") is None

    def test_valid_description(self):
        """Test that valid descriptions are accepted."""
        assert validate_description("Buy milk and eggs") == "Buy milk and eggs"
        assert validate_description("  Trim  ") == "Trim"

    def test_description_length_limit(self):
        """Test that descriptions exceeding 1000 chars are rejected."""
        valid_desc = "A" * 1000
        assert validate_description(valid_desc) == valid_desc

        invalid_desc = "A" * 1001
        with pytest.raises(ValueError, match="exceeds maximum length of 1000"):
            validate_description(invalid_desc)


class TestTaskModel:
    """Test Task dataclass."""

    def test_task_creation(self):
        """Test basic task creation with required fields."""
        task = Task(id=1, title="Buy groceries")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == "incomplete"
        assert task.created_at is not None
        assert task.completed_at is None

    def test_task_creation_with_description(self):
        """Test task creation with optional description."""
        task = Task(id=2, title="Finish project", description="Complete all features")
        assert task.description == "Complete all features"

    def test_mark_complete(self):
        """Test marking task as complete."""
        task = Task(id=1, title="Test task")
        assert task.status == "incomplete"
        assert task.completed_at is None

        task.mark_complete()
        assert task.status == "complete"
        assert task.completed_at is not None

    def test_mark_complete_idempotent(self):
        """Test that marking complete twice doesn't change completed_at."""
        task = Task(id=1, title="Test task")
        task.mark_complete()
        first_completed_at = task.completed_at

        task.mark_complete()
        assert task.completed_at == first_completed_at

    def test_update_title(self):
        """Test updating task title."""
        task = Task(id=1, title="Original title")
        task.update_title("New title")
        assert task.title == "New title"

    def test_update_title_with_whitespace(self):
        """Test that update_title trims whitespace."""
        task = Task(id=1, title="Original")
        task.update_title("  Updated  ")
        assert task.title == "Updated"

    def test_update_title_empty_raises_error(self):
        """Test that empty title raises error."""
        task = Task(id=1, title="Original")
        with pytest.raises(ValueError, match="Title cannot be empty"):
            task.update_title("")
        with pytest.raises(ValueError, match="Title cannot be empty"):
            task.update_title("   ")

    def test_update_title_too_long_raises_error(self):
        """Test that title exceeding 200 chars raises error."""
        task = Task(id=1, title="Original")
        with pytest.raises(ValueError, match="cannot exceed 200 characters"):
            task.update_title("A" * 201)

    def test_update_description(self):
        """Test updating task description."""
        task = Task(id=1, title="Task", description="Original")
        task.update_description("Updated description")
        assert task.description == "Updated description"

    def test_update_description_to_none(self):
        """Test that empty description is normalized to None."""
        task = Task(id=1, title="Task", description="Original")
        task.update_description("")
        assert task.description is None

        task.update_description("   ")
        assert task.description is None

    def test_update_description_too_long_raises_error(self):
        """Test that description exceeding 1000 chars raises error."""
        task = Task(id=1, title="Task")
        with pytest.raises(ValueError, match="cannot exceed 1000 characters"):
            task.update_description("A" * 1001)
