# Phase 0: Research & Technology Decisions

**Feature**: Perpetua Flow - Frontend Application
**Date**: 2026-01-08 (Updated)
**Status**: Complete (Updated with Reminders & Recurrence)

## Research Areas

This document consolidates all technology research and architectural decisions for the Perpetua Flow frontend application.

---

## 1. Next.js App Router Architecture

### Decision
Use Next.js 14+ App Router with client components for interactive features.

### Rationale
- **App Router**: Native support for route groups `(public)` and `(dashboard)` allows clean separation of authenticated vs. public routes without URL pollution
- **Client Components**: Required for Framer Motion animations, Zustand state, and all interactive UI (FR-052, FR-053)
- **Server Components**: Not heavily utilized in this frontend-only app; layout and metadata only
- **Route-based Navigation**: FR-034 requires URL-addressable routes for all dashboard sections

### Alternatives Considered
- **Pages Router**: Rejected - lacks route groups, less ergonomic for app-like navigation patterns
- **Create React App**: Rejected - no built-in routing, larger bundle size, no SSR/SSG benefits
- **Vite + React Router**: Rejected - requires more boilerplate for routing, metadata management

### Implementation Notes
- Route structure: `app/(public)/page.tsx` for landing, `app/(dashboard)/tasks/page.tsx` for tasks view
- All dashboard routes share layout with sidebar component
- Use `"use client"` directive for components requiring state, effects, or animations

---

## 2. State Management Strategy

### Decision
**Dual-state approach**: TanStack Query for server-like state (MSW), Zustand for client UI state.

### Rationale
- **TanStack Query**:
  - Built-in caching, invalidation, optimistic updates
  - Simulates realistic server state behavior with MSW (FR-057, FR-058)
  - Supports loading states, error handling, retry logic
  - Ephemeral optimistic updates (FR-059) align with "server wins" philosophy
- **Zustand**:
  - Lightweight for client state (sidebar open/closed, theme tweaks, Focus Mode flags)
  - localStorage middleware for persistence (FR-060)
  - No prop drilling for global UI state

### Alternatives Considered
- **Redux Toolkit**: Rejected - too heavyweight for client state needs, unnecessary boilerplate
- **Context API**: Rejected - performance issues with frequent updates, no built-in persistence
- **Zustand alone**: Rejected - doesn't provide server state caching/invalidation patterns
- **TanStack Query alone**: Rejected - awkward for non-server state (sidebar preferences, UI flags)

### Implementation Notes
- Create stores: `lib/stores/uiStore.ts` (Zustand), `lib/queries/useTasks.ts` (TanStack Query)
- Zustand middleware: `persist` for sidebar and theme, plain store for Focus Mode
- TanStack Query: Default staleTime 5 minutes, gcTime 10 minutes, retry 2 times

---

## 3. Mock Service Worker (MSW) Integration

### Decision
Use MSW 2.x for simulating backend API during development.

### Rationale
- **Realistic Network Behavior**: Simulates latency (100-500ms per FR-SC-014), loading states, errors
- **Offline Development**: No backend dependency during frontend development (Assumption 9)
- **Contract Compatibility**: MSW handlers mirror expected real API contracts (RESTful JSON)
- **Testing**: Same handlers used in Jest/Playwright tests for consistency

### Alternatives Considered
- **JSON Server**: Rejected - requires separate process, less flexible error simulation
- **Mirage.js**: Rejected - smaller ecosystem, less active maintenance
- **Hard-coded fixtures**: Rejected - no loading states, unrealistic UX testing

### Implementation Notes
- Setup: `mocks/browser.ts` (dev), `mocks/server.ts` (tests), `mocks/handlers/tasks.ts`
- Handlers: RESTful endpoints (`GET /api/tasks`, `POST /api/tasks`, `PATCH /api/tasks/:id`, etc.)
- Simulate network latency: `await delay(randomBetween(100, 500))`
- Error simulation: 10% random failure rate for edge case testing

---

## 4. Zod Schema Validation

### Decision
Centralize all data contracts in `/schemas` directory using Zod.

### Rationale
- **Type Safety**: Runtime validation + TypeScript inference (FR-062)
- **Single Source of Truth**: Schemas shared by TanStack Query, MSW handlers, components
- **UI Exclusion**: UI-only flags (`isEditing`, `isStreaming`) excluded from schemas (FR-063)
- **Future Backend Alignment**: Zod schemas map 1:1 to backend Pydantic schemas (Constitution VII.1)

