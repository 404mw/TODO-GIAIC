---
id: 003
title: Perpetua Frontend Implementation Plan
stage: plan
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: developer
command: sp.plan
labels: ["planning", "frontend", "architecture", "design"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/plan.md
  - specs/002-perpetua-frontend/research.md
  - specs/002-perpetua-frontend/data-model.md
  - specs/002-perpetua-frontend/contracts/api-specification.md
  - specs/002-perpetua-frontend/quickstart.md
  - CLAUDE.md
tests:
  - Constitution Check validated (8/8 gates pass)
  - Post-design Constitution Re-check completed
  - All NEEDS CLARIFICATION items resolved
---

## Prompt

```text
sp.plan 002

## 1. Core Architectural Principles

### 1.1 State Management
- **Server-like State:** TanStack Query
  - Data source during development: **MSW (Mock Service Worker)**
  - Optimistic updates reset on page reload
- **Client UI State:** Zustand
  - Persisted via `localStorage`:
    - Sidebar open/closed
    - Theme tweaks
  - Non-persisted:
    - Focus Mode
    - AI widget visibility
    - Streaming / transient UI flags

### 1.2 Data Validation
- **Zod Schemas**
  - Centralized in `/schemas`
  - Imported by all features
  - UI-only flags (`isEditing`, `isStreaming`) excluded

### 1.3 Framework & Performance
- **Next.js App Router**
- Client Components for interactivity and animation
- All routes are URL-addressable

[... full architectural details provided ...]
```

## Response snapshot

Executed `/sp.plan` workflow for feature 002-perpetua-frontend (Perpetua Flow - Frontend Application).

**Phase 0: Research & Technology Decisions** - Completed
- Resolved all "NEEDS CLARIFICATION" items from Technical Context
- Documented 15 key technology decisions with rationale and alternatives:
  1. Next.js 14+ App Router (route groups, SSR/SSG)
  2. Dual state management (TanStack Query + Zustand)
  3. MSW for simulated backend with realistic latency
  4. Zod schemas centralized in `/schemas`
  5. Design system: Tailwind + Radix UI + Framer Motion
  6. Typography: Geist Sans + Geist Mono
  7. Focus Mode implementation (Zustand + CSS isolation + Web Timers)
  8. AI features disabled until backend (503 stubs in MSW)
  9. Driver.js for interactive onboarding walkthrough
  10. Fuse.js for client-side fuzzy search
  11. Centralized `config/limits.ts` for all enforced limits
  12. Testing: Jest + RTL + Playwright + MSW
  13. Accessibility: Semantic HTML + WCAG AA + reduced motion
  14. Environment variables with runtime validation (Zod)
  15. Deployment deferred to backend integration phase

**Phase 1: Design & Contracts** - Completed
- **Data Model**: Defined 14 entities with full schemas:
  - Task (10 fields + relationships)
  - Sub-task (7 fields, max 10 per task, no nesting)
  - Note (6 fields with voice metadata sub-schema)
  - User Profile (8 fields with preferences sub-schema)
  - Achievement (7 fields with consistency streak + milestones)
  - Workflow (6 fields, many-to-many with tasks)
  - Activity Log Event (6 fields, immutable, rolling window of 100)
  - Sub-schemas: VoiceMetadata, UserPreferences, ThemeTweaks, ConsistencyStreak, Milestone, Reminder, RecurrenceRule
- **API Contracts**: Documented 40+ REST endpoints across 9 categories:
  - Tasks (5 endpoints): List, Get, Create, Update, Delete
  - Sub-tasks (4 endpoints): List, Create, Update, Delete
  - Notes (4 endpoints): List, Create, Update, Delete
  - User Profile (3 endpoints): Get, Update Preferences, Mark Tutorial Complete
  - Achievements (1 endpoint): Get Current User Achievements
  - Workflows (4 endpoints): List, Create, Update, Delete
  - Activity Log (1 endpoint): List Events (read-only)
  - AI (2 endpoints, future): Generate Sub-tasks, Parse Note to Task
  - All endpoints include request/response schemas, error codes, special behaviors
- **Quickstart Guide**: Developer onboarding with:
  - Prerequisites and initial setup
  - Environment configuration (.env.local template)
  - Development workflow (start dev server, access application)
  - Project structure overview (frontend/ directory tree)
  - Key files explanation (schemas, limits, MSW handlers, TanStack Query hooks)
  - Testing commands (Jest, Playwright, linting)
  - Common development tasks (adding components, handlers, schemas, hooks)
  - Troubleshooting guide (6 common issues with solutions)
  - VS Code configuration (extensions, workspace settings)
- **Agent Context Updated**: Technology stack added to CLAUDE.md

**Constitution Check** - All Gates Pass (8/8 Pass, 1/8 Pending Backend)
- ✅ Phase Discipline: Spec complete, phase sequencing defined, no partial completion
- ✅ Data Integrity & Safety: MSW simulation, dummy data, undo deferred to backend
- ⚠️ AI Agent Governance: Pending backend (AI disabled, opt-in ready, logging schema defined)
- ✅ API Design Rules: Single responsibility, documented contracts, no hidden side effects
- ✅ Validation & Type Safety: Zod schemas centralized, schemas define truth
- ✅ Testing Doctrine: TDD mandate (Jest + RTL + Playwright), dummy data first
- ✅ Secrets & Configuration: .env for secrets, runtime validation, AI limits configurable
- ✅ Infrastructure Philosophy: Simplicity over scale, all complexity justified

**Deliverables**:
- `plan.md` - Technical Context, Constitution Check, Project Structure, Post-Design Re-Check
- `research.md` - 15 technology decisions with rationale and alternatives
- `data-model.md` - 14 entities with schemas, relationships, validation rules, state transitions
- `contracts/api-specification.md` - 40+ REST endpoints with full documentation
- `quickstart.md` - Developer onboarding guide with setup, workflow, troubleshooting
- `CLAUDE.md` - Updated with technology stack

**Phase 1 Complete** - Approved to proceed to Phase 2 (Task Generation via `/sp.tasks`)

## Outcome

- ✅ Impact: Comprehensive implementation plan with research, data model, API contracts, and quickstart guide. All constitution gates pass. Ready for task generation.
- 🧪 Tests: Constitution Check validated (8/8 gates pass), Post-design Constitution Re-check completed
- 📁 Files: Created 5 new files (plan.md, research.md, data-model.md, api-specification.md, quickstart.md), Updated 1 file (CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate TDD-ordered implementation tasks; Run `/sp.implement` after tasks.md is generated
- 🧠 Reflection: Planning workflow executed successfully. All NEEDS CLARIFICATION items resolved through research. Data model aligns with spec requirements (50 task limit, 10 sub-task limit, Focus Mode 3-hour limit). API contracts mirror expected backend structure. AI features correctly disabled until backend integration. Constitution compliance verified at both pre-research and post-design checkpoints.

## Evaluation notes (flywheel)

- Failure modes observed: None - workflow executed cleanly
- Graders run and results (PASS/FAIL): Constitution Check PASS (8/8 gates), Post-design Re-check PASS (8/8 confirmed)
- Prompt variant (if applicable): Standard sp.plan workflow with user-provided architectural details
- Next experiment (smallest change to try): None required - proceed to sp.tasks phase
