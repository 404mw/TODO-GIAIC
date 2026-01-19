# Directory: `frontend/src/app/dashboard/achievements`

**Note for AI:** This file must be updated with any changes made to this directory.

This directory contains the main page for the "Achievements" feature, accessible at `/dashboard/achievements`. It serves as a gamification and motivation hub, displaying the user's productivity statistics and earned milestones.

## Structure and Behavior

- **`page.tsx`**: The sole file in this directory, this client component (`'use client'`) is responsible for fetching and rendering all achievement-related data.
    - **Data Fetching**: It uses the `useAchievements` custom hook (from `src/lib/hooks`) to fetch data from the `/api/achievements` endpoint. It handles loading and error states gracefully.
    - **Metric Display**: It visualizes key productivity metrics using a reusable `MetricCard` component defined within the same file. The metrics displayed are:
        - **Consistency Streak**: Shows the user's current and longest streaks of daily task completions.
        - **High Priority Slays**: The number of high-priority tasks completed.
        - **Completion Ratio**: The percentage of tasks completed on time.
        - **Milestones Unlocked**: The total number of achievements earned.
    - **Milestone Listing**: If the user has unlocked any milestones, it renders a list of them with their names and descriptions.
    - **Motivational Feedback**: Includes a dynamic text block at the bottom that provides a motivational message based on the user's performance (specifically, the number of high-priority tasks completed).

## Key Features

- **Gamification**: Motivates users by turning their productivity into a game with streaks, stats, and unlockable milestones.
- **Data Visualization**: Presents key performance indicators in a clear and visually appealing card-based layout.
- **Dynamic Content**: The content of the page, including the motivational messages, changes based on the user's data.
- **Asynchronous Handling**: Shows loading and error states while fetching achievement data, ensuring a smooth user experience.
