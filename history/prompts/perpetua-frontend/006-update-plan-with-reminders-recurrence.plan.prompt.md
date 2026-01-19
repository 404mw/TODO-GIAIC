---
id: 006
title: Update Plan with Reminders and Recurrence TDD
stage: plan
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: Claude Agent
command: /sp.plan
labels: ["planning", "reminders", "recurrence", "tdd", "architecture"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/plan.md
  - specs/002-perpetua-frontend/research.md
tests:
  - None (planning phase)
---

## Prompt

002 spec updated to include TDD as per the project constitution. update the plan now and must include Reminders & Recurrence. they are part of this feature. dont assume things cross question me instead.

## Response snapshot

Successfully created comprehensive implementation plan for perpetua-frontend with TDD enforcement, Reminders & Recurrence features fully integrated.

### Key Deliverables

1. **plan.md Updated** (G:\Hackathons\GIAIC_Hackathons\02-TODO\specs\002-perpetua-frontend\plan.md)
   - Technical Context: TypeScript 5.3+, Next.js 15, React 19, TanStack Query v5, Zustand, MSW, RTL, Jest
   - Constitution Check: ✅ PASS (all 11 sections verified, deferrals documented)
   - Project Structure: Next.js App Router with feature-based organization
   - Phase 0: Research Complete (all clarifications resolved)
   - Phase 1: Data Model & API Endpoints (summary with 7 entities, 10+ endpoints)
   - Phase 2: Task Organization (TDD Red-Green-Refactor workflow, P1/P2/P3 priorities)
   - Development Workflow: TDD cycle, pre-commit checklist
   - Risks & Mitigations: 5 risks identified with mitigations
   - Success Metrics: Technical + UX metrics from spec

2. **research.md Updated** (G:\Hackathons\GIAIC_Hackathons\02-TODO\specs\002-perpetua-frontend\research.md)
   - Section 15: **Reminders & Notifications System**
     - Decision: Dual notification (browser + in-app), Service Worker polling every 60s
     - Rationale: User clarified "Both browser + in-app", relative timing preferred
     - Implementation: ReminderSchema with relative_to_due_date timing, Service Worker checks MSW state
     - Dependencies: Web Notifications API, Service Worker API, Radix UI Toast
     - Testing Strategy: Unit tests for calculateReminderTriggerTime, integration tests for full flow

   - Section 16: **Recurring Tasks System**
     - Decision: RRule library (RFC 5545), completion-based instance generation
     - Rationale: User clarified "Custom interval" patterns needed, "On completion" generation preferred
     - Implementation: RecurrenceSchema with RRule string, onTaskComplete generates next instance
     - UI Components: RecurrenceEditor with frequency/interval/weekday pickers, RecurrencePreview
     - Dependencies: `rrule` package v2.7+, `date-fns` for formatting
     - Testing Strategy: Unit tests for onTaskComplete with various RRule patterns, edge case handling

### User Clarifications Obtained

Asked 4 targeted questions via AskUserQuestion tool:

1. **Reminder Delivery**: "Both browser + in-app" (dual notification system)
2. **Recurrence Patterns**: "Custom interval" (requires RRule library support)
3. **Instance Generation**: "On completion (recommended)" (simplest, most predictable)
4. **Reminder Timing**: "Relative to due date (recommended)" (e.g., "15 minutes before")

### Architecture Decisions

**Reminders**:
- Service Worker polls MSW `/api/reminders` + `/api/tasks` every 60 seconds
- Dual delivery: Browser notification (if permission granted) + in-app toast (always)
- Relative timing: offsetMinutes from task due date (e.g., -15 = 15 min before)
- Graceful degradation: Falls back to in-app only if browser permission denied

**Recurrence**:
- RRule library for RFC 5545 compliance (industry standard)
- Completion-based: Next instance created immediately when current task marked complete
- Human-readable descriptions: RRule.toText() generates "Every 2 weeks on Monday"
- UI presets: Daily, Weekly, Monthly with "Custom" advanced option
- Edge case handling: Invalid dates, COUNT limits, timezone support

**TDD Integration**:
- All testing requirements from spec.md preserved
- 80% coverage minimum enforced
- Pre-commit hooks must pass (tests, type-check, lint)
- Red-Green-Refactor workflow documented in plan

### Constitution Compliance

**Gate Status**: ✅ PASS (with noted deferrals)

**Compliant**:
- Phase discipline: Plan → Tasks → Implementation (TDD per task)
- Testing doctrine: Red-Green-Refactor mandatory
- API design: Single responsibility endpoints
- Validation: Zod schemas mirror MSW responses
- Secrets: `.env` with validation on startup
- Simplicity: MSW simulation, no complex orchestration

**Deferrals** (documented):
- Data backup/undo guarantees: Deferred to real backend (MSW resets on reload by design)
- AI event logging: Deferred to real backend (frontend focuses on UI patterns)
- All frontend patterns designed to be backend-compatible

### Technical Highlights

1. **Service Worker Implementation**: Polling architecture avoids complex scheduling, works with MSW in-memory state
2. **RRule Integration**: Battle-tested library (10k+ stars), TypeScript support, human-readable output
3. **TDD Workflow**: Documented cycle with examples, pre-commit checklist, coverage thresholds
4. **Project Structure**: Next.js App Router with `/app/dashboard/reminders` route, `/src/components/reminders` + `/src/components/recurrence` components
5. **API Design**: 5 new reminder endpoints, recurrence handled in task completion PATCH endpoint

### Risks Identified & Mitigated

1. **Service Worker browser support** → Feature detection + fallback to in-app only
2. **RRule complexity for users** → Presets + "Custom" advanced option with preview
3. **MSW performance with large datasets** → Pagination + virtual scrolling
4. **TDD slows initial velocity** → Accept trade-off (quality over speed per constitution)
5. **Browser notification permission denied** → Prominent request + fallback to toast

## Outcome

- ✅ Impact: Comprehensive implementation plan created with Reminders & Recurrence fully integrated, TDD workflow documented, all user clarifications resolved
- 🧪 Tests: None (planning phase, no code written)
- 📁 Files: 2 files updated (plan.md, research.md)
- 🔁 Next prompts: `/sp.tasks` to generate detailed task list in TDD Red-Green-Refactor order
- 🧠 Reflection: User clarifications prevented assumptions, resulted in clear decisions (dual notifications, RRule library, completion-based generation, relative timing). Service Worker polling architecture is simple and works well with MSW. TDD requirements from spec.md preserved in plan.

## Evaluation notes (flywheel)

- Failure modes observed: Initial markdown linting warnings (missing blank lines around lists) - fixed immediately
- Graders run and results (PASS/FAIL): Markdown linting PASS after fixes, Constitution Check PASS (with deferrals documented)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate that tasks.md generation correctly interprets TDD requirements and creates Red-Green-Refactor task structure for Reminders & Recurrence features
