---
id: 002
title: Spec Clarifications
stage: spec
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: perpetua-frontend
branch: 002-perpetua-frontend
user: claude-agent
command: /sp.clarify
labels: ["clarification", "specification", "data-model", "ui-ux", "ai-features", "rate-limiting"]
links:
  spec: specs/002-perpetua-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-perpetua-frontend/spec.md
tests:
  - All 5 clarification questions answered and integrated
---

## Prompt

User invoked `/sp.clarify` to identify and resolve ambiguities in the Perpetua Flow frontend specification before proceeding to planning phase.

Performed structured ambiguity scan across taxonomy categories:
- Functional Scope & Behavior
- Domain & Data Model
- Interaction & UX Flow
- Non-Functional Quality Attributes
- Integration & External Dependencies
- Edge Cases & Failure Handling
- Constraints & Tradeoffs
- Terminology & Consistency
- Completion Signals

Identified 5 high-impact clarifications prioritized by (Impact × Uncertainty):

1. **Task Identity & Uniqueness**: How are tasks uniquely identified?
2. **Consistency Streak Reset**: When/how do streaks reset?
3. **Optimistic Update Conflicts**: How to handle client/server state conflicts?
4. **AI Rate Limiting**: How to handle quota exhaustion gracefully?
5. **Tag Input Method**: How should users input and manage tags?

User accepted all 5 recommended answers through interactive questioning loop.

## Response snapshot

**Clarifications Integrated**:

1. **Q**: How should the system identify and handle duplicate tasks?
   **A**: Client-generated UUID (collision-resistant, offline-friendly, no server dependency)
   - Updated FR-001, Task entity, Sub-task entity with UUID identifiers
   - Added creation timestamps to entities

2. **Q**: When should a consistency streak reset?
   **A**: Reset at midnight UTC (consistent but ignores user timezone)
   - Updated FR-033 (renumbered from FR-032) with UTC midnight clarification
   - Updated Achievement entity with grace day tracking
   - Note: User modified recommended answer from "local timezone" to "UTC" for consistency

3. **Q**: How should the system handle conflicts between optimistic updates and server responses?
   **A**: Server wins, discard optimistic changes silently (simple, consistent with ephemeral design)
   - Updated FR-059 (renumbered from FR-058) with conflict resolution policy
   - Added edge case for optimistic update conflicts

4. **Q**: How should the system handle AI rate limit or quota exhaustion?
   **A**: Show error, disable AI features temporarily, retry after cooldown period (graceful degradation)
   - Added FR-028 for AI rate limiting with configurable cooldown via .env
   - Added edge case with default 15-minute cooldown
   - Renumbered subsequent FRs (FR-029 through FR-070)

5. **Q**: How should users input and manage task tags?
   **A**: Freeform with autocomplete from previously used tags (balance of flexibility and consistency)
   - Updated FR-001 with tag input method details
   - Updated Task entity with tag structure (array of freeform strings with autocomplete history)

**Sections Modified**:
- Clarifications (new section created)
- Requirements → Core Task Management
- Requirements → AI Features
- Requirements → Achievements & Metrics
- Requirements → State Management & Data
- Key Entities (Task, Sub-task, Achievement)
- Edge Cases

**Total Functional Requirements**: 70 (was 69, added FR-028)

**Coverage Status**: All critical categories resolved (Functional Scope, Data Model, UX Flow, Non-Functional Quality, Integration, Edge Cases, Constraints)

## Outcome

- ✅ Impact: Specification fully clarified with 5 critical ambiguities resolved; ready for architectural planning
- 🧪 Tests: All 5 questions answered via interactive Q&A; answers integrated atomically after each acceptance
- 📁 Files: Updated specs/002-perpetua-frontend/spec.md with clarifications, updated requirements, enhanced entities, new edge cases
- 🔁 Next prompts: `/sp.plan` to generate architectural design and implementation plan
- 🧠 Reflection: UTC timezone choice for streaks (vs local timezone) improves consistency across users but may feel less intuitive for international users; tradeoff accepted for simplicity. Client-generated UUIDs align with offline-first principles despite no persistent offline mode being in scope. Server-wins conflict resolution is simple but provides no user warning on data loss (acceptable given ephemeral updates and single-user scope).

## Evaluation notes (flywheel)

- Failure modes observed: None. All 5 questions answered successfully with recommended options (user modified Q2 from local to UTC). Incremental integration prevented context loss.
- Graders run and results (PASS/FAIL): PASS - All clarifications integrated correctly; no unresolved placeholders; FR numbering corrected after insertion
- Prompt variant (if applicable): Standard interactive clarification loop with recommended answers (new pattern)
- Next experiment (smallest change to try): Consider presenting all 5 questions upfront with recommendations to reduce interaction rounds (trade-off: less adaptive to user preferences vs faster completion)
