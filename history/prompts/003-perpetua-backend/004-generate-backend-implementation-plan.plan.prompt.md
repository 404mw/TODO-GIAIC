---
id: 004
title: Generate Backend Implementation Plan
stage: plan
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 002-perpetua-frontend
user: architect
command: /sp.plan
labels: ["planning", "architecture", "backend", "fastapi", "postgresql"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/plan.md
  - specs/003-perpetua-backend/research.md
  - specs/003-perpetua-backend/quickstart.md
  - specs/003-perpetua-backend/contracts/openapi.yaml
tests:
  - null
---

## Prompt

003 @003-prompt_plan.md

Generate an implementation plan for the Perpetua Flow Backend API using the context from 003-prompt_plan.md which specifies:
- Technology Stack: Python 3.11+, FastAPI, SQLModel, PostgreSQL (Neon Serverless), Alembic
- Architecture: Single database, in-process event bus, PostgreSQL-based job queue
- Scope: All 13 user stories (P1-P4) covering authentication, tasks, notes, AI, subscriptions, achievements
- Deployment: Railway (API + Worker services)

## Response snapshot

Successfully generated a comprehensive implementation plan for the Perpetua Flow Backend API:

**Phase 0 (Research):**
- Resolved all technical unknowns including Google OAuth verification, JWT implementation (RS256), database connection pooling (Neon), PostgreSQL SKIP LOCKED job queue, OpenAI function calling, Deepgram batch transcription, Checkout.com webhook security, SSE streaming, rate limiting (slowapi), RRULE parsing, credit FIFO consumption, and idempotency key storage.

**Phase 1 (Design):**
- Verified data-model.md completeness (13 entities, all relationships documented)
- Created quickstart.md for local development setup
- Generated OpenAPI 3.1 specification with 40+ endpoints covering all API routes

**Key Architecture Decisions:**
- AD-001: Direct Google ID token verification with own JWT issuance
- AD-002: PostgreSQL SKIP LOCKED for background jobs (no Redis/RabbitMQ)
- AD-003: In-process synchronous event bus
- AD-004: AI returns suggestions requiring user confirmation
- AD-005: URL path versioning (/api/v1/)

**Constitution Check:** All 15 principles PASS - no violations requiring justification.

**Generated Artifacts:**
1. plan.md - Complete implementation plan with 7 phases
2. research.md - Technical research with 12 decisions documented
3. quickstart.md - Local development setup guide
4. contracts/openapi.yaml - Full OpenAPI 3.1 specification

## Outcome

- ✅ Impact: High - Provides complete technical blueprint for backend implementation
- 🧪 Tests: N/A (planning phase)
- 📁 Files: 4 files created (plan.md, research.md, quickstart.md, openapi.yaml)
- 🔁 Next prompts: Run `/sp.tasks` to generate task breakdown for implementation
- 🧠 Reflection: Comprehensive plan covers all 13 user stories with clear implementation phases. Architecture decisions favor simplicity (PostgreSQL-only infrastructure) per constitution.

## Evaluation notes (flywheel)

- Failure modes observed: Setup script detected wrong feature (002 vs 003) - required manual override
- Graders run and results (PASS/FAIL): Constitution check PASS (15/15 principles)
- Prompt variant (if applicable): Standard /sp.plan with custom context file
- Next experiment (smallest change to try): Improve setup-plan.ps1 to accept feature number as parameter
