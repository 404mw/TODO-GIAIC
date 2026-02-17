---
id: 070
title: Reverse Engineer Backend Codebase to SDD Artifacts
stage: misc
date: 2026-02-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 003-perpetua-backend
user: 404mw
command: /sp.reverse-engineer
labels: ["reverse-engineering", "specification", "architecture", "documentation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/docs/reverse-engineered/spec.md
 - backend/docs/reverse-engineered/plan.md
 - backend/docs/reverse-engineered/tasks.md
 - backend/docs/reverse-engineered/intelligence-object.md
tests:
 - None (documentation/analysis task)
---

## Prompt

```
Command: sp.reverse-engineer

Codebase path: `/backend`
Project Constitution path: `/.specify/memory/constitution.md`
Output location: `/backend/docs/reverse-engineered/`
```

Execute comprehensive codebase reverse engineering workflow to extract specifications, plans, tasks, and reusable intelligence from the existing Perpetua Flow backend implementation (FastAPI + SQLModel + PostgreSQL).

## Response snapshot

Successfully completed comprehensive reverse engineering of the Perpetua Flow backend codebase (4233 Python files, 1044 tests). Generated four SDD-RI artifacts:

1. **spec.md** (Production specification)
   - 15 functional requirements (FR-001 to FR-015) with full acceptance criteria
   - Task management, AI integration, credits, achievements, focus mode, recovery
   - 5 non-functional requirements (performance, security, reliability, scalability, observability)
   - Known gaps documented (6 items with remediation plans)
   - Acceptance tests for critical flows

2. **plan.md** (Implementation architecture)
   - Layered architecture analysis (Middleware → API → Service → Model → Database)
   - 7 design patterns extracted (Service Layer, Optimistic Locking, Idempotency, etc.)
   - Technology stack rationale (FastAPI async, SQLModel, PostgreSQL, JWT RS256)
   - Data flow diagrams (synchronous request, async AI chat, background jobs)
   - 12-week regeneration timeline with quality gates

3. **tasks.md** (Task breakdown)
   - 12-week implementation plan (8 phases)
   - 90+ actionable tasks with acceptance criteria
   - TDD approach (write tests first)
   - Phase dependencies clearly mapped
   - Test targets: 800+ unit, 200+ integration, 150+ contract tests

4. **intelligence-object.md** (Reusable knowledge)
   - 6 skills documented in Persona + Questions + Principles format:
     - SQLAlchemy Async Pattern (MissingGreenlet prevention)
     - Optimistic Locking (concurrent edit safety)
     - Multi-Tier Credit System (priority-based deduction)
     - Idempotency for Safe Retries
     - Soft Delete with Recovery Window
   - 3 Architecture Decision Records (ADRs) inferred from code evidence
   - Lessons learned (what worked, what didn't)
   - Reusability assessment (portable patterns vs domain-specific)

**Key Architectural Patterns Discovered**:
- Async-first FastAPI with comprehensive middleware stack (7 layers)
- SQLAlchemy async with explicit eager loading (selectinload pattern)
- Optimistic locking via version field (VersionedModel base class)
- Multi-tier credit system (daily → subscription → purchased → kickstart)
- Idempotency middleware with 24-hour response caching
- Tombstone pattern for 7-day soft delete recovery
- JWT RS256 asymmetric auth + opaque refresh token rotation
- Service layer pattern with dependency injection
- Response wrappers (DataResponse, PaginatedResponse)

**Analysis Depth**:
- Reconnaissance: Directory structure, dependencies, test coverage
- Deep analysis: Intent archaeology, architectural patterns, intelligence extraction
- 6 analysis dimensions: Intent, Architecture, Structure, Intelligence, Gaps, Regeneration

**Completeness**: All artifacts cross-reference and enable full system regeneration from specification.

## Outcome

- ✅ Impact: Complete reverse-engineered specification suite enabling system regeneration and knowledge preservation
- 🧪 Tests: No tests run (documentation/analysis task)
- 📁 Files: 4 comprehensive artifacts created (spec.md, plan.md, tasks.md, intelligence-object.md)
- 🔁 Next prompts: Can now regenerate backend using spec.md, implement improvements from gaps, extract skills to template library
- 🧠 Reflection: Reverse engineering successfully extracted implicit knowledge (async patterns, credit system, soft delete) that wasn't documented anywhere. The tombstone pattern and multi-tier credit system are particularly reusable for other projects.

## Evaluation notes (flywheel)

- Failure modes observed: None (workflow completed successfully)
- Graders run and results (PASS/FAIL): N/A (no automated grading for reverse engineering)
- Prompt variant (if applicable): N/A (first execution of sp.reverse-engineer workflow)
- Next experiment (smallest change to try): Apply extracted skills to new project to validate portability; create cookiecutter template from patterns
