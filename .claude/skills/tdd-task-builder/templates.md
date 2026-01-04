# TDD Task Templates

## Complete Task Structure

```markdown
### Task [N]: [Task Title] (Phase: RED/GREEN/REFACTOR)

**Type:** [Unit Test / Integration Test / Implementation / Refactoring]

**Description:**
[What needs to be done]

**Acceptance Criteria:**
- [ ] [Specific testable criterion 1]
- [ ] [Specific testable criterion 2]
- [ ] [Specific testable criterion 3]

**Test Coverage:**
- [What this task tests/implements]

**Depends On:** Task [X], Task [Y]

**Dummy Data Required:**
- [List of dummy data needed]

**Files Affected:**
- [List of files to create/modify]
```

## TDD Phase Templates

### Red Phase Template (Write Failing Tests)

```markdown
### Red Phase (Write Failing Tests)

#### Task [N]: Write unit tests for [component] (Phase: RED)
**Type:** Unit Test
**Description:** Create failing tests for [component] behavior
**Acceptance Criteria:**
- [ ] Tests exist for all public methods
- [ ] Tests cover edge cases (null, empty, invalid inputs)
- [ ] Tests assert expected behavior from spec
- [ ] All tests currently FAIL (no implementation yet)

**Test Coverage:**
- Happy path scenarios
- Edge cases: [list specific cases]
- Error conditions: [list error scenarios]

**Dummy Data Required:**
- Valid [entity]: {example data}
- Invalid [entity]: {example invalid data}
- Edge case: {example edge case data}

**Files Affected:**
- tests/test_[component].py (new)

---

#### Task [N+1]: Write integration tests for [API endpoint] (Phase: RED)
**Type:** Integration Test
**Description:** Create failing tests for [endpoint] API contract
**Acceptance Criteria:**
- [ ] Tests cover all HTTP methods (GET/POST/PUT/DELETE)
- [ ] Tests verify request/response schemas
- [ ] Tests check status codes (200, 400, 404, 422, 500)
- [ ] Tests validate error messages
- [ ] All tests currently FAIL

**Test Coverage:**
- POST /api/[endpoint]: create with valid/invalid data
- GET /api/[endpoint]: list, filter, pagination
- PUT /api/[endpoint]/:id: update existing
- DELETE /api/[endpoint]/:id: delete and 404

**Dummy Data Required:**
- [List of test fixtures]

**Depends On:** None

**Files Affected:**
- tests/integration/test_[endpoint]_api.py (new)
```

### Green Phase Template (Make Tests Pass)

```markdown
### Green Phase (Make Tests Pass)

#### Task [N]: Implement [component] core logic (Phase: GREEN)
**Type:** Implementation
**Description:** Write minimal code to make Task [N-X] tests pass
**Acceptance Criteria:**
- [ ] All unit tests from Task [N-X] now PASS
- [ ] Implementation matches spec behavior
- [ ] No extra features added (minimal code only)
- [ ] Type hints included (Python) / Types defined (TypeScript)

**Test Coverage:**
- Verified by Task [N-X] tests passing

**Depends On:** Task [N-X] (tests must exist first)

**Files Affected:**
- app/[component].py (new)
- app/models/[component].py (new, if needed)

---

#### Task [N+1]: Implement [API endpoint] (Phase: GREEN)
**Type:** Implementation
**Description:** Create API endpoint to make Task [N-Y] tests pass
**Acceptance Criteria:**
- [ ] All integration tests from Task [N-Y] now PASS
- [ ] Endpoint follows single-responsibility (Constitution VI.1)
- [ ] Request/response schemas documented
- [ ] Error handling matches test expectations

**Test Coverage:**
- Verified by Task [N-Y] tests passing

**Depends On:** Task [N-Y], Task [N]

**Files Affected:**
- app/api/[endpoint].py (new)
- app/schemas/[endpoint].py (new)
```

### Refactor Phase Template (Improve Code)

```markdown
### Refactor Phase (Improve Code)

#### Task [N]: Refactor [component] for clarity (Phase: REFACTOR)
**Type:** Refactoring
**Description:** Improve code quality while keeping tests green
**Acceptance Criteria:**
- [ ] All tests still pass (no behavior change)
- [ ] Code follows project style guide
- [ ] Complexity reduced (cyclomatic complexity < 10)
- [ ] No duplication (DRY principle)
- [ ] Type safety enforced

**Test Coverage:**
- All previous tests still pass (regression check)

**Depends On:** Task [N-X], Task [N-Y]

**Files Affected:**
- app/[component].py (modify)
```

## Common Task Patterns

### Database Migration Task

```markdown
### Task [N]: Create database migration for [change] (Phase: GREEN)

**Type:** Implementation

**Description:**
Generate and test Alembic migration for schema change

**Acceptance Criteria:**
- [ ] Migration file created: alembic/versions/[hash]_[description].py
- [ ] Migration runs successfully (upgrade)
- [ ] Migration reverses successfully (downgrade)
- [ ] No data loss during migration
- [ ] Existing data handled (defaults, transformations)

**Test Coverage:**
- Migration tested with dummy data
- Rollback tested

**Files Affected:**
- alembic/versions/[timestamp]_[description].py (new)
```

### Dummy Data Task

```markdown
### Task [N]: Create dummy data fixtures (Phase: RED)

**Type:** Test Data

**Description:**
Generate realistic dummy data for testing

**Acceptance Criteria:**
- [ ] Fixtures cover all test scenarios
- [ ] Data is realistic but obviously fake
- [ ] No real user data used (Constitution III.3)
- [ ] Fixtures reusable across tests

**Dummy Data Created:**
- users_dummy.json: 20 fake users
- tasks_dummy.json: 100 fake tasks with varied properties

**Files Affected:**
- tests/fixtures/dummy_data.py (new)
```

### Frontend Schema Sync Task

```markdown
### Task [N]: Update frontend schema (Zod) (Phase: GREEN)

**Type:** Implementation

**Description:**
Add [field] to frontend TypeScript schema

**Acceptance Criteria:**
- [ ] [Field] added to Zod schema
- [ ] Enum/Type matches backend exactly
- [ ] Default value matches backend
- [ ] Type exported: type [Entity] = z.infer<typeof [Entity]Schema>

**Test Coverage:**
- Schema alignment verified (use schema-sync-validator skill)

**Depends On:** Task [N-X] (backend model)

**Files Affected:**
- src/schemas/[entity].ts (modify)
- src/types/[entity].ts (modify)
```

### Refactor Constants Task

```markdown
### Task [N]: Refactor [field] constants (Phase: REFACTOR)

**Type:** Refactoring

**Description:**
Extract [field] enum/constants to shared location

**Acceptance Criteria:**
- [ ] All tests still pass
- [ ] Values defined once (DRY)
- [ ] Backend and frontend use same source (if possible)
- [ ] No magic strings in code

**Test Coverage:**
- All previous tests still pass

**Depends On:** Task [N-X], Task [N-Y]

**Files Affected:**
- app/constants/[field].py (new)
- app/models/[entity].py (modify - import constant)
- src/constants/[field].ts (new)
- src/schemas/[entity].ts (modify - import constant)
```
