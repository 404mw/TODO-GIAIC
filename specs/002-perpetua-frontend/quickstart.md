# Quickstart Guide - Perpetua Flow Frontend

**Feature**: 002-perpetua-frontend
**Last Updated**: 2026-01-07
**Target Audience**: Developers setting up the project for the first time

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: v20.x or later ([Download](https://nodejs.org/))
- **npm** or **pnpm**: Latest version (pnpm recommended for faster installs)
- **Git**: For version control
- **VS Code** (recommended): With ESLint, Prettier, Tailwind CSS IntelliSense extensions
- **Modern Browser**: Chrome, Firefox, Safari, or Edge (latest version)

---

## Initial Setup

### 1. Clone and Navigate

```bash
cd g:/Hackathons/GIAIC_Hackathons/02-TODO
```

**Note**: Repository already exists at this location.

### 2. Install Dependencies

```bash
cd frontend
pnpm install
```

**Alternative with npm**:
```bash
npm install
```

**Expected Duration**: 1-2 minutes (first install)

---

## Environment Configuration

### 1. Create Environment File

```bash
cp .env.example .env.local
```

### 2. Edit `.env.local`

```bash
# AI Features (disabled until backend integration)
NEXT_PUBLIC_AI_ENABLED=false

# AI API Configuration (future use)
AI_API_KEY=your_api_key_here
AI_RATE_LIMIT_PER_MINUTE=10
AI_QUOTA_DAILY=1000

# MSW Configuration (development only)
NEXT_PUBLIC_MSW_ENABLED=true

# App Configuration
NEXT_PUBLIC_MAX_TASKS=50
NEXT_PUBLIC_MAX_SUBTASKS_PER_TASK=10
```

**Important**:
- `.env.local` is **gitignored** - never commit secrets
- `.env.example` documents required variables without values
- AI features are **disabled** until backend is integrated

---

## Development Workflow

### 1. Start Development Server

```bash
pnpm dev
```

**Output**:
```
▲ Next.js 14.x
- Local:        http://localhost:3000
- Network:      http://192.168.1.x:3000

✓ Ready in 2.5s
[MSW] Mocking enabled for development
```

**Default Port**: 3000 (configurable in `package.json`)

### 2. Access Application

Open browser to:
- **Landing Page**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard/tasks (requires login in future)

**MSW Status**: Check browser console for `[MSW] Mocking enabled` message.

---

## Project Structure Overview

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (public)/          # Public routes
│   │   │   ├── page.tsx       # Landing page
│   │   │   ├── pricing/       # Pricing page
│   │   │   └── about/         # About page
│   │   ├── (dashboard)/       # Protected routes
│   │   │   ├── layout.tsx     # Dashboard layout with sidebar
│   │   │   ├── tasks/         # Tasks page
│   │   │   ├── notes/         # Notes page
│   │   │   ├── workflows/     # Workflows page
│   │   │   ├── achievements/  # Achievements page
│   │   │   └── activity/      # Activity log page
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ui/                # Base components (buttons, cards, etc.)
│   │   ├── tasks/             # Task-specific components
│   │   ├── notes/             # Note-specific components
│   │   ├── focus/             # Focus Mode components
│   │   └── achievements/      # Achievement components
│   ├── lib/
│   │   ├── stores/            # Zustand stores
│   │   │   ├── uiStore.ts     # UI state (sidebar, theme)
│   │   │   └── focusModeStore.ts  # Focus Mode state
│   │   ├── queries/           # TanStack Query hooks
│   │   │   ├── useTasks.ts    # Task queries/mutations
│   │   │   ├── useNotes.ts    # Note queries/mutations
│   │   │   └── useAchievements.ts  # Achievement queries
│   │   ├── utils/             # Utility functions
│   │   └── env.ts             # Environment validation
│   ├── schemas/               # Zod schemas
│   │   ├── task.schema.ts
│   │   ├── note.schema.ts
│   │   ├── user.schema.ts
│   │   └── achievement.schema.ts
│   ├── mocks/                 # MSW configuration
│   │   ├── browser.ts         # Browser MSW setup
│   │   ├── server.ts          # Server MSW setup (tests)
│   │   ├── fixtures/          # Mock data
│   │   └── handlers/          # API handlers
│   │       ├── tasks.ts
│   │       ├── notes.ts
│   │       ├── user.ts
│   │       └── achievements.ts
│   ├── config/
│   │   └── limits.ts          # Centralized limits
│   └── styles/
│       ├── globals.css        # Global styles
│       └── tailwind.css       # Tailwind imports
├── tests/
│   ├── unit/                  # Jest + RTL tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # Playwright tests
├── public/                    # Static assets
├── .env.example               # Environment template
├── .env.local                 # Local secrets (gitignored)
├── next.config.js             # Next.js configuration
├── tailwind.config.ts         # Tailwind configuration
├── jest.config.js             # Jest configuration
└── playwright.config.ts       # Playwright configuration
```

---

## Key Files to Understand

### 1. Schemas (`src/schemas/`)

All data contracts defined with Zod:

```typescript
// src/schemas/task.schema.ts
import { z } from 'zod';

export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional().default(''),
  tags: z.array(z.string().max(30)).max(20).default([]),
  priority: z.enum(['low', 'medium', 'high']),
  estimatedDuration: z.number().int().min(1).max(720).nullable(),
  // ... more fields
});

