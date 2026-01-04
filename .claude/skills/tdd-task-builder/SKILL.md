---
name: tdd-task-builder
description: Generates tasks in strict TDD order (Red → Green → Refactor). Use when creating tasks.md, planning implementations, or breaking down features. Ensures tests are written before implementation.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# TDD Task Builder

## Purpose

Generate and organize tasks following Test-Driven Development (TDD) methodology per Constitution Section VIII. Ensure tests precede implementation and coverage expectations are met.

## TDD Phases

1. **Red:** Write a failing test
2. **Green:** Write minimal code to pass the test
3. **Refactor:** Improve code while keeping tests green

## Instructions

### When Creating tasks.md

When user requests task generation for a feature:

1. **Read the specification**
   - Load `specs/<feature>/spec.md`
   - Extract behavioral requirements
   - Identify testable acceptance criteria

2. **Read the plan (if exists)**
   - Load `specs/<feature>/plan.md`
   - Understand architectural decisions
   - Note technical constraints

3. **Generate TDD-ordered tasks**
   - Group by Red → Green → Refactor cycles
   - Each feature gets its own TDD cycle
   - Include dummy data requirements

4. **Add acceptance criteria**
   - Every task has testable outcomes
   - Coverage expectations explicit
   - Edge cases identified

5. **Verify coverage doctrine**
   - Core logic
   - API behavior
   - State transitions
   - AI interaction boundaries (if applicable)

### Task Structure Template

See: `.claude/skills/tdd-task-builder/templates.md` for complete task structure format

**Brief format:**
```markdown
### Task [N]: [Title] (Phase: RED/GREEN/REFACTOR)

**Type:** [Unit Test / Integration Test / Implementation / Refactoring]
**Description:** [What needs to be done]
**Acceptance Criteria:** [Checkboxes]
**Test Coverage:** [What this tests/implements]
**Depends On:** Task [X], Task [Y]
**Dummy Data Required:** [List]
**Files Affected:** [List]
```

## Response Format

### When Generating tasks.md

```
📋 TDD TASK GENERATION

Feature: [Feature name]
Spec: specs/[feature]/spec.md
Plan: specs/[feature]/plan.md (if exists)

Task Breakdown:
- Total Tasks: [N]
- Red Phase: [X] tasks (tests)
- Green Phase: [Y] tasks (implementation)
- Refactor Phase: [Z] tasks (improvements)

Coverage Plan:
✓ Core logic: [components covered]
✓ API behavior: [endpoints covered]
✓ State transitions: [states covered]
✓ Edge cases: [cases covered]

Dummy Data Required:
- [List of fixtures/test data needed]

Generated: specs/[feature]/tasks.md

[Present full tasks.md content]

Review and approve?
```

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Task Templates**: `.claude/skills/tdd-task-builder/templates.md`
  - Complete task structure format
  - Red/Green/Refactor phase templates
  - Database migration pattern
  - Dummy data pattern

- **Complete Examples**: `.claude/skills/tdd-task-builder/examples.md`
  - Full task generation for Priority feature (9 tasks)
  - Shows complete Red → Green → Refactor cycle
  - Multi-stack implementation (backend + frontend)

## Quick Reference

**TDD Order (Strict)**:
1. Red: Write failing tests FIRST
2. Green: Make tests pass with minimal code
3. Refactor: Improve while keeping tests green

**Never Skip**:
- Red phase (always write tests first)
- Refactor phase (mandatory, not optional)
- Dummy data (Constitution III.3)

**Always Include**:
- Acceptance criteria (testable)
- Test coverage expectations
- Dependencies between tasks
- Files affected by each task

**Coverage Doctrine (Constitution VIII)**:
- Core logic: Required
- API behavior: Required
- State transitions: Required
- Edge cases: Required

## Common Patterns

For detailed patterns, see: `.claude/skills/tdd-task-builder/templates.md`

**Quick patterns:**
- Database migrations: Always GREEN phase
- Dummy data: Always RED phase (before tests)
- Schema updates: GREEN phase, both backend + frontend
- Refactoring: Always REFACTOR phase (tests stay green)

## Notes

- **Always Red → Green → Refactor** (never skip Red)
- Tests MUST be written before implementation
- One TDD cycle per feature (can have multiple cycles in a spec)
- Refactor phase is mandatory, not optional
- Dummy data is required (Constitution III.3)
- Coverage expectations from Constitution Section VIII
- **Read sub-modules on-demand** to avoid context bloat
