# Technical Architecture

This document describes the technical architecture, design patterns, and implementation details of the Perpetua Flow frontend application.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Next.js App Router                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      App Directory                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │  │
│  │  │   Public    │  │  Dashboard  │  │   Root Layout       │ │  │
│  │  │   Routes    │  │   Routes    │  │   (Providers)       │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Components  │       │     Lib      │       │    Mocks     │
│              │       │              │       │   (MSW)      │
│ • Layout     │       │ • Hooks      │       │              │
│ • Tasks      │       │ • Stores     │       │ • Handlers   │
│ • Focus      │       │ • Schemas    │       │ • Fixtures   │
│ • Notes      │       │ • Utils      │       │              │
│ • UI         │       │ • Config     │       │              │
└──────────────┘       └──────────────┘       └──────────────┘
```

## Component Architecture

### Component Categories

#### 1. Page Components (`src/app/`)
- Route-based components using Next.js App Router
- Handle URL parameters and search params
- Minimal logic, delegate to feature components

#### 2. Layout Components (`src/components/layout/`)
- Structural components (Sidebar, Header, DashboardLayout)
- Handle navigation and global UI state
- Persistent across route changes

#### 3. Feature Components (`src/components/tasks/`, `focus/`, `notes/`)
- Domain-specific components
- Compose UI components
- Connect to data hooks

#### 4. UI Components (`src/components/ui/`)
- Generic, reusable primitives
- Built on Radix UI
- Styled with Tailwind CSS
- No business logic

### Component Composition Pattern

```tsx
// Page Component
function TasksPage() {
  return (
    <div>
      <TaskList /> {/* Feature Component */}
    </div>
  );
}

// Feature Component
function TaskList() {
  const { data: tasks } = useTasks();
  return (
    <div>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} /> {/* Feature Component */}
      ))}
    </div>
  );
}

// Feature Component using UI Components
function TaskCard({ task }: { task: Task }) {
  return (
    <div>
      <Badge variant={task.priority}>{task.priority}</Badge> {/* UI Component */}
      <Button onClick={...}>Complete</Button> {/* UI Component */}
    </div>
  );
}
```

## State Management Architecture

### Zustand Stores (Client UI State)

Located in `src/lib/stores/`:

| Store | Responsibility | Persistence |
|-------|----------------|-------------|
| `useSidebarStore` | Sidebar collapsed state | localStorage |
| `useFocusModeStore` | Focus mode active state, selected task | Memory |
| `useNewTaskModalStore` | Modal visibility, edit mode | Memory |
| `useTaskDetailModalStore` | Detail modal visibility, task ID | Memory |
| `useCommandPaletteStore` | Command palette visibility | Memory |
| `useNotificationStore` | Notifications list | Memory |
| `usePendingCompletionsStore` | Tasks pending completion | Memory |

**Store Pattern:**

```typescript
// src/lib/stores/sidebar.store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isCollapsed: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      isCollapsed: false,
      toggle: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
    }),
    { name: 'sidebar-storage' }
  )
);
```

### React Query (Server State)

Located in `src/lib/hooks/`:

**Query Key Structure:**

```typescript
// Hierarchical query keys for cache management
const queryKeys = {
  tasks: {
    all: ['tasks'] as const,
    lists: () => [...queryKeys.tasks.all, 'list'] as const,
    list: (filters: TaskFilters) => [...queryKeys.tasks.lists(), filters] as const,
    details: () => [...queryKeys.tasks.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.tasks.details(), id] as const,
  },
  // Similar pattern for subtasks, notes, reminders, achievements
};
```

**Hook Pattern:**

```typescript
// src/lib/hooks/use-tasks.ts
export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: queryKeys.tasks.list(filters),
    queryFn: () => fetchTasks(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.lists() });
    },
  });
}
```

## Data Flow Patterns

### Optimistic Updates

```typescript
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateTask,
    onMutate: async (newTask) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: queryKeys.tasks.detail(newTask.id) });

      // Snapshot current data
      const previousTask = queryClient.getQueryData(queryKeys.tasks.detail(newTask.id));

      // Optimistically update
      queryClient.setQueryData(queryKeys.tasks.detail(newTask.id), newTask);

      return { previousTask };
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      queryClient.setQueryData(
        queryKeys.tasks.detail(newTask.id),
        context?.previousTask
      );
    },
    onSettled: (data, error, variables) => {
      // Invalidate to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(variables.id) });
    },
  });
}
```

### Pending Completions Pattern

```typescript
// Batch completion with user confirmation
interface PendingCompletionsState {
  tasks: Map<string, { task: Task; hasIncompleteSubtasks: boolean }>;
  add: (task: Task, hasIncompleteSubtasks: boolean) => void;
  remove: (taskId: string) => void;
  clear: () => void;
  save: () => Promise<void>;
}
```

## Validation Architecture

### Zod Schema Structure

Located in `src/lib/schemas/`:

```typescript
// src/lib/schemas/task.schema.ts
import { z } from 'zod';

export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  priority: z.enum(['high', 'medium', 'low']).default('medium'),
  completed: z.boolean().default(false),
  dueDate: z.string().datetime().optional(),
  tags: z.array(z.string().max(30)).max(20).default([]),
  recurrence: RecurrenceSchema.optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type Task = z.infer<typeof TaskSchema>;

