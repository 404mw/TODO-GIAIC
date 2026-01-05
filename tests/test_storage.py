"""Tests for TaskStore in-memory storage."""

import pytest
from todo_core.storage import TaskStore
from todo_core.models import Task


class TestTaskStore:
    """Test TaskStore class."""

    def setup_method(self):
        """Reset ID counter before each test."""
        TaskStore.reset_id_counter()

    def test_create_task(self):
        """Test creating a task with sequential ID."""
        store = TaskStore()
        task = store.create_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == "incomplete"

    def test_create_task_with_description(self):
        """Test creating a task with description."""
        store = TaskStore()
        task = store.create_task("Buy groceries", "Milk, bread, eggs")

        assert task.description == "Milk, bread, eggs"

    def test_sequential_id_generation(self):
        """Test that IDs are sequential starting from 1."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")
        task3 = store.create_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_get_task(self):
        """Test getting a task by ID."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")

        retrieved = store.get_task(1)
        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Task 1"

        retrieved2 = store.get_task(2)
        assert retrieved2.id == 2

    def test_get_task_not_found(self):
        """Test getting a non-existent task returns None."""
        store = TaskStore()
        store.create_task("Task 1")

        assert store.get_task(999) is None

    def test_list_all_tasks(self):
        """Test listing all tasks."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")
        task3 = store.create_task("Task 3")

        all_tasks = store.list_all_tasks()
        assert len(all_tasks) == 3
        assert all_tasks[0].id == 1
        assert all_tasks[1].id == 2
        assert all_tasks[2].id == 3

    def test_list_all_tasks_empty(self):
        """Test listing tasks when store is empty."""
        store = TaskStore()
        assert store.list_all_tasks() == []

    def test_list_by_status_incomplete(self):
        """Test filtering tasks by incomplete status."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")
        task3 = store.create_task("Task 3")

        # Mark one task as complete
        task2.mark_complete()

        incomplete_tasks = store.list_by_status("incomplete")
        assert len(incomplete_tasks) == 2
        assert incomplete_tasks[0].id == 1
        assert incomplete_tasks[1].id == 3

    def test_list_by_status_complete(self):
        """Test filtering tasks by complete status."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")
        task3 = store.create_task("Task 3")

        task1.mark_complete()
        task3.mark_complete()

        complete_tasks = store.list_by_status("complete")
        assert len(complete_tasks) == 2
        assert complete_tasks[0].id == 1
        assert complete_tasks[1].id == 3

    def test_delete_task(self):
        """Test deleting a task by ID."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")
        task3 = store.create_task("Task 3")

        result = store.delete_task(2)
        assert result is True

        all_tasks = store.list_all_tasks()
        assert len(all_tasks) == 2
        assert all_tasks[0].id == 1
        assert all_tasks[1].id == 3

        # Verify task 2 is gone
        assert store.get_task(2) is None

    def test_delete_task_not_found(self):
        """Test deleting a non-existent task returns False."""
        store = TaskStore()
        store.create_task("Task 1")

        result = store.delete_task(999)
        assert result is False

    def test_id_counter_persists_across_instances(self):
        """Test that ID counter is class-level and persists."""
        store1 = TaskStore()
        task1 = store1.create_task("Task 1")
        assert task1.id == 1

        store2 = TaskStore()
        task2 = store2.create_task("Task 2")
        assert task2.id == 2  # ID continues from previous store

    def test_reset_id_counter(self):
        """Test resetting ID counter to 1."""
        store = TaskStore()
        task1 = store.create_task("Task 1")
        task2 = store.create_task("Task 2")

        TaskStore.reset_id_counter()

        store2 = TaskStore()
        task3 = store2.create_task("Task 3")
        assert task3.id == 1  # Counter reset to 1
