# Known Bugs and Issues

This document tracks known bugs, potential issues, and areas that need attention in the Perpetua Flow frontend application.

## Critical Issues

### 1. No Backend Integration
**Severity:** Critical
**Location:** Entire application
**Description:** The application currently runs entirely on MSW (Mock Service Worker) mocks. There is no real backend API implementation.

**Impact:**
- Data is not persisted across browser sessions (unless localStorage is used)
- Multi-device sync is not possible
- User authentication is not implemented
- Data could be lost on browser clear

**Required Action:** Implement real backend API and authentication system.

---

### 2. No Authentication System
**Severity:** Critical
**Location:** All `/dashboard` routes
**Description:** Dashboard routes are not protected by authentication. Anyone can access them directly.

**Current State:**
- No login/logout functionality
- No user session management
- Profile data is mocked

**Required Action:** Implement authentication flow (OAuth, JWT, etc.) and route protection.

---

## High Priority Issues

### 3. Mobile Sidebar UX Issues
**Severity:** High
**Location:** [Sidebar.tsx](frontend/src/components/layout/Sidebar.tsx)
**Description:** On mobile devices, the sidebar overlay behavior can be inconsistent.

**Issues:**
- Sidebar may remain open when navigating between pages
- Tap outside doesn't always close on some mobile browsers
- No swipe gesture support for open/close

**Workaround:** Users must tap the hamburger icon to close.

---

