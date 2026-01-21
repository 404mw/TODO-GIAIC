---
id: 001
title: Plan Refinement OAuth WebSocket Endpoints
stage: plan
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.plan
labels: ["plan-refinement", "oauth", "websocket", "deployment", "api-spec"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/docs/api-specification.md
tests:
  - null
---

## Prompt

```text
003-perpetua-backend --refine

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
additionally check spec for missing plans and update. ask me for clarifications without making assumptions
```

User clarifications received:
1. No multi-instance for v1 (single Railway instance, in-memory rate limiter only)
2. OAuth flow: Frontend (BetterAuth) handles code exchange, backend receives ID token directly
3. Three environments: Local (Docker Compose) → Staging (Railway preview) → Production (Railway main)
4. Add api/users.py route handler for FR-070
5. Backend focus for UI - can adjust later
6. Add WebSocket endpoint for voice streaming to Deepgram

## Response snapshot

Refined the 003-perpetua-backend plan.md and api-specification.md with the following changes:

### Changes Applied:

1. **AD-001 OAuth Strategy** - Updated to clarify that frontend (BetterAuth) handles OAuth code exchange, backend receives and verifies Google ID token
   - Added explicit 5-step flow documentation
   - Updated api-specification.md endpoint to receive `id_token` instead of `code`

2. **Multi-Instance Scope** - Explicitly marked as out-of-scope for v1
   - Rate limiting section now states "Single-instance deployment; multi-instance via Redis is out-of-scope for v1"
   - Added deployment scope note

3. **Deployment Architecture** - Added environments table
   - Local: Docker Compose with local PostgreSQL
   - Staging: Railway preview branch with Neon staging
   - Production: Railway main branch with Neon main

4. **User Profile Endpoint** - Added api/users.py to project structure
   - GET /api/v1/users/me
   - PATCH /api/v1/users/me (FR-070)
   - Full API spec documentation added

5. **WebSocket Voice Streaming** - Added comprehensive documentation
   - WS /api/v1/ws/voice/transcribe endpoint
   - Backend acts as relay to Deepgram NOVA2
   - Message protocol with auth, transcripts, errors
   - Constraints: Pro only, 300s max, 5 credits/min
   - Added websocket.py to project structure

6. **Implementation Phases** - Updated to include new endpoints
   - Phase 1: Added user profile endpoint
   - Phase 4: Added WebSocket voice streaming

## Outcome

- ✅ Impact: Plan aligned with spec, OAuth flow clarified, WebSocket endpoint documented
- 🧪 Tests: N/A (documentation only)
- 📁 Files: 2 files modified (plan.md, api-specification.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Clarification questions prevented incorrect assumptions; OAuth flow needed alignment between plan and API spec

## Evaluation notes (flywheel)

- Failure modes observed: None - user provided clear answers to all clarification questions
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Could auto-detect inconsistencies between plan AD sections and API spec endpoints