### Alternatives Considered
- **Yup**: Rejected - less TypeScript-first, weaker type inference
- **io-ts**: Rejected - more verbose syntax, steeper learning curve
- **AJV**: Rejected - JSON Schema-based, less ergonomic for TypeScript

### Implementation Notes
- Schema files: `schemas/task.schema.ts`, `schemas/note.schema.ts`, etc.
- Export both schema and TypeScript type: `export const TaskSchema = z.object({...}); export type Task = z.infer<typeof TaskSchema>`
- Validation: `TaskSchema.parse(data)` in MSW handlers, `TaskSchema.safeParse(data)` in forms

---

## 5. Design System: Tailwind + Radix UI + Framer Motion

### Decision
**Tailwind CSS** for styling, **Radix UI** for headless primitives, **Framer Motion** for animations.

### Rationale
- **Tailwind CSS**:
  - Utility-first aligns with component-based architecture
  - Dark mode via `class` strategy (FR-049)
  - Custom glassmorphism utilities (FR-050)
  - WCAG AA contrast enforcement via custom color palette (FR-051)
- **Radix UI**:
  - Headless components (Popover for profile, future Dialog/Dropdown)
  - Built-in accessibility (ARIA labels, keyboard nav)
  - Unstyled = full control over futuristic design
- **Framer Motion**:
  - Declarative animations for entry/exit, route transitions (FR-052, FR-053)
  - `prefers-reduced-motion` support via `useReducedMotion` hook (FR-054)
  - Duration ≤200ms enforced via config

### Alternatives Considered
- **CSS Modules**: Rejected - more verbose, harder to maintain consistency
- **Styled Components**: Rejected - runtime CSS-in-JS performance overhead
- **Headless UI**: Rejected - less comprehensive than Radix, smaller ecosystem
- **React Spring**: Rejected - more complex API, overkill for simple transitions
- **CSS Transitions**: Rejected - less declarative, harder to choreograph complex animations

### Implementation Notes
- Tailwind config: Custom dark palette, glassmorphism plugin, WCAG AA color validation
- Radix components: Install `@radix-ui/react-popover`, future: Dialog, DropdownMenu
- Framer Motion: `motion.div` for all animated components, `AnimatePresence` for route transitions
- Reduced motion: `const prefersReducedMotion = useReducedMotion(); const animate = prefersReducedMotion ? {} : {...}`

---

## 6. Typography: Inter vs. Geist Sans

### Decision
**Geist Sans** for primary typography, **Geist Mono** for monospace (duration, status).

### Rationale
- **Geist Sans**: Modern, clean, designed for dark UIs, excellent readability
- **Geist Mono**: Matches Geist Sans aesthetically, clear monospace distinction
- **Next.js Integration**: Built-in `next/font` optimization (preloading, subsetting)
- **WCAG Compliance**: Both fonts maintain legibility at WCAG AA contrast ratios

### Alternatives Considered
- **Inter**: Rejected - slightly less optimized for dark mode, though still excellent
- **System Fonts**: Rejected - inconsistent cross-platform experience
- **Custom Font**: Rejected - unnecessary complexity, licensing overhead

### Implementation Notes
- Font setup: `app/layout.tsx` with `next/font/google` for Geist Sans and Geist Mono
- CSS variables: `--font-sans`, `--font-mono` for consistent usage
- Tailwind: `fontFamily: { sans: 'var(--font-sans)', mono: 'var(--font-mono)' }`

---

## 7. Focus Mode Implementation

### Decision
**Zustand store** for Focus Mode state, **CSS isolation** for UI hiding, **Web Timers API** for countdown.

### Rationale
- **Zustand Store**: Non-persisted client state (FR-010 to FR-016)
  - `focusModeActive: boolean`, `activeTaskId: string | null`, `remainingSeconds: number`
- **CSS Isolation**: Conditionally hide sidebar and other tasks via `display: none` when `focusModeActive === true`
- **Timers**: `setInterval` for countdown, `Notification API` for audio/visual alert (FR-016)
- **Popovers Disabled**: Check `focusModeActive` in Radix Popover `disabled` prop (FR-015)

### Alternatives Considered
- **Route-based**: Rejected - breaks URL addressability requirement (FR-034)
- **localStorage**: Rejected - Focus Mode should reset on refresh (non-persistent)
- **Web Workers**: Rejected - overkill for simple countdown timer

