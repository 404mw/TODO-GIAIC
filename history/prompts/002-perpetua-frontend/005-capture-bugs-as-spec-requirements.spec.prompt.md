---
id: "005"
title: capture bugs as spec requirements
stage: spec
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: /sp.specify
labels: ["spec-update", "bug-requirements", "api-contracts", "security", "responsive-ui"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md (modified — v1.0 → v1.1)
  - specs/002-perpetua-frontend/checklists/requirements.md (created)
tests:
  - none (spec update, no code changes)
---

## Prompt

feature: 002
detailed findings: @FINDINGS.md

user prompt:
The following bugs need to be captured as requirements in the spec:

1. Task completion must call POST /tasks/{id}/force-complete with a version field (optimistic locking). Endpoint /complete and /auto-complete do not exist.
2. All task update mutations must include the version field for optimistic locking.
3. Notes must be created/listed via task-scoped endpoints: POST /tasks/{task_id}/notes and GET /tasks/{task_id}/notes. A standalone POST /notes endpoint does not exist.
4. Note updates must use PATCH /notes/{note_id}, not PUT.
5. Reminders must be wired to real API calls (POST /tasks/{task_id}/reminders and DELETE /reminders/{id}), not stubs.
6. Subtask queries must be deferred until the task card is expanded (enabled: isExpanded) to prevent N stray API requests per render.
7. Duplicate subtask cache invalidation must use camelCase taskId not snake_case task_id.
8. The /dashboard/notifications full-page route must exist.
9. Subscription upgrade must call POST /subscription/upgrade, not /subscription/checkout.
10. Mark-notification-as-read must call PATCH /notifications/{id}/read, not PATCH /notifications/{id}.
11. All modals (task creation, completion confirmation) must be responsive on screens below 480px.
12. Tokens must not be stored in localStorage; migrate to HttpOnly cookies.

## Response snapshot

Updated `specs/002-perpetua-frontend/spec.md` from v1.0.0 to v1.1.0, capturing all 12 bugs as enforceable requirements across the following sections:

- **FR-001** (Authentication): Added HttpOnly cookie constraint; banned localStorage token storage; banned production console.log of auth data
- **FR-002** (Task Management): Strengthened version-field mandate on all PATCH mutations; clarified force-complete as the sole completion endpoint; corrected response schema to `{ data: { task, unlocked_achievements[], streak } }`
- **FR-003** (Subtask Management): Added deferred-fetch requirement (enabled: isExpanded); added camelCase taskId cache-key requirement
- **FR-005** (Quick Notes): Corrected all note endpoints to task-scoped paths; corrected HTTP method to PATCH for updates
- **FR-006** (Reminder System): Added explicit CRUD API operations with correct endpoints; banned stub implementations
- **FR-011** (NEW — Notifications Page): Route /dashboard/notifications must exist
- **FR-012** (NEW — Subscription Upgrade): Must call POST /subscription/upgrade; /subscription/checkout banned
- **FR-013** (NEW — Mark Notification Read): Must call PATCH /notifications/{id}/read
- **NFR-002** (Security): Added HttpOnly cookie mandate; added production logging ban
- **NFR-007** (NEW — Responsive Modals): All dialogs usable on ≤480px viewports
- **Appendix A**: Corrected notes endpoint table; added notification and subscription endpoints
- **Known Gaps**: Added Gap-4 tracking table mapping all 12 bugs to spec sections

Created checklist at `specs/002-perpetua-frontend/checklists/requirements.md` — all items pass.

## Outcome

- ✅ Impact: All 12 FINDINGS.md bugs are now enforceable specification requirements; spec version bumped to 1.1.0
- 🧪 Tests: No code tests (spec-only update); checklist validation complete
- 📁 Files: specs/002-perpetua-frontend/spec.md, specs/002-perpetua-frontend/checklists/requirements.md
- 🔁 Next prompts: `/sp.tasks` to regenerate tasks.md incorporating the new requirements; or `/sp.implement` to begin fixing the bugs
- 🧠 Reflection: Pattern confirmed — when analysis surfaces API contract violations, they should be encoded in the spec before any implementation begins; this creates a single source of truth for bug acceptance criteria

## Evaluation notes (flywheel)

- Failure modes observed: none — all 12 bugs mapped cleanly to spec sections
- Graders run and results (PASS/FAIL): checklist validation PASS (all items)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): run /sp.tasks to see if task decomposition captures the correct acceptance criteria from the updated spec
