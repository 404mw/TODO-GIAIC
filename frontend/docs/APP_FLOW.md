# Application Flow

This document describes the user flows, navigation patterns, and data flow within the Perpetua Flow application.

## Route Structure

### Public Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `page.tsx` | Landing page with hero, features, CTA |
| `/about` | `(public)/about/page.tsx` | About page |
| `/contact` | `(public)/contact/page.tsx` | Contact page |
| `/pricing` | `(public)/pricing/page.tsx` | Pricing information |

### Dashboard Routes (Protected)

| Route | Component | Description |
|-------|-----------|-------------|
| `/dashboard` | `dashboard/page.tsx` | Main dashboard with stats and quick views |
| `/dashboard/tasks` | `dashboard/tasks/page.tsx` | All tasks with filtering/sorting |
| `/dashboard/tasks/completed` | `dashboard/tasks/completed/page.tsx` | Completed/archived tasks |
| `/dashboard/tasks/[id]` | `dashboard/tasks/[id]/page.tsx` | Single task detail view |
| `/dashboard/tasks/[id]/edit` | `dashboard/tasks/[id]/edit/page.tsx` | Task edit page |
| `/dashboard/tasks/new` | `dashboard/tasks/new/page.tsx` | Dedicated new task page |
| `/dashboard/focus` | `dashboard/focus/page.tsx` | Focus mode session |
| `/dashboard/notes` | `dashboard/notes/page.tsx` | Notes management |
| `/dashboard/achievements` | `dashboard/achievements/page.tsx` | Streak and achievements |
| `/dashboard/settings` | `dashboard/settings/page.tsx` | User preferences |
| `/dashboard/settings/hidden-tasks` | `dashboard/settings/hidden-tasks/page.tsx` | View/manage hidden tasks |

## Layout Hierarchy

```
RootLayout (app/layout.tsx)
├── Providers (React Query, MSW)
├── WebVitals Reporter
├── Reminders Components
├── Toaster
│
├── (public) Group Layout
│   └── Public Pages
│
└── dashboard Group Layout (DashboardLayout)
    ├── Sidebar (collapsible)
    ├── Header (fixed top)
    ├── Main Content Area
    ├── PendingCompletionsBar (fixed bottom)
    ├── NewTaskModal (overlay)
    └── TaskDetailModal (overlay)
```

## User Flows

### 1. Landing to Dashboard Flow

```
Landing Page
    │
    ├─→ Sign Up CTA → [Future: Auth Flow] → Dashboard
    │
    └─→ Navigation → About / Contact / Pricing
```

### 2. Task Creation Flow

```
User clicks "New Task" (Header button or Cmd+K)
    │
    ▼
NewTaskModal opens
    │
    ├─→ Fill required fields:
    │   • Title (required, 1-200 chars)
    │   • Description (optional, max 1000 chars)
    │   • Priority (optional, default: medium)
    │   • Due Date (optional)
    │   • Tags (optional, max 20 tags)
    │
    ├─→ Add Subtasks (optional, max 10)
    │   • Title
    │   • Estimated duration
    │
    ├─→ Configure Recurrence (optional)
    │   • Pattern (daily, weekly, monthly, custom)
    │   • End date or count
    │
    └─→ Submit
        │
        ├─→ Validation (Zod schema)
        │   ├─→ Pass → API POST /api/tasks
        │   └─→ Fail → Show errors
        │
        └─→ Success
            ├─→ Cache invalidation
            ├─→ Toast notification
            └─→ Modal closes
```

### 3. Task Completion Flow

```
User clicks checkbox on TaskCard
    │
    ▼
Task added to Pending Completions Store
    │
    ├─→ Has incomplete subtasks?
    │   └─→ Yes → Warning indicator shown
    │
    └─→ PendingCompletionsBar appears (bottom)
        │
        ├─→ "Save" button
        │   ├─→ API PATCH /api/tasks/:id (completed: true)
        │   ├─→ If recurring → Generate next instance
        │   ├─→ Cache invalidation
        │   ├─→ Toast: "Task completed!"
        │   └─→ Bar disappears
        │
        └─→ "Discard" button
            ├─→ Clear pending completions
            └─→ Bar disappears
```

### 4. Focus Mode Flow

```
User navigates to /dashboard/focus
    │
    └─→ OR clicks "Focus" button on TaskCard
        │
        ▼
TaskSelector (if no task pre-selected)
    │
    ▼
Select task → Start focus session
    │
    ▼
Focus Mode Active:
├─→ Sidebar hidden
├─→ Timer displayed with progress ring
├─→ Keyboard shortcuts active:
│   • Space → Pause/Resume
│   • Esc → Exit focus mode
│
├─→ Timer running...
│   │
│   └─→ Timer completes
│       ├─→ Audio notification
│       ├─→ Browser notification (if permitted)
│       ├─→ Task marked complete
│       └─→ Return to normal view
│
└─→ User exits early (Esc)
    └─→ Confirm dialog → Exit
```

### 5. Task Filtering Flow

```
Tasks Page (/dashboard/tasks)
    │
    ├─→ Filter Tabs:
    │   • All → Show all active tasks
    │   • Active → Incomplete tasks only
    │   • High Priority → priority === 'high'
    │   • Today → due date is today
    │
    ├─→ Sort Options:
    │   • Due Date (default)
    │   • Priority
    │   • Created Date
    │   • Title (alphabetical)
    │
    └─→ Search:
        └─→ Filter by title/description/tags
```

