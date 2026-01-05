"""Main entry point for TODO Core Logic application."""

from todo_core.storage import TaskStore
from todo_core.cli import (
    display_menu,
    get_menu_choice,
    create_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
)


def main() -> None:
    """Main application loop."""
    store = TaskStore()

    print("\n" + "=" * 50)
    print("Welcome to TODO Core Logic!")
    print("=" * 50)

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == "1":
            create_task(store)
        elif choice == "2":
            list_tasks(store)
        elif choice == "3":
            complete_task(store)
        elif choice == "4":
            update_task(store)
        elif choice == "5":
            delete_task(store)
        elif choice == "6":
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