### Implementation Notes
- Store: `lib/stores/focusModeStore.ts` with actions `activateFocusMode`, `exitFocusMode`, `tick`
- Countdown: `useEffect` in Focus Mode component starts interval, clears on exit/unmount
- Alerts: Browser `Notification.requestPermission()`, fallback to modal if denied

---

## 8. AI Features (Disabled Until Backend)

### Decision
**Disabled UI state** for all AI features (Magic Sub-tasks, Quick Notes, Voice-to-Text, Convert Note → Task).

### Rationale
- **No Backend**: AI API endpoints don't exist yet (Assumption 4, 5)
- **Constitution Compliance**: AI actions require logging, opt-in, undo (Constitution IV, V)
- **User Clarity**: Buttons disabled with inline tooltip explanation (FR-UX philosophy section 9)
- **Future-Ready**: UI components built but non-functional; backend integration requires minimal UI changes

### Alternatives Considered
- **Fake AI**: Rejected - misleading to users, doesn't test real integration
- **Delay Implementation**: Rejected - UI design decisions affect architecture now
- **Client-side AI**: Rejected - unrealistic for complex NLP tasks, privacy concerns

### Implementation Notes
- Components: Build `MagicSubtasksButton`, `VoiceNoteRecorder`, `ConvertNoteDrawer` with `disabled={true}`
- Tooltips: "AI features available after backend integration" on hover
- Environment flag: `NEXT_PUBLIC_AI_ENABLED=false` in `.env.local` for future toggle

---

## 9. Onboarding: Driver.js Integration

### Decision
**Driver.js** for interactive walkthrough (FR-044 to FR-048).

### Rationale
- **Lightweight**: Small bundle size (~6KB gzipped)
- **Customizable**: Full control over styling to match dark futuristic aesthetic
- **Programmatic Control**: Easy to trigger on first login and from Settings
- **Step Highlighting**: Built-in element highlighting with spotlight effect

### Alternatives Considered
- **Intro.js**: Rejected - heavier bundle, less modern styling options
- **Shepherd.js**: Rejected - requires Popper.js dependency, more complex API
- **Custom Implementation**: Rejected - unnecessary reinvention, accessibility concerns

### Implementation Notes
- Setup: `lib/onboarding/steps.ts` defines walkthrough steps
- Trigger: Check `userProfile.firstLogin` flag, auto-start Driver on `true`
- Replay: Settings page button calls `driver.drive(steps)`
- Tutorial Task: Create on first login completion, flag `deletable: false`, `archivable: true`

---

## 10. Global Search Implementation

### Decision
**Client-side Fuse.js** for fuzzy search across tasks, notes, workflows, achievements.

### Rationale
- **Performance**: <1s search for 10,000 items (FR-SC-005)
- **Fuzzy Matching**: Handles typos, partial matches better than exact string matching
- **Lightweight**: ~2KB gzipped
- **Offline**: No backend dependency (aligns with MSW simulation)

### Alternatives Considered
- **Backend Search**: Rejected - no backend in this phase
- **Native `Array.filter()`**: Rejected - no fuzzy matching, slower for large datasets
- **Lunr.js**: Rejected - heavier bundle, more complex setup for simple use case

### Implementation Notes
- Setup: `lib/search/searchIndex.ts` initializes Fuse with options `threshold: 0.3`, `keys: ['title', 'description', 'tags']`
- Hook: `useGlobalSearch(query)` returns grouped results `{ tasks: [...], notes: [...], workflows: [...] }`
- UI: Sidebar search input, results popover with sections

---

## 11. Limits Configuration

### Decision
**Centralized `config/limits.ts`** file for all enforced limits (FR-Limits table).

### Rationale
- **Single Source of Truth**: No magic numbers in components
- **Easy Adjustment**: Update one file to change all limits
- **Type Safety**: Export as `const` object with TypeScript types
- **Constitutional Compliance**: Simplicity over scale (Constitution X.1)

### Alternatives Considered
- **Environment Variables**: Rejected - limits are app behavior, not deployment config
- **Database**: Rejected - no backend, overkill for static limits
- **Per-Component Constants**: Rejected - duplication, inconsistency risk

