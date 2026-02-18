---
id: 002
title: Generate tasks and intelligence object
stage: tasks
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.tasks
labels: ["tasks", "intelligence", "reverse-engineering", "planning"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/tasks.md
  - specs/002-perpetua-frontend/intelligence-object.md
tests:
  - None (planning task)
---

## Prompt

"do it"

(User confirmed creation of the two missing reverse-engineering artifacts after the previous `/sp.reverse-engineer` session only produced `spec.md` and `plan.md`. Invoked `/sp.tasks` skill to generate `tasks.md` and `intelligence-object.md`.)

## Response snapshot

Generated two comprehensive SDD-RI artifacts:

### tasks.md (121 tasks across 13 phases)

Organized by user story (US1–US10 mapping to FR-001–FR-010 from spec.md):

- **Phase 1**: Setup — 9 tasks (Next.js init, tooling config)
- **Phase 2**: Foundational — 18 tasks (API client, AuthContext, layout, MSW)
- **Phase 3 (US1)**: Authentication — 8 tasks (Google OAuth, tokens, login page)
- **Phase 4 (US2)**: Task Management — 19 tasks (core CRUD, TaskCard, TaskList, TaskForm, NewTaskModal, detail view, completed page) 🎯 MVP
- **Phase 5 (US3)**: Subtasks — 9 tasks (schema, hooks, SubTaskList, AddSubTaskForm, AI generator, integration)
- **Phase 6 (US4)**: Focus Mode — 5 tasks (store, FocusTimer, FocusTaskView, focus page, TaskCard integration)
- **Phase 7 (US5)**: Quick Notes — 8 tasks (schema, hooks, NoteCard, QuickNoteInput, notes page, archived notes)
- **Phase 8 (US6)**: Achievement System — 8 tasks (schema, handlers, hooks, AchievementCard, StreakDisplay, unlock toast, achievements page)
- **Phase 9 (US7)**: Reminder System — 8 tasks (schema, handlers, hooks, ReminderForm, service worker, SW hook)
- **Phase 10 (US8)**: Recurring Tasks — 7 tasks (template schema, recurrence.ts, RecurrenceEditor, RecurrencePreview, form integration, instance refresh)
- **Phase 11 (US9)**: AI Features — 5 tasks (AI schema, mock handlers, useAI hook, AISubtasksGenerator, note smart convert)
- **Phase 12 (US10)**: Command Palette — 5 tasks (store, commands, CommandPalette component, global Cmd+K listener, layout mount)
- **Phase 13**: Polish — 12 tasks (P0 gap fixes, accessibility, rate limiting, security headers, settings pages, onboarding tour)

### intelligence-object.md

6 reusable skills extracted:
1. **Schema-First API Validation** (Zod) — never write types separate from schemas
2. **Dual-State Task Completion** (Optimistic UI) — separate optimistic store + always rollback on error
3. **Layered Error Handling** (ApiError class) — typed errors, dual-format support, request_id propagation
4. **TanStack Query Hook Abstraction** — one hook per operation, centralized query keys, `enabled` guards
5. **Service Worker Message Bus** — postMessage config injection, dual notification (browser + in-app), stop on public pages
6. **Zustand Store Slice Pattern** — one store per concern, actions co-located, selector-based subscriptions

4 inferred ADRs documented:
- ADR-001: TanStack Query over Redux
- ADR-002: MSW over JSON Server
- ADR-003: Soft Delete over Hard Delete
- ADR-004: Optimistic Locking via `version` field

5 pitfalls documented (with fixes):
1. SW token access gap → use IndexedDB
2. Missing Error Boundary → add at root layout
3. Optimistic updates without rollback → always pair onSuccess + onError
4. Query key typos → export `QUERY_KEYS` constants
5. Unchecked subtask limit → validate client-side before form allows submit

## Outcome

- ✅ Impact: All 4 SDD-RI artifacts now complete: spec.md (1,506 lines), plan.md (1,199 lines), tasks.md (121 tasks / 13 phases), intelligence-object.md (6 skills, 4 ADRs, 5 pitfalls). Full reverse engineering of 171-file Next.js frontend now documented and actionable.

- 🧪 Tests: No tests (planning task). Test approach documented in tasks.md Notes section.

- 📁 Files created:
  - `specs/002-perpetua-frontend/tasks.md` — 121 actionable tasks across 13 phases
  - `specs/002-perpetua-frontend/intelligence-object.md` — 6 reusable skills, 4 ADRs, 5 pitfalls

- 🔁 Next prompts:
  1. `/sp.implement` — execute tasks.md phase by phase
  2. `/sp.clarify` — clarify any ambiguous requirements before implementation
  3. `/sp.adr` — document ADR-001 through ADR-004 formally

- 🧠 Reflection: Tasks organized by user story enables incremental MVP delivery. Phase 4 (Task Management) is the true MVP — completing Phases 1–4 gives a working task manager. Intelligence object captures tacit knowledge that would otherwise be lost when developer context switches, making the codebase regenerable.

## Evaluation notes (flywheel)

- Failure modes observed: None. Used sp.tasks skill with full spec.md + plan.md context. all 121 tasks follow required `[ID] [P?] [Story] description with file path` format.

- Graders run and results (PASS/FAIL): Format validation PASS — every task has checkbox, T-ID, optional [P], story label where required, and file path.

- Prompt variant (if applicable): sp.tasks (standard invocation via "do it" after missing artifacts flagged)

- Next experiment (smallest change to try): Run `/sp.implement` starting from Phase 1 to validate tasks are specific enough for autonomous execution.
