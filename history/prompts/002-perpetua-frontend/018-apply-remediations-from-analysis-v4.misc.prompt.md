---
id: "018"
title: Apply sp.analyze v4 Remediation Edits
stage: misc
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 002-perpetua-frontend
branch: 002-perpetua-frontend
user: 404mw
command: apply concrete remediation edits for all items
labels: ["remediation","spec","plan","tasks","constitution","bug-fix"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
  - specs/002-perpetua-frontend/plan.md
  - specs/002-perpetua-frontend/tasks.md
tests:
  - none (documentation-only changes)
---

## Prompt

apply concrete remediation edits for all items

(Follow-up to PHR 017 sp.analyze v4 — user requested all 16 findings be remediated across spec.md, plan.md, and tasks.md)

## Response snapshot

Applied all 16 remediation items across 3 artifacts. Key changes:

**CRITICAL:**
- C1: Added T173 (RED→T125 notes migration) and T174 (RED→T128 notifications page) to Phase 14 — satisfies Constitution §VIII TDD mandate for the two previously untested GREEN tasks
- C2: Reclassified T157-T159 (NFR-003 a11y) from Phase 13 to Phase 14; updated Phase 13 accessibility section with reclassification note; updated Phase Dependencies; resolves Constitution §II phase overlap violation
- C3: T112 (ConflictResolutionModal.tsx) confirmed absent on disk; corrected from [X] to [ ] in tasks.md; updated spec.md Gap 3; updated T124 acceptance criteria to note T112 must be built first; updated P0 Gaps section
- C4: Updated tasks.md prerequisite header from spec v1.2.0 to v1.4.0

**HIGH:**
- H1: Fixed plan.md header version from 1.2.0 to 1.3.0→1.4.0; added version log entry
- H2: Annotated T063 with ⚠️ notice that implementation has confirmed bug (plan §XI.3); acceptance criteria not verified per preamble
- H3: Updated spec.md FR-009 AI Logging to use entity_id (not task_id); added note that entity_id=task_id for subtask/priority, note_id for note-parsing; updated T160 in tasks.md to match
- H4: Added T171 (notification.schema.ts creation task) to Phase 9 before T092
- H5: Changed plan.md NFR-003 from "✅ Fully compliant" to "⚠️ Partially compliant — T157-T159 open"
- H6: Added T172 (FR-004 navigation guard) to Phase 14 as Phase 6 backfill fix

**MEDIUM:**
- M1: Added T175 (Lighthouse CI gate) and T176 (Web Vitals threshold alerts) to Phase 13 Performance section
- M2: Updated T079 to include achievement cache invalidation note — on unlock, invalidate ['achievements', 'me'] so perks apply immediately
- M3: Resolved via C2 (reclassifying T157-T159 clears Phase 13 open tasks; Phase 15 dependency chain now valid)
- M4: Added daily_ai_credits_used to T077 UserAchievementStateSchema definition
- M5: Added [DEFERRED] tag to circuit breaker criterion in spec.md NFR-005

**LOW:**
- L1: Verified T135/T138 coordination note is sufficient — no edit needed
- L2: Qualified FR-007 "1 minute" criterion as backend-owned in spec.md
- L3: Marked NFR-006 P95 dashboard as out-of-scope current sprint in spec.md

**Net task additions**: 6 new tasks (T171-T176); total 176 tasks
**Spec version**: bumped to 1.4.0
**Plan version**: bumped to 1.4.0
**T112 status**: corrected from [X] to [ ]

## Outcome

- ✅ Impact: All 16 sp.analyze findings remediated; 4 CRITICAL constitution violations resolved; 6 HIGH issues corrected; 5 MEDIUM gaps addressed; 3 LOW qualifications added; T112 correctly reopened; 6 new tasks added (T171-T176)
- 🧪 Tests: No tests run (documentation-only changes to spec/plan/tasks)
- 📁 Files: specs/002-perpetua-frontend/spec.md (v1.4.0), specs/002-perpetua-frontend/plan.md (v1.4.0), specs/002-perpetua-frontend/tasks.md (176 tasks)
- 🔁 Next prompts: Run /sp.implement to begin Phase 14 Bug Fix Sprint; build T112 (ConflictResolutionModal) before T124; build T171-T174 in Phase 14 order
- 🧠 Reflection: ConflictResolutionModal.tsx being absent despite [X] marker is a significant deviation — the preamble's "[X] = code exists" rule was violated for this task. The reclassification of T157-T159 resolves the Phase 13/14 boundary ambiguity cleanly. The entity_id naming drift between spec and plan was subtle — both artifacts agreed on meaning but disagreed on field name, which would have caused test/log schema mismatches.

## Evaluation notes (flywheel)

- Failure modes observed: [X] marker semantics are ambiguous — "code exists" vs "correct implementation"; need automated file-existence check for [X]-marked tasks
- Graders run and results (PASS/FAIL): n/a (documentation remediation)
- Prompt variant (if applicable): Follow-up to /sp.analyze 002 (PHR 017)
- Next experiment: Add file-existence validation step to sp.analyze to auto-detect [X] tasks pointing to absent files
