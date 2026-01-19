# Directory: `frontend/src/app/dashboard/tasks/[id]/edit`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the dynamic route for the "Edit Task" page. The URL, such as `/dashboard/tasks/123-abc/edit`, allows users to modify an existing task.

## Structure and Behavior

- **`page.tsx`**: The main component for the edit task page.
    - **Data Fetching**: It fetches the data for the specific task to be edited by using the `useTask(params.id)` hook. The `id` is extracted from the URL.
    - **State Handling**: It manages loading and error states. A loading spinner is shown while the task data is being fetched. If the task cannot be found, it displays a "Task not found" error message.
    - **Component Reusability**: This page is a prime example of component reuse. Instead of containing a separate form, it renders the generic `<TaskForm />` component.
    - **Pre-populating Form**: It passes the fetched `task` object as a prop to the `<TaskForm />`, which then uses this data to pre-fill all the form fields for editing.
    - **Navigation**: It uses the `useRouter` hook to handle navigation. Upon successful form submission (`onSuccess`) or cancellation (`onCancel`), it redirects the user back to the task detail page (`/dashboard/tasks/[id]`).

## Key Features

- **Task Editing**: Provides the core interface for modifying the details of an existing task.
- **Dynamic Routing**: Leverages Next.js's dynamic routing to create a unique editing page for each task.
- **Component Reuse**: Demonstrates a smart reuse of the `TaskForm` component for both creating and editing tasks, reducing code duplication.
- **Seamless User Experience**: After editing, the user is automatically navigated back to the task detail page to see their updated information, providing a smooth workflow.
