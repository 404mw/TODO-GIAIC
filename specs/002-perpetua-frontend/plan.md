# Implementation Plan: Perpetua Flow - Frontend Application

**Branch**: `002-perpetua-frontend` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-perpetua-frontend/spec.md`

## Summary

Perpetua Flow is a frontend-only task management application with futuristic minimal design, AI automation, focus mode, and dopamine engine for achievements. The application uses Next.js 15+ with App Router, TanStack Query for server-state simulation via MSW, Zustand for client UI state, and follows strict dark-mode-only glassmorphism design. All AI features require explicit user confirmation, and the system maintains comprehensive logging for auditability.

## Technical Context

**Language/Version**: TypeScript 5.x, Next.js 15+ (App Router)
**Primary Dependencies**: React 18+, TanStack Query v5, Zustand v4, MSW v2, Zod v3, Framer Motion v11, Radix UI, driver.js
**Storage**: Mock Service Worker (MSW) for simulated backend, localStorage for sidebar state and theme preferences only
**Testing**: React Testing Library, Jest, @testing-library/user-event, @testing-library/jest-dom
**Target Platform**: Web browsers (Chrome/Firefox/Safari/Edge, ES6+ support required)
**Project Type**: Web (Next.js frontend-only with MSW-simulated backend)
**Performance Goals**: Dashboard load <2s, route transitions <200ms, MSW responses 100-500ms, responsive with 1,000 tasks
**Constraints**: Dark mode only, animations ≤200ms, WCAG AA contrast, prefers-reduced-motion support, no localStorage persistence for task data
**Scale/Scope**: Single-user SaaS, up to 10,000 tasks, 8 primary routes, 5+ AI-powered features, comprehensive TDD coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Authority & Source of Truth
- **Compliance**: Feature specification in [spec.md](./spec.md) defines all system states, transitions, invariants, constraints, and AI permissions
- **Executable Spec Verification**: All functional requirements (FR-001 through FR-077) define concrete acceptance criteria
- **Hotfix Protocol**: Not applicable (no production deployment yet); hotfix process acknowledged for future

### ✅ II. Phase Discipline (Hard Gates)
- **Compliance**: This plan enforces strict phase sequencing (Phase 0 → Phase 1 → Phase 2)
- **No Spec, No Code**: All behavioral changes documented in spec.md before implementation begins
- **Phase Completion Criteria**: Each phase has explicit "Done" criteria and deliverables

### ✅ III. Data Integrity & Safety
- **Compliance**: All development uses MSW-generated dummy data; no real user data exists yet
- **Undo Guarantee Implementation**: Section 6.3 defines ephemeral undo for current session mutations
- **Backup Strategy**: Not applicable for frontend-only MSW simulation; acknowledged for future backend integration
- **Data Loss Prevention**: Optimistic updates are ephemeral; server state always wins (FR-059)

### ✅ IV. AI Agent Governance
- **Compliance**: All AI features require explicit user confirmation (FR-027)
- **Default Restrictions**: AI cannot change task state or delete tasks without user-initiated action
- **Opt-in Behavior**: Note-to-Task conversion (FR-021) and Magic Sub-tasks (FR-023) require user confirmation
- **Interaction Flow**: Section 6.2 implements mandatory confirmation → action → undo popup flow
- **AI Loop Control**: Voice recording (FR-018) provides stop button; streaming generation (FR-023) disables button during execution

### ✅ V. AI Logging & Auditability
- **Compliance**: FR-074 mandates comprehensive AI interaction logging
- **Logged Fields**: task ID, timestamp, actor identity (user vs. AI), prompt text, response text
- **Immutability**: AI Interaction Log entity (spec.md line 308) defines immutable event log structure

### ✅ VI. API Design Rules
- **Compliance**: Section 5 defines single-responsibility MSW endpoints with documented intent, schemas, and error behavior
- **Error Response Documentation**: Section 5.1 provides comprehensive error taxonomy with status codes, error shapes, and recovery guidance
- **No Hidden Side Effects**: All MSW handlers explicitly document state changes (e.g., task completion triggers achievement recalculation)

### ✅ VII. Validation & Type Safety
- **Compliance**: FR-062 mandates centralized Zod schemas in `/schemas` directory
- **Schema Consistency**: All MSW handlers use Zod schemas for validation; UI-only flags (isEditing, isStreaming) excluded from schemas (FR-063)
- **Type Safety**: TypeScript strict mode enforced; no `any` types in production code

### ✅ VIII. Testing Doctrine
- **Compliance**: Comprehensive TDD requirements in spec.md Testing Requirements section (lines 385-645)
- **Coverage**: Unit tests for all components, integration tests for critical flows, MSW handlers for all endpoints
- **Red-Green-Refactor**: TDD workflow explicitly documented (spec.md lines 600-625)
- **Test-First Mandate**: All tasks.md tasks will follow Red → Green → Refactor sequence

### ✅ IX. Secrets & Configuration
- **Compliance**: Section 7 defines `.env` structure for AI API keys, cooldown periods, and feature flags
- **Environment Validation**: Startup validator blocks application if required variables missing
- **No Secret Leakage**: All AI API calls proxied through `/api/ai/*` routes; keys never exposed to client
- **Configurable Limits**: AI cooldown period (FR-028), rate limit thresholds (FR-202) configurable via `.env`

### ✅ X. Infrastructure Philosophy
- **Compliance**: Frontend-only with MSW avoids backend complexity
- **Simplicity Justification**: TanStack Query + Zustand preferred over Redux Toolkit (simpler mental model)
- **Complexity Tracking**: Section 9 documents justified complexity (Radix UI for accessibility, Framer Motion for animations)

### ✅ XI. Enforcement
- **Compliance Verification**: Pre-commit hooks run tests, linting, and type checks
- **Violation Protocol**: Constitution violations treated as bugs; intentional deviations documented in Complexity Tracking section
- **Transparent Enforcement**: CI pipeline blocks merges on test failures or type errors

### Constitution Re-Check Trigger Points
- **After Phase 1 Design**: Verify API contracts align with single-responsibility principle (Section VI)
- **After Schema Definition**: Verify Zod schemas align with validation requirements (Section VII)
- **After AI Feature Implementation**: Verify confirmation flows meet governance requirements (Section IV)

## Project Structure

### Documentation (this feature)

```text
specs/002-perpetua-frontend/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature specification (input to planning)
├── research.md          # Phase 0 output (technology best practices)
├── data-model.md        # Phase 1 output (entity schemas)
├── quickstart.md        # Phase 1 output (local dev setup)
├── contracts/           # Phase 1 output (API contracts)
│   ├── tasks.yaml       # Task CRUD + Focus Mode endpoints
│   ├── notes.yaml       # Note CRUD + voice transcription endpoints
│   ├── ai.yaml          # AI parsing + sub-task generation endpoints
│   ├── achievements.yaml # Metrics + milestone endpoints
│   └── search.yaml      # Global search endpoint
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/                     # Next.js application root
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── (auth)/           # Auth route group (login, signup)
│   │   ├── (public)/         # Public pages (landing, pricing, about)
│   │   ├── dashboard/        # Protected dashboard routes
│   │   │   ├── tasks/        # Task management views
│   │   │   ├── notes/        # Quick notes interface
│   │   │   ├── achievements/ # Metrics dashboard
│   │   │   ├── archive/      # Archived tasks view
│   │   │   ├── settings/     # User settings + hidden tasks
│   │   │   └── layout.tsx    # Dashboard layout with sidebar
│   │   ├── api/              # API routes (MSW proxies)
│   │   │   ├── ai/           # AI endpoints (parse-note, generate-sub-tasks)
│   │   │   └── health/       # Health check endpoint
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles + dark theme
│   ├── components/           # React components
│   │   ├── dashboard/        # Dashboard-specific components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ProfilePopover.tsx
│   │   │   ├── GlobalSearch.tsx
│   │   │   └── AIWidget.tsx
│   │   ├── tasks/            # Task-related components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── SubTaskList.tsx
│   │   │   ├── FocusMode.tsx
│   │   │   └── MagicSubTasks.tsx
│   │   ├── notes/            # Note-related components
│   │   │   ├── NoteEditor.tsx
│   │   │   ├── VoiceRecorder.tsx
│   │   │   └── NoteToTaskDrawer.tsx
│   │   ├── achievements/     # Achievement components
│   │   │   ├── MetricCard.tsx
│   │   │   └── MilestoneAnimation.tsx
│   │   ├── onboarding/       # Onboarding walkthrough
│   │   │   └── Walkthrough.tsx
│   │   └── ui/               # Shared UI components (buttons, inputs, etc.)
│   ├── lib/                  # Utilities and configuration
│   │   ├── msw/              # MSW mock handlers
│   │   │   ├── handlers/     # API endpoint handlers
│   │   │   │   ├── tasks.ts
│   │   │   │   ├── notes.ts
│   │   │   │   ├── ai.ts
│   │   │   │   ├── achievements.ts
│   │   │   │   └── search.ts
│   │   │   ├── db.ts         # In-memory mock database
│   │   │   └── browser.ts    # MSW browser setup
│   │   ├── schemas/          # Zod schemas (centralized)
│   │   │   ├── task.ts       # Task + SubTask schemas
│   │   │   ├── note.ts       # Note schema
│   │   │   ├── user.ts       # User profile schema
│   │   │   ├── achievement.ts # Achievement schema
│   │   │   └── ai.ts         # AI request/response schemas
│   │   ├── stores/           # Zustand stores (UI state)
│   │   │   ├── useSidebarStore.ts
│   │   │   ├── useFocusModeStore.ts
│   │   │   └── useOnboardingStore.ts
│   │   ├── hooks/            # TanStack Query hooks
│   │   │   ├── useTasks.ts   # Task CRUD queries
│   │   │   ├── useNotes.ts   # Note CRUD queries
│   │   │   ├── useAI.ts      # AI feature queries
│   │   │   └── useAchievements.ts # Metrics queries
│   │   ├── utils/            # Helper functions
│   │   │   ├── validation.ts # Zod validation wrappers
│   │   │   ├── date.ts       # Date formatting utilities
│   │   │   └── animations.ts # Framer Motion variants
│   │   └── config.ts         # App configuration (env vars)
│   └── types/                # TypeScript type definitions
│       └── global.d.ts       # Global type augmentations
├── tests/                    # Test files (mirrors src/ structure)
│   ├── components/           # Component unit tests
│   ├── integration/          # Integration tests (user flows)
│   ├── msw/                  # MSW handler tests
│   └── setup.ts              # Test environment setup
├── public/                   # Static assets
│   └── fonts/                # Custom fonts (Inter/Geist Sans)
├── .env.example              # Environment variable template
├── .env.local                # Local environment variables (gitignored)
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind + dark theme configuration
├── tsconfig.json             # TypeScript configuration
├── jest.config.js            # Jest configuration
└── package.json              # Dependencies
```

**Structure Decision**: Web application structure with Next.js App Router. The `frontend/` directory contains all source code since this is a frontend-only feature using MSW to simulate backend behavior. The App Router structure (`src/app/`) organizes routes by feature (tasks, notes, achievements) with route groups for authentication and public pages. MSW handlers in `src/lib/msw/` simulate a RESTful API with in-memory data storage.

## Complexity Tracking

> Constitution Check passed with no violations. This section documents justified complexity that aligns with constitutional principles.

| Justified Complexity | Why Needed | Aligns With Constitution Section |
|---------------------|------------|----------------------------------|
| Radix UI Primitives | Provides accessible, WCAG AA-compliant headless components (Popover, Dialog, Dropdown) that meet FR-051 without custom implementation | X. Infrastructure Philosophy (simplicity: leverage battle-tested accessibility) |
| Framer Motion | Required for FR-052 (component entry/exit animations), FR-053 (≤200ms duration), FR-054 (prefers-reduced-motion support); simpler than custom animation implementation | X. Infrastructure Philosophy (justified: animations are core UX requirement) |
| TanStack Query | Provides optimistic updates (FR-059), loading/error states, and cache invalidation with minimal boilerplate compared to Redux Toolkit or manual fetch management | X. Infrastructure Philosophy (simplicity: reduces state management complexity) |
| Zustand | Lightweight client UI state (sidebar, focus mode, onboarding) without Redux boilerplate; simpler than Context API for complex state | X. Infrastructure Philosophy (simplicity: 1KB library vs. Redux Toolkit) |
| MSW (Mock Service Worker) | Enables realistic backend simulation (FR-057, FR-058) without actual server setup; simplifies testing and development | X. Infrastructure Philosophy (simplicity: no backend infrastructure needed) |
| driver.js | Interactive walkthrough library for FR-044 through FR-048; mature solution preferred over custom tour implementation | X. Infrastructure Philosophy (justified: proven library for onboarding UX) |
| Zod Schemas (centralized) | FR-062 mandates centralized validation; Zod provides runtime validation + TypeScript inference from single source of truth | VII. Validation & Type Safety (type safety mandate) |

## Phase 0: Research & Technology Validation

**Goal**: Resolve all "NEEDS CLARIFICATION" items from Technical Context and establish best practices for chosen technologies.

**Status**: ✅ COMPLETE (Technical Context fully specified)

**Deliverable**: `research.md` with technology decisions, best practices, and alternatives considered.

### Research Tasks

1. **Next.js 15 App Router Best Practices**
   - **Decision**: Use App Router with React Server Components for static pages, Client Components for interactive dashboard
   - **Rationale**: App Router provides file-based routing, nested layouts, and better performance via RSC
   - **Alternatives Considered**: Pages Router (deprecated in Next.js 15+), React Router (no SSR benefits)

2. **MSW v2 Setup & API Simulation Patterns**
   - **Decision**: Use MSW with in-memory database (`lib/msw/db.ts`) for realistic CRUD operations
   - **Rationale**: MSW intercepts network requests seamlessly in both dev and test environments (FR-057)
   - **Alternatives Considered**: JSON Server (requires separate server process), Mirage.js (heavier, less maintained)

3. **TanStack Query + Zustand Integration**
   - **Decision**: TanStack Query for server-state (tasks, notes), Zustand for client UI state (sidebar, focus mode)
   - **Rationale**: Clear separation of concerns; TanStack Query handles cache invalidation, Zustand handles ephemeral UI state
   - **Alternatives Considered**: Redux Toolkit (more boilerplate), React Context (no built-in caching or optimistic updates)

4. **Zod Schema-First Development**
   - **Decision**: Centralize all schemas in `lib/schemas/`, generate TypeScript types via `z.infer<typeof schema>`
   - **Rationale**: Single source of truth for validation (FR-062); runtime validation + compile-time types
   - **Alternatives Considered**: TypeScript-only types (no runtime validation), Yup (less TypeScript integration)

5. **Radix UI + Tailwind Dark Mode**
   - **Decision**: Radix UI for accessible primitives, Tailwind CSS with custom dark palette, no light mode (FR-049)
   - **Rationale**: Radix provides WAI-ARIA compliant components; Tailwind enables rapid styling with strict dark theme
   - **Alternatives Considered**: Headless UI (less comprehensive), Material UI (opinionated design, conflicts with glassmorphism)

6. **Framer Motion Animation Patterns**
   - **Decision**: Use Framer Motion variants for page transitions, component entry/exit, and milestone animations
   - **Rationale**: Declarative API with built-in `prefers-reduced-motion` support (FR-054); ≤200ms durations (FR-053)
   - **Alternatives Considered**: React Spring (more complex API), CSS transitions (no JS control for complex sequences)

7. **React Testing Library + MSW Testing Strategy**
   - **Decision**: RTL for component tests, MSW for API mocking, integration tests for user flows (Given-When-Then)
   - **Rationale**: RTL enforces accessibility testing (query by role); MSW reuses same handlers in tests and dev
   - **Alternatives Considered**: Enzyme (deprecated), Cypress (E2E overkill for frontend-only app)

8. **Voice Recording with Web Audio API**
   - **Decision**: Use Web Speech API for transcription, Web Audio API for waveform visualization (FR-018)
   - **Rationale**: Native browser APIs; no external dependencies for voice recording
   - **Alternatives Considered**: Cloud speech APIs (adds latency, costs), Wavesurfer.js (overkill for simple waveform)

9. **AI API Proxy Pattern**
   - **Decision**: All AI calls proxied through Next.js API routes (`/api/ai/parse-note`, `/api/ai/generate-sub-tasks`)
   - **Rationale**: Keeps API keys server-side (FR-075), enables rate limiting and logging (FR-074)
   - **Alternatives Considered**: Direct client calls (exposes keys), separate backend (adds infrastructure complexity)

10. **LocalStorage vs. MSW Persistence Strategy**
    - **Decision**: localStorage ONLY for sidebar state and theme preferences (FR-060); all task data in MSW ephemeral storage
    - **Rationale**: Simplifies state management; ephemeral optimistic updates (FR-059); no localStorage quota issues
    - **Alternatives Considered**: IndexedDB (overkill for UI preferences), SessionStorage (lost on tab close)

**Done Criteria**:
- ✅ All Technical Context fields specified (no "NEEDS CLARIFICATION" remaining)
- ✅ Technology stack validated with rationale for each choice
- ✅ Best practices documented for Next.js, MSW, TanStack Query, Zod, Radix UI, Framer Motion, RTL
- ✅ Alternatives considered and rejected with justification

## Phase 1: Design & API Contracts

**Goal**: Define data model, API contracts, and development environment setup.

**Status**: 🔄 IN PROGRESS (generated during this planning session)

**Deliverables**:
- `data-model.md` - Entity schemas, relationships, state transitions
- `contracts/*.yaml` - OpenAPI-style API contract definitions
- `quickstart.md` - Local development setup guide

### Phase 1.1: Data Model Design

**Entity Extraction** (from spec.md Key Entities section):

1. **Task Entity**
   - Unique identifier: Client-generated UUID (v4)
   - Core fields: title (string, 1-200 chars), description (string, optional, max 2000 chars), priority (enum: "low" | "medium" | "high"), estimatedDuration (number, minutes), tags (string[], freeform with autocomplete history), completionStatus (boolean, default false)
   - Temporal fields: createdAt (ISO 8601 timestamp), completedAt (ISO 8601 timestamp, nullable, required when archived=true), dueDate (ISO 8601 timestamp, nullable, distinct from reminder), reminder (ISO 8601 timestamp, nullable)
   - State flags: hidden (boolean, default false, mutually exclusive with archived), archived (boolean, default false, requires completionStatus=true)
   - Relationships: parentTaskId (UUID, nullable, references Task.id for sub-tasks), subTasks (array of SubTask IDs, computed relationship)
   - Recurrence: recurrenceSettings (object, nullable, contains intervalType, intervalValue, endDate)

2. **SubTask Entity**
   - Unique identifier: Client-generated UUID (v4)
   - Core fields: title (string, 1-200 chars), completionStatus (boolean, default false)
   - Temporal fields: createdAt (ISO 8601 timestamp)
   - Relationships: parentTaskId (UUID, required, references Task.id, cannot reference another SubTask)

3. **Note Entity**
   - Unique identifier: Client-generated UUID (v4)
   - Core fields: content (string, 1-10000 chars)
   - Temporal fields: createdAt (ISO 8601 timestamp)
   - State flags: archived (boolean, default false)
   - Metadata: voiceTranscriptionMetadata (object, nullable, contains recordingDuration, transcriptionService, confidence score)

4. **User Profile Entity**
   - Unique identifier: Client-generated UUID (v4, or auth provider ID)
   - Core fields: name (string, 1-100 chars), email (string, email format)
   - Preferences: sidebarCollapsed (boolean, default false), themeAccentColor (string, hex color code)
   - Onboarding: isFirstLogin (boolean, default true), walkthroughCompletedAt (ISO 8601 timestamp, nullable)

5. **Achievement Entity**
   - Unique identifier: User ID (one achievement record per user)
   - Metrics: highPrioritySLays (number, count of completed high-priority tasks), consistencyStreakDays (number, current streak length), lastCompletionDate (ISO 8601 date, for streak calculation), graceDay (boolean, true if user missed 1 day but streak preserved), completionRatio (number, 0-100, calculated as completedTasks / totalTasks × 100)
   - Milestones: milestones (array of objects, each contains threshold [number], unlockedAt [ISO 8601 timestamp, nullable])

6. **AI Interaction Log Entity**
   - Unique identifier: Client-generated UUID (v4)
   - Core fields: requestType (enum: "note-to-task" | "generate-sub-tasks"), promptText (string), responseText (string), timestamp (ISO 8601 timestamp), associatedEntityId (UUID, references Task or Note)
   - Immutability: Logs are append-only; no updates or deletes allowed

7. **Recurrence Settings (Embedded in Task)**
   - Fields: intervalType (enum: "daily" | "weekly" | "monthly" | "custom"), intervalValue (number, integer ≥1), endDate (ISO 8601 timestamp, nullable)

**State Transitions**:
```
Task State Machine:
  [New] → [Active] (default state, visible in task list)
  [Active] → [Hidden] (user hides task, FR-005)
  [Hidden] → [Active] (user unhides task via Settings, FR-007)
  [Hidden] → [Deleted] (permanent deletion via Settings, FR-007)
  [Active] → [Completed] (user marks complete)
  [Completed] → [Archived] (manual or automatic, irreversible, FR-077)
  [Hidden] → [Active] → [Completed] → [Archived] (multi-step path)

Sub-task State Machine:
  [New] → [Active] (default state)
  [Active] → [Completed] (user marks complete)
  [Completed] → [Active] (user unchecks, task progress recalculates)

Note State Machine:
  [New] → [Active] (default state)
  [Active] → [Archived] (manual via archive action)
  [Active] → [Converted] (converted to task, note archived, FR-022)

Focus Mode State Machine:
  [Inactive] → [Active] (user clicks target icon on task, FR-010)
  [Active] → [Inactive] (manual exit, FR-013)
  [Active] → [Inactive] (task completed, FR-014)
  [Active] → [Inactive] (countdown reaches zero, FR-016)

Consistency Streak State Machine:
  [Active] → [Active] (user completes task today, increment or maintain)
  [Active] → [Grace] (user misses 1 day, grace day activated, FR-033)
  [Grace] → [Active] (user completes task within grace period)
  [Grace] → [Broken] (user misses 2+ consecutive days)
  [Broken] → [Active] (user completes task, streak resets to 1)
```

**Done Criteria**:
- ✅ All entities documented with field types, constraints, and relationships
- ✅ State transitions defined as state machines with valid paths
- ✅ Validation rules extracted from functional requirements
- ✅ `data-model.md` file created in `specs/002-perpetua-frontend/`

### Phase 1.2: API Contract Definition

**Endpoint Design** (RESTful, organized by resource):

**Tasks Resource** (`contracts/tasks.yaml`):
- `POST /api/tasks` - Create task (201, location header, returns Task)
- `GET /api/tasks` - List tasks with filters (200, query params: hidden, archived, priority)
- `GET /api/tasks/:id` - Get single task (200 or 404)
- `PATCH /api/tasks/:id` - Update task (200 or 404, partial updates allowed)
- `DELETE /api/tasks/:id` - Soft-delete task (204 or 404, sets hidden=true)
- `POST /api/tasks/:id/sub-tasks` - Add sub-task (201, returns SubTask)
- `PATCH /api/tasks/:id/sub-tasks/:subTaskId` - Update sub-task (200 or 404)
- `DELETE /api/tasks/:id/sub-tasks/:subTaskId` - Delete sub-task (204 or 404)
- `POST /api/tasks/:id/focus` - Activate Focus Mode (200, returns focus session)
- `DELETE /api/tasks/:id/focus` - Exit Focus Mode (204)
- `POST /api/tasks/:id/archive` - Archive task (200 or 400 if not completed)

**Notes Resource** (`contracts/notes.yaml`):
- `POST /api/notes` - Create note (201, location header, returns Note)
- `GET /api/notes` - List notes (200, query params: archived)
- `GET /api/notes/:id` - Get single note (200 or 404)
- `PATCH /api/notes/:id` - Update note content (200 or 404)
- `DELETE /api/notes/:id` - Soft-delete note (204, sets archived=true)
- `POST /api/notes/:id/voice` - Upload voice transcription (200, updates voiceTranscriptionMetadata)

**AI Resource** (`contracts/ai.yaml`):
- `POST /api/ai/parse-note` - Parse note into task fields (200, streaming disabled, returns structured task fields)
- `POST /api/ai/generate-sub-tasks` - Generate sub-tasks for task (200, Server-Sent Events stream, returns array of sub-task suggestions)

**Achievements Resource** (`contracts/achievements.yaml`):
- `GET /api/achievements` - Get current user metrics (200, returns Achievement)
- `PATCH /api/achievements` - Recalculate metrics (200, triggered after task completion, returns updated Achievement)

**Search Resource** (`contracts/search.yaml`):
- `GET /api/search?q=<query>` - Global search across entities (200, returns grouped results by type)

**User Profile Resource** (`contracts/user.yaml`):
- `GET /api/user/profile` - Get current user profile (200, returns UserProfile)
- `PATCH /api/user/profile` - Update user preferences (200, returns updated UserProfile)
- `POST /api/user/walkthrough/complete` - Mark walkthrough as completed (200)

**Done Criteria**:
- ✅ All endpoints documented with HTTP methods, paths, request/response schemas
- ✅ OpenAPI-style YAML contracts created in `specs/002-perpetua-frontend/contracts/`
- ✅ Error responses documented for each endpoint (see Section 5.1)
- ✅ MSW handler mapping defined for each endpoint

### Phase 1.3: Quickstart & Environment Setup

**Development Environment Requirements**:
- Node.js 18+ (LTS) or 20+
- Package manager: npm, yarn, or pnpm (recommended)
- VS Code (recommended) with extensions: ESLint, Prettier, Tailwind CSS IntelliSense

**Initial Setup Steps**:
1. Clone repository and checkout `002-perpetua-frontend` branch
2. Install dependencies: `pnpm install`
3. Copy `.env.example` to `.env.local` and configure:
   - `NEXT_PUBLIC_AI_API_KEY` (OpenAI or Claude API key for AI features)
   - `NEXT_PUBLIC_AI_COOLDOWN_MS` (default 900000 = 15 minutes)
   - `NEXT_PUBLIC_ENABLE_MSW` (default true for development)
4. Run development server: `pnpm dev` (starts Next.js on http://localhost:3000)
5. Run tests: `pnpm test` (Jest + RTL)
6. Run type check: `pnpm type-check` (TypeScript compiler)
7. Run linting: `pnpm lint` (ESLint + Prettier)

**MSW Initialization**:
- MSW automatically initializes in development via `src/lib/msw/browser.ts` imported in `src/app/layout.tsx`
- Mock database seeded with sample tasks, notes, and user profile on first load
- MSW DevTools panel visible in browser console for debugging intercepted requests

**Done Criteria**:
- ✅ `quickstart.md` created with setup instructions
- ✅ `.env.example` file created with all required variables documented
- ✅ MSW browser setup configured in `src/lib/msw/browser.ts`
- ✅ Sample data seed script created for initial development

### Phase 1.4: Agent Context Update

**Agent Type Detection**: Claude (claude-code environment detected)

**Context File**: `.specify/memory/agent-context.md` (or `.claude/context.md` if using Claude-specific directory)

**New Technologies to Add**:
- Next.js 15 App Router (file-based routing, React Server Components, nested layouts)
- TanStack Query v5 (server-state management, optimistic updates, cache invalidation)
- Zustand v4 (client UI state management, lightweight alternative to Redux)
- Mock Service Worker v2 (API mocking, request interception, in-memory database simulation)
- Zod v3 (runtime validation, TypeScript inference, schema-first development)
- Framer Motion v11 (declarative animations, prefers-reduced-motion support, gesture handling)
- Radix UI (headless accessible components, WAI-ARIA compliant, Popover, Dialog, Dropdown)
- driver.js (interactive onboarding walkthroughs, step-by-step tutorials)
- React Testing Library (user-centric testing, accessibility queries, async utilities)
- Jest (test runner, assertion library, snapshot testing, coverage reporting)
- @testing-library/user-event (user interaction simulation, keyboard navigation, form input)
- @testing-library/jest-dom (custom DOM matchers, accessibility assertions)
- Web Speech API (voice recognition, speech-to-text transcription)
- Web Audio API (audio recording, waveform visualization, microphone access)
- Tailwind CSS (utility-first styling, dark mode support, custom theme configuration)

**Update Command**:
```bash
powershell.exe -ExecutionPolicy Bypass -File .specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Done Criteria**:
- ✅ Agent context file updated with new technologies (preserving manual additions between markers)
- ✅ Technology descriptions include usage patterns and common pitfalls
- ✅ Agent can reference updated context for future feature development

## Phase 2: Implementation Task Generation

**Note**: Phase 2 (task generation) is **NOT** executed by `/sp.plan`. This section documents what `/sp.tasks` will generate.

**Deliverable**: `tasks.md` (created by `/sp.tasks` command after Phase 1 completion)

**Task Organization** (TDD Red-Green-Refactor):
1. **Setup & Infrastructure Tasks** (foundation for all features)
   - Setup Next.js project with TypeScript, Tailwind, ESLint, Prettier
   - Configure MSW with in-memory database and browser initialization
   - Define Zod schemas for all entities (Task, SubTask, Note, UserProfile, Achievement, AI Log)
   - Create MSW handlers for all API endpoints
   - Setup React Testing Library with Jest and custom matchers
   - Configure Framer Motion with prefers-reduced-motion support
   - Setup Radix UI primitives (Popover, Dialog, Dropdown)
   - Implement environment variable validation (blocks startup if keys missing)

2. **Core Task Management Tasks** (P1 - User Story 1)
   - RED: Write tests for TaskForm component (rendering, validation, submission)
   - GREEN: Implement TaskForm component (title, description, priority, duration, tags, recurrence)
   - REFACTOR: Extract tag autocomplete logic into reusable hook
   - RED: Write tests for TaskList component (display, filtering, progress calculation)
   - GREEN: Implement TaskList component with TanStack Query hooks
   - REFACTOR: Optimize rendering with React.memo and useMemo
   - RED: Write tests for SubTaskList component (add, complete, progress calculation)
   - GREEN: Implement SubTaskList component with optimistic updates
   - REFACTOR: Extract progress calculation into utility function
   - RED: Write tests for hidden task functionality (hide, unhide, delete via Settings)
   - GREEN: Implement hidden task state management in Zustand store
   - REFACTOR: Extract task filtering logic into custom hook

3. **Dashboard Layout & Navigation Tasks** (P1 - User Story 8)
   - RED: Write tests for Sidebar component (collapse, persist state, route highlighting)
   - GREEN: Implement Sidebar component with Zustand store for collapse state
   - REFACTOR: Extract localStorage persistence logic into custom hook
   - RED: Write tests for ProfilePopover component (display, click-outside, disabled in Focus Mode)
   - GREEN: Implement ProfilePopover using Radix UI Popover primitive
   - REFACTOR: Extract user profile logic into custom hook
   - RED: Write tests for route navigation (dashboard/tasks, dashboard/notes, dashboard/achievements, etc.)
   - GREEN: Implement Next.js App Router layout with nested routes
   - REFACTOR: Extract layout logic into reusable components

4. **Focus Mode Tasks** (P2 - User Story 2)
   - RED: Write tests for FocusMode component (activate, countdown, manual exit, auto-exit on completion)
   - GREEN: Implement FocusMode component with Zustand store for active task state
   - REFACTOR: Extract countdown timer logic into custom hook
   - RED: Write tests for Focus Mode UI changes (sidebar hidden, other tasks hidden)
   - GREEN: Implement conditional rendering based on Focus Mode state
   - REFACTOR: Extract Focus Mode CSS classes into Tailwind utilities
   - RED: Write tests for Focus Mode alert (audio/visual when countdown reaches zero)
   - GREEN: Implement alert notification using Web Notification API
   - REFACTOR: Extract notification logic into utility function

5. **AI Quick Notes & Conversion Tasks** (P2 - User Story 3)
   - RED: Write tests for NoteEditor component (create, edit, voice recording)
   - GREEN: Implement NoteEditor component with TanStack Query hooks
   - REFACTOR: Extract note CRUD logic into custom hook
   - RED: Write tests for VoiceRecorder component (start recording, stop recording, waveform visualization, transcription)
   - GREEN: Implement VoiceRecorder using Web Speech API and Web Audio API
   - REFACTOR: Extract waveform visualization logic into utility function
   - RED: Write tests for NoteToTaskDrawer component (AI parsing, field pre-fill, user confirmation)
   - GREEN: Implement NoteToTaskDrawer using Radix UI Drawer and AI API proxy
   - REFACTOR: Extract AI parsing logic into custom hook
   - RED: Write tests for AI interaction logging (prompt, response, timestamp, entity ID)
   - GREEN: Implement AI logging in MSW handler with immutable append-only storage
   - REFACTOR: Extract AI logging logic into utility function

6. **AI Sub-task Generation Tasks** (P3 - User Story 4)
   - RED: Write tests for MagicSubTasks component (generate button, streaming output, confirmation prompt)
   - GREEN: Implement MagicSubTasks component with Server-Sent Events (SSE) handling
   - REFACTOR: Extract SSE handling logic into custom hook
   - RED: Write tests for AI rate limiting (error display, feature disable, cooldown retry)
   - GREEN: Implement AI rate limiting in MSW handler with cooldown period from .env
   - REFACTOR: Extract rate limit logic into middleware function
   - RED: Write tests for partial output preservation on AI failure
   - GREEN: Implement error handling with partial state preservation
   - REFACTOR: Extract error recovery logic into utility function

7. **Achievements & Metrics Tasks** (P3 - User Story 5)
   - RED: Write tests for MetricCard component (display, shimmer animation, milestone feedback)
   - GREEN: Implement MetricCard component with Framer Motion animations
   - REFACTOR: Extract animation variants into shared configuration
   - RED: Write tests for achievement calculations (High Priority Slays, Consistency Streak, Completion Ratio)
   - GREEN: Implement achievement calculations in MSW handler triggered by task completion
   - REFACTOR: Extract calculation logic into pure functions
   - RED: Write tests for Consistency Streak logic (daily completion, grace day, UTC midnight reset)
   - GREEN: Implement Consistency Streak logic with grace day handling
   - REFACTOR: Extract date comparison logic into utility function

8. **Global Search Tasks** (P2 - User Story 7)
   - RED: Write tests for GlobalSearch component (input, grouped results, navigation)
   - GREEN: Implement GlobalSearch component with debounced search query
   - REFACTOR: Extract debounce logic into custom hook
   - RED: Write tests for search result grouping (tasks, notes, archived tasks, achievements)
   - GREEN: Implement search result grouping in MSW handler
   - REFACTOR: Extract grouping logic into utility function

9. **Onboarding Walkthrough Tasks** (P3 - User Story 6)
   - RED: Write tests for Walkthrough component (auto-start on first login, step progression, tutorial task creation)
   - GREEN: Implement Walkthrough component using driver.js
   - REFACTOR: Extract walkthrough steps configuration into JSON file
   - RED: Write tests for tutorial task creation (permanent, archivable, non-deletable)
   - GREEN: Implement tutorial task creation logic with special flag in MSW database
   - REFACTOR: Extract tutorial task logic into utility function
   - RED: Write tests for walkthrough replay from Settings
   - GREEN: Implement replay functionality with state reset
   - REFACTOR: Extract replay logic into custom hook

10. **Public Pages Tasks** (FR-064 through FR-067)
    - RED: Write tests for Landing page (animated gradient mesh, glassmorphic cards)
    - GREEN: Implement Landing page with Framer Motion animations
    - REFACTOR: Extract gradient mesh logic into reusable component
    - RED: Write tests for Pricing, Contact, About pages (dark aesthetic, consistent layout)
    - GREEN: Implement public pages with shared layout component
    - REFACTOR: Extract shared layout logic into reusable component
    - RED: Write tests for Footer component (social links, legal pages)
    - GREEN: Implement Footer component with dynamic link generation
    - REFACTOR: Extract footer configuration into JSON file

11. **Settings & Configuration Tasks** (FR-075)
    - RED: Write tests for Settings page (AI cooldown, notification preferences, tutorial replay, hidden tasks)
    - GREEN: Implement Settings page with form validation using Zod
    - REFACTOR: Extract settings form logic into custom hook
    - RED: Write tests for hidden task management (list, unhide, delete)
    - GREEN: Implement hidden task management interface
    - REFACTOR: Extract hidden task logic into custom hook

12. **Archive & Task Management Tasks** (FR-077)
    - RED: Write tests for Archive page (list archived tasks, prevent unarchive)
    - GREEN: Implement Archive page with TanStack Query hooks
    - REFACTOR: Extract archive filtering logic into custom hook
    - RED: Write tests for archive state transitions (completed → archived, immutable)
    - GREEN: Implement archive logic in MSW handler with immutability checks
    - REFACTOR: Extract state transition validation into utility function

**Done Criteria**:
- Tasks organized in dependency order (setup → core features → advanced features)
- Each task follows Red-Green-Refactor TDD cycle
- Each task has clear acceptance criteria from spec.md
- Tasks reference specific functional requirements (FR-XXX)
- Estimated effort and dependencies documented for each task

## Section 5: API Contract Details

### 5.1 Error Response Documentation

All API endpoints follow a standardized error response format for consistency and debuggability.

**Standard Error Response Shape**:
```json
{
  "error": {
    "code": "ERROR_CODE_SNAKE_CASE",
    "message": "Human-readable error description",
    "details": {
      "field": "specificField",
      "value": "invalidValue",
      "constraint": "validation rule that was violated"
    },
    "timestamp": "2026-01-08T12:34:56.789Z",
    "requestId": "uuid-v4-request-identifier"
  }
}
```

**HTTP Status Codes & Error Codes**:

| Status | Error Code | Description | Recovery Action |
|--------|-----------|-------------|-----------------|
| 400 | `VALIDATION_ERROR` | Request body fails Zod schema validation | Display field-level errors; user corrects input |
| 400 | `INVALID_STATE_TRANSITION` | Action violates state machine rules (e.g., archive incomplete task) | Display error message; guide user to valid action (complete task first) |
| 400 | `ORPHANED_SUBTASK` | Attempt to create sub-task without valid parent task | Display error; prompt user to select parent task |
| 400 | `NESTING_LIMIT_EXCEEDED` | Attempt to create sub-task of sub-task | Display error; explain one-level nesting limit |
| 401 | `AUTHENTICATION_REQUIRED` | User not authenticated or token expired | Redirect to login page; preserve current route for post-login redirect |
| 403 | `FORBIDDEN` | User lacks permission for action (e.g., edit another user's task) | Display error; disable action in UI |
| 404 | `RESOURCE_NOT_FOUND` | Task, note, or user profile does not exist | Display "Not Found" message; redirect to list view |
| 409 | `CONFLICT` | Optimistic update conflict (server state differs from client) | Discard optimistic update; refetch server state; display notification |
| 422 | `UNPROCESSABLE_ENTITY` | Business logic validation fails (e.g., archive task without completion) | Display error; explain prerequisite action |
| 429 | `RATE_LIMIT_EXCEEDED` | AI rate limit or quota exhausted (FR-028) | Display cooldown timer; disable AI features temporarily; auto-retry after cooldown |
| 500 | `INTERNAL_SERVER_ERROR` | Unhandled exception in MSW handler | Display generic error; log to console; retry with exponential backoff |
| 503 | `SERVICE_UNAVAILABLE` | AI service unavailable or timeout | Display error; suggest manual task creation; retry after delay |

**AI-Specific Error Codes**:

| Error Code | Status | Description | Recovery Action |
|-----------|--------|-------------|-----------------|
| `AI_RATE_LIMIT_EXCEEDED` | 429 | User exceeded AI calls per hour/day | Display cooldown message; show time until retry available; disable AI buttons |
| `AI_QUOTA_EXHAUSTED` | 429 | Monthly AI quota exhausted | Display upgrade prompt; disable AI features until quota reset |
| `AI_PARSING_FAILED` | 422 | AI could not parse note into task fields | Display error; allow manual task creation from note content |
| `AI_GENERATION_TIMEOUT` | 503 | Sub-task generation exceeded 30s timeout | Preserve partial output; display error; allow manual sub-task addition |
| `AI_INVALID_RESPONSE` | 500 | AI returned malformed response | Display error; log full response for debugging; retry with different prompt |
| `AI_CONTENT_POLICY_VIOLATION` | 400 | AI rejected prompt due to content policy | Display policy violation message; allow user to edit prompt |

**Voice Recording Error Codes**:

| Error Code | Status | Description | Recovery Action |
|-----------|--------|-------------|-----------------|
| `MICROPHONE_PERMISSION_DENIED` | 403 | User denied microphone access | Display permission instructions; provide link to browser settings |
| `MICROPHONE_NOT_AVAILABLE` | 503 | No microphone detected or hardware issue | Display error; suggest checking device connections |
| `TRANSCRIPTION_FAILED` | 422 | Speech-to-text service failed or returned empty result | Display error; allow manual text entry |
| `TRANSCRIPTION_LOW_CONFIDENCE` | 200 | Transcription completed but confidence <50% | Display warning; highlight low-confidence text; allow editing |
| `RECORDING_TOO_SHORT` | 400 | Recording <1 second, likely accidental | Display error; suggest recording longer audio |
| `RECORDING_TOO_LONG` | 400 | Recording exceeded 5-minute limit (FR-018) | Auto-stop recording; display warning; transcribe captured audio |

**Validation Error Details**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "task.title",
      "value": "",
      "constraint": "String must contain at least 1 character(s)",
      "zodError": {
        "issues": [
          {
            "code": "too_small",
            "minimum": 1,
            "type": "string",
            "inclusive": true,
            "message": "String must contain at least 1 character(s)",
            "path": ["title"]
          }
        ]
      }
    },
    "timestamp": "2026-01-08T12:34:56.789Z",
    "requestId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Client-Side Error Handling Strategy**:
1. **Validation Errors (400)**: Display field-level errors inline; highlight invalid fields; prevent form submission until corrected
2. **Authentication Errors (401)**: Clear local auth token; redirect to login; preserve intended destination for post-login redirect
3. **Not Found Errors (404)**: Display user-friendly "Not Found" message; offer navigation to list view or dashboard
4. **Conflict Errors (409)**: Discard optimistic update; refetch server state; display toast notification explaining server state took precedence
5. **Rate Limit Errors (429)**: Display countdown timer; disable AI features; store retry timestamp in localStorage; auto-enable after cooldown
6. **Server Errors (500/503)**: Display generic error message; log full error to console for debugging; retry with exponential backoff (1s, 2s, 4s, max 10s)

**MSW Handler Error Simulation**:
- MSW handlers MUST simulate realistic error scenarios for testing
- Random error injection: 5% chance of 500 error, 2% chance of 503 error (configurable via `.env`)
- AI rate limiting: Configurable threshold (default 10 calls per 15 minutes) with automatic reset
- Validation errors: Test all Zod schema constraints with invalid payloads

**Error Logging & Monitoring**:
- All errors logged to console with full context (request ID, user ID, endpoint, payload)
- AI errors include prompt text, response text, and full error object (FR-074)
- Error logs formatted for easy parsing by external monitoring tools (structured JSON)

## Section 6: State Management Architecture

### 6.1 TanStack Query (Server State)

**Purpose**: Manage server-like state (tasks, notes, achievements) with caching, optimistic updates, and automatic refetching.

**Query Keys Structure**:
```typescript
// Task queries
['tasks'] // List all tasks
['tasks', { hidden: true }] // Filtered list
['tasks', { archived: true }] // Archived tasks
['tasks', taskId] // Single task detail
['tasks', taskId, 'sub-tasks'] // Sub-tasks for task

// Note queries
['notes'] // List all notes
['notes', { archived: true }] // Archived notes
['notes', noteId] // Single note detail

// Achievement queries
['achievements'] // Current user metrics

// Search queries
['search', query] // Global search results
```

**Mutation Patterns**:
```typescript
// Optimistic update pattern (task completion)
const mutation = useMutation({
  mutationFn: (taskId) => api.patch(`/tasks/${taskId}`, { completionStatus: true }),
  onMutate: async (taskId) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['tasks', taskId] });

    // Snapshot previous value
    const previousTask = queryClient.getQueryData(['tasks', taskId]);

    // Optimistically update to new value
    queryClient.setQueryData(['tasks', taskId], (old) => ({
      ...old,
      completionStatus: true,
      completedAt: new Date().toISOString()
    }));

    // Return snapshot for rollback
    return { previousTask };
  },
  onError: (err, taskId, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks', taskId], context.previousTask);
  },
  onSettled: (taskId) => {
    // Always refetch to ensure sync with server
    queryClient.invalidateQueries({ queryKey: ['tasks', taskId] });
    queryClient.invalidateQueries({ queryKey: ['achievements'] }); // Recalculate metrics
  }
});
```

**Cache Configuration**:
- `staleTime`: 5 minutes (data considered fresh for 5 minutes before refetch)
- `cacheTime`: 10 minutes (unused data garbage collected after 10 minutes)
- `refetchOnWindowFocus`: true (refetch when user returns to tab)
- `refetchOnReconnect`: true (refetch when network reconnects)
- `retry`: 3 (retry failed requests up to 3 times with exponential backoff)

### 6.2 Zustand (Client UI State)

**Purpose**: Manage ephemeral UI state (sidebar collapse, focus mode, onboarding) that doesn't persist to server.

**Store Structure**:
```typescript
// Sidebar store (persisted to localStorage)
interface SidebarStore {
  isCollapsed: boolean;
  toggleCollapse: () => void;
}

// Focus Mode store (ephemeral, resets on reload)
interface FocusModeStore {
  activeTaskId: string | null;
  countdownEndTime: number | null; // Unix timestamp
  activateFocusMode: (taskId: string, durationMinutes: number) => void;
  exitFocusMode: () => void;
  isInFocusMode: boolean; // Computed from activeTaskId
}

// Onboarding store (persisted to localStorage)
interface OnboardingStore {
  walkthroughStep: number;
  isWalkthroughActive: boolean;
  startWalkthrough: () => void;
  nextStep: () => void;
  completeWalkthrough: () => void;
  replayWalkthrough: () => void;
}

// AI Feature store (ephemeral, tracks cooldown state)
interface AIFeatureStore {
  isAIDisabled: boolean;
  cooldownEndTime: number | null; // Unix timestamp
  triggerCooldown: (durationMs: number) => void;
  checkCooldownStatus: () => boolean; // True if still in cooldown
}
```

**Persistence Strategy**:
- Sidebar collapse state: Persisted to `localStorage.sidebarCollapsed` (boolean)
- Onboarding state: Persisted to `localStorage.walkthroughCompleted` (boolean)
- Focus Mode state: NOT persisted (ephemeral, resets on page reload)
- AI cooldown state: Persisted to `localStorage.aiCooldownEndTime` (Unix timestamp)

### 6.3 Undo Mechanism

**Scope**: Undo is guaranteed for all mutations performed during the current session until the next mutation occurs (Constitution Section III.4).

**Implementation**:
```typescript
interface UndoStore {
  undoStack: Array<{
    mutationType: 'CREATE' | 'UPDATE' | 'DELETE';
    entityType: 'task' | 'note' | 'sub-task';
    entityId: string;
    previousState: any; // Snapshot of entity before mutation
    timestamp: number;
  }>;
  pushUndo: (entry) => void;
  popUndo: () => void; // Removes top entry when new mutation occurs
  executeUndo: () => Promise<void>; // Reverts last mutation
}

// Undo popup component (appears after successful mutation)
<UndoPopup
  message="Task marked as complete"
  onUndo={async () => {
    await undoStore.executeUndo();
    toast.success('Action undone');
  }}
  timeout={5000} // Auto-dismiss after 5 seconds
/>
```

**Undo Limitations**:
- Only the most recent mutation can be undone (no multi-level undo stack)
- Undo is invalid once a new mutation occurs (stack is cleared)
- Undo is not available after page reload (ephemeral session state)

## Section 7: Environment Configuration

### 7.1 Required Environment Variables

**Development (`.env.local`)**:
```bash
# AI API Configuration
NEXT_PUBLIC_AI_API_KEY=sk-... # OpenAI or Claude API key (REQUIRED)
NEXT_PUBLIC_AI_API_BASE_URL=https://api.openai.com/v1 # Default OpenAI endpoint
NEXT_PUBLIC_AI_MODEL=gpt-4-turbo-preview # AI model for parsing and generation

# AI Rate Limiting
NEXT_PUBLIC_AI_COOLDOWN_MS=900000 # 15 minutes (FR-028)
NEXT_PUBLIC_AI_MAX_CALLS_PER_WINDOW=10 # Max calls before cooldown
NEXT_PUBLIC_AI_WINDOW_DURATION_MS=900000 # Time window for rate limit

# MSW Configuration
NEXT_PUBLIC_ENABLE_MSW=true # Enable MSW in development (default true)
NEXT_PUBLIC_MSW_LATENCY_MIN=100 # Min simulated latency (ms)
NEXT_PUBLIC_MSW_LATENCY_MAX=500 # Max simulated latency (ms)
NEXT_PUBLIC_MSW_ERROR_RATE=0.05 # 5% random error injection for testing

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE_RECORDING=true # Enable voice features (FR-017)
NEXT_PUBLIC_ENABLE_AI_SUB_TASKS=true # Enable Magic Sub-tasks (FR-022)
NEXT_PUBLIC_ENABLE_ACHIEVEMENTS=true # Enable achievements tracking (FR-029)
NEXT_PUBLIC_ENABLE_ONBOARDING=true # Enable walkthrough (FR-044)

# Logging
NEXT_PUBLIC_LOG_LEVEL=debug # Console log level (debug, info, warn, error)
NEXT_PUBLIC_LOG_AI_INTERACTIONS=true # Log AI prompts and responses (FR-074)

# Notification Configuration
NEXT_PUBLIC_ENABLE_BROWSER_NOTIFICATIONS=true # Request notification permission
NEXT_PUBLIC_NOTIFICATION_SOUND_URL=/sounds/notification.mp3 # Alert sound for Focus Mode timer
```

**Production (`.env.production`)**:
```bash
# AI API Configuration (same as dev, different keys)
NEXT_PUBLIC_AI_API_KEY=sk-prod-... # Production API key
NEXT_PUBLIC_AI_API_BASE_URL=https://api.openai.com/v1
NEXT_PUBLIC_AI_MODEL=gpt-4-turbo-preview

# AI Rate Limiting (stricter in production)
NEXT_PUBLIC_AI_COOLDOWN_MS=1800000 # 30 minutes
NEXT_PUBLIC_AI_MAX_CALLS_PER_WINDOW=5
NEXT_PUBLIC_AI_WINDOW_DURATION_MS=3600000 # 1 hour window

# MSW Configuration (disabled in production)
NEXT_PUBLIC_ENABLE_MSW=false # MSW only for dev/test

# Feature Flags (stable features only)
NEXT_PUBLIC_ENABLE_VOICE_RECORDING=true
NEXT_PUBLIC_ENABLE_AI_SUB_TASKS=true
NEXT_PUBLIC_ENABLE_ACHIEVEMENTS=true
NEXT_PUBLIC_ENABLE_ONBOARDING=true

# Logging (minimal in production)
NEXT_PUBLIC_LOG_LEVEL=error
NEXT_PUBLIC_LOG_AI_INTERACTIONS=false # Disable verbose AI logging

# Notification Configuration
NEXT_PUBLIC_ENABLE_BROWSER_NOTIFICATIONS=true
NEXT_PUBLIC_NOTIFICATION_SOUND_URL=/sounds/notification.mp3
```

### 7.2 Environment Variable Validation

**Startup Validator** (`src/lib/config.ts`):
```typescript
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_AI_API_KEY: z.string().min(1, 'AI API key is required'),
  NEXT_PUBLIC_AI_API_BASE_URL: z.string().url('AI API base URL must be valid'),
  NEXT_PUBLIC_AI_MODEL: z.string().min(1, 'AI model is required'),
  NEXT_PUBLIC_AI_COOLDOWN_MS: z.coerce.number().positive(),
  NEXT_PUBLIC_AI_MAX_CALLS_PER_WINDOW: z.coerce.number().positive(),
  NEXT_PUBLIC_AI_WINDOW_DURATION_MS: z.coerce.number().positive(),
  NEXT_PUBLIC_ENABLE_MSW: z.coerce.boolean().default(true),
  NEXT_PUBLIC_MSW_LATENCY_MIN: z.coerce.number().nonnegative().optional(),
  NEXT_PUBLIC_MSW_LATENCY_MAX: z.coerce.number().nonnegative().optional(),
  NEXT_PUBLIC_MSW_ERROR_RATE: z.coerce.number().min(0).max(1).optional(),
  NEXT_PUBLIC_ENABLE_VOICE_RECORDING: z.coerce.boolean().default(true),
  NEXT_PUBLIC_ENABLE_AI_SUB_TASKS: z.coerce.boolean().default(true),
  NEXT_PUBLIC_ENABLE_ACHIEVEMENTS: z.coerce.boolean().default(true),
  NEXT_PUBLIC_ENABLE_ONBOARDING: z.coerce.boolean().default(true),
  NEXT_PUBLIC_LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  NEXT_PUBLIC_LOG_AI_INTERACTIONS: z.coerce.boolean().default(false),
  NEXT_PUBLIC_ENABLE_BROWSER_NOTIFICATIONS: z.coerce.boolean().default(true),
  NEXT_PUBLIC_NOTIFICATION_SOUND_URL: z.string().optional(),
});

export const env = envSchema.parse(process.env);

// Throws ZodError with detailed validation errors if any required variables are missing or invalid
// Application startup is blocked until all validations pass (Constitution Section IX.2)
```

## Section 8: Testing Strategy

### 8.1 Test Organization

**Test Directory Structure**:
```text
tests/
├── components/           # Component unit tests
│   ├── dashboard/        # Dashboard-specific component tests
│   │   ├── Sidebar.test.tsx
│   │   ├── ProfilePopover.test.tsx
│   │   └── GlobalSearch.test.tsx
│   ├── tasks/            # Task-related component tests
│   │   ├── TaskList.test.tsx
│   │   ├── TaskForm.test.tsx
│   │   ├── TaskCard.test.tsx
│   │   ├── SubTaskList.test.tsx
│   │   ├── FocusMode.test.tsx
│   │   └── MagicSubTasks.test.tsx
│   ├── notes/            # Note-related component tests
│   │   ├── NoteEditor.test.tsx
│   │   ├── VoiceRecorder.test.tsx
│   │   └── NoteToTaskDrawer.test.tsx
│   └── achievements/     # Achievement component tests
│       ├── MetricCard.test.tsx
│       └── MilestoneAnimation.test.tsx
├── integration/          # Integration tests (user flows)
│   ├── task-creation-flow.test.tsx
│   ├── focus-mode-flow.test.tsx
│   ├── ai-note-conversion-flow.test.tsx
│   ├── global-search-flow.test.tsx
│   └── onboarding-flow.test.tsx
├── msw/                  # MSW handler tests
│   ├── tasks-handler.test.ts
│   ├── notes-handler.test.ts
│   ├── ai-handler.test.ts
│   └── achievements-handler.test.ts
├── schemas/              # Zod schema validation tests
│   ├── task-schema.test.ts
│   ├── note-schema.test.ts
│   └── ai-schema.test.ts
├── utils/                # Utility function tests
│   ├── validation.test.ts
│   ├── date.test.ts
│   └── animations.test.ts
└── setup.ts              # Test environment setup (MSW, matchers, global mocks)
```

### 8.2 Test Coverage Requirements

**Minimum Coverage Thresholds** (`jest.config.js`):
```javascript
module.exports = {
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80
    },
    './src/lib/schemas/': {
      statements: 100, // Schemas must be fully covered
      branches: 100,
      functions: 100,
      lines: 100
    },
    './src/lib/msw/handlers/': {
      statements: 90, // API handlers require high coverage
      branches: 85,
      functions: 90,
      lines: 90
    }
  }
};
```

### 8.3 TDD Red-Green-Refactor Workflow

**Example TDD Cycle** (Task Completion):
```typescript
// ========================================
// RED: Write failing test
// ========================================
describe('TaskCard - mark task as complete', () => {
  test('updates completion status when user clicks checkbox', async () => {
    // GIVEN: A task exists in the list
    const mockTask = {
      id: 'task-1',
      title: 'Finish report',
      completionStatus: false,
      priority: 'high'
    };
    render(<TaskCard task={mockTask} />);
    const checkbox = screen.getByRole('checkbox', { name: /finish report/i });

    // WHEN: User clicks the checkbox
    await userEvent.click(checkbox);

    // THEN: Task is marked complete and API is called
    expect(checkbox).toBeChecked();
    await waitFor(() => {
      expect(screen.getByText(/completed/i)).toBeInTheDocument();
    });
  });
});

// Test fails: TaskCard component doesn't exist yet
// Error: Cannot find module './TaskCard'

// ========================================
// GREEN: Write minimal code to pass test
// ========================================
export function TaskCard({ task }) {
  const [isComplete, setIsComplete] = useState(task.completionStatus);
  const mutation = useMutation({
    mutationFn: () => api.patch(`/tasks/${task.id}`, { completionStatus: true })
  });

  const handleCheckboxChange = () => {
    setIsComplete(true);
    mutation.mutate();
  };

  return (
    <div>
      <input
        type="checkbox"
        checked={isComplete}
        onChange={handleCheckboxChange}
        aria-label={task.title}
      />
      <span>{task.title}</span>
      {isComplete && <span>completed</span>}
    </div>
  );
}

// Test passes: Basic functionality works

// ========================================
// REFACTOR: Improve code quality
// ========================================
export function TaskCard({ task }) {
  const { mutate, isLoading } = useCompleteTask(task.id); // Extract mutation into custom hook
  const [isComplete, setIsComplete] = useState(task.completionStatus);

  const handleCheckboxChange = () => {
    setIsComplete(true);
    mutate({ completionStatus: true }, {
      onError: () => setIsComplete(false) // Rollback on error
    });
  };

  return (
    <Card className="task-card">
      <Checkbox
        checked={isComplete}
        onCheckedChange={handleCheckboxChange}
        disabled={isLoading}
        aria-label={task.title}
      />
      <TaskTitle>{task.title}</TaskTitle>
      {isComplete && <Badge variant="success">Completed</Badge>}
    </Card>
  );
}

// Test still passes: Refactored code maintains functionality
// Next cycle: Add test for error handling, then implement, then refactor
```

## Section 9: Complexity Tracking

(Copied from earlier section; no additional complexity identified)

| Justified Complexity | Why Needed | Aligns With Constitution Section |
|---------------------|------------|----------------------------------|
| Radix UI Primitives | Provides accessible, WCAG AA-compliant headless components (Popover, Dialog, Dropdown) that meet FR-051 without custom implementation | X. Infrastructure Philosophy (simplicity: leverage battle-tested accessibility) |
| Framer Motion | Required for FR-052 (component entry/exit animations), FR-053 (≤200ms duration), FR-054 (prefers-reduced-motion support); simpler than custom animation implementation | X. Infrastructure Philosophy (justified: animations are core UX requirement) |
| TanStack Query | Provides optimistic updates (FR-059), loading/error states, and cache invalidation with minimal boilerplate compared to Redux Toolkit or manual fetch management | X. Infrastructure Philosophy (simplicity: reduces state management complexity) |
| Zustand | Lightweight client UI state (sidebar, focus mode, onboarding) without Redux boilerplate; simpler than Context API for complex state | X. Infrastructure Philosophy (simplicity: 1KB library vs. Redux Toolkit) |
| MSW (Mock Service Worker) | Enables realistic backend simulation (FR-057, FR-058) without actual server setup; simplifies testing and development | X. Infrastructure Philosophy (simplicity: no backend infrastructure needed) |
| driver.js | Interactive walkthrough library for FR-044 through FR-048; mature solution preferred over custom tour implementation | X. Infrastructure Philosophy (justified: proven library for onboarding UX) |
| Zod Schemas (centralized) | FR-062 mandates centralized validation; Zod provides runtime validation + TypeScript inference from single source of truth | VII. Validation & Type Safety (type safety mandate) |

## Section 10: Unified Terminology

**Purpose**: Ensure consistent language across specification, code, tests, and documentation to prevent miscommunication and implementation errors.

### 10.1 Core Entity Terminology

| Term | Definition | Avoid Using |
|------|-----------|-------------|
| **Task** | Top-level actionable item with title, description, priority, and optional sub-tasks | Todo, Item, Entry, Action |
| **Sub-task** | Child task that contributes to parent task progress; maximum one level of nesting | Child task, Nested task, Step |
| **Note** | Quick capture of user thoughts with optional voice transcription | Entry, Memo, Comment |
| **Achievement** | Tracked productivity metric (High Priority Slays, Consistency Streak, Completion Ratio) | Badge, Reward, Trophy, Goal |
| **User Profile** | User account information including preferences and onboarding status | Account, Settings, User |
| **AI Interaction Log** | Immutable record of AI prompts and responses | AI Log, History, Event |

### 10.2 State Terminology

| Term | Definition | Avoid Using |
|------|-----------|-------------|
| **Hidden** | Task temporarily removed from views but recoverable via Settings; incomplete state | Archived (incorrect), Deleted (incorrect), Paused |
| **Archived** | Task permanently removed from active views; requires completion first; immutable | Hidden (incorrect), Deleted (incorrect), Completed |
| **Deleted** | Task permanently removed from system; only available for hidden tasks; non-recoverable | Removed, Destroyed, Erased |
| **Completed** | Task marked as done; can transition to archived state | Done, Finished, Closed |
| **Active** | Task visible in default views; not hidden, archived, or deleted | Open, Pending, Current |

### 10.3 Feature Terminology

| Term | Definition | Avoid Using |
|------|-----------|-------------|
| **Focus Mode** | Distraction-free interface showing only one task with countdown timer | Zen Mode, Concentration Mode, Deep Work Mode |
| **Magic Sub-tasks** | AI-powered sub-task generation feature with streaming output | Auto Sub-tasks, AI Breakdown, Smart Sub-tasks |
| **Quick Notes** | Voice-to-text note capture interface with waveform visualization | Voice Notes, Audio Notes, Dictation |
| **Note-to-Task Conversion** | AI parsing of note content into structured task fields | AI Parsing, Smart Conversion, Auto-Task |
| **Dopamine Engine** | Achievements system with metrics and milestone animations | Gamification, Reward System, Metrics Dashboard |
| **Consistency Streak** | Daily task completion tracking with 1-day grace period | Streak, Daily Streak, Completion Streak |
| **Glassmorphism** | Design pattern using frosted-glass effect with backdrop blur | Frosted Glass, Blurred Background, Acrylic |

### 10.4 Technical Terminology

| Term | Definition | Avoid Using |
|------|-----------|-------------|
| **MSW (Mock Service Worker)** | API mocking library for simulating backend in dev/test | Mock API, Fake Backend, Stub Server |
| **TanStack Query** | Server-state management library for caching and optimistic updates | React Query, Data Fetching Library, API Client |
| **Zustand** | Lightweight client UI state management library | State Manager, Store, Context |
| **Optimistic Update** | Immediate UI update before server confirmation; rolled back on error | Eager Update, Preemptive Update, Instant Update |
| **Server State** | Data fetched from API (tasks, notes, achievements); cached by TanStack Query | Remote State, API State, Backend State |
| **Client State** | Ephemeral UI state (sidebar collapse, focus mode); managed by Zustand | Local State, UI State, Frontend State |
| **Zod Schema** | Runtime validation schema with TypeScript type inference | Validation Schema, Type Schema, Data Schema |
| **API Contract** | OpenAPI-style endpoint definition with request/response schemas | API Spec, Endpoint Definition, Interface Contract |

### 10.5 UI Component Terminology

| Term | Definition | Avoid Using |
|------|-----------|-------------|
| **Sidebar** | Collapsible navigation menu with global search and profile popover | Nav, Menu, Side Panel |
| **Profile Popover** | Radix UI popover showing user info, settings, theme tweaks, logout | User Menu, Account Menu, Profile Dropdown |
| **Global Search** | Search bar in sidebar for finding tasks, notes, achievements across all entities | Omnibox, Universal Search, Search Bar |
| **AI Widget** | Floating bottom-right bubble for future command palette (CMD+K) | Chat Widget, AI Assistant, Help Bubble |
| **Task Card** | Glassmorphic card displaying task with checkbox, title, priority, duration | Task Item, Task Row, Task Entry |
| **Metric Card** | Animated glassmorphic card showing achievement metric with shimmer effect | Stat Card, Achievement Card, Metric Widget |
| **Walkthrough** | Interactive onboarding tutorial using driver.js | Tutorial, Onboarding, Tour |

### 10.6 Code Naming Conventions

**File Naming**:
- Components: PascalCase (e.g., `TaskCard.tsx`, `FocusMode.tsx`)
- Utilities: camelCase (e.g., `validation.ts`, `dateHelpers.ts`)
- Hooks: camelCase with `use` prefix (e.g., `useTasks.ts`, `useFocusMode.ts`)
- Schemas: camelCase with `Schema` suffix (e.g., `taskSchema.ts`, `noteSchema.ts`)
- Tests: Match source file with `.test` suffix (e.g., `TaskCard.test.tsx`)

**Variable Naming**:
- Boolean flags: `is` or `has` prefix (e.g., `isHidden`, `hasSubTasks`, `isInFocusMode`)
- Counts: `count` or `total` suffix (e.g., `taskCount`, `completedTotal`)
- Arrays: Plural nouns (e.g., `tasks`, `subTasks`, `achievements`)
- IDs: `id` suffix (e.g., `taskId`, `parentTaskId`, `userId`)
- Timestamps: ISO 8601 strings (e.g., `createdAt`, `completedAt`, `dueDate`)

**Function Naming**:
- Event handlers: `handle` prefix (e.g., `handleCheckboxChange`, `handleSubmit`)
- Async functions: Descriptive verb phrase (e.g., `fetchTasks`, `createTask`, `completeTask`)
- Boolean returns: `is`, `has`, `can` prefix (e.g., `isTaskComplete`, `hasSubTasks`, `canArchive`)
- Utilities: Verb phrase (e.g., `calculateProgress`, `formatDate`, `validateSchema`)

### 10.7 Test Naming Convention

**Format**: `[Component/Feature] - [User Action] - [Expected Outcome]`

**Examples**:
- `TaskForm - submits valid data - creates new task`
- `FocusMode - countdown reaches zero - shows alert and exits`
- `MagicSubTasks - AI generation fails - preserves partial output`
- `GlobalSearch - searches for "budget" - groups results by entity type`
- `VoiceRecorder - microphone permission denied - displays error with instructions`

## Section 11: Next Steps

**Immediate Actions**:
1. ✅ Plan.md generated with constitution compliance, unified terminology, and API error documentation
2. 🔄 Generate `research.md` (Phase 0 output) documenting technology decisions and best practices
3. 🔄 Generate `data-model.md` (Phase 1 output) with entity schemas and state machines
4. 🔄 Generate API contracts in `contracts/*.yaml` (Phase 1 output) with OpenAPI format
5. 🔄 Generate `quickstart.md` (Phase 1 output) with local development setup instructions
6. 🔄 Update agent context with new technologies (Phase 1.4)

**Post-Planning Actions** (requires `/sp.tasks` command):
7. Generate `tasks.md` with TDD Red-Green-Refactor sequence
8. Begin implementation following task dependency order
9. Re-check Constitution compliance after Phase 1 design completion
10. Execute tasks following TDD workflow with continuous testing

**Constitution Re-Check Trigger Points**:
- After Phase 1 Design: Verify API contracts align with single-responsibility principle (Section VI)
- After Schema Definition: Verify Zod schemas align with validation requirements (Section VII)
- After AI Feature Implementation: Verify confirmation flows meet governance requirements (Section IV)

---

**Planning Session Complete**. Next command: `/sp.tasks` to generate dependency-ordered task breakdown.
