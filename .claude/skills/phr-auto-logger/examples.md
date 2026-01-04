# Detailed PHR Examples

## Example 1: Constitution Work

### User Request
"Update the constitution to add a new principle about error handling"

### After Completing the Work

```
📝 CREATING PROMPT HISTORY RECORD

Stage: constitution
Title: add error handling principle
Route: history/prompts/constitution/

ID: 005 (allocated)
File: history/prompts/constitution/005-add-error-handling-principle.constitution.prompt.md

---
id: 005
title: Add Error Handling Principle
stage: constitution
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: update constitution
labels: ["constitution", "error-handling", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
---

# Add Error Handling Principle

## Prompt

Update the constitution to add a new principle about error handling:
All errors must be logged with full context and never silently swallowed.

## Response

Added Section XII: Error Handling to constitution.md

New Principle:
1. All errors must be logged with full context
2. Silent error swallowing is forbidden
3. User-facing errors must be actionable
4. Stack traces required in development, sanitized in production

Updated constitution to version 1.1.0 (MINOR version bump).

## Outcome

Constitution updated with error handling principle.
Version bumped: 1.0.0 → 1.1.0
All dependent templates verified for compatibility.

## Evaluation

✓ Constitutional compliance: Amendment procedure followed
✓ Completeness: Principle fully specified with examples
✓ Impact assessment: No breaking changes to existing code

✅ PHR Created Successfully
```

## Example 2: Feature Spec Work

### User Request
"Create a spec for the priority feature"

### After Completing

```
📝 CREATING PROMPT HISTORY RECORD

Stage: spec
Title: create priority feature spec
Route: history/prompts/task-priority/

ID: 001 (allocated)
File: history/prompts/task-priority/001-create-priority-feature-spec.spec.prompt.md

---
id: 001
title: Create Priority Feature Spec
stage: spec
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: task-priority
branch: master
user: user
command: create spec
labels: ["spec", "priority", "task-management"]
links:
  spec: specs/task-priority/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/task-priority/spec.md
tests: []
---

# Create Priority Feature Spec

## Prompt

Create a spec for the priority feature:
- Tasks should have priority: low, medium, high
- Default to medium
- Tasks can be sorted by priority

## Response

Created complete specification in specs/task-priority/spec.md

Includes:
- Feature overview
- User scenarios (3 scenarios)
- Data model (priority field, enum, default)
- API contracts (POST, PUT, GET with ?sort=priority)
- Validation rules (enum validation, edge cases)
- State transitions
- Acceptance criteria

## Outcome

Specification created: specs/task-priority/spec.md
Ready for planning and implementation.

## Evaluation

✓ Executable spec: States, invariants, edge cases defined
✓ Constitutional compliance: Spec-first approach followed
✓ Completeness: All required sections present

✅ PHR Created Successfully
```

## Example 3: Implementation Work

### User Request
"Implement the priority field (we already have spec and plan)"

### After Implementation

```
📝 CREATING PROMPT HISTORY RECORD

Stage: green
Title: implement priority field
Route: history/prompts/task-priority/

ID: 004 (allocated from existing PHRs in task-priority/)
File: history/prompts/task-priority/004-implement-priority-field.green.prompt.md

---
id: 004
title: Implement Priority Field
stage: green
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: task-priority
branch: feature/task-priority
user: user
command: implement
labels: ["implementation", "green-phase", "tdd", "priority"]
links:
  spec: specs/task-priority/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - app/models/task.py
  - app/api/tasks.py
  - src/schemas/task.ts
  - alembic/versions/20260104_add_priority.py
tests:
  - tests/test_task_priority.py
  - tests/integration/test_priority_api.py
---

# Implement Priority Field

## Prompt

Implement the priority field following the spec and plan.
We already have tests written (RED phase complete).
Make the tests pass (GREEN phase).

## Response

Implemented priority feature across full stack:

Backend:
- Updated Task model with priority field (Literal["low", "medium", "high"])
- Added priority to API endpoints (POST, PUT, GET)
- Created database migration
- All unit tests passing ✓
- All integration tests passing ✓

Frontend:
- Updated Zod schema with priority enum
- Added priority to TypeScript types
- Schema alignment verified ✓

Files Modified:
- app/models/task.py: Added priority field
- app/api/tasks.py: Updated endpoints
- src/schemas/task.ts: Added priority to schema
- alembic/versions/20260104_add_priority.py: Migration

Test Results:
- tests/test_task_priority.py: 12/12 passing ✓
- tests/integration/test_priority_api.py: 8/8 passing ✓

## Outcome

Priority feature implemented successfully.
All tests passing (RED → GREEN transition complete).
Ready for REFACTOR phase.

## Evaluation

✓ TDD followed: Tests written first, implementation makes them pass
✓ Constitutional compliance: Spec existed before implementation
✓ Schema alignment: Zod and Pydantic schemas match
✓ Test coverage: 100% of spec requirements tested
✓ No violations: All checks passed

✅ PHR Created Successfully
```

## Example 4: General Work

### User Request
"Explain how the authentication flow works"

### After Explanation

```
📝 CREATING PROMPT HISTORY RECORD

Stage: general
Title: explain authentication flow
Route: history/prompts/general/

ID: 023 (allocated from existing general PHRs)
File: history/prompts/general/023-explain-authentication-flow.general.prompt.md

---
id: 023
title: Explain Authentication Flow
stage: general
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: explain
labels: ["explanation", "authentication", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files: []
tests: []
---

# Explain Authentication Flow

## Prompt

Explain how the authentication flow works in the TODO app.

## Response

Provided detailed explanation of authentication using Better Auth:

1. User Registration:
   - POST /api/auth/register
   - Password hashed with bcrypt
   - User created in database
   - Session token generated

2. User Login:
   - POST /api/auth/login
   - Credentials validated
   - JWT token issued
   - Token stored in httpOnly cookie

3. Protected Routes:
   - Middleware checks JWT token
   - Token verified and decoded
   - User identity attached to request
   - Unauthorized → 401 response

4. Token Refresh:
   - Automatic refresh before expiry
   - New token issued
   - Old token invalidated

Explained with diagrams and code examples.

## Outcome

User understands authentication flow.
No code changes made (explanation only).

## Evaluation

✓ Clarity: Explanation was clear and complete
✓ Accuracy: Matched actual implementation
✗ No implementation work (explanation only)

✅ PHR Created Successfully
```