// Create/Update schemas with required fields
export const CreateTaskSchema = TaskSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const UpdateTaskSchema = CreateTaskSchema.partial();
```

### Validation Points

1. **Client-side**: Form submission validation
2. **API Layer**: MSW handler request validation
3. **Runtime**: Response data validation

## UI Component Architecture

### Radix UI Integration

```
┌────────────────────────────────────────────────┐
│              Application Layer                  │
│  (TaskCard, NewTaskModal, etc.)                │
└────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────┐
│           Custom UI Components                  │
│  (src/components/ui/)                          │
│  - Button, Dialog, Select, Popover, etc.       │
│  - Styled with Tailwind CSS                    │
│  - Enhanced with class-variance-authority      │
└────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────┐
│              Radix UI Primitives               │
│  @radix-ui/react-dialog                        │
│  @radix-ui/react-select                        │
│  @radix-ui/react-popover                       │
│  @radix-ui/react-toast                         │
│  etc.                                          │
└────────────────────────────────────────────────┘
```

### Button Variants (CVA Pattern)

```typescript
// src/components/ui/button.tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border border-gray-300 bg-transparent hover:bg-gray-100',
        ghost: 'hover:bg-gray-100',
        danger: 'bg-red-600 text-white hover:bg-red-700',
        success: 'bg-green-600 text-white hover:bg-green-700',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);
```

## API Mocking Architecture (MSW)

### Handler Structure

```typescript
// src/mocks/handlers/tasks.handler.ts
import { http, HttpResponse } from 'msw';

export const taskHandlers = [
  // GET /api/tasks
  http.get('/api/tasks', async ({ request }) => {
    const url = new URL(request.url);
    const filters = parseFilters(url.searchParams);

    // Simulate latency
    await delay(100 + Math.random() * 400);

    const tasks = filterTasks(fixtures.tasks, filters);
    return HttpResponse.json(tasks);
  }),

  // POST /api/tasks
  http.post('/api/tasks', async ({ request }) => {
    const body = await request.json();

    // Validate with Zod
    const result = CreateTaskSchema.safeParse(body);
    if (!result.success) {
      return HttpResponse.json(
        { error: result.error.format() },
        { status: 400 }
      );
    }

    const newTask = createTask(result.data);
    fixtures.tasks.push(newTask);

    return HttpResponse.json(newTask, { status: 201 });
  }),

  // PATCH, DELETE handlers...
];
```

### Fixture Data

```typescript
// src/mocks/data/tasks.fixture.ts
export const taskFixtures: Task[] = [
  {
    id: '1',
    title: 'Complete project documentation',
    description: 'Write comprehensive docs for the API',
    priority: 'high',
    completed: false,
    dueDate: '2024-01-20T10:00:00Z',
    tags: ['documentation', 'urgent'],
    createdAt: '2024-01-15T09:00:00Z',
    updatedAt: '2024-01-15T09:00:00Z',
  },
  // More fixtures...
];
```

## Configuration Architecture

### Centralized Limits

```typescript
// src/lib/config/limits.ts
export const LIMITS = {
  // Task limits
  MAX_TASKS: 50,
  MAX_TASK_TITLE: 200,
  MAX_TASK_DESCRIPTION: 1000,
  MAX_TAGS_PER_TASK: 20,
  MAX_TAG_LENGTH: 30,

  // Subtask limits
  MAX_SUBTASKS_PER_TASK: 10,
  MAX_SUBTASK_TITLE: 100,

  // Reminder limits
  MAX_REMINDERS_PER_TASK: 5,

  // Note limits
  NOTE_SOFT_LIMIT: 750,
  NOTE_HARD_LIMIT: 1000,

  // Focus mode limits
  MIN_FOCUS_DURATION: 1,
  MAX_FOCUS_DURATION: 720, // 12 hours
} as const;
```

### Navigation Configuration

```typescript
// src/lib/config/navigation.tsx
export const navigationItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboardIcon,
    onboardingId: 'nav-dashboard',
  },
  {
    title: 'Tasks',
    href: '/dashboard/tasks',
    icon: CheckSquareIcon,
    onboardingId: 'nav-tasks',
    children: [
      { title: 'All Tasks', href: '/dashboard/tasks' },
      { title: 'Completed', href: '/dashboard/tasks/completed' },
    ],
  },
  // More items...
];
```

## Animation Architecture

### Framer Motion Patterns

```typescript
// src/lib/utils/animations.ts
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.2 },
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const blobAnimation = {
  animate: {
    scale: [1, 1.1, 1],
    opacity: [0.3, 0.5, 0.3],
  },
  transition: {
    duration: 8,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};
```

### Reduced Motion Support

```typescript
// src/lib/hooks/use-reduced-motion.ts
export function useReducedMotion() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return reducedMotion;
}
```

## Error Handling Architecture

### Error Boundaries

```typescript
// src/app/dashboard/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

### Toast Notifications

```typescript
// Usage in components
const { toast } = useToast();

try {
  await createTask(data);
  toast({ title: 'Task created successfully' });
} catch (error) {
  toast({
    title: 'Failed to create task',
    description: error.message,
    variant: 'destructive',
  });
}
```

## Performance Optimizations

### React Query Caching

- **Stale Time**: 5 minutes for list queries
- **Cache Time**: 30 minutes default
- **Automatic Refetch**: On window focus, reconnect

### Code Splitting

- Dynamic imports for modals and heavy components
- Route-based code splitting via Next.js
- Lazy loading of non-critical UI components

### Bundle Optimization

- Tree shaking via Next.js
- CSS purging via Tailwind
- Image optimization via Next.js Image component
