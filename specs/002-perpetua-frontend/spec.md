# Feature Specification: Perpetua Flow - Frontend Application

**Feature Branch**: `002-perpetua-frontend`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "Perpetua Flow - Frontend-only task management app with futuristic minimal design, AI automation, focus mode, and Achievements System for gamification"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage Tasks (Priority: P1)

A user wants to capture, organize, and track their tasks with a clean, distraction-free interface. They need to create tasks with relevant metadata (title, description, tags, priority, estimated duration), organize them with sub-tasks, and track progress visually.

**Why this priority**: Core task management is the foundation of the entire application. Without this, no other features can function. This represents the minimum viable product.

**Independent Test**: Can be fully tested by creating a task, adding sub-tasks, marking items complete, and verifying progress calculation. Delivers immediate value as a basic task tracker.

**Acceptance Scenarios**:

1. **Given** the user is on the dashboard tasks view, **When** they click "New Task" and fill in title "Finish report", description "Q4 metrics", priority "High", and duration "2h", **Then** the task appears in the task list with all metadata visible
2. **Given** a task exists, **When** the user adds 3 sub-tasks and marks 1 complete, **Then** the progress bar shows 33% completion
3. **Given** multiple tasks exist with different priorities, **When** the user views the task list, **Then** tasks are organized by priority (High, Medium, Low)
4. **Given** a task has no sub-tasks, **When** the user views the task, **Then** no progress bar is displayed
5. **Given** a task exists, **When** the user marks it as hidden, **Then** the task disappears from all default views and can only be accessed via Settings → Tasks → Hidden

---

### User Story 2 - Focus Mode for Deep Work (Priority: P2)

A user needs to eliminate distractions and concentrate on a single task. They activate Focus Mode on a specific task, which hides everything else and shows only that task with a countdown timer based on estimated duration.

**Why this priority**: Differentiation feature that provides significant productivity value. Can be implemented independently after basic task management exists.

**Independent Test**: Can be tested by selecting any task, activating Focus Mode, verifying UI changes (sidebar hidden, other tasks hidden, countdown visible), and confirming exit conditions work properly.

**Acceptance Scenarios**:

1. **Given** a task with 30-minute duration exists, **When** the user clicks the target icon on that task, **Then** Focus Mode activates, sidebar disappears, all other tasks are hidden, and a 30-minute countdown timer appears
2. **Given** Focus Mode is active, **When** the user manually exits, **Then** the normal dashboard view returns with sidebar and all tasks visible
3. **Given** Focus Mode is active, **When** the user marks the task complete, **Then** Focus Mode automatically exits and achievement feedback appears
4. **Given** Focus Mode is active, **When** the countdown reaches zero, **Then** an audio/visual alert notifies the user
5. **Given** Focus Mode is active, **When** the user attempts to open profile popover or other distractions, **Then** those interactions are disabled

---

### User Story 3 - AI-Powered Quick Notes & Task Conversion (Priority: P2)

A user wants to quickly capture ideas via text or voice, then optionally convert them into structured tasks using AI. They can record voice notes with visual feedback, then use AI to parse the note into task fields automatically.

**Why this priority**: Unique AI integration feature that reduces friction in task creation. Can be built independently once task creation exists.

**Independent Test**: Can be tested by creating a quick note via voice or text, then converting it to a task using the AI parser. Verifies voice recording, AI parsing, and task creation integration.

**Acceptance Scenarios**:

1. **Given** the user is on the notes page, **When** they click the voice-to-text button and speak "Buy groceries tomorrow morning", **Then** a red recording indicator appears with animated waveform, and the text is transcribed into the note
2. **Given** a note exists with content "Finish project proposal by Friday, high priority", **When** the user clicks "Convert to Task", **Then** a right-side drawer opens with AI-parsed fields: title "Finish project proposal", description includes full note text, priority set to "High", reminder set for Friday
3. **Given** the AI conversion drawer is open, **When** the user reviews and confirms the parsed fields, **Then** a new task is created and the note is archived
4. **Given** the user is recording voice, **When** recording exceeds 5 minutes, **Then** recording automatically stops and the content is transcribed

---

### User Story 4 - AI-Generated Sub-tasks (Priority: P3)

A user has a complex task and wants AI assistance to break it down into actionable sub-tasks. They use the "Magic Sub-tasks" feature which analyzes the task title and description to generate relevant sub-tasks with streaming output.

**Why this priority**: Advanced AI feature that enhances task breakdown. Provides value but isn't essential for core functionality.

**Independent Test**: Can be tested by creating a task with a detailed description, clicking "Generate Sub-tasks", and verifying the AI streams suggestions that can be accepted or rejected.

**Acceptance Scenarios**:

