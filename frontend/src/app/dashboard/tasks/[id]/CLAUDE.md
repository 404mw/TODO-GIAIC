# Directory: `frontend/src/app/dashboard/tasks/[id]`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory represents a dynamic route in Next.js, responsible for displaying the detailed view of a single, specific task. The `[id]` in the directory name is a placeholder for the unique identifier of the task. For example, a URL like `/dashboard/tasks/123-abc` would be handled by this route.

## Structure and Behavior

- **`page.tsx`**: The main component for the task detail page.
    - **Dynamic Data Fetching**: It uses the `useTask(id)` hook to fetch the specific task corresponding to the `id` parameter from the URL.
    - **React `use` Hook**: It leverages React's `use` hook to handle the promise-based `params` prop, which is a modern way to handle data in Server Components and their descendants.
    - **State Handling**: It gracefully handles `isLoading` and `error` states. While the task is being fetched, it displays a loading spinner. If the task is not found or an error occurs, it shows a "Task not found" message.
    - **Component Delegation**: Once the task data is successfully fetched, it delegates the entire rendering of the task's details to the `<TaskDetailView />` component, passing the `task` object as a prop. This keeps the page component clean and focused on data fetching and state management.

- **`edit/` (Subdirectory)**: This subdirectory contains the page for editing the task that is being viewed.

## Key Features

- **Detailed View**: Provides a focused view of a single task, showing all its properties, including description, sub-tasks, reminders, and other metadata.
- **Dynamic Routing**: A core feature of the Next.js App Router, allowing the application to have unique, bookmarkable URLs for every task.
- **Data-Driven Content**: The content of the page is entirely dependent on the task data fetched from the API based on the URL parameter.
- **Clean Architecture**: Follows a good architectural pattern by separating the data-fetching and state-management logic (in `page.tsx`) from the presentation logic (in `TaskDetailView.tsx`).
