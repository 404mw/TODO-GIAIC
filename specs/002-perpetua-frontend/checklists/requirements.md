# Specification Quality Checklist: Perpetua Flow Frontend Bug Fixes (v1.1)

**Purpose**: Validate specification completeness and quality after v1.1 update
**Created**: 2026-02-18
**Feature**: [specs/002-perpetua-frontend/spec.md](../spec.md)
**Trigger**: `/sp.specify` — 12 bugs from FINDINGS.md captured as requirements

---

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
  - *Note: Endpoint paths and HTTP methods are part of the API contract, not implementation details — they are acceptably present as constraints*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders (with targeted technical constraints where needed for correctness)
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous — each FR has explicit success criteria with checkboxes
- [x] Success criteria are measurable
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded (v1.1 additions tracked in Gap-4 table)
- [x] Dependencies and assumptions identified (API.md cross-referenced)

## Feature Readiness

- [x] All 12 bugs from FINDINGS.md captured as requirements:
  - [x] Bug #1 — FR-002: force-complete is the sole completion endpoint
  - [x] Bug #2 — FR-002: version field mandatory on all PATCH mutations
  - [x] Bug #3 — FR-005: notes are task-scoped (POST/GET /tasks/{task_id}/notes)
  - [x] Bug #4 — FR-005: note updates use PATCH not PUT
  - [x] Bug #5 — FR-006: reminders wired to real API (not stubs)
  - [x] Bug #6 — FR-003: subtask fetching deferred until card expanded
  - [x] Bug #7 — FR-003: cache invalidation uses camelCase taskId
  - [x] Bug #8 — FR-011: /dashboard/notifications page must exist
  - [x] Bug #9 — FR-012: subscription upgrade calls /subscription/upgrade
  - [x] Bug #10 — FR-013: mark-as-read calls /notifications/{id}/read
  - [x] Bug #11 — NFR-007: all modals responsive below 480px
  - [x] Bug #12 — FR-001 + NFR-002: tokens in HttpOnly cookies, not localStorage
- [x] User scenarios cover primary flows
- [x] No implementation details leak into specification

## Notes

- Spec updated from v1.0.0 → v1.1.0 in-place (same branch: 002-perpetua-frontend)
- All checklist items pass — spec is ready for `/sp.plan` or `/sp.tasks`
- Remaining open gap: conflict resolution UI (Gap 3B) — still needs implementation; not a spec deficiency
- S-03 (production console.log) added to NFR-002 production logging constraint