1. **Given** a task exists with title "Plan company retreat" and description "3-day offsite for 50 people in mountain location", **When** the user clicks "Generate Sub-tasks" in the task detail view, **Then** AI streams sub-task suggestions in real-time (e.g., "Research mountain venues", "Create budget breakdown", "Survey team for dates", "Book accommodations")
2. **Given** sub-tasks are being generated, **When** streaming is in progress, **Then** the Generate button is disabled and shows a loading state
3. **Given** sub-tasks already exist for a task, **When** the user clicks "Generate Sub-tasks", **Then** a confirmation prompt warns that existing sub-tasks will be overwritten
4. **Given** AI generation fails mid-stream, **When** the error occurs, **Then** partial output is preserved and an error message is shown

---

### User Story 5 - Achievements & Motivation Tracking (Priority: P3)

A user wants to stay motivated by seeing their accomplishment history and earning achievements. The system tracks fixed metrics (High Priority Slays, Consistency Streaks, Completion Ratio) and displays them with animated visualizations.

**Why this priority**: Gamification feature that enhances long-term engagement. Can be added after core task management is stable.

**Independent Test**: Can be tested by completing various tasks over time and verifying metrics update correctly, achievements unlock at milestones, and visualizations display properly.

**Acceptance Scenarios**:

1. **Given** the user completes 10 high-priority tasks, **When** they navigate to the achievements page, **Then** the "High Priority Slays" metric shows 10 and triggers subtle shimmer animation
2. **Given** the user completes at least one task per day for 7 consecutive days, **When** they view achievements, **Then** the "Consistency Streak" metric shows 7 days
3. **Given** the user creates 20 tasks and completes 15, **When** they view the completion ratio, **Then** it displays 75% with an animated progress visualization
4. **Given** the user reaches a milestone (e.g., 50 completed tasks), **When** the milestone triggers, **Then** a rare confetti animation appears briefly

---

### User Story 6 - New User Onboarding (Priority: P3)

A first-time user needs guidance to understand the app's key features. An interactive walkthrough automatically starts on first login, teaching them about the sidebar, note creation, task conversion, and Focus Mode.

**Why this priority**: Improves first-time user experience but not critical for existing users. Can be implemented after all core features are stable.

**Independent Test**: Can be tested by creating a new user account and verifying the walkthrough starts automatically, guides through all steps, and can be replayed from Settings.

**Acceptance Scenarios**:

1. **Given** a user logs in for the first time, **When** the dashboard loads, **Then** an interactive walkthrough automatically starts highlighting the sidebar
2. **Given** the walkthrough is active, **When** the user completes the "Create Quick Note" step, **Then** the walkthrough advances to the "Convert Note to Task" step
3. **Given** the walkthrough is active, **When** the user activates Focus Mode, **Then** the walkthrough completes and a tutorial task "Master Perpetua" appears in their task list
4. **Given** the user has completed the walkthrough, **When** they navigate to Settings and click "Replay Tutorial", **Then** the walkthrough restarts from the beginning

---

### User Story 7 - Global Search Across Entities (Priority: P2)

A user wants to quickly find tasks, notes, or achievements without navigating through different pages. They use the global search bar in the sidebar to search across all entities with results scoped by type.

**Why this priority**: Quality-of-life feature that significantly improves navigation efficiency. Should be implemented after multiple entity types exist.

**Independent Test**: Can be tested by creating tasks, notes, and achievements, then searching for keywords and verifying results are correctly categorized and linked.

**Acceptance Scenarios**:

1. **Given** multiple tasks and notes exist containing the word "budget", **When** the user types "budget" in the global search bar, **Then** results appear grouped by type (Tasks, Notes, Archived Tasks) with matching items highlighted
2. **Given** search results are displayed, **When** the user clicks a task result, **Then** they navigate to that task's detail view
3. **Given** the user searches for a term with no matches, **When** the search completes, **Then** a "No results found" message appears

---

### User Story 8 - Dashboard Layout & Navigation (Priority: P1)

A user needs intuitive navigation between different sections of the app (Tasks, Notes, Workflows, Achievements, Activity) with a consistent layout featuring a collapsible sidebar and route-based main content area.

**Why this priority**: Foundation for all other features. Must exist before implementing any content-specific functionality.

**Independent Test**: Can be tested by navigating between all routes, collapsing/expanding the sidebar, and verifying state persists across sessions.

**Acceptance Scenarios**:

1. **Given** the user is on the dashboard, **When** they click "Tasks" in the sidebar, **Then** the main view shows `/dashboard/tasks` content and the Tasks menu item is highlighted
2. **Given** the sidebar is open, **When** the user clicks the collapse button, **Then** the sidebar minimizes to icons only and this preference is saved to localStorage
3. **Given** the user has collapsed the sidebar, **When** they reload the page, **Then** the sidebar remains collapsed
4. **Given** Focus Mode is active, **When** the user attempts to interact with the sidebar, **Then** the sidebar is hidden and unavailable

