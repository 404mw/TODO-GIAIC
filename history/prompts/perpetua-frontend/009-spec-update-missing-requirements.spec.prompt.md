---
id: 009
title: Spec Update Missing Requirements
stage: spec
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: system
command: /sp.specify
labels: ["spec-update", "requirements-completion", "data-model-clarification"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
tests:
  - No tests (spec-only update)
---

## Prompt

```text
Update spec.md to add:
  - FR-071 to FR-077 (Reminders, Recurrence, AI Logging, Settings, Due Dates, Archive)
  - Remove or define Workflows and Activity Log
  - Resolve data model conflicts (Recurrence structure, hidden vs soft-deleted)
```

## Response snapshot

Updated [spec.md](../../specs/002-perpetua-frontend/spec.md) with the following changes:

1. **Added FR-071 to FR-077**: New functional requirements covering:
   - FR-071: Set reminder timestamps for tasks
   - FR-072: Display reminder notifications at configured time
   - FR-073: Recurrence settings structure (intervalType, intervalValue, endDate)
   - FR-074: Log all AI interactions for transparency
   - FR-075: Settings page with configurable preferences
   - FR-076: Set due dates for tasks (separate from reminders)
   - FR-077: Task archiving as distinct from hiding

2. **Resolved Workflows and Activity Log**:
   - Marked both features as [OUT OF SCOPE for initial release]
   - Added entries #16 and #17 to Out of Scope section
   - Removed `/dashboard/workflows` and `/dashboard/activity` from FR-034 navigation routes
   - Added `/dashboard/settings` and `/dashboard/archive` as replacement routes
   - Updated global search (FR-040) to exclude workflows
   - Updated User Story 7 to reflect correct entity types

3. **Resolved Data Model Conflicts**:
   - Added "Task State Management Clarifications" section explaining:
     - **Hidden**: Incomplete tasks, temporarily removed, reversible
     - **Archived**: Complete tasks, permanently removed from active views, irreversible
     - **Deleted**: Hard delete, only for hidden tasks via Settings
   - Defined state transitions with clear flow diagram
   - Updated Task entity to clarify: `hidden flag (boolean, mutually exclusive with archived)` and `archived flag (boolean, requires completion status true)`
   - Expanded Recurrence Settings as standalone entity with full structure

4. **Data Model Enhancements**:
   - Added `due date` field to Task entity (optional timestamp, separate from reminder)
   - Added `AI Interaction Log` entity for logging AI prompts/responses
   - Clarified recurrence settings structure as embedded object

## Outcome

- ✅ Impact: Spec now has complete requirements for Reminders, Recurrence, Settings, Archive features; data model conflicts resolved with clear state management documentation
- 🧪 Tests: No tests (spec-only update); all changes are documentation
- 📁 Files: 1 file modified (specs/002-perpetua-frontend/spec.md)
- 🔁 Next prompts: `/sp.plan` to update implementation plan with new requirements, then `/sp.tasks` to generate tasks for FR-071 to FR-077
- 🧠 Reflection: State management clarifications prevent implementation ambiguity; separating due dates from reminders provides flexibility; marking Workflows/Activity as out-of-scope reduces initial complexity

## Evaluation notes (flywheel)

- Failure modes observed: None; spec update completed successfully without conflicts
- Graders run and results (PASS/FAIL): PASS - All quality criteria met (no [NEEDS CLARIFICATION] markers, testable requirements, technology-agnostic success criteria)
- Prompt variant (if applicable): Standard `/sp.specify` update workflow
- Next experiment (smallest change to try): Consider adding user stories for Settings and Archive pages if needed during planning phase
