---
id: 006
title: Generate Backend Tasks
stage: tasks
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: 003-perpetua-backend
branch: 003-perpetua-backend
user: developer
command: /sp.tasks
labels: ["tasks", "tdd", "backend", "fastapi", "postgresql"]
links:
  spec: specs/003-perpetua-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-perpetua-backend/tasks.md
tests:
  - null
---

## Prompt

Generate a comprehensive, dependency-ordered tasks.md for the Perpetua Flow Backend API.

## Feature Context

- **Feature Branch**: `003-perpetua-backend`
- **Spec Location**: `specs/003-perpetua-backend/spec.md`
- **Plan Location**: `specs/003-perpetua-backend/plan.md`
- **Research Location**: `specs/003-perpetua-backend/research.md`
- **Data Model**: `specs/003-perpetua-backend/docs/data-model.md`
- **API Specification**: `specs/003-perpetua-backend/docs/api-specification.md`
- **Authentication**: `specs/003-perpetua-backend/docs/authentication.md`
- **Output Location**: `specs/003-perpetua-backend/tasks.md`

## Technology Stack (Confirmed)

- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic
- **Background Jobs**: PostgreSQL-based queue (SKIP LOCKED pattern)
- **Events**: In-process event bus (synchronous)
- **AI Integration**: OpenAI Agents SDK (`openai-agents`) with Pydantic schemas
- **Voice Transcription**: Deepgram NOVA2 (batch API)
- **Payments**: Checkout.com webhooks
- **Deployment**: Railway (API service + Worker service)
- **Testing**: pytest, pytest-asyncio, httpx, factory-boy, respx, schemathesis

## Task Generation Requirements

### 1. TDD Enforcement (Mandatory)

ALL tasks MUST follow Red → Green → Refactor workflow:
- **RED**: Write failing tests FIRST (explicit test tasks)
- **GREEN**: Implement minimum code to pass tests
- **REFACTOR**: Improve code quality without changing behavior

### 2. Task Granularity: Fine-Grained (~200-250 tasks)

Break down into individual, atomic tasks per the specification requirements.

### 3. User Story Coverage: All 13 Stories

Cover ALL user stories with P1 marked as MVP.

## Response snapshot

Generated comprehensive `specs/003-perpetua-backend/tasks.md` with:

- **416 total tasks** across 24 phases
- **MVP tasks (P1)**: ~94 tasks (Phases 1-4: Foundation, Models, Auth, Tasks)
- **All 13 user stories** mapped with explicit task counts
- **All 69 functional requirements** (FR-001 to FR-069) covered
- **All 12 success criteria** (SC-001 to SC-012) with validation tasks
- **TDD structure** with RED/GREEN/REFACTOR phases per user story
- **All 8 database migrations** listed in Phase 1
- **All 5 background job types** defined in Phase 9
- **All 3 AI agents** (PerpetualFlowAssistant, SubtaskGenerator, NoteConverter)
- **Contract testing infrastructure** with schemathesis
- **Parallel opportunities**: ~120 tasks marked [P]
- **24 checkpoints** for validation milestones
- **Clear dependency graph** and execution order
- **Implementation strategy** with MVP-first approach

## Outcome

- ✅ Impact: Comprehensive task breakdown for full backend implementation
- 🧪 Tests: TDD workflow explicit in each user story phase
- 📁 Files: Created specs/003-perpetua-backend/tasks.md (416 tasks)
- 🔁 Next prompts: /sp.implement to begin Phase 1 execution
- 🧠 Reflection: Fine-grained tasks enable parallel work and clear progress tracking

## Evaluation notes (flywheel)

- Failure modes observed: None - all spec requirements mapped to tasks
- Graders run and results (PASS/FAIL): PASS - All 13 US, 69 FR, 12 SC covered
- Prompt variant (if applicable): Used detailed prompt from my_prompts/003-prompt_tasks.md
- Next experiment (smallest change to try): Track task completion velocity during implementation
