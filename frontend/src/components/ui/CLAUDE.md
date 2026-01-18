# Directory: `frontend/src/components/ui`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the core, reusable UI components that form the foundation of the application's design system. These components are designed to be generic, accessible, and stylable, providing consistent look and feel across the application. Many components are built on top of Radix UI primitives for accessibility and headless logic, with styling applied via Tailwind CSS and `class-variance-authority`.

## Core Concepts

- **Radix UI Primitives**: Components like `Dialog`, `Popover`, `Select`, and `Toast` are wrappers around Radix UI primitives. This provides a solid foundation for accessibility (keyboard navigation, focus management, ARIA attributes) while allowing for full style control.
- **`class-variance-authority` (CVA)**: Components like `Button` and `Input` use CVA to manage different visual variants (e.g., `primary`, `secondary`, `danger`) and sizes (`sm`, `md`, `lg`). This makes it easy to apply consistent styling across the application.
- **Accessibility**: A key focus of this directory is to provide accessible components out-of-the-box.
- **Reusability**: These components are fundamental building blocks used throughout the application, from simple forms to complex interactive elements.

## File Breakdown

- **`Button.tsx`**: A highly versatile button component with multiple variants (`primary`, `secondary`, `outline`, `ghost`, `danger`, `success`), sizes, and a `loading` state. It's a cornerstone of interactive elements in the app.

- **`CommandPalette.tsx`**: Implements a global command palette (accessible via `Cmd/Ctrl+K`). It allows users to quickly search for tasks and notes, and execute actions like creating a new task or navigating to different pages. It integrates with `zustand` state stores (`useCommandPaletteStore`, `useNewTaskModalStore`) and data hooks (`useTasks`, `useNotes`).

- **`Dialog.tsx`**: Provides an accessible modal dialog component based on Radix UI. It's used for creating and editing tasks, ensuring focus is trapped within the modal and providing an overlay.

- **`Input.tsx`**: A flexible `input` component that supports different sizes, validation states (`default`, `error`, `success`), labels, helper text, and icons.

- **`Label.tsx`**: A simple, styled `label` component for use with form elements like `Input` and `Textarea`.

- **`Popover.tsx`**: A generic popover component built on Radix UI, used for displaying floating content next to a trigger element.

- **`Select.tsx`**: An accessible and styled dropdown/select component based on Radix UI. Used for all dropdown menus, such as selecting a task's priority.

- **`Skeleton.tsx`**: Contains various skeleton loading components (`TaskCardSkeleton`, `NoteCardSkeleton`, etc.). These are used to provide visual placeholders while data is being fetched, improving the user's perception of performance.

- **`Textarea.tsx`**: A styled, multi-line text input component.

- **`Toast.tsx`**: Defines the visual structure and variants for toast notifications using Radix UI Toast primitives.

- **`Toaster.tsx`**: The container component that renders active toasts. It uses the `useToast` hook to listen for and display new notifications. It should be placed in the root layout of the application.
