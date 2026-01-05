"""Console interface for TODO application."""

from typing import Optional
from todo_core.storage import TaskStore
from todo_core.models import validate_title, validate_description


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("TODO APP MENU")
    print("=" * 50)
    print("1. Create task")
    print("2. List tasks")
    print("3. Complete task")
    print("4. Update task")
    print("5. Delete task")
    print("6. Exit")
    print("-" * 50)


def get_menu_choice() -> str:
    """Get and validate menu choice.

    Returns:
        Valid menu choice (1-6)
    """
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        print("ERROR: Enter a number between 1 and 6")


def get_task_title(prompt: str = "Enter task title: ") -> str:
    """Get and validate task title.

    Args:
        prompt: Input prompt text

    Returns:
        Valid, trimmed task title
    """
    while True:
        title = input(prompt).strip()
        try:
            validated_title = validate_title(title)
            return validated_title
        except ValueError as e:
            print(f"ERROR: {e}")


def get_task_description(prompt: str = "Enter task description (optional): ") -> Optional[str]:
    """Get and validate task description.

    Args:
        prompt: Input prompt text

    Returns:
        Valid, trimmed description or None if empty
    """
    while True:
        description = input(prompt).strip()
        try:
            validated_desc = validate_description(description)
            return validated_desc
        except ValueError as e:
            print(f"ERROR: {e}")


def create_task(store: TaskStore) -> None:
    """Create a new task via console input.

    Args:
        store: TaskStore instance to add task to
    """
    print("\n--- CREATE TASK ---")
    title = get_task_title()
    description = get_task_description()

    task = store.create_task(title, description)
    print(f"\n[OK] Task created (ID: {task.id})")


def list_tasks(store: TaskStore) -> None:
    """Display all tasks in a formatted table.

    Args:
        store: TaskStore instance to list tasks from
    """
    print("\n--- TASK LIST ---")
    tasks = store.list_all_tasks()

    if not tasks:
        print("No tasks found")
        return

    print("=" * 80)
    print(f"{'ID':<4} | {'Title':<30} | {'Status':<12} | {'Created':<19}")
    print("-" * 80)

    for task in tasks:
        status = "[X] DONE" if task.status == "complete" else "[ ] PENDING"
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        print(f"{task.id:<4} | {title:<30} | {status:<12} | {task.created_at}")

    print("=" * 80)


def get_task_id(store: TaskStore, prompt: str = "Enter task ID: ") -> int:
    """Get and validate task ID.

    Args:
        store: TaskStore instance to check task existence
        prompt: Input prompt text

    Returns:
        Valid task ID that exists in the store
    """
    while True:
        try:
            task_id = int(input(prompt).strip())
            if store.get_task(task_id) is None:
                print(f"ERROR: Task {task_id} not found")
                continue
            return task_id
        except ValueError:
            print("ERROR: Task ID must be a number")


def complete_task(store: TaskStore) -> None:
    """Mark a task as complete.

    Args:
        store: TaskStore instance
    """
    print("\n--- COMPLETE TASK ---")
    task_id = get_task_id(store)
    task = store.get_task(task_id)

    if task.status == "complete":
        print(f"\nTask {task_id} is already complete")
        return

    task.mark_complete()
    print(f"\n[OK] Task {task_id} marked as complete")


def update_task(store: TaskStore) -> None:
    """Update task title or description.

    Args:
        store: TaskStore instance
    """
    print("\n--- UPDATE TASK ---")
    task_id = get_task_id(store)
    task = store.get_task(task_id)

    print(f"Current: {task.title}")
    print("1. Update title")
    print("2. Update description")

    while True:
        choice = input("Choose (1-2): ").strip()
        if choice == "1":
            new_title = get_task_title("New title: ")
            task.update_title(new_title)
            print("\n[OK] Title updated")
            break
        elif choice == "2":
            new_desc = get_task_description("New description: ")
            task.update_description(new_desc)
            print("\n[OK] Description updated")
            break
        else:
            print("ERROR: Enter 1 or 2")


def delete_task(store: TaskStore) -> None:
    """Delete a task after confirmation.

    Args:
        store: TaskStore instance
    """
    print("\n--- DELETE TASK ---")
    task_id = get_task_id(store)
    task = store.get_task(task_id)

    while True:
        confirm = input(f"Delete '{task.title}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            store.delete_task(task_id)
            print(f"\n[OK] Task {task_id} deleted")
            break
        elif confirm == "no":
            print("\nCanceled")
            break
        else:
            print("ERROR: Enter 'yes' or 'no'")
