# Directory: `frontend/src/app/dashboard/settings/hidden-tasks`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the page for managing tasks that have been hidden by the user, accessible at `/dashboard/settings/hidden-tasks`. This feature provides a dedicated space for users to review and act upon tasks they have removed from their main views.

## Structure and Behavior

- **`page.tsx`**: The sole file, this client component (`'use client'`) is responsible for the entire "Hidden Tasks" management interface.
    - **Data Fetching**: It uses the `useTasks` hook with the filter `{ hidden: true }` to fetch only the tasks that have been marked as hidden. It also handles the corresponding loading and error states for this data query.
    - **Task Listing**: It displays the fetched hidden tasks in a list format. For each task, it shows key information like the title, priority, completion status, and due date.
    - **Actions**: Each task in the list has two primary actions:
        1.  **Restore**: The "Restore" button triggers the `useUpdateTask` mutation to set the task's `hidden` property back to `false`. This makes the task reappear in the main task lists.
        2.  **Delete**: The "Delete" button triggers the `useDeleteTask` mutation to permanently remove the task from the system. To prevent accidental data loss, it uses a native `confirm()` dialog to ask the user for confirmation before proceeding.
    - **User Feedback**: It utilizes the `useToast` hook to provide immediate feedback to the user after a "Restore" or "Delete" action is successfully completed or if an error occurs.
    - **Empty State**: If there are no hidden tasks, the component renders a helpful empty state message with an icon, explaining what the page is for and guiding the user.

## Key Features

- **Task Lifecycle Management**: Provides a crucial part of the task lifecycle, allowing users to manage tasks that are not immediately relevant without permanently deleting them.
- **Destructive Action Confirmation**: Implements a safety measure by requiring user confirmation for permanent deletion, which is a key usability best practice.
- **Clear User Feedback**: Uses toast notifications to keep the user informed about the outcome of their actions.
- **Focused View**: By fetching only hidden tasks, it provides a clean and focused interface for this specific management task.