### Implementation Notes
- File: `config/limits.ts`
  ```typescript
  export const LIMITS = {
    MAX_TASKS: 50,
    MAX_SUBTASKS_PER_TASK: 10,
    MAX_NOTE_CHARS_SOFT: 750,
    MAX_NOTE_CHARS_HARD: 1000,
    MAX_VOICE_RECORDING_SECONDS: 60,
    MAX_FOCUS_MODE_HOURS: 3,
    MAX_ACTIVITY_LOG_EVENTS: 100,
    MAX_AI_SUBTASKS_PER_GENERATION: 20,
  } as const;
  ```
- Usage: `import { LIMITS } from '@/config/limits'; if (tasks.length >= LIMITS.MAX_TASKS) { ... }`

---

## 12. Testing Strategy

### Decision
**Jest + React Testing Library** for unit/integration, **Playwright** for E2E, **MSW** for API mocking.

### Rationale
- **Jest + RTL**: Industry standard for React component testing, excellent Next.js support
- **Playwright**: Modern E2E tool, cross-browser, faster than Cypress
- **MSW**: Same handlers in tests and dev environment (DRY principle)
- **TDD Mandate**: Constitution VIII requires tests before implementation

### Alternatives Considered
- **Vitest**: Rejected - less mature Next.js integration (though promising)
- **Cypress**: Rejected - slower than Playwright, heavier setup
- **Testing Library alone**: Rejected - need E2E for full user flows (Focus Mode, onboarding)

### Implementation Notes
- Jest config: `jest.config.js` with `next/jest` transformer
- RTL: Test components with user interactions, not implementation details
- Playwright: Test critical paths (onboarding walkthrough, Focus Mode activation)
- MSW: `beforeAll(() => server.listen())`, `afterEach(() => server.resetHandlers())`

---

## 13. Accessibility Strategy

### Decision
**Semantic HTML** + **Radix UI** + **WCAG AA contrast** + **prefers-reduced-motion** support.

### Rationale
- **Semantic HTML**: `<nav>`, `<main>`, `<article>` for screen readers (Assumption 11)
- **Radix UI**: Built-in ARIA labels, keyboard navigation, focus management
- **Color Contrast**: Custom Tailwind palette validated against WCAG AA (4.5:1 for normal text)
- **Motion**: `useReducedMotion()` hook disables animations (FR-054)

### Alternatives Considered
- **Manual ARIA**: Rejected - error-prone, Radix provides out-of-box
- **WCAG AAA**: Rejected - not required by spec, harder to achieve with glassmorphism
- **Full keyboard-only testing**: Deferred - basic keyboard nav implemented, comprehensive testing in Phase 7

### Implementation Notes
- Contrast checker: Use `polypane` or `axe DevTools` during development
- Motion hook: `const shouldReduceMotion = useReducedMotion(); const variants = shouldReduceMotion ? {} : fullVariants;`
- Landmarks: Ensure every page has `<main>`, sidebar in `<nav>`, footer in `<footer>`

---

## 14. Environment Variables

### Decision
**`.env.local`** for development secrets, **`.env.example`** for documentation, **runtime validation** on startup.

### Rationale
- **Security**: `.env.local` in `.gitignore`, never committed (Constitution IX.1, IX.3)
- **Documentation**: `.env.example` shows required vars without secrets
- **Validation**: Startup script checks required vars exist, blocks launch if missing (Constitution IX.2)
- **AI Limits**: All AI rate limits configurable via env (Constitution IX.4)

### Alternatives Considered
- **Hardcoded Secrets**: Rejected - constitution violation
- **Runtime Checks Only**: Rejected - late failure, poor DX
- **No Validation**: Rejected - constitution mandate (IX.2)

### Implementation Notes
- Variables:
  ```
  NEXT_PUBLIC_AI_ENABLED=false
  AI_API_KEY=<secret>
  AI_RATE_LIMIT_PER_MINUTE=10
  AI_QUOTA_DAILY=1000
  ```
- Validation: `lib/env.ts` with Zod schema, import in `app/layout.tsx`

---

## 15. Reminders & Notifications System

### Decision

**Dual notification system**: Browser notifications + in-app toast, triggered by Service Worker polling MSW state every 60 seconds.

### Rationale

- **User Requirements**: User clarified preference for "Both browser + in-app" delivery
- **Maximum Visibility**: Ensures reminders seen regardless of browser focus state
- **Graceful Degradation**: Falls back to in-app toast if browser permission denied
- **Relative Timing**: Reminders calculated relative to task due dates (e.g., "15 minutes before")
- **Service Worker**: Enables background notification delivery when browser minimized

