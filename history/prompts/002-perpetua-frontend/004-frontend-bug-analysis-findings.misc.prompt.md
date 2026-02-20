---
id: "004"
title: Frontend Bug Analysis and Findings Report
stage: misc
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: main
user: 404mw
command: /sp.analyze
labels: ["bug-analysis","api-mismatch","security","frontend","findings"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - FINDINGS.md
tests:
  - none
---

## Prompt

- clicking anywhere on the screen send api requests to the backend.
- i also see duplicate subtasks requests being sent.
- confirmation modal ( the one appears after marking the task ) isnt optimized for mini screen.
- task creation modal also need mini screen optimization and additionally why theres no option to add subtasks.
- notification tab doesnt open in full screen. shows 404 page instead.
- task creation works but nothing else such as edit, mark complete, delete, add reminder.
- notes creation doesnt work
- /pricing payment doesnt work

i need the proper fixes not the temporary ones. @API.md will help alot about the most errors. save your findings in an md file at the project root which includes bugs fixes, api and schema missmatches, security or anything worth mentioning.

## Response snapshot

Performed a deep read-only analysis of the `002-perpetua-frontend` codebase, cross-referencing all reported bugs against `API.md` v1.0.0. Identified 8 distinct bug categories (10 total root causes), 9 API endpoint mismatches, and 3 security concerns. Produced `FINDINGS.md` at project root with root cause analysis, file/line citations, concrete fix snippets, and a prioritized fix order.

**Key findings:**
- `useSubtasks(task.id)` called unconditionally in `TaskCard.tsx:39` fires N API requests per render — root cause of "clicking anywhere sends requests"
- Mark complete uses non-existent `/tasks/{id}/complete` instead of `/tasks/{id}/force-complete` (CRITICAL)
- Notes creation uses non-existent `POST /notes` instead of `POST /tasks/{task_id}/notes` (CRITICAL)
- Reminder API calls are literally commented out in `TaskDetailView.tsx:119-153`
- Notification "View all" links to `/dashboard/notifications` which has no page file
- Payment calls `/subscription/checkout` instead of documented `/subscription/upgrade`
- Tokens stored in `localStorage` (XSS risk — recommend HttpOnly cookies)

## Outcome

- ✅ Impact: Comprehensive bug report with root causes, file citations, fix code snippets, and ordered fix plan saved to FINDINGS.md
- 🧪 Tests: None run (read-only analysis)
- 📁 Files: FINDINGS.md created at project root
- 🔁 Next prompts: Implement fixes in priority order starting with BUG-01-A (useSubtasks guard) and BUG-06A (force-complete endpoint)
- 🧠 Reflection: The most impactful single fix is guarding `useSubtasks` with `enabled: isExpanded` — this immediately stops the waterfall of background requests and makes the app testable. The API mismatches are consistent with an incomplete integration pass (schema/endpoint names diverged between backend spec and frontend implementation).

## Evaluation notes (flywheel)

- Failure modes observed: None — analysis was clean and findings are actionable
- Graders run and results (PASS/FAIL): N/A (read-only analysis)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fix BUG-01-A (`useSubtasks` enabled guard) and verify stray request flood stops
