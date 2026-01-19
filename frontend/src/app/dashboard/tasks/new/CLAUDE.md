# Directory: `frontend/src/app/dashboard/tasks/new`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the dedicated page for creating a new task, accessible at `/dashboard/tasks/new`. It provides a full-page form experience as an alternative to the "New Task" modal.

## Structure and Behavior

- **`page.tsx`**: The main component for the "Create New Task" page.
    - **Component Reusability**: This page's primary purpose is to host the `<TaskForm />` component, demonstrating a strong use of component reuse. The `TaskForm` is the same one used for editing a task, but when rendered here without a `task` prop, it operates in "create" mode.
    - **Layout**: It is wrapped in the `<DashboardLayout />`, ensuring it has the same consistent navigation and header as the rest of the dashboard pages.
    - **Navigation**: It includes a "Back to Tasks" link, providing a clear and easy way for users to return to the main task list without creating a new task.
    - **Focused Experience**: By providing a full page for task creation, it offers a more focused and less cluttered experience compared to a modal, which can be beneficial when creating complex tasks with many details.

## Key Features

- **Dedicated Creation Page**: Offers a full-screen, dedicated interface for creating a new task.
- **Component Reuse**: Effectively reuses the `TaskForm` component, ensuring consistency between the create and edit experiences and reducing code duplication.
- **Standard Layout**: It integrates seamlessly into the dashboard's design and navigation system.