### Alternatives Considered

- **Browser-only**: Rejected - user might miss if browser minimized
- **In-app-only**: Rejected - user might miss if on different tab
- **Silent reminder list**: Rejected - requires manual checking, defeats purpose
- **Absolute time**: Rejected - less intuitive for deadline-based tasks
- **Dual system**: **CHOSEN** - best UX, handles all focus states

### Implementation

```typescript
// Reminder schema with relative timing
const ReminderSchema = z.object({
  id: z.string().uuid(),
  taskId: z.string().uuid(),
  title: z.string(),
  timing: z.object({
    type: z.literal("relative_to_due_date"),
    offsetMinutes: z.number().int(), // Negative = before, positive = after
    // Examples: -15 (15 min before), -1440 (1 day before)
  }),
  deliveryMethod: z.enum(["browser", "in_app", "both"]).default("both"),
  enabled: z.boolean().default(true),
  createdAt: z.date(),
});

// Calculate trigger time
function calculateReminderTriggerTime(reminder: Reminder, task: Task): Date | null {
  if (!task.dueDate) return null; // Task must have due date

  const dueTime = task.dueDate.getTime();
  const offsetMs = reminder.timing.offsetMinutes * 60 * 1000;
  return new Date(dueTime + offsetMs);
}

// Service Worker checks every 60 seconds for due reminders
// File: public/service-worker.js
setInterval(async () => {
  const now = new Date();
  const reminders = await fetchRemindersFromMSW(); // Query MSW /api/reminders
  const tasks = await fetchTasksFromMSW(); // Query MSW /api/tasks

  const dueReminders = reminders.filter(r => {
    const task = tasks.find(t => t.id === r.taskId);
    if (!task) return false;

    const triggerTime = calculateReminderTriggerTime(r, task);
    return triggerTime && triggerTime <= now && r.enabled;
  });

  dueReminders.forEach(async (reminder) => {
    const task = tasks.find(t => t.id === reminder.taskId);

    // 1. Browser notification (if permission granted)
    if (reminder.deliveryMethod === "browser" || reminder.deliveryMethod === "both") {
      if (Notification.permission === "granted") {
        const notification = new Notification(reminder.title, {
          body: task.title,
          icon: "/icon-192.png",
          tag: reminder.id, // Prevent duplicates
          requireInteraction: true,
        });

        notification.onclick = () => {
          clients.openWindow(`/dashboard/tasks/${task.id}`);
        };
      }
    }

    // 2. In-app toast (postMessage to all clients)
    if (reminder.deliveryMethod === "in_app" || reminder.deliveryMethod === "both") {
      const allClients = await clients.matchAll();
      allClients.forEach(client => {
        client.postMessage({
          type: "REMINDER_DUE",
          reminder,
          task,
        });
      });
    }

    // Mark reminder as delivered (POST /api/reminders/:id/delivered)
    await fetch(`/api/reminders/${reminder.id}/delivered`, { method: "POST" });
  });
}, 60000); // Check every 60 seconds
```

```typescript
// Client-side: Listen for Service Worker messages
// File: app/layout.tsx
useEffect(() => {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (event.data.type === "REMINDER_DUE") {
        const { reminder, task } = event.data;

        toast({
          title: reminder.title,
          description: task.title,
          action: (
            <Button onClick={() => router.push(`/dashboard/tasks/${task.id}`)}>
              View Task
            </Button>
          ),
          duration: 10000, // 10 seconds
        });
      }
    });
  }
}, []);
```

### Dependencies

- Web Notifications API (browser native)
- Service Worker API (for background polling)
- MSW handlers: `GET /api/reminders`, `POST /api/reminders/:id/delivered`
- Radix UI Toast component (for in-app notifications)

### Testing Strategy

**Unit Tests**:

- `calculateReminderTriggerTime` function with various offsets (-15, -1440, -10080)
- ReminderForm component validation (requires task due date)
- ReminderList component rendering

**Integration Tests**:

- Create reminder → Service Worker detects due time → browser notification + toast appear
- Reminder with denied browser permission → only toast appears
- Reminder for task without due date → disabled state with error message

---

## 16. Recurring Tasks System

### Decision

**RRule library (RFC 5545)** for custom interval recurrence, **completion-based instance generation**.

### Rationale

