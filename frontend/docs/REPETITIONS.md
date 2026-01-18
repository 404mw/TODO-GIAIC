# Code Repetitions and Refactoring Opportunities

This document identifies repeated code patterns, duplications, and areas that should be consolidated for better maintainability.

## High Priority Repetitions

### 1. Inline SVG Icons
**Severity:** High
**Impact:** Bundle size, maintenance burden

**Problem:** SVG icons are defined inline throughout the codebase rather than using a centralized icon system.

**Examples Found:**

```typescript
// TaskCard.tsx - Checkmark icon (lines 206-217)
<svg className="h-full w-full text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
</svg>

// Same icon in SubTaskList, NewTaskModal, etc.
```

```typescript
// Search icon repeated in Sidebar.tsx, Header.tsx, CommandPalette.tsx
<svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
</svg>
```

**Locations:**
- [TaskCard.tsx](frontend/src/components/tasks/TaskCard.tsx) - 8+ inline SVGs
- [Sidebar.tsx](frontend/src/components/layout/Sidebar.tsx) - 3+ inline SVGs
- [NewTaskModal.tsx](frontend/src/components/tasks/NewTaskModal.tsx) - 2+ inline SVGs
- [Header.tsx](frontend/src/components/layout/Header.tsx)
- Multiple page components

**Recommended Solution:**
```typescript
// Create: frontend/src/components/ui/Icons.tsx
export const Icons = {
  Check: (props) => <svg {...props}>...</svg>,
  Search: (props) => <svg {...props}>...</svg>,
  Calendar: (props) => <svg {...props}>...</svg>,
  Clock: (props) => <svg {...props}>...</svg>,
  // etc.
}

// Or use a library like lucide-react
import { Check, Search, Calendar } from 'lucide-react'
```

---

### 2. Priority Color Mappings
**Severity:** High
**Impact:** Consistency, maintenance

**Problem:** Priority colors are defined in multiple components independently.

