# Analysis Findings: 003-perpetua-backend

**Generated:** 2026-01-19
**Feature:** 003-perpetua-backend
**Analysis Type:** Cross-artifact consistency and quality analysis

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Total Functional Requirements | 69 |
| Requirements with Task Coverage | 67 (97.1%) |
| Total Tasks | 416 |
| Critical Issues | 0 |
| High Issues | 4 |
| Medium Issues | 11 |
| Low Issues | 6 |
| Constitution Violations | 0 |

---

## Findings by Artifact

---

# SPEC FINDINGS (`/sp.specify`)

Use `/sp.specify 003-perpetua-backend --refine` to address these issues.

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

---

# PLAN FINDINGS (`/sp.plan`)

Use `/sp.plan 003-perpetua-backend --refine` to address these issues.

## MEDIUM Priority

### A3: Multi-Instance Deployment Scope
- **Location:** plan.md:L305
- **Issue:** "optional Redis backend for multi-instance" - is multi-instance in scope?
- **Recommendation:** Clarify in Technical Context:
  ```
  Deployment Scope: Single-instance initial deployment; multi-instance via Redis rate limiter is out-of-scope for v1
  ```

### I1: OAuth Implementation Inconsistency
- **Location:** plan.md AD-001 vs api-spec.md
- **Issue:** Plan says "Backend verifies Google ID tokens directly" but API spec shows code exchange endpoint
- **Recommendation:** Clarify flow:
  - Frontend sends code, backend exchanges code and verifies
  - **Current spec suggests this** - align plan AD-001 with this

## LOW Priority

### Deployment Architecture Clarity
- **Location:** plan.md Deployment Architecture diagram
- **Issue:** Shows Railway but doesn't mention staging vs production environments
- **Recommendation:** Add environment note:
  ```
  Environments:
  - Local (Docker Compose)
  - Staging (Railway preview)
  - Production (Railway main)
  ```

---

# TASKS FINDINGS (`/sp.tasks`)

Use `/sp.tasks 003-perpetua-backend --regenerate` after spec/plan updates.

## HIGH Priority

### Missing Task Coverage: FR-013
- **Location:** tasks.md (missing)
- **Issue:** FR-013 "maximum task duration of 30 days from creation" has no validation task
- **Recommendation:** Add to Phase 4:
  ```
  - [ ] T130a [US2] Test: Task creation fails if due_date > created_at + 30 days in tests/unit/services/test_task_service.py (FR-013)
  - [ ] T130b [US2] Implement 30-day max duration validation in src/services/task_service.py (FR-013)
  ```

### Missing Task Coverage: FR-069
- **Location:** tasks.md (missing)
- **Issue:** FR-069 "backward compatibility within major version" has no deprecation strategy task
- **Recommendation:** Add to Phase 24:
  ```
  - [ ] T416a [Polish] Document API versioning and deprecation policy in docs/api-versioning.md (FR-069)
  ```

## MEDIUM Priority

### I3: Task Count Inconsistency
- **Location:** tasks.md Summary vs Phase counts
- **Issue:** Summary says "Total Tasks: 416" but Phase 1 numbering (T001-T029) suggests 29 tasks while text says "28 tasks"
- **Recommendation:** Reconcile:
  - Phase 1 header says "28 tasks" but has T001-T029 (29 task IDs)
  - Verify each phase and update summary

### I5: User Story 5 Split Across Phases
- **Location:** tasks.md Phases 7, 12, 13
- **Issue:** US5 "Notes with Voice Recording" spans 3 non-consecutive phases (7, 12, 13) which may cause confusion
- **Recommendation:** Add phase notes explaining split:
  ```
  Phase 7: Core note CRUD (text notes, limits)
  Phase 12: AI-powered note conversion (depends on Phase 10 AI infrastructure)
  Phase 13: Voice transcription (depends on Phase 10 AI infrastructure + Deepgram)
  ```

### G1: Missing Concurrent Update Stress Test
- **Location:** tasks.md Phase 23
- **Issue:** spec.md Edge Cases mention concurrent updates but no dedicated stress test
- **Recommendation:** Add to Phase 23:
  ```
  - [ ] T402a [Validation] Create concurrent update stress test (optimistic locking) in tests/integration/test_concurrent_updates.py
  ```

### G2: Missing Readiness Probe Test
- **Location:** tasks.md
- **Issue:** T012 creates health endpoints but no integration test for readiness probe
- **Recommendation:** Add to Phase 1:
  ```
  - [ ] T012a [Infra] Integration test: Readiness probe returns 503 when DB unavailable in tests/integration/test_health.py
  ```

## LOW Priority

### T1: Terminology Standardization
- **Location:** tasks.md throughout
- **Issue:** "Task Instance" vs "task" used interchangeably
- **Recommendation:** Standardize during implementation:
  - Use "task" in API layer and user-facing docs
  - Use "task_instance" in database models and internal code

### Unmapped Documentation Tasks
- **Location:** tasks.md T138, T252, T262, T348, T366, T384
- **Issue:** 6 documentation tasks have no FR reference
- **Recommendation:** These are quality assurance tasks - acceptable but could reference a "documentation quality gate" requirement

---

# QUICK REFERENCE: Commands to Run

```bash
# 1. If clarifications needed (recommended first):
/sp.clarify 003-perpetua-backend

# 2. After clarifications, update spec:
/sp.specify 003-perpetua-backend --refine

# 3. If plan needs updates:
/sp.plan 003-perpetua-backend --refine

# 4. Regenerate tasks after spec/plan updates:
/sp.tasks 003-perpetua-backend

# 5. Re-run analysis to verify fixes:
/sp.analyze 003-perpetua-backend

# 6. When all issues resolved, start implementation:
/sp.implement 003-perpetua-backend --phase 1
```

---

# CONSTITUTION ALIGNMENT

**Status: ALL PASS**

| Principle | Status |
|-----------|--------|
| I. Spec is supreme | PASS |
| II. Phase discipline | PASS |
| III. Data integrity | PASS |
| III. Undo guarantee | PASS |
| IV. AI restrictions | PASS |
| V. AI logging | PASS |
| VI. Single-resp endpoints | PASS |
| VII. Schema consistency | PASS |
| VIII. TDD mandatory | PASS |
| IX. Secrets in .env | PASS |
| X. Simplicity | PASS |

No constitutional violations detected. All artifacts align with project principles.
