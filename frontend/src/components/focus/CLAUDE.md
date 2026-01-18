# Directory: `frontend/src/components/focus`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the reusable UI components that are specifically designed for the "Focus Mode" feature. These components are used on the main Focus Mode page (`/dashboard/focus`) to construct the setup and active session views.

## Structure and Behavior

- **`FocusTimer.tsx`**: This is a key component that renders the circular countdown timer during an active focus session.
    - **Visual Feedback**: It displays the remaining time in `MM:SS` format and shows a visual progress ring that depletes as time passes. The color of the ring changes to indicate the timer's state (e.g., blue for running, yellow for paused, green for complete).
    - **Timer Logic**: It contains all the logic for the countdown, including pausing, resuming, and resetting the timer.
    - **Callbacks**: It accepts a series of callback props (`onComplete`, `onPause`, `onResume`, `onExit`) to communicate its state changes back to the parent page.
    - **Notifications**: Upon completion, it triggers both an audio alert (`/sounds/notification.mp3`) and a browser notification to alert the user that the session is over.
    - **Keyboard Shortcuts**: It listens for keyboard events, allowing the user to control the timer with the `Space` key (pause/resume) and exit the session with the `Esc` key.

- **`TaskSelector.tsx`**: This component is used in the setup view of Focus Mode.
    - **Task Listing**: It receives a list of tasks, filters out any that are already completed or hidden, and sorts the remaining tasks by priority.
    - **Selection UI**: It renders the list of selectable tasks, allowing the user to click on one to choose it for the focus session. The currently selected task is visually highlighted.
    - **Empty State**: If there are no incomplete tasks available, it displays a helpful message prompting the user to create a task first.

## Key Features

- **Encapsulation**: These components encapsulate the specific UI and logic for the Focus Mode feature, keeping the main page component cleaner. `FocusTimer` handles all the complexity of the timer, while `TaskSelector` handles the task selection UI.
- **Interactivity**: The components are highly interactive, responding to user input via both mouse clicks and keyboard shortcuts.
- **User Experience**: They are designed to create an intuitive and engaging experience, from the animated timer ring to the simple task selection list.