**Duplicated In:**
- [TaskCard.tsx:63-73](frontend/src/components/tasks/TaskCard.tsx#L63-L73)
- TaskList.tsx
- Dashboard page
- Completed tasks page

**Current Pattern:**
```typescript
// TaskCard.tsx
const priorityColors = {
  high: 'border-l-4 border-l-red-500',
  medium: 'border-l-4 border-l-yellow-500',
  low: 'border-l-4 border-l-green-500',
}

const priorityBadgeColors = {
  high: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300',
  low: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300',
}
```

**Recommended Solution:**
```typescript
// Create: frontend/src/lib/config/colors.ts
export const PRIORITY_COLORS = {
  high: {
    border: 'border-l-4 border-l-red-500',
    badge: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
    text: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-950/50',
  },
  medium: { /* ... */ },
  low: { /* ... */ },
} as const

// Or create a PriorityBadge component
export function PriorityBadge({ priority }: { priority: Priority }) {
  return <span className={PRIORITY_COLORS[priority].badge}>{priority}</span>
}
```

---

### 3. Date Formatting Functions
**Severity:** Medium
**Impact:** Consistency, localization

**Problem:** Date formatting logic is repeated in multiple components.

**Duplicated Patterns:**

```typescript
// TaskCard.tsx:97-106 - getDueDateColor function
const getDueDateColor = (dueDate: string | null) => {
  if (!dueDate) return 'text-gray-500'
  const due = new Date(dueDate)
  const now = new Date()
  const diffHours = (due.getTime() - now.getTime()) / (1000 * 60 * 60)
  // ...
}

// completed/page.tsx:23-48 - Similar date comparison logic
function startOfDay(date: Date): Date { /* ... */ }
function getCompletionCategory(completedAt: string | undefined, updatedAt: string): string { /* ... */ }
```

**Locations:**
- TaskCard.tsx
- completed/page.tsx
- Dashboard page
- Various other components

**Recommended Solution:**
```typescript
// Consolidate in: frontend/src/lib/utils/date.ts
export function getDueDateUrgency(dueDate: string | null): 'overdue' | 'urgent' | 'normal' | 'none'
export function getDueDateColor(dueDate: string | null): string
export function getCompletionCategory(date: string): 'today' | 'yesterday' | 'lastWeek' | 'older'
export function formatRelativeDate(date: string): string
export function startOfDay(date: Date): Date
```

---

### 4. Loading State Skeletons
**Severity:** Medium
**Impact:** Consistency, UX

**Problem:** Loading skeleton patterns are implemented inline in multiple pages.

**Duplicated Pattern:**
```typescript
// Repeated in multiple pages
{isLoading && (
  <div className="space-y-3">
    {[...Array(3)].map((_, i) => (
      <div
        key={i}
        className="h-32 animate-pulse rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-800 dark:bg-gray-900"
      />
    ))}
  </div>
)}
```

**Locations:**
- completed/page.tsx:181-189
- Tasks page
- Dashboard page
- Notes page

**Recommended Solution:**
```typescript
// Create: frontend/src/components/ui/TaskListSkeleton.tsx
export function TaskListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-32 animate-pulse rounded-lg border ..." />
      ))}
    </div>
  )
}
```

---

### 5. Empty State Components
**Severity:** Medium
**Impact:** Consistency, UX

**Problem:** Empty states are implemented inline with similar patterns but different content.

**Pattern Found:**
```typescript
// Similar structure in multiple pages
<div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center ...">
  <svg className="mx-auto h-16 w-16 text-gray-400">...</svg>
  <h3 className="mt-4 text-lg font-medium ...">Title</h3>
  <p className="mt-2 text-sm ...">Description</p>
</div>
```

**Locations:**
- completed/page.tsx:216-238
- Tasks page
- Notes page
- Focus page

**Recommended Solution:**
```typescript
// Create: frontend/src/components/ui/EmptyState.tsx
interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-lg border-2 border-dashed ...">
      {icon}
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}
```

---

### 6. Error State Components
**Severity:** Medium
**Impact:** Consistency, error handling

**Problem:** Error display UI is repeated across pages.

**Pattern Found:**
```typescript
// completed/page.tsx:193-213
{error && (
  <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center ...">
    <svg className="mx-auto h-12 w-12 text-red-600 ...">...</svg>
    <h3>Failed to load tasks</h3>
    <p>{error.message}</p>
  </div>
)}
```

**Recommended Solution:**
```typescript
// Create: frontend/src/components/ui/ErrorState.tsx
export function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry
}: ErrorStateProps) { /* ... */ }
```

---

### 7. Class Name Array Pattern
**Severity:** Low
**Impact:** Code style, readability

**Problem:** The same array-filter-join pattern for conditional classes is repeated everywhere.

**Pattern:**
```typescript
// Repeated 50+ times across components
className={[
  'base-class',
  condition && 'conditional-class',
  anotherCondition ? 'class-a' : 'class-b',
]
  .filter(Boolean)
  .join(' ')}
```

**Locations:** Nearly every component file.

**Recommendation:** This is somewhat acceptable but could use the `cn` utility consistently:

```typescript
// Already have cn utility - use it consistently
import { cn } from '@/lib/utils/cn'

className={cn(
  'base-class',
  condition && 'conditional-class',
  anotherCondition ? 'class-a' : 'class-b'
)}
```

---

### 8. Toast Notification Patterns
**Severity:** Low
**Impact:** Consistency

**Problem:** Toast calls follow similar patterns with repeated structure.

**Pattern:**
```typescript
// Success pattern repeated many times
toast({
  title: 'Task created',
  description: 'Your task has been added',
  variant: 'success',
})

// Error pattern repeated many times
toast({
  title: 'Error',
  description: 'Failed to create task',
  variant: 'error',
})
```

**Recommendation:**
```typescript
// Create helper functions
export const toastSuccess = (title: string, description?: string) =>
  toast({ title, description, variant: 'success' })

export const toastError = (title: string, description?: string) =>
  toast({ title, description, variant: 'error' })

// Usage
toastSuccess('Task created', 'Your task has been added')
toastError('Error', 'Failed to create task')
```

---

### 9. Form Input Wrapper Patterns
**Severity:** Low
**Impact:** Consistency, DRY

**Problem:** Label + Input + Helper text pattern is repeated in forms.

**Pattern:**
```typescript
// Repeated for each form field
<div>
  <Label htmlFor="field-id">Field Name</Label>
  <Input
    id="field-id"
    value={value}
    onChange={(e) => setValue(e.target.value)}
    className="mt-1"
  />
  <p className="mt-1 text-xs text-gray-500">{helperText}</p>
</div>
```

**Recommendation:**
```typescript
// Create: FormField component
interface FormFieldProps {
  label: string
  htmlFor: string
  helperText?: string
  error?: string
  children: React.ReactNode
}

export function FormField({ label, htmlFor, helperText, error, children }: FormFieldProps) {
  return (
    <div>
      <Label htmlFor={htmlFor}>{label}</Label>
      <div className="mt-1">{children}</div>
      {helperText && <p className="mt-1 text-xs text-gray-500">{helperText}</p>}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
}
```

---

### 10. Subtask Display Logic
**Severity:** Low
**Impact:** Consistency

**Problem:** Subtask count and completion calculation repeated.

**Pattern:**
```typescript
// TaskCard.tsx
const completedSubtasks = subtasks.filter((st: SubTask) => st.completed).length
const subtaskCompletionPercent = subtasks.length > 0
  ? Math.round((completedSubtasks / subtasks.length) * 100)
  : 0

// Similar logic in other components
```

**Recommendation:**
```typescript
// Add to utils
export function getSubtaskProgress(subtasks: SubTask[]) {
  const completed = subtasks.filter(st => st.completed).length
  const total = subtasks.length
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0
  return { completed, total, percent }
}
```

---

## Summary: Refactoring Priorities

### Immediate (Quick Wins)
1. Create Icons component or integrate icon library
2. Centralize priority color configurations
3. Use `cn()` utility consistently

### Short-term
4. Create reusable EmptyState component
5. Create reusable ErrorState component
6. Create TaskListSkeleton component
7. Consolidate date utility functions

### Medium-term
8. Create FormField wrapper component
9. Add toast helper functions
10. Extract subtask progress calculation

## Benefits of Refactoring

| Area | Current Issues | After Refactoring |
|------|----------------|-------------------|
| **Bundle Size** | SVGs duplicated ~20x | Single definition, tree-shakable |
| **Maintenance** | Change colors in 10 places | Change in 1 config file |
| **Consistency** | Slight style variations | Guaranteed uniformity |
| **Developer Experience** | Copy-paste prone | Import and use |
| **Testing** | Test same logic in multiple places | Test once |

## Migration Strategy

1. **Phase 1:** Create new shared components/utilities without removing old code
2. **Phase 2:** Update components one-by-one to use shared code
3. **Phase 3:** Remove duplicate implementations
4. **Phase 4:** Add tests for shared utilities

## Notes

- Always maintain backwards compatibility during migration
- Add JSDoc comments to new shared utilities
- Consider creating a Storybook for UI components
- Document the new patterns in a style guide
