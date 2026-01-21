---
id: 011
title: Apply Spec Remediations
stage: spec
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: user
command: /sp.specify apply spec remediations
labels: ["remediation", "spec", "clarification", "FR-035", "FR-069", "US9"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/spec.md
tests:
  - null
---

## Prompt

apply spec remediations

## Response snapshot

Applied 3 spec remediations from 003-analysis2.md to specs/003-perpetua-backend/spec.md:

1. **SPEC-R1** (A2 - MEDIUM): Clarified FR-035 Per-Task AI Request Limit Scope
   - Added: "The counter is session-scoped. Counter resets at session change."

2. **SPEC-R2** (G1 - MEDIUM): Added API Deprecation Policy
   - Added FR-069a: 90-day deprecation notice requirement
   - Added FR-069b: Deprecation header with sunset date per RFC 8594

3. **SPEC-R3** (H1 - HIGH): Clarified Achievement Notification Delivery (US9 AS4)
   - Clarified that API response MUST include `unlocked_achievements` array with achievement details (id, name, description, perk)

## Outcome

- ✅ Impact: 3 spec clarifications applied, resolving 1 HIGH and 2 MEDIUM severity issues
- 🧪 Tests: N/A (spec changes only)
- 📁 Files: 1 file modified (spec.md)
- 🔁 Next prompts: Apply plan remediations (PLAN-R1, PLAN-R2), Apply task remediations (TASK-R1 through TASK-R7)
- 🧠 Reflection: Spec remediations focused on clarifying ambiguous requirements and adding missing policy details

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.analyze 003 to verify remediation effectiveness