- **User Requirements**: User clarified need for "Custom interval" patterns ("every 2 weeks on Tuesday")
- **RFC 5545 Standard**: RRule follows iCalendar standard (industry-proven)
- **Flexibility**: Supports simple (daily) to complex (first Monday of month) patterns
- **Human-Readable**: RRule generates descriptions like "Every 2 weeks on Monday"
- **Completion-Based**: User clarified preference for "On completion" instance generation
- **Type Safety**: Excellent TypeScript support via `rrule` package

### Alternatives Considered

- **Simple enum (daily/weekly/monthly)**: Rejected - insufficient for custom intervals
- **Cron syntax**: Rejected - too technical for users, no human-readable output
- **Custom parser**: Rejected - reinventing RFC 5545 standard, high maintenance
- **Scheduled generation**: Rejected - requires background scheduler, complex edge cases
- **Manual generation**: Rejected - defeats automation purpose
- **RRule + Completion-based**: **CHOSEN** - best balance of power and simplicity

### Implementation Details

```typescript
// Recurrence schema
const RecurrenceSchema = z.object({
  enabled: z.boolean().default(false),
  rule: z.string(), // RRule string (e.g., "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU")
  timezone: z.string().default("UTC"),
  instanceGenerationMode: z.enum(["on_completion"]).default("on_completion"),
  nextScheduledDate: z.date().optional(), // For UI display only
  humanReadable: z.string(), // Generated by RRule.toText()
});

// Task schema includes recurrence
const TaskSchema = z.object({
  // ... existing fields
  recurrence: RecurrenceSchema.optional(),
  isRecurringInstance: z.boolean().default(false), // True if generated from recurrence
  parentRecurringTaskId: z.string().uuid().optional(), // Link to template task
});

// Generate next instance on task completion
function onTaskComplete(task: Task): Task | null {
  if (!task.recurrence?.enabled) return null;

  // Parse RRule
  const rrule = RRule.fromString(task.recurrence.rule);

  // Get next occurrence after completion date
  const now = new Date();
  const nextOccurrence = rrule.after(now, true); // inclusive=true

  if (!nextOccurrence) {
    // Recurrence has ended (e.g., "FREQ=DAILY;COUNT=10" after 10 instances)
    return null;
  }

  // Create new task instance
  return {
    ...task,
    id: generateUUID(), // New UUID for instance
    completedAt: null, // Reset completion
    createdAt: now,
    dueDate: nextOccurrence, // Due date = next occurrence
    isRecurringInstance: true,
    parentRecurringTaskId: task.id,
    recurrence: {
      ...task.recurrence,
      nextScheduledDate: nextOccurrence,
    },
  };
}

// MSW handler for task completion
rest.patch('/api/tasks/:id', async (req, res, ctx) => {
  const { id } = req.params;
  const body = await req.json();

  const task = tasks.find(t => t.id === id);
  if (!task) return res(ctx.status(404));

  // Update task
  Object.assign(task, body);

  // Generate next instance if recurring
  if (body.completedAt && task.recurrence?.enabled) {
    const nextInstance = onTaskComplete(task);
    if (nextInstance) {
      tasks.push(nextInstance);
      return res(ctx.json({ task, nextInstance })); // Return both
    }
  }

  return res(ctx.json({ task }));
});
```

### Recurrence UI Component

```typescript
// RecurrenceEditor component
export function RecurrenceEditor({ task }: { task: Task }) {
  const [frequency, setFrequency] = useState<"DAILY" | "WEEKLY" | "MONTHLY">("WEEKLY");
  const [interval, setInterval] = useState(1);
  const [byweekday, setByweekday] = useState<number[]>([]); // [RRule.MO.weekday, RRule.WE.weekday]

  const rruleString = useMemo(() => {
    const parts = [`FREQ=${frequency}`, `INTERVAL=${interval}`];

    if (frequency === "WEEKLY" && byweekday.length > 0) {
      const days = byweekday.map(d => WEEKDAY_ABBR[d]).join(",");
      parts.push(`BYDAY=${days}`);
    }

    return parts.join(";");
  }, [frequency, interval, byweekday]);

  const humanReadable = useMemo(() => {
    const rrule = RRule.fromString(rruleString);
    return rrule.toText(); // "Every 2 weeks on Monday and Wednesday"
  }, [rruleString]);

  return (
    <div>
      <Select value={frequency} onValueChange={setFrequency}>
        <option value="DAILY">Daily</option>
        <option value="WEEKLY">Weekly</option>
        <option value="MONTHLY">Monthly</option>
      </Select>

      <Input
        type="number"
        value={interval}
        onChange={(e) => setInterval(parseInt(e.target.value))}
        min={1}
        label="Every"
      />

      {frequency === "WEEKLY" && (
        <WeekdayPicker
          selected={byweekday}
          onChange={setByweekday}
        />
      )}

      <p className="text-sm text-muted">{humanReadable}</p>

      <RecurrencePreview rrule={rruleString} count={5} />
    </div>
  );
}

// RecurrencePreview component
export function RecurrencePreview({ rrule, count }: { rrule: string; count: number }) {
  const occurrences = useMemo(() => {
    const rule = RRule.fromString(rrule);
    return rule.all((date, i) => i < count); // Get first 5 occurrences
  }, [rrule, count]);

  return (
    <div>
      <h4>Next {count} occurrences:</h4>
      <ul>
        {occurrences.map((date, i) => (
          <li key={i}>{format(date, "PPP")}</li> // "Jan 10, 2026"
        ))}
      </ul>
    </div>
  );
}
```

