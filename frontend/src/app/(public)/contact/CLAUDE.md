# Directory: `frontend/src/app/(public)/contact`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the route-specific files for the public-facing "Contact Us" page, located at the `/contact` URL path. As part of the `(public)` route group, it shares a common layout with other marketing pages.

## Structure and Behavior

- **`page.tsx`**: The main React component for the contact page. It's a client component (`'use client'`) that provides an interactive contact form. Key features include:
    - **State Management**: Uses the `useState` hook to manage form data, validation errors, and submission status.
    - **Client-Side Validation**: Implements a `validateForm` function to ensure all fields (name, email, subject, message) are correctly filled out before submission. It provides real-time feedback to the user.
    - **Simulated API Call**: The `handleSubmit` function currently simulates an API call with a `setTimeout`, mimicking a real-world network request.
    - **Submission States**: The UI changes based on the submission state, showing a loading indicator while submitting and a success message upon completion.
    - **Contact Information**: Alongside the form, it displays alternative contact methods such as an email address and links to social media profiles.

- **`layout.tsx`**: A simple layout component that wraps the page and exports the route's `metadata`.

- **`metadata.ts`**: Defines the SEO and social sharing metadata for the `/contact` page, including title, description, keywords, and Open Graph/Twitter card information. This ensures the page is properly indexed and displayed on external platforms.

## Key Features

- **User Interaction**: Provides a clear and direct way for users to send messages to the application's support or sales team.
- **Form Handling**: Demonstrates a complete client-side form handling lifecycle, including input management, validation, submission states, and user feedback.
- **User Experience**: The form clears errors as the user types and provides a clear success state, creating a smooth user experience.
- **Component Reusability**: While self-contained, the page is built using the reusable UI components from `frontend/src/components/ui` (like `Button`, `Input`, `Textarea`).