### 4. Completed Tasks Page - Double DashboardLayout
**Severity:** High
**Location:** [completed/page.tsx:131](frontend/src/app/dashboard/tasks/completed/page.tsx#L131)
**Description:** The completed tasks page wraps content in `<DashboardLayout>` but dashboard pages already have the layout applied via the dashboard layout file. This could cause nested layouts.

```tsx
// Line 130-131: Potential issue
return (
  <DashboardLayout>
```

**Impact:** Could cause duplicate sidebars, headers, or CSS conflicts.

**Required Action:** Remove `DashboardLayout` wrapper from individual page components if already wrapped by `app/dashboard/layout.tsx`.

---

### 5. Task Completion State Inconsistency
**Severity:** High
**Location:** [TaskCard.tsx](frontend/src/components/tasks/TaskCard.tsx), `usePendingCompletionsStore`
**Description:** The pending completions pattern can lead to confusing state where a task appears complete locally but isn't saved to the server.

**Scenario:**
1. User marks task for completion
2. User navigates away without saving
3. Task state is unclear (pending but not saved)

**Impact:** Users may lose track of which tasks are actually completed.

**Suggestion:** Auto-save after a timeout, or warn when navigating away with unsaved changes.

---

## Medium Priority Issues

### 6. Date/Time Handling Issues
**Severity:** Medium
**Location:** [NewTaskModal.tsx:100-106](frontend/src/components/tasks/NewTaskModal.tsx#L100-L106)
**Description:** Timezone handling for due dates can be inconsistent.

```typescript
// Current implementation:
const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
setDueDate(localDate.toISOString().slice(0, 16))
```

**Issues:**
- Due dates may shift when viewed in different timezones
- UTC vs local time confusion
- `datetime-local` input format depends on browser locale

**Impact:** Users may see incorrect due dates, especially when traveling or collaborating across timezones.

---

### 7. Subtasks Not Loaded in Edit Mode
**Severity:** Medium
**Location:** [NewTaskModal.tsx:107-109](frontend/src/components/tasks/NewTaskModal.tsx#L107-L109)
**Description:** When editing a task, existing subtasks are not loaded into the modal.

```typescript
// Note: subtasks are managed separately via API for existing tasks
// Edit mode will use the existing subtask management in TaskDetailView
```

**Impact:** Users cannot edit subtasks from the edit modal; must use TaskDetailView.

**User Expectation:** Edit modal should show all task data including subtasks.

---

### 8. Memory Leak in Click Outside Handler
**Severity:** Medium
**Location:** [TaskCard.tsx:48-61](frontend/src/components/tasks/TaskCard.tsx#L48-L61)
**Description:** Event listener cleanup may not run if component unmounts while expanded.

```typescript
useEffect(() => {
  if (isExpanded) {
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }
}, [isExpanded])
```

**Issue:** If `isExpanded` is true and component unmounts, cleanup runs. But if state changes before unmount, there could be edge cases.

**Impact:** Minor memory leak, potential console errors.

---

### 9. Recurrence Rule Validation
**Severity:** Medium
**Location:** Recurrence components
**Description:** RRULE strings from user input may not be fully validated before submission.

**Issues:**
- Invalid RRULE strings could break date calculations
- Edge cases like "February 30th" patterns not handled
- No server-side validation (MSW only)

---

### 10. Focus Mode Timer Drift
**Severity:** Medium
**Location:** FocusTimer component
**Description:** JavaScript timers (`setInterval`) can drift over long sessions due to browser throttling.

**Impact:**
- Timer may be slightly inaccurate for long sessions
- Background tabs may pause the timer
- Browser sleep can affect timing

**Suggestion:** Use `requestAnimationFrame` with timestamp comparison for accuracy.

---

## Low Priority Issues

### 11. Accessibility: Missing Focus Indicators
**Severity:** Low
**Location:** Various UI components
**Description:** Some interactive elements lack visible focus indicators for keyboard navigation.

**Affected Areas:**
- Tag remove buttons
- Subtask checkboxes
- Sort direction toggle

---

### 12. Toast Notification Stacking
**Severity:** Low
**Location:** Toaster component
**Description:** Multiple rapid toasts may stack awkwardly or overflow the viewport.

**Impact:** Information overload, poor UX during bulk operations.

---

### 13. Search Not Debounced
**Severity:** Low
**Location:** Command palette search
**Description:** Search input doesn't debounce, potentially causing excessive filtering operations.

**Impact:** Performance could degrade with large task lists.

---

### 14. SVG Icons Inline
**Severity:** Low
**Location:** Throughout components
**Description:** Many SVG icons are defined inline rather than using a centralized icon system.

**Impact:**
- Increased bundle size
- Harder to maintain consistency
- Difficult to update icons globally

**Suggestion:** Use an icon library (Lucide, Heroicons) or create an Icon component.

---

## Performance Concerns

### 15. TaskCard Re-renders
**Location:** [TaskCard.tsx](frontend/src/components/tasks/TaskCard.tsx)
**Description:** TaskCard subscribes to multiple stores and fetches subtasks, causing re-renders when unrelated state changes.

**Optimization Opportunities:**
- Memoize with `React.memo`
- Use selective store subscriptions
- Prefetch subtasks at list level

---

### 16. Large Task Lists
**Description:** No virtualization for task lists. Rendering 100+ tasks could cause lag.

**Affected Pages:**
- Tasks list page
- Completed tasks page

**Suggestion:** Implement `react-window` or `@tanstack/virtual` for large lists.

---

## Browser Compatibility

### 17. datetime-local Input
**Description:** The `datetime-local` input type has inconsistent behavior across browsers.

**Known Issues:**
- Safari on iOS: Limited support for min/max attributes
- Firefox: Date picker style differs significantly
- Mobile: Keyboard vs native picker varies

---

### 18. CSS Container Queries
**Description:** If using container queries for responsive design, older browsers may not support them.

**Fallback:** Ensure traditional media queries are available.

---

## Security Considerations

### 19. No Input Sanitization Display
**Description:** User input (task titles, descriptions) is rendered directly. While React escapes HTML, rich text or markdown could pose issues.

**Review:** Ensure no `dangerouslySetInnerHTML` is used with user content.

---

### 20. Local Storage Exposure
**Description:** Sidebar state and potentially sensitive data stored in localStorage.

**Risk:** XSS attacks could read localStorage.

**Mitigation:** Don't store sensitive data client-side; rely on HTTP-only cookies for auth tokens.

---

## Testing Gaps

### 21. Missing Test Coverage
**Description:** Limited unit and integration tests observed.

**Priority Test Areas:**
- Task CRUD operations
- Pending completions flow
- Focus mode timer
- Recurrence calculations
- Date formatting utilities

---

## MSW Mock Limitations

### 22. Mock Data Resets
**Description:** MSW handlers use in-memory fixtures that reset on page reload.

**Impact:**
- Changes don't persist
- Testing workflows require re-creating data
- Cannot test with realistic data volumes

---

## Documentation Needed

### 23. Component Prop Documentation
**Description:** Some components lack PropTypes or JSDoc comments explaining expected props.

**Priority:**
- TaskCard
- NewTaskModal
- FocusTimer

---

## Reporting New Issues

When reporting new bugs, please include:

1. **Severity:** Critical / High / Medium / Low
2. **Location:** File path and line numbers if applicable
3. **Steps to Reproduce:** Clear reproduction steps
4. **Expected Behavior:** What should happen
5. **Actual Behavior:** What actually happens
6. **Browser/Device:** Environment information
7. **Screenshots:** If applicable
