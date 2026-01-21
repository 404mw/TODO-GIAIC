---
id: 008
title: Refine Backend Spec with 10 Amendments
stage: spec
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.specify
labels: ["refinement", "spec", "backend", "amendments"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
  - specs/003-perpetua-backend/checklists/requirements.md
tests:
  - null
---

## Prompt

003-perpetua-backend --refine

## HIGH Priority

### U1: Missing User Profile Update Endpoint
- **Location:** spec.md (missing requirement)
- **Issue:** No FR exists for user profile management (update name etc)
- **Recommendation:** Add FR-070 for profile CRUD:
  ```
  FR-070: System MUST support user profile updates (name) via PATCH /api/v1/users/me
  ```

### U2: Missing Achievement Notification Delivery Mechanism
- **Location:** spec.md US9 (Achievement System)
- **Issue:** User Story 9 says users earn achievements but doesn't specify HOW they're notified
- **Recommendation:** Add to US9 acceptance scenarios:
  ```
  4. Given an achievement is unlocked, When unlock occurs, Then frontend receives the data which triggers a notification and shows info with UI toast
  ```

### A1: OAuth Sign-in Timing Ambiguity
- **Location:** spec.md:L376 (SC-001)
- **Issue:** "within 10 seconds of clicking 'Sign in'" - unclear if this includes:
  - Network latency to Google
  - User interaction with Google consent screen
  - Or just backend processing time
- **Recommendation:** Clarify in SC-001:
  ```
  SC-001: Backend OAuth token exchange and user creation/lookup completes within 2 seconds;
          end-to-end flow (excluding user interaction with Google) completes within 10 seconds
  ```

## MEDIUM Priority

### A2: Rate Limit Scope Ambiguity
- **Location:** spec.md:FR-061
- **Issue:** "100 req/min general" - per-endpoint or global bucket?
- **Recommendation:** Clarify:
  ```
  FR-061: System MUST enforce per-user rate limits: 100 req/min across all general endpoints (shared bucket),
          20 req/min for AI endpoints (separate bucket), 10 req/min for auth endpoints (per-IP)
  ```

### U3: Push Notification Permission Flow
- **Location:** spec.md:FR-028
- **Issue:** "requires permission" but doesn't specify responsibility
- **Recommendation:** Add clarification:
  ```
  FR-028a: Frontend manages WebPush subscription via browser API; backend stores push subscription tokens
  FR-028b: System MUST gracefully handle expired/invalid push tokens without blocking operations
  ```

### U4: Voice Note Audio Storage
- **Location:** spec.md (missing infrastructure requirement)
- **Issue:** Voice notes reference `voice_url` but no storage mechanism specified
- **Recommendation:** Add infrastructure assumption or requirement:
  ```
  Assumption 9: Audio is streamed in real time from the client to the STT provider over a WebSocket (via the backend as a relay); the backend does not persist voice recordings.
  ```

### D1: Focus Completion Tracking Duplication
- **Location:** spec.md FR-045, US9, US12
- **Issue:** Focus completion (>=50% duration) mentioned in 3 places with slight variation
- **Recommendation:** Consolidate:
  - Keep detailed definition in FR-045
  - Reference FR-045 from US9 and US12

## LOW Priority

### U5: Purchased Credits Lifecycle
- **Location:** spec.md:FR-042
- **Issue:** FIFO mentions `purchased` credits but purchase flow underspecified
- **Recommendation:** Add to FR-051:
  ```
  FR-051a: Purchased credits have no expiration date
  FR-051b: Purchased credits consumed last in FIFO order
  ```

### D2: Voice Transcription Requirements Split
- **Location:** spec.md FR-033, FR-036
- **Issue:** Billing (FR-033) and duration limit (FR-036) are separate but tightly related
- **Recommendation:** Consider merging into single "Voice Transcription" requirement section

### T2: Soft vs Hard Deletion Terminology
- **Location:** spec.md:FR-012
- **Issue:** Single requirement covers both soft (hidden flag) and hard (tombstone) deletion
- **Recommendation:** Split:
  ```
  FR-012a: System MUST support soft deletion via hidden flag (recoverable, not shown in default lists)
  FR-012b: System MUST support hard deletion with tombstone creation (limited recovery window)
  ```

## Response snapshot

Applied all 10 refinements to the 003-perpetua-backend spec:

**HIGH Priority (3 items):**
- FR-070: Added user profile updates endpoint (PATCH /api/v1/users/me)
- US9-4: Added acceptance scenario for achievement notification delivery via API response
- SC-001: Clarified OAuth timing (2s backend processing, 10s end-to-end excluding Google consent)

**MEDIUM Priority (4 items):**
- FR-061: Clarified rate limit scope (per-user shared bucket for general, separate buckets for AI/auth)
- FR-028a/FR-028b: Split push notification responsibility (frontend WebPush, backend token storage)
- Assumption 9: Added voice audio streaming assumption (no backend persistence)
- US9/US12: Added FR-045 cross-references for focus completion tracking consolidation

**LOW Priority (3 items):**
- FR-051a/FR-051b: Added purchased credits lifecycle (no expiration, consumed last in FIFO)
- FR-033/FR-036: Added cross-references for voice transcription requirements
- FR-012a/FR-012b: Split soft deletion (hidden flag) from hard deletion (tombstone)

Updated requirements checklist to reflect refinements (now 68 functional requirements).

## Outcome

- Impact: Improved spec clarity and completeness; resolved 10 ambiguities identified in cross-artifact analysis
- Tests: N/A (specification refinement)
- Files: 2 files modified (spec.md, requirements.md)
- Next prompts: /sp.plan to update implementation plan if needed, or proceed to implementation
- Reflection: Refinements addressed gaps identified during consistency analysis; spec now has clearer ownership boundaries between frontend/backend

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider automated spec validation tooling to catch ambiguities earlier
