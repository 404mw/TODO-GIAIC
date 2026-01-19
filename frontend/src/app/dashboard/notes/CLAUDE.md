# Directory: `frontend/src/app/dashboard/notes`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the main page for the "Notes" feature, accessible at `/dashboard/notes`. This page provides a space for users to quickly capture thoughts, ideas, and reminders that may not yet be concrete tasks.

## Structure and Behavior

- **`page.tsx`**: The sole file in this directory, this client component (`'use client'`) orchestrates the entire note management interface.
    - **State Management**: It uses `useState` to manage the UI state, such as toggling the display of archived notes (`showArchived`), showing the form for a new note (`isCreating`), and tracking which note is currently being edited (`editingNote`).
    - **Data Fetching**: It fetches notes using the `useNotes` hook, passing the `showArchived` state as a filter to the API. It also handles the `isLoading` and `error` states of the data query.
    - **Component Composition**: The page is built by composing several key components:
        - `DashboardLayout`: Provides the standard sidebar and header for the dashboard.
        - `NoteEditor`: A form component that is conditionally rendered when a user creates a new note or edits an existing one.
        - `NoteList`: A component that takes the fetched notes and renders them in a grid, handling the empty, loading, and error states.
        - `Button`: Used for actions like "New Note" and "Show Archived".
    - **CRUD Operations**: The page implicitly supports full CRUD (Create, Read, Update, Delete) functionality for notes through the components it uses. "Create" and "Update" are handled via the `NoteEditor`, while "Read" and "Delete"/"Archive" are handled within the `NoteList` and `NoteCard` components.

## Key Features

- **Quick Capture**: The primary goal of this page is to allow users to quickly write down information without the formal structure of a task.
- **In-place Editing**: Users can edit notes directly from the list, which displays the `NoteEditor` form inline with the selected note's content.
- **Archive Functionality**: Instead of just deleting, users can archive notes, allowing them to be hidden from the main view but still retrievable. The "Show Archived" toggle provides access to these notes.
- **Clean UI**: The page maintains a clean and simple interface, showing the editor only when needed and displaying the notes in a card-based grid.
