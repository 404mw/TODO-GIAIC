# Directory: `frontend/src/app/dashboard/focus`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the main page for the "Focus Mode" feature, accessible at `/dashboard/focus`. This page provides a distraction-free environment to help users concentrate on a single task for a set duration.

## Structure and Behavior

- **`page.tsx`**: The sole file, this is a complex client component (`'use client'`) that manages the entire Focus Mode lifecycle, from setup to an active session. It functions as a state machine with two primary states:
    1.  **Setup View**:
        - Allows the user to select a task from a list using the `<TaskSelector>` component.
        - If the selected task has sub-tasks, it dynamically shows a sub-task selection UI.
        - The duration of the focus session is automatically calculated from the `estimatedDuration` of the selected sub-tasks. Users do not manually set a timer.
        - The "Start" button is disabled until a valid selection is made.

    2.  **Active Session View**:
        - Once a session is started, the UI transitions to a minimalist, full-screen-like view.
        - It displays the title and description of the focused task.
        - The `<FocusTimer>` component shows a circular countdown timer.
        - A checklist of the selected sub-tasks is displayed, allowing the user to mark them as complete as they work. These completions are "pending" and are not saved until the end of the session.
        - It provides an "Exit" button and keyboard shortcuts (`Esc`, `Space`) for controlling the session.

- **State Management**: The component relies on the `useFocusModeStore` (a Zustand store) to manage the global state of whether a focus session is active and which task is being focused on. Local `useState` hooks are used to manage the setup flow (task selection, sub-task selection, etc.).

- **Data Fetching**: It uses the `useTasks` and `useSubTasks` hooks to fetch the necessary data for the selection process.

- **User Feedback**: It uses the `useToast` hook to provide feedback to the user when starting a session or when there are validation errors (e.g., no task selected).

## Key Features

- **Distraction-Free UI**: When a session is active, the regular dashboard navigation and other UI elements are hidden to help the user focus.
- **Sub-task Integration**: The focus session is built around completing specific sub-tasks, providing a clear checklist for the user to follow.
- **Automatic Duration**: The timer is not set manually but is derived from the estimated duration of the sub-tasks, encouraging better planning.
- **Pending Completions**: Sub-tasks marked as complete during a session are not immediately saved, giving the user a chance to review before finalizing their progress.
- **Keyboard Navigation**: Supports keyboard shortcuts for pausing/resuming the timer and exiting the session, enhancing accessibility and usability for power users.
