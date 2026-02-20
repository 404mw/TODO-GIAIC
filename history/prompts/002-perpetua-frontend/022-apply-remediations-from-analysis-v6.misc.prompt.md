---
id: 022
title: Apply Remediations From Analysis v6
stage: misc
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: apply remediation edits for all of them
labels: ["remediation","spec","plan","tasks","tdd","a11y","security","consistency"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md (modified — v1.5.0 → v1.6.0)
  - specs/002-perpetua-frontend/plan.md (modified — H1 version table, L3 next-version note)
  - specs/002-perpetua-frontend/tasks.md (modified — 177 → 185 tasks; T099 reopened; T112/T158/T160 updated; T178-T185 added; execution table updated)
tests:
  - none (artifact remediation run — no code tests executed)
---

## Prompt

apply remediation edits for all of them

(Invoked after /sp.analyze 002 v6 — PHR 021 — which identified 12 findings: 0 CRITICAL · 5 HIGH · 4 MEDIUM · 3 LOW. User approved applying all 12 remediations.)

## Response snapshot

Applied all 17 remediation edits across spec.md, plan.md, and tasks.md resolving all 12 findings from sp.analyze v6 (PHR 021).

**plan.md — 2 edits:**
- H1: Corrected version control table from "Plan version: 1.4.0" to "Plan version: 1.5.0"; removed duplicate 1.4.0 entry; restored correct previous-version ordering
- L3: Replaced vague "Next version: 1.6.0 (after T134 complete)" note with explicit conditional: "bump ONLY when BOTH: (1) T134 merged and confirmed, (2) all Phase 14 open tasks closed"

**spec.md — 7 edits (v1.5.0 → v1.6.0):**
- H4: Added `actor_type: 'ai'` as explicit field to AI log format in FR-009; updated success criteria to require it; satisfies Constitution §V.2 "actor identity (user or AI)"
- L1: Replaced "Constitution §IX.4" and "§IX.2" references with literal principle text (constitution has no numbered subsections)
- M3 Gap 5: Corrected @axe-core/react → jest-axe (correct CI assertion library); noted @axe-core/react as optional dev overlay only
- M4 NFR-007: Added ConflictResolutionModal (T112) to Affected Components; added acceptance criterion for 375px mobile layout and button reachability
- M1 NFR-005: Split reliability targets into frontend-owned vs backend-dependent ownership; restructured success criteria with same split
- M2 Non-Goals §V: Added items #7 (analytics events) and #8 (in-app feedback widget) as deferred; updated NFR-006 User Feedback to mark both [DEFERRED]
- Version bump: Header, footer, status line, and version control table updated to v1.6.0

**tasks.md — 8 edits (177 → 185 tasks):**
- H2: Reopened T099 ([ ]) — PATCH/DELETE template endpoints not confirmed in API.md; added 3-part completion gate annotation
- H3: Added T178 — backfill AI credit env vars (FREE_TIER_AI_CREDITS, PRO_TIER_AI_CREDITS, AI_CREDIT_RESET_HOUR, AI_MODEL_ID) to .env.local template and startup env validator
- H4: Updated T160 — both Sentry.addBreadcrumb and logger.info calls now include `actor_type: 'ai'` field
- H5: Added 7 RED test tasks paired to 7 Phase 14 GREEN implementation tasks that had no RED partners:
  - T179 [RED → T134]: localStorage-free auth test (HttpOnly cookie migration)
  - T180 [RED → T135]: unguarded console.log absence test (production build)
  - T181 [RED → T112]: cross-references T156 as RED test for ConflictResolutionModal
  - T182 [RED → T172]: focus mode navigation guard test (popstate + beforeunload)
  - T183 [RED → T131]: NewTaskModal responsive layout at 375px
  - T184 [RED → T132]: NotificationDropdown mousedown listener scope
  - T185 [RED → T133]: PendingCompletionsBar wraps at 375px viewport
- M4: Added NFR-007 responsive acceptance criteria block to T112 (375px layout, button reachability, 85dvh max height)
- L2: Expanded T158 to include `<audio>` element in NoteCard.tsx when `voice_url` is present — aria-label="Voice note playback"; jest-axe now checks "audio without accessible name"
- Execution table: Updated rows 0, 9, 13-17, 20 with T179-T185 as RED pairs; added T178 at priority 20
- Task count note: Updated from 177 to 185 with breakdown of v6 additions

## Outcome

- ✅ Impact: All 12 sp.analyze v6 findings resolved — 0 CRITICAL · 5 HIGH · 4 MEDIUM · 3 LOW. spec.md bumped to v1.6.0. tasks.md now has 185 tasks with full TDD RED-GREEN coverage for all Phase 14 implementation tasks. Constitution §V.2 actor identity gap closed. Phase 14 execution table updated.
- 🧪 Tests: None — artifact remediation only
- 📁 Files: spec.md (v1.6.0), plan.md (version table + next-version note), tasks.md (T099 reopened, T112/T158/T160 updated, T178-T185 added, execution table updated, count 177→185)
- 🔁 Next prompts: /sp.implement (safe to proceed — H2/H3/H5 resolved); address T099 API contract before implementing PATCH/DELETE endpoints
- 🧠 Reflection: v6 remediation was the cleanest run yet — 17 targeted edits, no collisions, no rework. The H5 TDD gap (7 GREEN tasks with no RED) was the largest structural change. Inserting T181 as a cross-reference to T156 (rather than a new test task) avoids duplication for ConflictResolutionModal. L2 audio ARIA was a genuine blind spot not caught in earlier analysis passes.

## Evaluation notes (flywheel)

- Failure modes observed: Context window exhaustion required session continuation; all edits completed correctly across resumed session
- Graders run and results (PASS/FAIL): Manual verification of all 17 edit targets — PASS; task count arithmetic verified (177 + 8 = 185) — PASS
- Prompt variant (if applicable): "apply remediation edits for all of them" — direct instruction after /sp.analyze output
- Next experiment: Consider whether T181 cross-referencing T156 as its RED test is sufficient, or whether a standalone test task is needed for complete TDD traceability
