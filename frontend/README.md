# Perpetua Flow - Frontend Application

A modern, AI-powered task management application built with Next.js 15, React 19, and TypeScript.

## Overview

Perpetua Flow helps users build lasting productivity habits through:

- **Smart Task Management**: Organize tasks with priorities, due dates, sub-tasks, and recurring schedules
- **Consistency Streaks**: Track daily productivity with streak mechanics and grace days
- **Focus Mode**: Eliminate distractions with dedicated focus sessions and countdown timers
- **Quick Notes**: Capture ideas instantly and convert them to actionable tasks
- **Smart Reminders**: Browser and in-app notifications with customizable timing
- **Achievements**: Gamified progress tracking to maintain motivation

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 15 (App Router) |
| UI | React 19, Tailwind CSS 4, Framer Motion |
| State | TanStack Query v5 (server), Zustand (client) |
| Validation | Zod |
| Components | Radix UI (accessible primitives) |
| Mock API | MSW v2 (Mock Service Worker) |
| Testing | Jest 30, React Testing Library |
| Search | Fuse.js (fuzzy search) |
| Recurrence | RRule (RFC 5545) |

## Getting Started

### Prerequisites

- Node.js 20.x or later
- npm, pnpm (recommended), or yarn

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd frontend

# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env.local

# Start development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Environment Variables

Create a `.env.local` file with:

```bash
# AI Features (disabled until backend)
NEXT_PUBLIC_AI_ENABLED=false

# MSW for development
NEXT_PUBLIC_MSW_ENABLED=true

# App limits
NEXT_PUBLIC_MAX_TASKS=50
NEXT_PUBLIC_MAX_SUBTASKS_PER_TASK=10
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (public)/          # Public marketing pages
│   │   ├── dashboard/         # Protected dashboard routes
│   │   └── focus/             # Focus mode pages
│   ├── components/
│   │   ├── ui/                # Base UI components
│   │   ├── tasks/             # Task-related components
│   │   ├── notes/             # Note components
│   │   ├── focus/             # Focus mode components
│   │   ├── reminders/         # Reminder components
│   │   └── achievements/      # Achievement components
│   ├── lib/
│   │   ├── hooks/             # TanStack Query hooks
│   │   ├── stores/            # Zustand stores
│   │   ├── schemas/           # Zod validation schemas
│   │   └── utils/             # Utility functions
│   └── mocks/                 # MSW handlers and fixtures
├── tests/                     # Test files
└── public/                    # Static assets
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Create production build |
| `pnpm start` | Start production server |
| `pnpm test` | Run unit tests |
| `pnpm test:watch` | Run tests in watch mode |
| `pnpm test:coverage` | Run tests with coverage |
| `pnpm lint` | Run ESLint |
| `pnpm lint:fix` | Fix ESLint issues |
| `pnpm type-check` | TypeScript type checking |
| `pnpm analyze` | Analyze bundle size |

## Key Features

### Task Management
- Create, edit, delete tasks with full CRUD operations
- Sub-tasks with progress tracking (percentage completion)
- Priority levels: low, medium, high
- Tags for organization
- Due dates and duration estimation
- Hide/archive functionality

### Reminders
- Browser notifications via Service Worker
- In-app toast notifications
- Relative timing (15min, 30min, 1hr, 1 day before)
- Mark as delivered tracking

### Recurrence
- RRule-based scheduling (RFC 5545)
- Presets: daily, weekly, monthly
- Custom intervals and patterns
- Completion-based instance generation

### Focus Mode
- Distraction-free task view
- Countdown timer based on task duration
- Auto-exit on task completion
- Keyboard shortcuts (Escape to exit)

### Achievements
- Consistency streak tracking
- Milestone achievements
- Visual progress indicators

## Design System

- **Theme**: Dark mode only (gray-950 backgrounds)
- **Effects**: Glassmorphism with backdrop-blur
- **Animations**: Framer Motion with reduced-motion support
- **Accessibility**: WCAG AA compliant (4.5:1 contrast)
- **Typography**: Geist Sans (primary), Geist Mono (code)

## Testing

```bash
# Run all tests
pnpm test

# Run with coverage
pnpm test:coverage

# Watch mode for development
pnpm test:watch
```

Coverage target: 80% for core logic and API interactions.

## Performance

- Bundle analysis: `pnpm analyze`
- Web Vitals tracking in development
- Optimized package imports for tree-shaking
- Image optimization with AVIF/WebP

## Documentation

For detailed documentation, see:

- [Quickstart Guide](../specs/002-perpetua-frontend/quickstart.md)
- [Data Model](../specs/002-perpetua-frontend/data-model.md)
- [Research & Decisions](../specs/002-perpetua-frontend/research.md)
- [API Specification](../specs/002-perpetua-frontend/contracts/)

## Contributing

1. Follow the TDD workflow: Red (failing test) → Green (implement) → Refactor
2. Ensure all tests pass before committing
3. Run `pnpm lint` and `pnpm type-check` before pushing
4. Reference task IDs in commit messages when applicable

## License

[MIT](LICENSE)