---

### Edge Cases

- What happens when a user tries to create a sub-task without a parent task? System prevents orphaned sub-tasks and shows an error message.
- How does the system handle voice recording if microphone permissions are denied? Display a clear error message with instructions to enable permissions.
- What happens if AI sub-task generation takes longer than 30 seconds? Show a timeout error and preserve any partial output generated so far.
- How does the system handle AI rate limits or quota exhaustion? Display clear error message, temporarily disable affected AI features (Magic Sub-tasks, Note-to-Task conversion), and automatically retry after configurable cooldown period (default 15 minutes).
- How does the system handle conflicting localStorage data between browser sessions? Latest write wins; no conflict resolution needed for UI preferences.
- How does the system handle optimistic update conflicts when server response differs from client state? Server state always wins; optimistic changes are discarded silently without user notification.
- What happens when a user tries to add a sub-task to another sub-task? System prevents nesting beyond one level and shows an error message.
- How does the system handle recurring tasks when the user's device is offline? Recurring instances are generated on next online session based on last completion timestamp.
- What happens if a user manually exits Focus Mode before the countdown completes? Task remains in its current state (incomplete unless explicitly marked complete).
- How does the system handle malformed voice transcription from the API? Display the raw transcription and allow manual editing before task conversion.
- What happens when localStorage quota is exceeded? Display a warning and stop persisting new preferences; existing preferences remain accessible.
- How does the system handle theme preferences if the dark mode CSS fails to load? Fall back to a minimal inline dark theme to prevent white flash.
- What happens if user denies browser notification permission? System falls back to in-app toasts only; Service Worker still polls and sends messages to all open tabs; no error shown, degraded experience is silent except for one-time informational prompt
- What happens if user creates invalid recurrence pattern like Feb 30? System validates via RRule parsing, shows error "Invalid date pattern: February 30 does not exist", suggests valid alternatives (e.g., "last day of February")
- What happens if user sets recurrence interval beyond 365 days? System shows error "Maximum interval is 365 days", suggests using manual task creation for longer cycles

## Requirements *(mandatory)*

### Functional Requirements

#### Core Task Management

- **FR-001**: System MUST allow users to create tasks with client-generated UUID identifier, title, description, tags (freeform text input with autocomplete from previously used tags), priority (Low/Medium/High), estimated duration, and optional recurrence settings
- **FR-002**: System MUST support one level of sub-tasks (sub-tasks cannot have their own sub-tasks)
- **FR-003**: System MUST calculate task progress as (completed sub-tasks / total sub-tasks) × 100
- **FR-004**: System MUST hide progress UI when a task has zero sub-tasks
- **FR-005**: System MUST allow users to hide tasks (sets hidden flag to true) without deleting them; hidden tasks remain incomplete and can be unhidden
- **FR-006**: System MUST exclude hidden tasks from all default views (Tasks page, search results, Focus Mode task selection)
- **FR-007**: System MUST provide access to hidden tasks via Settings → Tasks → Hidden, where users can unhide or permanently delete them
- **FR-008**: System MUST prevent orphaned sub-tasks (sub-tasks must have a parent task)
- **FR-009**: System MUST validate that duration represents estimated time only (no automatic time tracking)

#### Focus Mode

- **FR-010**: System MUST allow users to activate Focus Mode on any task via a target icon
- **FR-011**: When Focus Mode activates, system MUST hide sidebar, hide all other tasks, and display only the active task with countdown timer
- **FR-012**: System MUST initialize countdown timer using the task's estimated duration
- **FR-013**: System MUST allow manual exit from Focus Mode at any time
- **FR-014**: System MUST automatically exit Focus Mode when the active task is marked complete
- **FR-015**: System MUST disable all popovers and distractions during Focus Mode
- **FR-016**: System MUST alert user (audio/visual) when countdown reaches zero

#### AI Features

- **FR-017**: System MUST provide a Quick Notes interface with voice-to-text capability
- **FR-018**: During voice recording, system MUST display an unmistakable global red recording indicator with animated waveform
- **FR-019**: System MUST allow users to convert notes to tasks via a right-side sliding drawer
- **FR-020**: System MUST use AI to parse note content and pre-fill task fields (title, description, priority, tags, reminders)
- **FR-021**: Users MUST review and confirm AI-parsed fields before task creation
- **FR-022**: System MUST provide "Magic Sub-tasks" feature in Task Detail view
- **FR-023**: Magic Sub-tasks MUST stream AI-generated suggestions in real-time
- **FR-024**: System MUST disable Generate button during AI streaming
- **FR-025**: System MUST prompt user for confirmation before overwriting existing sub-tasks
- **FR-026**: System MUST preserve partial AI output if streaming fails
- **FR-027**: System MUST never execute AI actions without user confirmation
- **FR-028**: When AI rate limits or quotas are exceeded, system MUST display clear error message, temporarily disable affected AI features, and automatically retry after cooldown period (configurable via .env)

