---
name: multi-stack-code-generator
description: Generates type-safe code for Python (FastAPI/SQLModel) and TypeScript (Next.js/Zod) simultaneously. Use when implementing features across frontend and backend to ensure schema alignment and contract compliance.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Multi-Stack Code Generator

## Purpose

Generate synchronized, type-safe code across the full stack (FastAPI + Next.js) to maintain schema consistency and prevent contract violations.

## Tech Stack (from Project_Outline.md)

**Backend:**
- Python with FastAPI
- SQLModel (Pydantic + SQLAlchemy)
- Neon DB (PostgreSQL)
- UV for dependency management

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Zod for validation

## Instructions

### On Feature Implementation Request

When user requests a full-stack feature:

1. **Read specification first**
   - Load `specs/<feature>/spec.md`
   - Extract data model, API contracts, validation rules

2. **Generate backend code**
   - SQLModel models (database + Pydantic)
   - FastAPI endpoints
   - Request/response schemas
   - Validation logic

3. **Generate frontend code**
   - Zod schemas (matching backend)
   - TypeScript types
   - API client functions
   - React components (if requested)

4. **Verify alignment**
   - Run schema-sync-validator checks
   - Ensure single-responsibility endpoints
   - Check constitutional compliance

5. **Present synchronized code**
   - Show backend and frontend together
   - Highlight alignment points

## Code Generation Patterns

For detailed code templates, see: `.claude/skills/multi-stack-code-generator/patterns.md`

**Quick patterns:**
- New Entity: Model + API + Frontend + Migration
- Enum Alignment: Constants shared between stacks
- Date/Timestamp: ISO 8601 string handling

## Type Alignment

For complete type mappings, see: `.claude/skills/multi-stack-code-generator/type-mappings.md`

**Quick reference:**
- `str` → `z.string()`
- `UUID` → `z.string().uuid()`
- `datetime` → `z.string().datetime()`
- `Literal["a", "b"]` → `z.enum(["a", "b"])`
- `Optional[T]` → `.optional()`

## Response Format

### When Generating Full Stack Code

```
🔧 MULTI-STACK CODE GENERATION

Feature: [Feature name]
Spec: specs/[feature]/spec.md

Generated Code:

## Backend (Python/FastAPI)

### 1. Database Model
File: app/models/{entity}.py
[Show complete model code]

### 2. API Endpoints
File: app/api/{entity}.py
[Show complete API code]

### 3. Database Migration
File: alembic/versions/[timestamp]_add_{entity}.py
[Show migration code]

---

## Frontend (TypeScript/Next.js)

### 1. Zod Schema
File: src/schemas/{entity}.ts
[Show complete schema code]

### 2. API Client
File: src/lib/api/{entity}.ts
[Show complete client code]

### 3. Environment Variables
File: .env.local
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Alignment Verification

✓ Field names match (snake_case backend, camelCase frontend)
✓ Types aligned: [list mappings]
✓ Validation rules match
✓ API contracts documented
✓ Single-responsibility endpoints (Constitution VI.1)

Next Steps:
1. Review generated code
2. Create database migration
3. Update router in app/main.py
4. Run tests (TDD)

Approve code generation?
```

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Code Patterns**: `.claude/skills/multi-stack-code-generator/patterns.md`
  - Complete new entity template (Model + API + Frontend)
  - Enum alignment pattern
  - Date/timestamp handling
  - Full CRUD examples

- **Type Mappings**: `.claude/skills/multi-stack-code-generator/type-mappings.md`
  - Pydantic ↔ Zod type mappings
  - Naming conventions (snake_case ↔ camelCase)
  - Validation rules alignment
  - Field modifiers (Optional, default, min/max)

## Constitutional Compliance Checks

Before generating code, verify:

1. **Spec exists** (Constitution II.2: "No spec, no code")
2. **Type safety** (Constitution VII.1: Zod + Pydantic alignment)
3. **API design** (Constitution VI: Single responsibility, documented)
4. **Secrets** (Constitution IX: No hardcoded secrets)
5. **Tests planned** (Constitution VIII: TDD)

## Quick Reference

**Generation Order**:
1. Backend first (source of truth for database)
2. Frontend schema mirrors backend exactly
3. API client with runtime validation

**Naming Conventions**:
- Backend: `snake_case` (Python PEP 8)
- Frontend: `camelCase` (TypeScript/JavaScript)
- Auto-convert field names between stacks

**Validation**:
- Backend: Pydantic Field validators
- Frontend: Zod schema methods
- Must match exactly (use schema-sync-validator)

**Type Inference**:
- Frontend: Use `z.infer<typeof Schema>` for types
- Never manually duplicate type definitions

## Notes

- Always generate backend first (source of truth for database)
- Frontend schema mirrors backend exactly
- Use `z.infer<>` to generate TypeScript types from Zod
- Include OpenAPI docs in FastAPI (automatic)
- API client includes runtime validation (Zod parse)
- Follow naming conventions: snake_case (Python), camelCase (TypeScript)
- **Read sub-modules on-demand** to avoid context bloat