### Recurrence Dependencies

- `rrule` package (v2.7+): RFC 5545 implementation
- `date-fns`: Date formatting for preview

### Recurrence Testing Strategy

**Unit Tests**:

- `onTaskComplete` generates correct next instance for various RRule patterns
- RRule parsing and validation (invalid patterns rejected)
- Recurrence ending after COUNT reached (returns null)
- Next occurrence calculation with timezones

**Integration Tests**:

- Complete recurring task → next instance created with new UUID
- Complete non-recurring task → no instance generated
- Recurring task with UNTIL date → stops generating after end date
- User edits recurrence rule → preview updates immediately

**Edge Cases**:

- Task with recurrence but no due date → recurrence disabled with warning
- Recurrence every Feb 30 (invalid date) → error handling
- Completion-based generation offline → next instance created on next online session

---

## 17. Deployment Considerations (Future)

### Decision
**Deferred to backend integration phase** - no deployment in frontend-only scope.

### Rationale
- **MSW Limitation**: MSW browser.ts only works in development, not production
- **No Backend**: Can't deploy functioning app without real API
- **Out of Scope**: Deployment is backend integration concern (Assumption 9)

### Future Options
- **Vercel**: Native Next.js support, edge functions, preview deployments
- **Netlify**: Comparable features, good DX
- **Self-hosted**: Docker + Nginx if backend is also self-hosted

### Implementation Notes
- Placeholder: Add `next.config.js` with `output: 'standalone'` for future containerization
- Environment: Production env vars will replace `.env.local` secrets

---

## Summary of Unknowns Resolved

All "NEEDS CLARIFICATION" items from Technical Context are now resolved:

1. ✅ **Language/Version**: TypeScript 5.x + Next.js 15+
2. ✅ **Primary Dependencies**: TanStack Query, Zustand, Zod, Framer Motion, Radix UI, MSW, Driver.js, RRule
3. ✅ **Storage**: MSW for API simulation, localStorage for sidebar/theme only (NO IndexedDB)
4. ✅ **Testing**: Jest + RTL for components, TDD Red-Green-Refactor workflow
5. ✅ **Target Platform**: Modern browsers, desktop/tablet (1024px+)
6. ✅ **Performance Goals**: Specific targets defined in Technical Context
7. ✅ **Constraints**: Dark mode only, WCAG AA, reduced motion support, task/subtask limits
8. ✅ **Scale/Scope**: Single-user, <5,000 tasks, 8 routes, ~15 components (updated to include reminders/recurrence)
9. ✅ **Reminders**: Dual system (browser + in-app), relative to due date, Service Worker polling every 60s
10. ✅ **Recurrence**: RRule library (RFC 5545), custom intervals, completion-based instance generation

---

## Next Steps

Phase 0 research is complete. Proceed to **Phase 1: Design & Contracts**.

**Phase 1 Deliverables**:

1. `data-model.md` - Entity definitions and relationships (Tasks, Sub-tasks, Notes, Reminders, Recurrence, Achievements, User)
2. `contracts/` - API endpoint specifications (OpenAPI/JSON schema) including reminder and recurrence endpoints
3. `quickstart.md` - Developer setup guide with Service Worker and RRule setup
4. Update agent context with technology stack (including `rrule`, Service Worker API)