#### Achievements & Metrics

- **FR-029**: System MUST track fixed metrics: High Priority Slays, Consistency Streaks, % Addition to Completion
- **FR-030**: Metric definitions MUST be versioned and never change retroactively
- **FR-031**: System MUST display metrics on animated dashboard cards
- **FR-032**: System MUST provide subtle milestone feedback (shimmer or confetti) for rare achievements only
- **FR-033**: Consistency Streak MUST require at least one completed task per day (calculated using UTC midnight reset); streak breaks only after missing 2+ consecutive days (1 grace day allowed)

#### Navigation & Layout

- **FR-034**: System MUST provide route-based navigation for: /dashboard/tasks, /dashboard/notes, /dashboard/achievements, /dashboard/settings, /dashboard/archive
- **FR-035**: System MUST display a collapsible sidebar with navigation links and global search
- **FR-036**: System MUST persist sidebar open/closed state in localStorage
- **FR-037**: System MUST provide a profile section (Radix Popover) with: user name, email, account settings, theme tweaks, logout
- **FR-038**: Profile popover MUST close on click-outside
- **FR-039**: Profile popover MUST be disabled during Focus Mode

#### Search

- **FR-040**: System MUST provide global search across all entities (tasks, notes, achievements, archived tasks)
- **FR-041**: Search results MUST be scoped and grouped by entity type

#### AI Widget

- **FR-042**: System MUST display a floating AI widget bubble in bottom-right corner (dashboard only)
- **FR-043**: CMD+K MUST open AI input (reserved for future command palette)

#### New User Experience

- **FR-044**: System MUST auto-start interactive walkthrough on first login using driver.js
- **FR-045**: Walkthrough MUST include steps: Sidebar overview, Create Quick Note, Convert Note to Task, Activate Focus Mode
- **FR-046**: System MUST create a permanent tutorial task "Master Perpetua" with feature sub-tasks
- **FR-047**: Tutorial task MUST be archivable but not deletable
- **FR-048**: Users MUST be able to replay walkthrough from Settings

#### Design System

- **FR-049**: System MUST enforce strict dark mode only (no light mode option)
- **FR-050**: System MUST use glassmorphism exclusively for dashboard widgets and task cards
- **FR-051**: System MUST meet WCAG AA contrast standards
- **FR-052**: System MUST use Framer Motion for component entry/exit and route transitions
- **FR-053**: All animations MUST have duration ≤ 200ms
- **FR-054**: System MUST respect prefers-reduced-motion accessibility setting
- **FR-055**: System MUST use Inter or Geist Sans for primary typography
- **FR-056**: System MUST use monospace font exclusively for duration, status, and system metadata

#### State Management & Data

- **FR-057**: System MUST use simulated backend data via Mock Service Worker (MSW)
- **FR-058**: All data queries MUST simulate network behavior (latency, loading, failure)
- **FR-059**: Optimistic updates MUST be ephemeral and reset on page reload; server state always wins in conflicts (optimistic changes discarded silently)
- **FR-060**: System MUST persist only sidebar state and theme preferences in localStorage
- **FR-061**: System MUST NOT persist task data in localStorage
- **FR-062**: System MUST define all data contracts using centralized Zod schemas in /schemas
- **FR-063**: Zod schemas MUST exclude UI-only flags (isEditing, isStreaming, etc.)

#### Public Pages

- **FR-064**: System MUST provide landing page with animated gradient mesh background
- **FR-065**: Landing page MUST include glassmorphic feature cards
- **FR-066**: System MUST provide Pricing, Contact, About pages following dark aesthetic
- **FR-067**: Footer MUST contain social links and legal pages

#### Reminders & Recurrence

- **FR-068**: System MUST support task reminders with configurable notification timing
- **FR-069**: System MUST support recurring task intervals (daily, weekly, monthly, custom)
- **FR-070**: Recurring tasks MUST generate next instance based on completion timestamp
- **FR-071**: System MUST allow users to set reminder timestamps for tasks (absolute date/time)
- **FR-072**: System MUST display reminder notifications at configured time (browser notifications)
- **FR-072a**: If browser notification permission is denied, system MUST fall back to in-app toast notifications only; Service Worker continues polling MSW but only sends postMessage to clients (no Notification API calls); users are shown a one-time prompt explaining reduced notification functionality with link to browser settings to enable permissions
- **FR-073**: Recurrence settings MUST include: interval type (daily/weekly/monthly/custom), interval value (e.g., every 3 days), and optional end date
- **FR-073a**: Custom recurrence intervals MUST: be limited to maximum 365 days (1 year); be validated via RRule RFC 5545 parsing before storage; reject invalid patterns (e.g., "every Feb 30", "every 0 days") with specific error messages; support common patterns: "every N days" (1-365), "every N weeks on [weekdays]" (1-52), "every month on day X" (1-28 to avoid month-end issues); display validation errors inline in RecurrenceEditor component; provide human-readable pattern description preview using RRule.toText()
- **FR-074**: System MUST log all AI interactions (prompts, responses, timestamps) for transparency and debugging

