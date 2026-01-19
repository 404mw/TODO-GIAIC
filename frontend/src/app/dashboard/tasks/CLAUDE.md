# Directory: `frontend/src/app/dashboard/tasks`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory serves as the root for all task-related pages within the dashboard. The `page.tsx` file in this directory is the main "All Tasks" view, which is one of the most critical and frequently used pages in the application.

## Structure and Behavior

- **`page.tsx`**: The primary component for displaying the main task list.
    - **Client Component**: It is a client component (`'use client'`) to allow for interactive filtering and sorting.
    - **Data Fetching**: It uses the `useTasks({ hidden: false })` hook to fetch all tasks that are not hidden.
    - **Filtering**: It implements client-side filtering logic to allow users to view tasks by different criteria:
        - `all`: All active tasks.
        - `active`: All non-completed tasks (the default behavior).
        - `high`: Only tasks with 'high' priority.
        - `today`: Only tasks due on the current day.
        Completed tasks are always excluded from this view, as they have their own dedicated page.
    - **Sorting**: It provides comprehensive client-side sorting capabilities, allowing users to sort the filtered tasks by `priority`, `dueDate`, `created` date, or `title`, in both `asc` and `desc` order.
    - **Component Composition**: It uses the `<TaskList>` component to render the filtered and sorted list of tasks. This promotes a clean separation of concerns, where this page handles the filtering/sorting logic and `TaskList` handles the rendering.
    - **New Task Action**: It includes a "New Task" button that triggers a modal for creating a new task, managed by the `useNewTaskModalStore`.

- **Subdirectories**:
    - **`[id]/`**: Contains the dynamic route for viewing the details of a single task.
    - **`completed/`**: Contains the page for viewing all completed tasks.
    - **`new/`**: Contains a dedicated page for creating a new task, which could be used as an alternative to the modal.

## Key Features

- **Central Task Hub**: This is the default and most important view for users to manage their ongoing work.
- **Rich Interaction**: The combination of filtering and sorting provides users with powerful tools to organize and find their tasks according to their current needs.
- **State Management**: Uses `useState` for managing the local filter and sort states.
- **Separation of Concerns**: Effectively delegates the rendering of the task list to the `TaskList` component.
