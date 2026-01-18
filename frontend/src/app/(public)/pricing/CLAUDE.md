# Directory: `frontend/src/app/(public)/pricing`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory is responsible for rendering the public-facing "Pricing" page, located at the `/pricing` URL path. As part of the `(public)` route group, it uses the shared public layout.

## Structure and Behavior

- **`page.tsx`**: The main React component for the pricing page. It is a client component (`'use client'`) that outlines the different subscription plans available.
    - **Static Content**: The plan details (Free, Pro) and FAQ content are hard-coded as constants within the component. This is suitable for content that does not change frequently.
    - **Feature Comparison**: It clearly lists the features available in each plan, allowing users to easily compare them. The "Pro" plan is visually highlighted as the recommended option.
    - **FAQ Section**: Includes a section to answer common questions related to pricing, billing, and plan management.
    - **Animations**: Uses `framer-motion` for subtle animations on page load and as the user scrolls, enhancing the visual presentation. It respects user preferences via the `useReducedMotion` hook.

- **`layout.tsx`**: The route-specific layout that exports the page's metadata.

- **`metadata.ts`**: Contains the SEO and social sharing metadata for the `/pricing` page, ensuring it is well-described on search engines and social media platforms.

## Key Features

- **Clear Pricing Tiers**: Presents a clear, side-by-side comparison of the "Free" and "Pro" plans, including price, features, and a call-to-action (CTA) for each.
- **User Conversion**: The page is designed to convert users by highlighting the benefits of the "Pro" plan and providing a clear path to get started with a free trial.
- **Informative**: The FAQ section proactively addresses potential user questions, reducing uncertainty and building trust.