#### Settings & Configuration

- **FR-075**: System MUST provide Settings page with configurable preferences: AI cooldown period, notification preferences, tutorial replay, hidden task management
- **FR-076**: Users MUST be able to set due dates for tasks (optional field, separate from reminders)

#### Archive & Task Management

- **FR-077**: System MUST support task archiving as distinct from hiding (archived tasks are completed and removed from active views but accessible via Archive page; archiving sets archived flag to true and requires task to be marked complete first)

### Task State Management Clarifications

**Hidden vs Archived vs Deleted**:

- **Hidden**: Task is incomplete, temporarily removed from views, can be unhidden or permanently deleted via Settings → Tasks → Hidden
- **Archived**: Task is complete, permanently removed from active views, accessible via Archive page, cannot be unarchived (immutable completed state)
- **Deleted**: Task is permanently removed from the system (hard delete, no recovery); only available for hidden tasks via Settings

**State Transitions**:

- Incomplete Task → Hidden (reversible via unhide)
- Hidden Task → Deleted (permanent, via Settings)
- Complete Task → Archived (automatic or manual, irreversible)
- Hidden Task → Complete → Archived (unhide first, then complete, then archive)

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's to-do item with unique client-generated UUID identifier, title, description, tags (array of freeform strings with autocomplete history), priority (Low/Medium/High), estimated duration, reminder (optional timestamp), recurrence settings (optional object containing intervalType, intervalValue, endDate), due date (optional timestamp, separate from reminder), hidden flag (boolean, mutually exclusive with archived), archived flag (boolean, requires completion status true), completion status (boolean), creation timestamp, completion timestamp (optional, required when archived is true), and optional parent task UUID reference
- **Sub-task**: Represents a child task that contributes to parent task progress; can only be one level deep; contains unique client-generated UUID identifier, title, completion status, creation timestamp, and required parent task UUID reference
- **Note**: Represents a quick capture of user thoughts with content text, creation timestamp, archived flag, and optional voice transcription metadata
- **User Profile**: Represents user account information including name, email, preferences (sidebar state, theme tweaks), first-login flag, and tutorial completion status
- **Achievement**: Represents tracked metrics including High Priority Slays count, Consistency Streak days (with last completion date and grace day tracking), Completion Ratio percentage, and milestone thresholds with timestamps

**Terminology Note**: The feature was originally referred to as "dopamine engine" in early discussions, but the official term used throughout this specification and implementation is "Achievements System" to better reflect its gamification purpose.

- **Recurrence Settings** (embedded in Task): Object containing intervalType (enum: "daily" | "weekly" | "monthly" | "custom"), intervalValue (integer, e.g., 3 for "every 3 days"), and optional endDate (timestamp)
- **AI Interaction Log**: Represents logged AI interactions with request type (enum: "note-to-task" | "generate-sub-tasks"), prompt text, response text, timestamp, and associated entity UUID (task or note)
- **Workflow**: [OUT OF SCOPE for initial release] Future feature for grouping related tasks into sequential workflows; removed from navigation and data model
- **Activity Log**: [OUT OF SCOPE for initial release] Future feature for displaying user action history; removed from navigation and data model

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### User Productivity

- **SC-001**: Users can create a basic task (title + priority) in under 15 seconds
- **SC-002**: Users can activate Focus Mode on any task within 2 clicks
- **SC-003**: 90% of users successfully complete their first task within 5 minutes of account creation
- **SC-004**: Users can convert a voice note to a structured task in under 60 seconds
- **SC-005**: Global search returns relevant results in under 1 second for datasets up to 10,000 tasks

#### AI Feature Adoption

- **SC-006**: 70% of users who create notes with >20 words use the "Convert to Task" feature
- **SC-007**: AI sub-task generation completes streaming within 10 seconds for 95% of requests
- **SC-008**: Voice transcription accuracy exceeds 90% for clear recordings in supported languages

#### User Engagement

- **SC-009**: 60% of new users complete the entire onboarding walkthrough
- **SC-010**: Users with active Consistency Streaks complete tasks 40% more frequently than users without streaks
- **SC-011**: Users who activate Focus Mode at least once per week complete 30% more high-priority tasks

