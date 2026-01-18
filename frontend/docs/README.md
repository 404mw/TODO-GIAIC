# Perpetua Flow - AI-Powered Task Management

## Overview

Perpetua Flow is a modern, feature-rich task management application designed to help users stay organized, focused, and productive. Built with Next.js 16 and React 19, it combines intuitive task management with advanced features like focus mode, recurring tasks, and achievement tracking.

## Key Features

### Core Task Management
- **CRUD Operations**: Create, read, update, and delete tasks with full validation
- **Priority Levels**: High, Medium, Low with color-coded visual indicators
- **Due Dates**: Date-based task scheduling with urgency highlighting
- **Tags**: Flexible tagging system for task organization and filtering
- **Soft Delete**: Hidden tasks functionality for non-destructive archiving

### Subtasks
- Up to 10 subtasks per task
- Progress tracking with visual indicators
- Individual estimated durations
- Completion warnings when parent task has incomplete subtasks

### Recurring Tasks
- RRule-based recurrence patterns (daily, weekly, monthly, custom)
- Human-readable recurrence descriptions
- Automatic next instance generation on completion
- Visual scheduling indicators

### Focus Mode
- Configurable timer (1-720 minutes)
- Pause/resume functionality
- Visual progress ring animation
- Keyboard shortcuts (Space = pause/resume, Esc = exit)
- Audio and browser notifications on completion
- Distraction-free UI (hides sidebar)

### Reminders
- Multiple reminders per task (up to 5)
- Relative timing to due dates
- Browser push notifications
- In-app notification system
- Service worker integration for background notifications

### Notes
- Quick note creation and editing
- Convert notes to tasks
- Character limits with soft/hard warnings

### Achievements & Streaks
- Daily consistency streak tracking
- Milestone badges
- Activity logging
- Motivational progress indicators

### Dashboard
- Current streak display
- Tasks completed today
- Active tasks count
- Overdue tasks alert
- High-priority tasks section
- Due today quick view

## Technology Stack

| Category | Technology |
|----------|------------|
| Framework | Next.js 16.1.1 |
| UI Library | React 19.2.3 |
| Styling | Tailwind CSS 4 |
| State Management | Zustand 5.0.9 |
| Server State | TanStack React Query 5.90.16 |
| UI Primitives | Radix UI |
| Animations | Framer Motion 12.24.12 |
| Validation | Zod 4.3.5 |
| API Mocking | MSW 2.12.7 |
| Testing | Jest 30.2.0 + React Testing Library |

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app directory (routing)
│   │   ├── (public)/          # Public pages (About, Contact, Pricing)
│   │   ├── dashboard/         # Protected dashboard routes
│   │   ├── page.tsx           # Landing page
│   │   └── layout.tsx         # Root layout
│   ├── components/            # React components
│   │   ├── layout/           # Layout (Sidebar, Header)
│   │   ├── tasks/            # Task components
│   │   ├── focus/            # Focus mode
│   │   ├── notes/            # Notes
│   │   └── ui/               # Base UI components
│   ├── lib/
│   │   ├── hooks/            # Custom React hooks
│   │   ├── stores/           # Zustand stores
│   │   ├── schemas/          # Zod validation schemas
│   │   └── utils/            # Utility functions
│   └── mocks/                # MSW handlers & fixtures
└── public/                   # Static assets
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app runs at `http://localhost:3000` with MSW mocking API requests.

### Testing

```bash
npm test
```

### Build

```bash
npm run build
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [APP_FLOW.md](./APP_FLOW.md) | User flows and navigation |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical architecture details |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | Expected backend API endpoints |
| [BUGS_AND_ISSUES.md](./BUGS_AND_ISSUES.md) | Known bugs and issues |
| [REPETITIONS.md](./REPETITIONS.md) | Code repetitions to address |
| [IMPROVEMENTS.md](./IMPROVEMENTS.md) | Suggestions for improvements |

## Design Principles

1. **User-Centric**: Every feature designed around productivity and focus
2. **Accessibility First**: Built on Radix UI with full keyboard navigation
3. **Performance**: React Query caching, optimistic updates, lazy loading
4. **Type Safety**: Full TypeScript coverage with runtime Zod validation
5. **Maintainability**: Clear separation of concerns, modular architecture
