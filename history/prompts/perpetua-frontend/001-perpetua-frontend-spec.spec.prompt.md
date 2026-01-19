---
id: 001
title: Perpetua Frontend Spec
stage: spec
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: claude-agent
command: /sp.specify
labels: ["frontend", "task-management", "ai-features", "focus-mode", "achievements", "nextjs", "specification"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
  - specs/002-perpetua-frontend/checklists/requirements.md
tests:
  - Spec validation checklist (all items passed)
---

## Prompt

User requested creation of a comprehensive feature specification for "Perpetua Flow" - a frontend-only task management application with the following key characteristics:

- **App Name**: Perpetua Flow
- **Scope**: Frontend-only SDD (Spec-Driven Development), backend assumed nonexistent
- **Architecture**: All data interactions simulated but architected for real backend integration later with minimal refactor

**Core Architectural Principles**:
1. State Management: TanStack Query for server-like state with MSW (Mock Service Worker), Zustand for client UI state
2. Data Validation: Centralized Zod schemas for data contracts
3. Framework: Next.js App Router with selective client components

**Design System**: "Futuristic Minimal"
- Strict dark mode only (no light mode)
- Glassmorphism for dashboard widgets and task cards
- Framer Motion for animations (≤200ms duration)
- WCAG AA contrast standards
- Typography: Inter/Geist Sans primary, monospace for metadata

**Key Features**:
1. **Task Management**: Flat tasks with one-level sub-tasks, progress tracking, soft-hide, priority (Low/Medium/High), duration estimation, tags, reminders, recurrence
2. **Focus Mode** ("Kill the Noise"): Single-task view with countdown timer, sidebar hidden, all distractions disabled
3. **AI & Automation**:
   - Magic Sub-tasks: LLM-generated sub-tasks with real-time streaming
   - Quick Notes with Voice-to-Text: Recording indicator with waveform animation
   - Convert Note → Task: AI-parsed fields in sliding drawer with user confirmation
4. **Dopamine Engine**: Fixed metrics (High Priority Slays, Consistency Streaks, % Completion), animated visualizations, milestone feedback
5. **NUX**: Interactive walkthrough (driver.js) with tutorial task "Master Perpetua"
6. **Dashboard Layout**: Left sidebar with route-based navigation (/workflows, /tasks, /notes, /achievements, /activity), global search, profile popover
7. **AI Widget**: Floating bottom-right bubble, CMD+K opens AI input

**Technical Constraints**:
- Local caching only for sidebar state and theme preferences
- MSW simulates realistic network behavior
- Optimistic updates are ephemeral

**Explicit Non-Goals**: Time tracking, infinite nesting, light mode, AI auto-actions without confirmation, backend assumptions beyond API shape compatibility

## Response snapshot

Created comprehensive feature specification following SDD template structure with:

1. **8 Prioritized User Stories** (P1-P3) with independent test criteria:
   - P1: Core task management (MVP foundation)
   - P1: Dashboard layout & navigation (infrastructure)
   - P2: Focus Mode, AI Quick Notes & Conversion, Global Search (differentiation)
   - P3: AI-Generated Sub-tasks, Achievements, Onboarding (enhancement)

2. **69 Functional Requirements** organized by domain:
   - Core Task Management (FR-001 to FR-009)
   - Focus Mode (FR-010 to FR-016)
   - AI Features (FR-017 to FR-027)
   - Achievements & Metrics (FR-028 to FR-032)
   - Navigation & Layout (FR-033 to FR-038)
   - Search (FR-039 to FR-040)
   - AI Widget (FR-041 to FR-042)
   - New User Experience (FR-043 to FR-047)
   - Design System (FR-048 to FR-055)
   - State Management & Data (FR-056 to FR-062)
   - Public Pages (FR-063 to FR-066)
   - Reminders & Recurrence (FR-067 to FR-069)

3. **24 Success Criteria** with measurable outcomes:
   - User Productivity: 5 metrics (task creation speed, Focus Mode activation, first-task completion, note conversion, search performance)
   - AI Feature Adoption: 3 metrics (conversion rate, streaming speed, transcription accuracy)
   - User Engagement: 3 metrics (walkthrough completion, streak impact, Focus Mode impact)
   - Technical Performance: 4 metrics (load time, transitions, API latency, responsiveness)
   - Accessibility & UX: 4 metrics (contrast, reduced motion, navigation efficiency, error messaging)
   - Design System Compliance: 3 metrics (readability, dark aesthetic consistency, typography)
   - Retention & Motivation: 2 metrics (achievement return rate, tutorial completion)

4. **Key Entities**: 7 data models (Task, Sub-task, Note, User Profile, Achievement, Workflow, Activity Log) with attributes and relationships

5. **12 Assumptions**: Authentication scope, browser support, network conditions, AI services, language support, screen size, data volume, backend migration, notifications, accessibility, theme customization

6. **11 Dependencies**: Next.js, TanStack Query, Zustand, MSW, Zod, Framer Motion, Radix UI, driver.js, AI API, Speech-to-Text API, Web Audio API

7. **15 Explicit Non-Goals**: Time tracking, infinite nesting, light mode, AI auto-actions, backend details, team collaboration, mobile apps, offline mode, data export/import, integrations, customizable metrics, workflow automation, advanced search, sub-task dependencies, task templates

8. **10 Edge Cases**: Orphaned sub-tasks, microphone permissions, AI timeouts, localStorage conflicts/quota, nested sub-tasks prevention, offline recurrence, Focus Mode early exit, malformed transcriptions, theme fallback

9. **Quality Validation Checklist**: All 12 validation items passed, spec is ready for planning phase

## Outcome

- ✅ Impact: Complete, validated specification for Perpetua Flow frontend feature ready for architectural planning
- 🧪 Tests: Spec validation checklist executed with 12/12 items passed (content quality, requirement completeness, feature readiness)
- 📁 Files: Created specs/002-perpetua-frontend/spec.md (357 lines), specs/002-perpetua-frontend/checklists/requirements.md
- 🔁 Next prompts: `/sp.plan` for architecture and implementation planning, or `/sp.clarify` if questions arise during review
- 🧠 Reflection: Spec makes informed assumptions instead of leaving gaps (e.g., authentication exists separately, English-only v1, desktop-first). All success criteria are technology-agnostic and measurable. User stories are independently testable as vertical slices.

## Evaluation notes (flywheel)

- Failure modes observed: None. Spec completeness validated against template requirements. No [NEEDS CLARIFICATION] markers required due to comprehensive feature description input.
- Graders run and results (PASS/FAIL): Manual validation checklist - PASS (12/12 items). Markdown linting - minor formatting warnings (non-blocking).
- Prompt variant (if applicable): N/A (first iteration)
- Next experiment (smallest change to try): Consider auto-generating user story priorities based on dependency analysis (e.g., navigation/layout must precede feature-specific routes)