#### Technical Performance

- **SC-012**: Dashboard initial load completes in under 2 seconds on standard broadband
- **SC-013**: Route transitions complete in under 200ms
- **SC-014**: MSW simulated API responses return within 100-500ms (realistic latency)
- **SC-015**: Application remains responsive with up to 1,000 tasks loaded in memory

#### Accessibility & UX

- **SC-016**: All interactive elements meet WCAG AA contrast requirements (minimum 4.5:1 for normal text)
- **SC-017**: Users with prefers-reduced-motion enabled experience zero animation disruption
- **SC-018**: 95% of users can navigate to any primary feature (Tasks, Notes, Focus Mode) within 3 clicks from dashboard
- **SC-019**: Error messages for failed AI operations provide clear next steps in under 50 words

#### Design System Compliance

- **SC-020**: 100% of glassmorphic elements maintain readability (blur does not obscure critical text)
- **SC-021**: Color palette maintains consistent dark aesthetic across all pages (no accidental light backgrounds)
- **SC-022**: Typography hierarchy is immediately recognizable (primary vs. monospace usage is unambiguous)

#### Retention & Motivation

- **SC-023**: Users who unlock at least one achievement return to the app 50% more frequently within the following week
- **SC-024**: Tutorial task "Master Perpetua" completion rate reaches 40% within 30 days of account creation

## Clarifications

### Session 2026-01-07

- Q: How should the system identify and handle duplicate tasks? → A: Client-generated UUID (collision-resistant, offline-friendly, no server dependency)
- Q: When should a consistency streak reset? → A: Reset at midnight UTC (consistent but ignores user timezone)
- Q: How should the system handle conflicts between optimistic updates and server responses? → A: Server wins, discard optimistic changes silently (simple, consistent with ephemeral design)
- Q: How should the system handle AI rate limit or quota exhaustion? → A: Show error, disable AI features temporarily, retry after cooldown period (graceful degradation)
- Q: How should users input and manage task tags? → A: Freeform with autocomplete from previously used tags (balance of flexibility and consistency)

## Assumptions

1. **Authentication**: User authentication exists but is implemented outside this feature scope (login/signup flows are separate)
2. **Browser Support**: Modern browsers supporting ES6+, CSS Grid, Flexbox, and Web Speech API
3. **Network**: Users have reasonably stable internet connections (MSW simulates offline behavior for testing)
4. **AI Backend**: An AI API endpoint exists that accepts task context and returns structured sub-task suggestions or note parsing
5. **Voice API**: A speech-to-text API (e.g., Web Speech API or cloud service) is available for voice transcription
6. **Language Support**: Initial release supports English only; internationalization is out of scope
7. **Screen Size**: Primary support for desktop/tablet (1024px+ width); mobile optimization is future work
8. **Data Volume**: Typical user has <5,000 tasks; performance optimization beyond this is deferred
9. **Backend Migration**: The MSW mock structure mirrors expected real API contracts (RESTful JSON endpoints)
10. **Notifications**: Browser notification permissions are requested but not required for core functionality
11. **Accessibility Tools**: Users with screen readers rely on semantic HTML and ARIA labels (to be implemented following WAI-ARIA best practices)
12. **Theme Customization**: "Theme tweaks" refers to minor adjustments (accent colors, spacing preferences) within the dark mode palette

## Testing Requirements *(mandatory)*

### Testing Philosophy

This feature MUST follow Test-Driven Development (TDD) as mandated by the project constitution (Section VIII). All functionality MUST be proven with tests before implementation.

### Testing Framework & Tools

- **React Testing Library**: Primary testing framework for component testing (user-centric, accessibility-focused)
- **Jest**: Test runner and assertion library
- **MSW (Mock Service Worker)**: API mocking for integration tests
- **@testing-library/jest-dom**: Custom matchers for DOM assertions
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/react-hooks**: Hook testing utilities (if needed)

### Test Coverage Requirements

#### Unit Tests (React Testing Library)

All components MUST have tests covering:

1. **Rendering & Display**
   - Component renders without crashing
   - Required elements are present in the document
   - Correct text content is displayed
   - Conditional rendering based on props/state

2. **User Interactions**
   - Click events trigger expected behavior
   - Form input changes update state correctly
   - Keyboard navigation works as expected
   - Focus management is correct

3. **Accessibility**
   - Required ARIA labels are present
   - Semantic HTML elements are used correctly
   - Keyboard interactions follow WCAG guidelines
   - Screen reader announcements are correct

4. **State Management**
   - Zustand stores update correctly
   - TanStack Query cache updates optimistically
   - LocalStorage persistence works as expected
   - State resets appropriately on unmount

