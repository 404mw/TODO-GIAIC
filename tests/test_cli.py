"""Tests for CLI console interface."""

import pytest
from io import StringIO
from unittest.mock import patch
from todo_core.cli import (
    display_menu,
    get_menu_choice,
    get_task_title,
    get_task_description,
    create_task,
    list_tasks,
)
from todo_core.storage import TaskStore


class TestDisplayMenu:
    """Test menu display function."""

    def test_display_menu(self, capsys):
        """Test that menu is displayed correctly."""
        display_menu()
        captured = capsys.readouterr()
        output = captured.out

        assert "TODO APP MENU" in output
        assert "1. Create task" in output
        assert "2. List tasks" in output
        assert "3. Complete task" in output
        assert "4. Update task" in output
        assert "5. Delete task" in output
        assert "6. Exit" in output


class TestGetMenuChoice:
    """Test menu choice input function."""

    @patch("builtins.input", return_value="1")
    def test_valid_choice(self, mock_input):
        """Test that valid menu choice is accepted."""
        assert get_menu_choice() == "1"

    @patch("builtins.input", side_effect=["7", "0", "3"])
    def test_invalid_choice_retry(self, mock_input, capsys):
        """Test that invalid choices cause retry."""
        result = get_menu_choice()
        assert result == "3"

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "Invalid" in captured.out


class TestGetTaskTitle:
    """Test task title input function."""

    @patch("builtins.input", return_value="Buy groceries")
    def test_valid_title(self, mock_input):
        """Test that valid title is accepted."""
        assert get_task_title() == "Buy groceries"

    @patch("builtins.input", side_effect=["", "   ", "Valid title"])
    def test_empty_title_retry(self, mock_input, capsys):
        """Test that empty title causes retry."""
        result = get_task_title()
        assert result == "Valid title"

        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    @patch("builtins.input", return_value="  Trim whitespace  ")
    def test_title_trimmed(self, mock_input):
        """Test that title is trimmed."""
        assert get_task_title() == "Trim whitespace"

    @patch("builtins.input", side_effect=["A" * 201, "Valid title"])
    def test_title_too_long_retry(self, mock_input, capsys):
        """Test that title exceeding 200 chars causes retry."""
        result = get_task_title()
        assert result == "Valid title"

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "200" in captured.out


class TestGetTaskDescription:
    """Test task description input function."""

    @patch("builtins.input", return_value="Buy milk and eggs")
    def test_valid_description(self, mock_input):
        """Test that valid description is accepted."""
        assert get_task_description() == "Buy milk and eggs"

    @patch("builtins.input", return_value="")
    def test_empty_description_returns_none(self, mock_input):
        """Test that empty description returns None."""
        assert get_task_description() is None

    @patch("builtins.input", return_value="   ")
    def test_whitespace_description_returns_none(self, mock_input):
        """Test that whitespace-only description returns None."""
        assert get_task_description() is None

    @patch("builtins.input", side_effect=["A" * 1001, "Valid description"])
    def test_description_too_long_retry(self, mock_input, capsys):
        """Test that description exceeding 1000 chars causes retry."""
        result = get_task_description()
        assert result == "Valid description"

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "1000" in captured.out


class TestCreateTaskFlow:
    """Test create task workflow."""

    def setup_method(self):
        """Reset TaskStore before each test."""
        TaskStore.reset_id_counter()

    @patch("builtins.input", side_effect=["Buy groceries", "Milk, bread, eggs"])
    def test_create_task_with_description(self, mock_input, capsys):
        """Test creating a task with description."""
        store = TaskStore()
        create_task(store)

        assert len(store.tasks) == 1
        task = store.tasks[0]
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, bread, eggs"

        captured = capsys.readouterr()
        assert "created" in captured.out.lower() or "ID: 1" in captured.out

    @patch("builtins.input", side_effect=["Finish project", ""])
    def test_create_task_without_description(self, mock_input, capsys):
        """Test creating a task without description."""
        store = TaskStore()
        create_task(store)

        assert len(store.tasks) == 1
        task = store.tasks[0]
        assert task.title == "Finish project"
        assert task.description is None


class TestListTasksFlow:
    """Test list tasks workflow."""

    def setup_method(self):
        """Reset TaskStore before each test."""
        TaskStore.reset_id_counter()

    def test_list_tasks_empty(self, capsys):
        """Test listing tasks when store is empty."""
        store = TaskStore()
        list_tasks(store)

        captured = capsys.readouterr()
        assert "No tasks" in captured.out or "empty" in captured.out.lower()

    def test_list_tasks_with_tasks(self, capsys):
        """Test listing tasks with multiple tasks."""
        store = TaskStore()
        task1 = store.create_task("Buy groceries", "Milk, bread")
        task2 = store.create_task("Finish project")
        task3 = store.create_task("Call dentist")

        list_tasks(store)

        captured = capsys.readouterr()
        output = captured.out

        # Check that all task IDs and titles appear
        assert "1" in output
        assert "2" in output
        assert "3" in output
        assert "Buy groceries" in output
        assert "Finish project" in output
        assert "Call dentist" in output

        # Check for status indicators
        assert "PENDING" in output or "incomplete" in output

    def test_list_tasks_shows_completed_status(self, capsys):
        """Test that completed tasks show proper status."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")

        task1.mark_complete()

        list_tasks(store)

        captured = capsys.readouterr()
        output = captured.out

        # Should show both complete and incomplete statuses
        assert ("complete" in output.lower() or "done" in output.lower() or "✓" in output)
