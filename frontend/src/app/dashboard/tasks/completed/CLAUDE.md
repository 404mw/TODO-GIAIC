# Directory: `frontend/src/app/dashboard/tasks/completed`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the page for displaying all tasks that have been marked as completed, accessible at `/dashboard/tasks/completed`. It provides a historical view of the user's finished work.

## Structure and Behavior

- **`page.tsx`**: The main component for the "Completed Tasks" page.
    - **Client-Side Filtering**: It fetches all non-hidden tasks using `useTasks({ hidden: false })` and then performs a client-side filter to isolate only the tasks where the `completed` property is `true`.
    - **Sorting**: It provides robust client-side sorting for the completed tasks. Users can sort the list by:
        - **Completed Date**: The primary sort option, which uses `completedAt` and falls back to `updatedAt`.
        - **Priority**: Sorts by high, medium, and low priority.
        - **Title**: Sorts alphabetically by task title.
        The user can also toggle the sort direction between ascending and descending.
    - **State Management**: Uses `useState` to manage the user's selected sort criteria and direction.
    - **Component Composition**: It uses the `<TaskList>` component to render the final sorted list of completed tasks, passing the prepared array as a prop.

## Key Features

- **Archive View**: Acts as an archive of all completed work, allowing users to review their accomplishments.
- **Organized Display**: The sorting options give users the flexibility to organize their completed tasks in a way that is meaningful to them, whether it's by when they were finished, their importance, or their name.
- **Clean Separation**: Separates completed tasks from active tasks, which helps to keep the main "All Tasks" view clean and focused on pending work, reducing clutter.