#### Integration Tests

Critical user flows MUST have integration tests:

1. **Task Creation Flow**
   - User fills form → submits → task appears in list → MSW intercepts API call

2. **Focus Mode Flow**
   - User clicks target icon → sidebar hides → countdown starts → timer completes → exit behavior

3. **AI Note Conversion Flow**
   - User creates note → clicks convert → drawer opens → AI parses (MSW mocked) → user confirms → task created

4. **Global Search Flow**
   - User types query → results appear grouped → user clicks result → navigation occurs

#### Test Structure (Given-When-Then)

All tests MUST follow the Given-When-Then pattern:

```typescript
test('marks task as complete when user clicks checkbox', async () => {
  // GIVEN: A task exists in the list
  render(<TaskList tasks={[mockTask]} />);
  const checkbox = screen.getByRole('checkbox', { name: /finish report/i });

  // WHEN: User clicks the checkbox
  await userEvent.click(checkbox);

  // THEN: Task is marked complete and API is called
  expect(checkbox).toBeChecked();
  await waitFor(() => {
    expect(screen.getByText(/completed/i)).toBeInTheDocument();
  });
});
```

#### Critical Test Cases

Each user story MUST have corresponding tests:

##### User Story 1 - Create and Manage Tasks (P1)

- `TaskForm` component renders all input fields
- Submitting form with valid data creates task
- Sub-task progress calculates correctly (33% for 1/3 complete)
- Hidden tasks are excluded from default view
- Orphaned sub-tasks are prevented with error message

##### User Story 2 - Focus Mode (P2)

- Target icon activates Focus Mode
- Sidebar hides and other tasks disappear
- Countdown timer displays and counts down
- Manual exit restores normal view
- Auto-exit on task completion triggers achievement feedback

##### User Story 3 - AI Quick Notes (P2)

- Voice recording indicator appears during recording
- AI conversion drawer opens with pre-filled fields (MSW mocked response)
- User can edit AI-parsed fields before confirming
- Recording auto-stops after 5 minutes

##### User Story 4 - AI Sub-tasks (P3)

- Generate button is disabled during streaming
- Confirmation prompt appears if sub-tasks exist
- Partial output preserved on AI failure
- Streaming completes and sub-tasks are added

##### User Story 5 - Achievements (P3)

- Metrics update correctly on task completion
- Shimmer animation triggers at milestones
- Consistency streak increments daily
- Completion ratio calculates accurately (75% for 15/20)

##### User Story 6 - Onboarding (P3)

- Walkthrough auto-starts on first login
- User can complete all walkthrough steps
- Tutorial task is created and marked non-deletable
- Replay tutorial works from Settings

##### User Story 7 - Global Search (P2)

- Search results are grouped by entity type
- Clicking result navigates to correct page
- "No results found" appears for empty queries

##### User Story 8 - Dashboard Layout (P1)

- Sidebar collapse persists in localStorage
- Route navigation highlights active menu item
- Focus Mode hides sidebar completely

#### Edge Case Tests

All edge cases MUST have explicit tests:

- Sub-task without parent task shows error
- Microphone permission denied shows error message
- AI timeout preserves partial output
- AI rate limit shows error and disables features
- localStorage quota exceeded shows warning
- Malformed voice transcription allows manual edit
- Dark mode CSS failure falls back to minimal theme
- Optimistic update conflict reverts to server state

#### Test Naming Convention

Tests MUST follow this naming pattern:

```text
[Component/Feature] - [User Action] - [Expected Outcome]
```

Examples:

- `TaskForm - submits valid data - creates new task`
- `FocusMode - countdown reaches zero - shows alert`
- `GlobalSearch - searches for "budget" - groups results by type`

#### MSW Mock Handlers

All API endpoints MUST have MSW handlers:

- `POST /api/tasks` - Create task (201 response)
- `PATCH /api/tasks/:id` - Update task (200 response)
- `DELETE /api/tasks/:id` - Soft-delete task (204 response)
- `POST /api/tasks/:id/sub-tasks` - Add sub-task (201 response)
- `POST /api/notes` - Create note (201 response)
- `POST /api/ai/parse-note` - AI note parsing (200 with structured response, simulated 2s delay)
- `POST /api/ai/generate-sub-tasks` - AI sub-task generation (SSE stream simulation)
- `GET /api/search` - Global search (200 with grouped results)
- `GET /api/achievements` - Fetch metrics (200 response)

#### Test Execution Requirements

1. **Pre-commit Hook**: All tests MUST pass before commit
2. **CI Pipeline**: Tests run on every push and PR
3. **Coverage Threshold**: Minimum 80% line coverage for core features
4. **Performance**: Test suite MUST complete in under 2 minutes
5. **Isolation**: Each test MUST be independent (no shared state)

