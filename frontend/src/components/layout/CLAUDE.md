# Directory: `frontend/src/components/layout`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains all the major components responsible for the overall structure and layout of the authenticated application (the dashboard). These components provide the persistent UI elements like the sidebar, header, and main content area that wrap the various feature pages.

## Structure and Behavior

- **`DashboardLayout.tsx`**: This is the top-level layout component for the entire dashboard. It orchestrates all the other layout components. It renders the `<Sidebar>`, `<Header>`, and the main content area for the current page. It also includes global components like the `<PendingCompletionsBar>` and the `<NewTaskModal>`, making them available across the entire dashboard. Its main responsibility is to correctly position the main content area relative to the collapsible sidebar.

- **`Header.tsx`**: The application's top header bar. It is a sticky component that remains visible at the top of the page. It contains the current page title, a "New Task" button (which opens a dropdown for creating new tasks or notes), and the `<NotificationDropdown>`. On mobile screens, it also includes the hamburger icon to toggle the sidebar.

- **`Sidebar.tsx`**: The main navigation sidebar on the left.
    - **Collapsible**: It can be expanded or collapsed by the user, and this state is persisted to `localStorage` via the `useSidebarStore`.
    - **Content**: It contains the application logo, a search button to trigger the `<CommandPalette>`, the primary `<NavigationMenu>`, and a `<ProfilePopover>` at the bottom.
    - **Focus Mode Integration**: It is aware of the Focus Mode state (`useFocusStore`) and will completely hide itself when a focus session is active.

- **`NavigationMenu.tsx`**: This component is rendered inside the `Sidebar` and is responsible for displaying the list of primary navigation links (Dashboard, Tasks, Notes, etc.). It handles active route highlighting, showing a different style for the link that corresponds to the current page.

- **`NotificationDropdown.tsx`**: A component within the `Header` that shows a dropdown list of recent notifications when clicked. It gets its state from the `useNotificationStore`.

- **`PendingCompletionsBar.tsx`**: A unique UI element that appears as a fixed bar at the bottom of the screen only when the user has marked one or more tasks as complete but has not yet saved the changes. It allows the user to either confirm and save the completions or discard them. It also includes a warning state if the user tries to complete a task that still has open sub-tasks.

- **`ProfilePopover.tsx`**: A component at the bottom of the `Sidebar` that shows the current user's name and email. When clicked, it opens a popover with links to the user's profile and settings, as well as a logout button.

## Key Features

- **Consistent Layout**: Provides a consistent and responsive layout for all pages within the authenticated part of the application.
- **Stateful UI**: Many of the layout components are connected to `zustand` stores to manage global UI state (e.g., sidebar collapse state, pending completions, new task modal).
- **Responsive Design**: The layout adjusts for different screen sizes, with the sidebar being hidden by default on mobile and the header adapting its content.
- **Improved User Experience**: Features like the pending completions bar and the notification dropdown provide immediate feedback and context to the user about the state of the application.
