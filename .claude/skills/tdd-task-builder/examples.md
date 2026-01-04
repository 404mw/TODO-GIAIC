# Complete TDD Task Generation Examples

## Example: Task Priority Feature (9 Tasks)

### User Request
"Generate tasks for adding priority field to tasks"

### Response

```
📋 TDD TASK GENERATION

Feature: Task Priority
Spec: specs/task-priority/spec.md
Plan: specs/task-priority/plan.md

Task Breakdown:
- Total Tasks: 9
- Red Phase: 3 tasks (tests)
- Green Phase: 4 tasks (implementation)
- Refactor Phase: 2 tasks (improvements)

Coverage Plan:
✓ Core logic: Task model, validation, priority enum
✓ API behavior: POST /api/tasks, PUT /api/tasks/:id, GET with ?sort=priority
✓ State transitions: priority changes, defaults
✓ Edge cases: invalid priority, null handling, sorting edge cases

Dummy Data Required:
- tasks_with_priority.json (high, medium, low examples)
- invalid_priority_values.json (test data for validation)
- mixed_priority_tasks.json (for sorting tests)
```

---

## Feature: Task Priority

### Red Phase (Write Failing Tests)

#### Task 1: Write unit tests for priority validation (Phase: RED)

**Type:** Unit Test

**Description:**
Create failing tests for priority enum validation on Task model

**Acceptance Criteria:**
- [ ] Test valid priorities: "low", "medium", "high"
- [ ] Test invalid priority raises ValidationError
- [ ] Test null/undefined defaults to "medium"
- [ ] Test priority is preserved on task updates
- [ ] All tests currently FAIL (no implementation)

**Test Coverage:**
- Valid inputs: priority in ["low", "medium", "high"]
- Invalid inputs: priority = "urgent", "normal", 123, null
- Default behavior: no priority specified → "medium"
- Edge cases: empty string, whitespace, case sensitivity

**Depends On:** None

**Dummy Data Required:**
- Valid: {"title": "Task", "priority": "high"}
- Invalid: {"title": "Task", "priority": "urgent"}
- Default: {"title": "Task"} (no priority field)

**Files Affected:**
- tests/test_task_priority.py (new)

---

#### Task 2: Write integration tests for priority API (Phase: RED)

**Type:** Integration Test

**Description:**
Create failing tests for API endpoints supporting priority

**Acceptance Criteria:**
- [ ] Test POST /api/tasks with priority field
- [ ] Test PUT /api/tasks/:id updates priority
- [ ] Test GET /api/tasks?sort=priority returns sorted tasks
- [ ] Test 422 error for invalid priority values
- [ ] All tests currently FAIL

**Test Coverage:**
- POST with valid priority → 201, task created with priority
- POST with invalid priority → 422, error message
- POST without priority → 201, defaults to "medium"
- PUT update priority → 200, priority changed
- GET with sort → tasks ordered high→medium→low

**Depends On:** None

**Dummy Data Required:**
- 10 tasks with mixed priorities (3 high, 4 medium, 3 low)

**Files Affected:**
- tests/integration/test_priority_api.py (new)

---

#### Task 3: Write tests for priority sorting (Phase: RED)

**Type:** Unit Test

**Description:**
Create failing tests for sorting tasks by priority

**Acceptance Criteria:**
- [ ] Test priority sort order: high → medium → low
- [ ] Test secondary sort by created_at within same priority
- [ ] Test empty list handling
- [ ] Test all same priority
- [ ] All tests currently FAIL

**Test Coverage:**
- Mixed priorities: verify high comes before medium before low
- Same priority: verify created_at descending (newest first)
- Edge: empty list returns empty
- Edge: all high priority, sorted by created_at

**Depends On:** None

**Dummy Data Required:**
- 20 tasks with timestamps and mixed priorities

**Files Affected:**
- tests/test_task_sorting.py (new)

---

### Green Phase (Make Tests Pass)

#### Task 4: Add priority field to Task model (Phase: GREEN)

**Type:** Implementation

**Description:**
Update Task model with priority field (backend)

**Acceptance Criteria:**
- [ ] Priority field added to SQLModel
- [ ] Enum validation: Literal["low", "medium", "high"]
- [ ] Default value: "medium"
- [ ] Database migration created
- [ ] Task 1 unit tests now PASS

**Test Coverage:**
- Verified by Task 1 tests passing

**Depends On:** Task 1

**Files Affected:**
- app/models/task.py (modify)
- alembic/versions/[timestamp]_add_priority.py (new)

---

#### Task 5: Update API endpoints for priority (Phase: GREEN)

**Type:** Implementation

**Description:**
Modify API to accept/return priority field

**Acceptance Criteria:**
- [ ] POST /api/tasks accepts optional priority
- [ ] PUT /api/tasks/:id accepts optional priority
- [ ] GET /api/tasks returns priority in response
- [ ] Schema validation enforces priority enum
- [ ] Task 2 integration tests now PASS

**Test Coverage:**
- Verified by Task 2 tests passing

**Depends On:** Task 2, Task 4

**Files Affected:**
- app/api/tasks.py (modify)
- app/schemas/task.py (modify)

---

#### Task 6: Implement priority sorting (Phase: GREEN)

**Type:** Implementation

**Description:**
Add priority sorting logic to task queries

**Acceptance Criteria:**
- [ ] GET /api/tasks?sort=priority works
- [ ] Sort order: high → medium → low
- [ ] Secondary sort: created_at DESC
- [ ] Task 3 sorting tests now PASS

**Test Coverage:**
- Verified by Task 3 tests passing

**Depends On:** Task 3, Task 5

**Files Affected:**
- app/api/tasks.py (modify)
- app/services/task_service.py (new or modify)

---

#### Task 7: Update frontend schema (Zod) (Phase: GREEN)

**Type:** Implementation

**Description:**
Add priority to frontend TypeScript schema

**Acceptance Criteria:**
- [ ] Priority added to Zod schema
- [ ] Enum: z.enum(["low", "medium", "high"])
- [ ] Default: .default("medium")
- [ ] Type exported: type Task = z.infer<typeof TaskSchema>

**Test Coverage:**
- Schema alignment verified (see schema-sync-validator skill)

**Depends On:** Task 4

**Files Affected:**
- src/schemas/task.ts (modify)
- src/types/task.ts (modify)

---

### Refactor Phase (Improve Code)

#### Task 8: Refactor priority constants (Phase: REFACTOR)

**Type:** Refactoring

**Description:**
Extract priority enum to shared constant

**Acceptance Criteria:**
- [ ] All tests still pass
- [ ] Priority values defined once (DRY)
- [ ] Backend and frontend use same source (if possible)
- [ ] No magic strings in code

**Test Coverage:**
- All previous tests still pass

**Depends On:** Task 4, Task 7

**Files Affected:**
- app/constants/priority.py (new)
- app/models/task.py (modify - import constant)
- src/constants/priority.ts (new)
- src/schemas/task.ts (modify - import constant)

---

#### Task 9: Add priority to dummy data generator (Phase: REFACTOR)

**Type:** Refactoring

**Description:**
Update dummy data generator to include priority

**Acceptance Criteria:**
- [ ] Dummy tasks include random priorities
- [ ] Distribution: 30% high, 50% medium, 20% low
- [ ] All tests still pass with new dummy data

**Test Coverage:**
- All previous tests still pass with enhanced dummy data

**Depends On:** Task 8

**Files Affected:**
- tests/fixtures/dummy_data.py (modify)

---

Review and approve?
