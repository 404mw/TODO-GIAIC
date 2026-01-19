# Directory: `frontend/src/app/(public)/about`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the route-specific files for the public-facing "About Us" page, located at the `/about` URL path. As part of the `(public)` route group, it shares a common layout with other marketing pages.

## Structure and-Behavior

- **`page.tsx`**: The main React component that renders the content of the "About" page. It's a client component (`'use client'`) that leverages `framer-motion` for engaging animations and `useReducedMotion` to respect user accessibility preferences. The page is composed of several sections:
    - A hero section introducing the project's mission.
    - A stats bar showing key metrics like active users and tasks completed.
    - Detailed sections on the project's mission and core values (Simplicity, Habit Science, Privacy, Accessibility).
    - A section highlighting the modern technology stack used (Next.js, React, TypeScript).
    - A final Call-to-Action (CTA) section encouraging users to get started.
    
- **`layout.tsx`**: A simple layout component that wraps the page. Its primary purpose is to export the `metadata` for this specific route.

- **`metadata.ts`**: Defines the SEO and social sharing metadata for the `/about` page. This includes the page title, description, keywords, and Open Graph/Twitter card information, ensuring the page is well-represented on search engines and social media platforms.

## Key Features

- **Marketing Content**: Provides detailed information about the application's purpose and philosophy to attract and inform potential users.
- **Animated UI**: Uses `framer-motion` to create a dynamic and visually appealing user experience with fade-in and staggering animations.
- **Accessibility**: Adheres to accessibility best practices by using the `useReducedMotion` hook to disable animations for users who prefer it.
- **SEO Optimized**: Contains rich metadata to improve search engine ranking and social media sharing appearance.
- **Component Composition**: Built from smaller, reusable components (though none are defined within this directory itself) and adheres to the overall public page design aesthetic.