#### Testing Best Practices

1. **Query Priority** (React Testing Library):
   - Use `getByRole` for accessibility testing
   - Use `getByLabelText` for form fields
   - Use `getByText` as last resort
   - Avoid `getByTestId` unless necessary

2. **Async Testing**:
   - Always use `waitFor` for async state changes
   - Use `findBy*` queries for elements that appear asynchronously
   - Set reasonable timeouts (default 1000ms)

3. **User-Centric Testing**:
   - Test behavior, not implementation
   - Simulate real user interactions (click, type, navigate)
   - Avoid testing internal state directly

4. **Accessibility Testing**:
   - Every interactive element MUST have accessible name
   - Test keyboard navigation (Tab, Enter, Escape)
   - Verify ARIA attributes are correct

#### TDD Workflow (Red-Green-Refactor)

1. **RED**: Write failing test for new feature
2. **GREEN**: Write minimal code to pass test
3. **REFACTOR**: Improve code while keeping tests green
4. **REPEAT**: Add next test case

Example TDD cycle for task creation:

```typescript
// RED: Test fails (component doesn't exist yet)
test('TaskForm - submits valid data - creates new task', async () => {
  render(<TaskForm onSubmit={mockSubmit} />);
  // ... test implementation
});

// GREEN: Implement TaskForm to pass test
export function TaskForm({ onSubmit }) {
  // ... minimal implementation
}

// REFACTOR: Improve TaskForm code quality
export function TaskForm({ onSubmit }) {
  // ... refactored with better structure
}
```

### Testing Anti-Patterns (AVOID)

❌ Testing implementation details (internal state, private methods)
❌ Snapshot testing for dynamic content
❌ Testing third-party libraries (Framer Motion, Radix UI)
❌ Writing tests after implementation (violates TDD)
❌ Using `act()` directly (use RTL's async utilities instead)
❌ Testing CSS styles (test behavior, not appearance)

### Testing Documentation

Each test file MUST include:

1. **File header**: Brief description of what's being tested
2. **Setup/teardown**: Clear `beforeEach`/`afterEach` blocks
3. **Test grouping**: Use `describe` blocks for logical grouping
4. **Comments**: Explain complex assertions or edge cases

## Dependencies

- **Next.js App Router**: Framework choice is specified; routing and server component capabilities are required
- **TanStack Query**: State management for server-like data (with MSW)
- **Zustand**: State management for client UI state
- **Mock Service Worker (MSW)**: Simulates backend during development
- **Zod**: Schema validation for data contracts
- **Framer Motion**: Animation library for transitions and interactions
- **Radix UI**: Headless UI components (Popover confirmed; others likely for accessibility)
- **driver.js**: Interactive walkthrough library for onboarding
- **React Testing Library**: Testing framework for component tests (TDD requirement)
- **Jest**: Test runner and assertion library
- **@testing-library/jest-dom**: Custom matchers for DOM assertions
- **@testing-library/user-event**: User interaction simulation
- **AI API Service**: External or internal service for sub-task generation and note parsing (contract TBD in planning phase)
- **Speech-to-Text API**: Web Speech API or cloud provider (Google Cloud Speech, Azure, etc.)
- **Web Audio API**: For voice recording waveform visualization

## Out of Scope (Non-Goals)

The following are explicitly excluded from this feature:

1. **Time Tracking**: No automatic or manual time tracking; duration is estimation only
2. **Infinite Task Nesting**: Sub-tasks cannot have their own sub-tasks (one level maximum)
3. **Light Mode**: No light theme or theme toggle
4. **AI Auto-Actions**: No AI-initiated actions without user confirmation
5. **Backend Assumptions**: No backend-specific implementation details beyond API shape compatibility
6. **Team Collaboration**: No multi-user features, sharing, or real-time collaboration
7. **Mobile Native Apps**: No iOS/Android native applications (web-only)
8. **Offline Mode**: No persistent offline functionality (MSW simulates network conditions for testing only)
9. **Data Export/Import**: No bulk export or import features
10. **Integrations**: No third-party integrations (calendar, email, Slack, etc.)
11. **Customizable Metrics**: Metrics are fixed and versioned; users cannot define custom metrics
12. **Workflow Automation**: No if-then rules or automated task routing
13. **Advanced Search Filters**: No complex search operators or saved searches
14. **Sub-task Dependencies**: No dependency management between sub-tasks
15. **Task Templates**: No reusable task templates or task cloning
16. **Workflows Feature**: No workflow creation, management, or visualization (removed from navigation; reserved for future release)
17. **Activity Log Feature**: No historical activity tracking or timeline view (removed from navigation; reserved for future release)
18. **Task Unarchiving**: Archived tasks cannot be moved back to active state (immutable completed state)