export type Task = z.infer<typeof TaskSchema>;
```

**Usage**:
- Import schema in forms: `TaskSchema.parse(formData)`
- Import type in components: `const task: Task = ...`
- MSW handlers validate with schema

### 2. Limits Configuration (`src/config/limits.ts`)

Central source of truth for all limits:

```typescript
export const LIMITS = {
  MAX_TASKS: 50,
  MAX_SUBTASKS_PER_TASK: 10,
  MAX_NOTE_CHARS_SOFT: 750,
  MAX_NOTE_CHARS_HARD: 1000,
  MAX_VOICE_RECORDING_SECONDS: 60,
  MAX_FOCUS_MODE_HOURS: 3,
  MAX_ACTIVITY_LOG_EVENTS: 100,
} as const;
```

**Usage**: `import { LIMITS } from '@/config/limits'`

### 3. MSW Handlers (`src/mocks/handlers/`)

Simulate backend API endpoints:

```typescript
// src/mocks/handlers/tasks.ts
import { http, HttpResponse, delay } from 'msw';
import { TaskSchema } from '@/schemas/task.schema';

export const taskHandlers = [
  http.get('/api/tasks', async () => {
    await delay(randomBetween(100, 500));  // Simulate latency
    return HttpResponse.json({ tasks: mockTasks });
  }),

  http.post('/api/tasks', async ({ request }) => {
    const body = await request.json();
    const task = TaskSchema.parse(body);  // Validate
    // ... save to in-memory store
    return HttpResponse.json({ task }, { status: 201 });
  }),
];
```

### 4. TanStack Query Hooks (`src/lib/queries/`)

React hooks for data fetching:

```typescript
// src/lib/queries/useTasks.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const res = await fetch('/api/tasks');
      return res.json();
    },
  });
}

export function useCreateTask() {
  return useMutation({
    mutationFn: async (task: TaskCreate) => {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(task),
      });
      return res.json();
    },
  });
}
```

---

## Running Tests

### Unit Tests (Jest + React Testing Library)

```bash
pnpm test
```

**Watch Mode**:
```bash
pnpm test:watch
```

**Coverage**:
```bash
pnpm test:coverage
```

**Expected Coverage**: >80% for core logic, state management, and API interactions.

### E2E Tests (Playwright)

```bash
pnpm test:e2e
```

**Headless Mode**:
```bash
pnpm test:e2e:headless
```

**UI Mode** (interactive):
```bash
pnpm test:e2e:ui
```

**Test Critical Paths**:
- Onboarding walkthrough
- Focus Mode activation/exit
- Task creation with sub-tasks
- Note-to-task conversion (disabled)

---

## Linting and Formatting

### Run ESLint

```bash
pnpm lint
```

**Fix Auto-fixable Issues**:
```bash
pnpm lint:fix
```

### Run Prettier

```bash
pnpm format
```

**Check Formatting** (CI):
```bash
pnpm format:check
```

---

## Build and Production

### Production Build

```bash
pnpm build
```

**Output**: `.next/` directory with optimized build.

### Start Production Server

```bash
pnpm start
```

**Note**: MSW does **not** run in production. Real backend required.

### Preview Build Locally

```bash
pnpm build && pnpm start
```

**Access**: http://localhost:3000 (production mode)

---

## Common Development Tasks

### 1. Adding a New Component

```bash
# Create component file
mkdir -p src/components/tasks
touch src/components/tasks/TaskCard.tsx

# Create test file
touch tests/unit/components/tasks/TaskCard.test.tsx
```

**Component Template**:
```typescript
'use client';

import { motion } from 'framer-motion';
import type { Task } from '@/schemas/task.schema';

interface TaskCardProps {
  task: Task;
  onComplete: (id: string) => void;
}

export function TaskCard({ task, onComplete }: TaskCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="glass-card p-4"
    >
      <h3>{task.title}</h3>
      {/* ... */}
    </motion.div>
  );
}
```

### 2. Adding a New MSW Handler

```typescript
// src/mocks/handlers/newEntity.ts
import { http, HttpResponse } from 'msw';

export const newEntityHandlers = [
  http.get('/api/new-entity', async () => {
    // ... handler logic
    return HttpResponse.json({ data: [] });
  }),
];