### 6. Subtask Management Flow

```
TaskCard expanded or TaskDetailModal
    │
    ▼
SubTaskList displayed
    │
    ├─→ Toggle subtask completion
    │   └─→ API PATCH /api/subtasks/:id
    │
    ├─→ Add new subtask (AddSubTaskForm)
    │   └─→ API POST /api/subtasks
    │
    └─→ Edit subtask
        └─→ API PATCH /api/subtasks/:id
```

### 7. Notes to Task Conversion Flow

```
Notes Page (/dashboard/notes)
    │
    ▼
User clicks "Convert to Task" on NoteCard
    │
    ▼
ConvertNoteDrawer opens
    │
    ├─→ Pre-filled with note content
    ├─→ Add task-specific fields (priority, due date)
    │
    └─→ Submit
        ├─→ API POST /api/tasks (from note content)
        ├─→ Option: Delete original note
        └─→ Navigate to tasks page
```

## Data Flow Architecture

### State Management Layers

```
┌─────────────────────────────────────────────────────────┐
│                    React Components                      │
│  (Pages, Layout Components, Feature Components)         │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│   Zustand Stores    │       │   React Query Hooks     │
│   (UI State)        │       │   (Server State)        │
├─────────────────────┤       ├─────────────────────────┤
│ • useSidebarStore   │       │ • useTasks              │
│ • useFocusModeStore │       │ • useTask               │
│ • useNewTaskModal   │       │ • useCreateTask         │
│ • useTaskDetailModal│       │ • useUpdateTask         │
│ • usePendingComps   │       │ • useNotes              │
│ • useCommandPalette │       │ • useReminders          │
│ • useNotifications  │       │ • useAchievements       │
└─────────────────────┘       └─────────────────────────┘
           │                               │
           │                               ▼
           │                  ┌─────────────────────────┐
           │                  │      API Layer          │
           │                  │   (MSW in development)  │
           │                  ├─────────────────────────┤
           │                  │ GET/POST/PATCH/DELETE   │
           │                  │ /api/tasks              │
           │                  │ /api/subtasks           │
           │                  │ /api/notes              │
           │                  │ /api/reminders          │
           │                  └─────────────────────────┘
           │                               │
           └───────────────┬───────────────┘
                           ▼
                  ┌─────────────────┐
                  │  localStorage   │
                  │  (persistence)  │
                  └─────────────────┘
```

### React Query Data Flow

```
Component Mount
    │
    ▼
useQuery Hook (e.g., useTasks)
    │
    ├─→ Check Cache
    │   ├─→ Fresh data → Return cached
    │   └─→ Stale/Missing → Fetch
    │
    ▼
API Request
    │
    ▼
Response → Update Cache → Re-render Component
```

### Mutation Flow

```
User Action (e.g., create task)
    │
    ▼
useMutation Hook (e.g., useCreateTask)
    │
    ├─→ Optimistic Update (optional)
    │   └─→ Immediately update cache
    │
    ▼
API Request
    │
    ├─→ Success
    │   ├─→ Confirm optimistic update
    │   └─→ Invalidate related queries
    │
    └─→ Error
        ├─→ Rollback optimistic update
        └─→ Show error toast
```

## Modal Management

### NewTaskModal

- **Trigger**: Header "New Task" button, Command Palette, dedicated page
- **Store**: `useNewTaskModalStore`
- **State**: `isOpen`, `editingTask` (for edit mode)
- **Behavior**: Opens in create mode or edit mode with pre-filled data

### TaskDetailModal

- **Trigger**: Click on TaskCard (when not in edit mode)
- **Store**: `useTaskDetailModalStore`
- **State**: `isOpen`, `taskId`
- **Behavior**: Shows full task details with edit/delete actions

### Command Palette

- **Trigger**: Cmd/Ctrl + K keyboard shortcut
- **Store**: `useCommandPaletteStore`
- **State**: `isOpen`
- **Actions**: Quick navigation, create task, search

## Keyboard Shortcuts

| Shortcut | Context | Action |
|----------|---------|--------|
| `Cmd/Ctrl + K` | Global | Open Command Palette |
| `Space` | Focus Mode | Pause/Resume timer |
| `Esc` | Focus Mode | Exit focus mode |
| `Esc` | Modal Open | Close modal |

## Error Handling Flow

```
API Error
    │
    ├─→ Network Error
    │   └─→ Toast: "Network error. Please try again."
    │
    ├─→ Validation Error (400)
    │   └─→ Toast: Specific validation message
    │
    ├─→ Not Found (404)
    │   └─→ Toast: "Resource not found"
    │
    └─→ Server Error (500)
        └─→ Toast: "Something went wrong. Please try again."
```

## Navigation Patterns

### Primary Navigation (Sidebar)

1. Dashboard
2. Tasks (with sub-items: All, Completed)
3. Notes
4. Focus
5. Achievements
6. Settings

### Secondary Navigation

- Header: Page title, New Task button, Notifications
- Command Palette: Quick actions and search
- Breadcrumbs: On nested pages (e.g., task detail)

### Mobile Navigation

- Hamburger menu toggles sidebar
- Sidebar overlays content on mobile
- Touch-friendly tap targets
