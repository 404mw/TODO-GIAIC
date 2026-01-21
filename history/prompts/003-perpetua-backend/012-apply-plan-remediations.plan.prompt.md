---
id: 012
title: Apply Plan Remediations from Analysis
stage: plan
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.plan
labels: ["remediation", "plan", "analysis", "cross-artifact"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
tests:
  - null
---

## Prompt

@003-analysis2.md

spec remediations has been applied. mirror then in feature plan in addition to applying suggested plan remediations

## Response snapshot

Applied all remediations from 003-analysis2.md to the feature plan:

**Plan Remediations Applied:**
1. **PLAN-R1**: Added Audio Format Requirements section after WebSocket Message Protocol with WebM/Opus specs, sample rate, chunk size, and silence detection requirements
2. **PLAN-R2**: Added Refresh Token Storage section after AD-001 documenting hash storage, rotation behavior, revocation handling, and single active token policy

**Spec Remediations Mirrored in Plan:**
3. **SPEC-R1 (FR-035)**: Added Per-Task AI Request Limits section clarifying session-scoped counter, warn at 5, block at 10, reset on session change
4. **SPEC-R2 (FR-069a, FR-069b)**: Added AD-006 API Deprecation Policy section with 90-day notice requirement and RFC 8594 Deprecation header implementation
5. **SPEC-R3 (US9 AS4)**: Added Achievement Notification Delivery section clarifying inline response mechanism with unlocked_achievements array schema

**Additional Alignment:**
- Updated websocket.py to ws_voice.py in project structure for consistency with endpoint path

## Outcome

- ✅ Impact: Plan now fully aligned with spec remediations; all HIGH and MEDIUM severity gaps addressed
- 🧪 Tests: N/A (documentation update)
- 📁 Files: 1 file modified (specs/003-perpetua-backend/plan.md)
- 🔁 Next prompts: /sp.tasks to regenerate tasks with new coverage, /sp.analyze to verify alignment
- 🧠 Reflection: Mirroring spec changes in plan ensures traceability and prevents implementation drift

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.analyze 003 to verify 100% coverage