// src/mocks/handlers/index.ts (add to exports)
export { newEntityHandlers } from './newEntity';
```

### 3. Adding a New Zod Schema

```typescript
// src/schemas/newEntity.schema.ts
import { z } from 'zod';

export const NewEntitySchema = z.object({
  id: z.string().uuid(),
  // ... fields
});

export type NewEntity = z.infer<typeof NewEntitySchema>;
```

### 4. Adding a TanStack Query Hook

```typescript
// src/lib/queries/useNewEntity.ts
import { useQuery } from '@tanstack/react-query';
import { NewEntitySchema } from '@/schemas/newEntity.schema';

export function useNewEntity(id: string) {
  return useQuery({
    queryKey: ['newEntity', id],
    queryFn: async () => {
      const res = await fetch(`/api/new-entity/${id}`);
      const data = await res.json();
      return NewEntitySchema.parse(data);
    },
  });
}
```

---

## Troubleshooting

### Issue: MSW Not Intercepting Requests

**Symptoms**: Fetch requests fail with CORS or network errors.

**Solution**:
1. Check browser console for `[MSW] Mocking enabled`
2. Ensure `NEXT_PUBLIC_MSW_ENABLED=true` in `.env.local`
3. Restart dev server: `pnpm dev`
4. Clear browser cache and hard reload

### Issue: Type Errors After Schema Changes

**Symptoms**: TypeScript errors in components after updating Zod schema.

**Solution**:
1. Regenerate types: Zod types are auto-inferred, so restart TS server in VS Code
2. VS Code: `Cmd+Shift+P` → "TypeScript: Restart TS Server"
3. Re-run type check: `pnpm type-check`

### Issue: Tests Fail with "Network Request Failed"

**Symptoms**: Jest tests fail with fetch errors.

**Solution**:
1. Ensure MSW server is initialized in test setup
2. Check `tests/setup.ts` has `server.listen()` in `beforeAll`
3. Verify handlers are imported in `mocks/server.ts`

### Issue: Focus Mode Timer Not Working

**Symptoms**: Countdown doesn't update every second.

**Solution**:
1. Check Zustand store: `focusModeStore.ts` should have interval logic
2. Ensure `useEffect` cleanup clears interval on unmount
3. Check browser console for JavaScript errors

### Issue: Dark Mode Styles Not Applied

**Symptoms**: Components have light backgrounds or wrong colors.

**Solution**:
1. Ensure `tailwind.config.ts` has `darkMode: 'class'`
2. Verify `<html class="dark">` in `app/layout.tsx`
3. Check Tailwind purge config includes all component paths
4. Restart dev server: `pnpm dev`

---

## VS Code Configuration

### Recommended Extensions

Install via Extensions panel (`Cmd+Shift+X`):

- **ESLint** (`dbaeumer.vscode-eslint`)
- **Prettier** (`esbenp.prettier-vscode`)
- **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
- **Playwright Test for VSCode** (`ms-playwright.playwright`)
- **Jest** (`orta.vscode-jest`)

### Workspace Settings (`.vscode/settings.json`)

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ],
  "typescript.tsdk": "node_modules/typescript/lib",
  "jest.autoRun": "off"
}
```

---

## Useful Commands Reference

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Create production build |
| `pnpm start` | Start production server |
| `pnpm test` | Run unit tests |
| `pnpm test:watch` | Run tests in watch mode |
| `pnpm test:e2e` | Run E2E tests |
| `pnpm lint` | Run ESLint |
| `pnpm lint:fix` | Fix ESLint issues |
| `pnpm format` | Format code with Prettier |
| `pnpm type-check` | Run TypeScript compiler check |
| `pnpm analyze` | Analyze bundle size |

---

## Next Steps

After completing setup:

1. **Read Documentation**:
   - [research.md](./research.md) - Technology decisions and rationale
   - [data-model.md](./data-model.md) - Entity definitions and relationships
   - [contracts/api-specification.md](./contracts/api-specification.md) - API endpoints

2. **Explore Codebase**:
   - Start with `src/app/(dashboard)/tasks/page.tsx` (main view)
   - Review Zod schemas in `src/schemas/`
   - Check MSW handlers in `src/mocks/handlers/`

3. **Run Tests**:
   - `pnpm test` to ensure everything works
   - `pnpm test:e2e` to run full user flows

4. **Start Development**:
   - Refer to `tasks.md` (generated by `/sp.tasks` command) for implementation tasks
   - Follow TDD: write tests before implementation
   - Use `git` for version control: commit frequently, use descriptive messages

---

## Getting Help

- **Documentation**: Check `specs/002-perpetua-frontend/` for design artifacts
- **Constitution**: See `.specify/memory/constitution.md` for project principles
- **Issues**: Report bugs/questions in project issue tracker (if available)
- **Code Review**: Request reviews before merging significant changes

---

**Last Updated**: 2026-01-07 | **Maintained By**: Development Team
