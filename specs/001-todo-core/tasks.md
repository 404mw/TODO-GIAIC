# Tasks: TODO Core Logic

**Input**: Design documents from `specs/001-todo-core/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [research.md](research.md)

**Tests**: Tests are included following TDD principles (constitution Section VIII). All tests must be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure as defined in plan.md:
- Source: `src/todo_core/`
- Tests: `tests/`
- Config: Repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create .gitignore file at repository root with Python patterns
- [X] T002 Create .python-version file specifying Python 3.11+
- [X] T003 [P] Create pyproject.toml with UV configuration and pytest dev dependencies
- [X] T004 [P] Create src/todo_core/__init__.py (empty package marker)
- [X] T005 [P] Create tests/__init__.py (empty package marker)
- [X] T006 Initialize UV project with `uv sync` command

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model and storage infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation (TDD - Write FIRST, Ensure FAIL)

- [X] T007 [P] Create tests/test_models.py with test cases for Task creation, validation (title length, empty title, description length), mark_complete(), update_title(), update_description()
- [X] T008 [P] Create tests/test_storage.py with test cases for TaskStore.create_task(), get_task(), list_all_tasks(), list_by_status(), delete_task(), sequential ID generation, ID counter reset

### Implementation for Foundation

- [X] T009 [P] Implement validate_title() function in src/todo_core/models.py (trim whitespace, check empty, check 200 char limit)
- [X] T010 [P] Implement validate_description() function in src/todo_core/models.py (trim whitespace, normalize empty to None, check 1000 char limit)
- [X] T011 Create Task dataclass in src/todo_core/models.py with slots=True, fields (id, title, description, status, created_at, completed_at), mark_complete(), update_title(), update_description() methods
- [X] T012 Create TaskStore class in src/todo_core/storage.py with _next_id counter, __init__(), create_task(), get_task(), list_all_tasks(), list_by_status(), delete_task(), reset_id_counter() methods
- [X] T013 Run pytest for test_models.py and test_storage.py - ensure all tests PASS

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title/description and view their current task list

**Independent Test**: Create a task via console input, then list all tasks to verify the created task appears with correct ID, title, status, and timestamp

### Tests for User Story 1 (TDD - Write FIRST, Ensure FAIL)

- [X] T014 [P] [US1] Create tests/test_cli.py with test_display_menu(), test_get_menu_choice() for valid/invalid input
- [X] T015 [P] [US1] Add test_get_task_title() to tests/test_cli.py for empty title rejection, whitespace trimming, 200 char limit
- [X] T016 [P] [US1] Add test_get_task_description() to tests/test_cli.py for optional description, 1000 char limit, empty normalization to None
- [X] T017 [P] [US1] Add test_create_task_flow() to tests/test_cli.py for full creation workflow (menu → input → task created)
- [X] T018 [P] [US1] Add test_list_tasks_flow() to tests/test_cli.py for displaying tasks (with tasks, without tasks)

### Implementation for User Story 1

- [X] T019 [P] [US1] Implement display_menu() function in src/todo_core/cli.py (show 6 menu options)
- [X] T020 [P] [US1] Implement get_menu_choice() function in src/todo_core/cli.py (validate 1-6, retry on invalid)
- [X] T021 [P] [US1] Implement get_task_title() function in src/todo_core/cli.py (prompt, validate, retry on error)
- [X] T022 [P] [US1] Implement get_task_description() function in src/todo_core/cli.py (prompt, optional, validate if provided)
- [X] T023 [US1] Implement create_task() function in src/todo_core/cli.py (get title, get description, call store.create_task(), display success with ID)
- [X] T024 [US1] Implement list_tasks() function in src/todo_core/cli.py (format table with ID, title, status, created_at; handle empty list)
- [X] T025 [US1] Create main() function skeleton in src/todo_core/main.py (initialize TaskStore, loop with menu options 1, 2, 6)
- [X] T026 [US1] Run pytest for test_cli.py User Story 1 tests - ensure all tests PASS
- [X] T027 [US1] Manual integration test: Run `uv run todo`, create 3 tasks, list tasks, verify display

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create and view tasks

---

## Phase 4: User Story 2 - Mark Tasks as Complete (Priority: P2)

**Goal**: Users can mark tasks as complete to track progress

**Independent Test**: Create a task, mark it complete via its ID, verify status changes to "complete" in task list with completion timestamp

### Tests for User Story 2 (TDD - Write FIRST, Ensure FAIL)

- [X] T028 [P] [US2] Add test_get_task_id() to tests/test_cli.py for valid ID, invalid ID (not found), non-numeric input
- [X] T029 [P] [US2] Add test_complete_task_flow() to tests/test_cli.py for marking incomplete task complete, already complete task, invalid task ID

### Implementation for User Story 2

- [X] T030 [P] [US2] Implement get_task_id() function in src/todo_core/cli.py (prompt for ID, validate numeric, check task exists in store, retry on error)
- [X] T031 [US2] Implement complete_task() function in src/todo_core/cli.py (get task ID, get task from store, check if already complete, call task.mark_complete(), display success)
- [X] T032 [US2] Add menu option 3 handler in src/todo_core/main.py main() loop to call complete_task()
- [X] T033 [US2] Run pytest for test_cli.py User Story 2 tests - ensure all tests PASS
- [X] T034 [US2] Manual integration test: Run `uv run todo`, create task, complete it, verify status and completion timestamp

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can modify task title or description after creation

**Independent Test**: Create a task, update its title or description, verify changes appear when listing tasks

### Tests for User Story 3 (TDD - Write FIRST, Ensure FAIL)

- [X] T035 [P] [US3] Add test_update_task_flow() to tests/test_cli.py for updating title (valid, empty rejection, 200 char limit), updating description (valid, optional, 1000 char limit), invalid task ID

### Implementation for User Story 3

- [X] T036 [US3] Implement update_task() function in src/todo_core/cli.py (get task ID, get task from store, prompt for title or description choice, get new value, call task.update_title() or task.update_description(), display success)
- [X] T037 [US3] Add menu option 4 handler in src/todo_core/main.py main() loop to call update_task()
- [X] T038 [US3] Run pytest for test_cli.py User Story 3 tests - ensure all tests PASS
- [X] T039 [US3] Manual integration test: Run `uv run todo`, create task, update title, update description, verify changes

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Users can remove tasks that are no longer relevant

**Independent Test**: Create a task, delete it by ID, verify it no longer appears in task list

### Tests for User Story 4 (TDD - Write FIRST, Ensure FAIL)

- [X] T040 [P] [US4] Add test_delete_task_flow() to tests/test_cli.py for deleting existing task (success), invalid task ID (error), verify task removed from list

### Implementation for User Story 4

- [X] T041 [US4] Implement delete_task() function in src/todo_core/cli.py (get task ID, get task from store, confirm deletion with yes/no, call store.delete_task(), display success)
- [X] T042 [US4] Add menu option 5 handler in src/todo_core/main.py main() loop to call delete_task()
- [X] T043 [US4] Run pytest for test_cli.py User Story 4 tests - ensure all tests PASS
- [X] T044 [US4] Manual integration test: Run `uv run todo`, create task, delete it, verify removal from list

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T045 [P] Add project scripts entry point in pyproject.toml: `[project.scripts] todo = "todo_core.main:main"`
- [X] T046 [P] Create README.md at repository root with quick start instructions (link to quickstart.md)
- [X] T047 [P] Add comprehensive docstrings to all functions in src/todo_core/models.py
- [X] T048 [P] Add comprehensive docstrings to all functions in src/todo_core/storage.py
- [X] T049 [P] Add comprehensive docstrings to all functions in src/todo_core/cli.py
- [X] T050 Run full pytest suite with coverage: `uv run pytest --cov=src` - ensure 100% coverage on models.py and storage.py
- [X] T051 Validate quickstart.md instructions: Follow setup steps from scratch in clean environment
- [X] T052 Performance validation: Create 1000 tasks via script, verify list operation completes in <2 seconds (SC-006)
- [X] T053 Edge case validation: Test empty title rejection, 200 char title limit, 1000 char description limit, special characters, unicode/emoji support
- [X] T054 Final integration test: Complete full CRUD cycle (create, list, complete, update, delete) for single task within 2 minutes (SC-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD principle)
2. CLI functions for input/validation before workflow functions
3. Workflow functions before main() integration
4. Tests PASS before moving to manual integration test
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005 can run in parallel (different files)

**Phase 2 (Foundational Tests)**:
- T007, T008 can run in parallel (different test files)

**Phase 2 (Foundational Implementation)**:
- T009, T010 can run in parallel (different validation functions)

**Phase 3 (User Story 1 Tests)**:
- T014, T015, T016, T017, T018 can run in parallel (different test functions in same file)

**Phase 3 (User Story 1 Implementation)**:
- T019, T020, T021, T022 can run in parallel (different CLI helper functions)

**Phase 4 (User Story 2 Tests)**:
- T028, T029 can run in parallel (different test functions)

**Phase 4 (User Story 2 Implementation)**:
- T030 can run in parallel with other user story implementations (different function)

**Phase 5 (User Story 3 Tests)**:
- T035 can run in parallel with other user story tests (different test function)

**Phase 7 (Polish)**:
- T045, T046, T047, T048, T049 can run in parallel (different files/non-overlapping sections)

**User Stories (After Foundational Complete)**:
- Once Phase 2 completes, all user stories (Phase 3, 4, 5, 6) can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch User Story 1 tests in parallel:
Task: "Create tests/test_cli.py with test_display_menu(), test_get_menu_choice()"
Task: "Add test_get_task_title() to tests/test_cli.py"
Task: "Add test_get_task_description() to tests/test_cli.py"
Task: "Add test_create_task_flow() to tests/test_cli.py"
Task: "Add test_list_tasks_flow() to tests/test_cli.py"

# After tests fail, launch User Story 1 implementation in parallel:
Task: "Implement display_menu() in src/todo_core/cli.py"
Task: "Implement get_menu_choice() in src/todo_core/cli.py"
Task: "Implement get_task_title() in src/todo_core/cli.py"
Task: "Implement get_task_description() in src/todo_core/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T014-T027)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo basic TODO app with create and list functionality

**Estimated Tasks for MVP**: 27 tasks (Setup + Foundational + US1)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (13 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - 27 tasks total)
3. Add User Story 2 → Test independently → Deploy/Demo (34 tasks total)
4. Add User Story 3 → Test independently → Deploy/Demo (39 tasks total)
5. Add User Story 4 → Test independently → Deploy/Demo (44 tasks total)
6. Complete Polish phase → Final release (54 tasks total)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (13 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (14 tasks)
   - Developer B: User Story 2 (7 tasks)
   - Developer C: User Story 3 (5 tasks)
   - Developer D: User Story 4 (5 tasks)
3. Stories complete and integrate independently
4. Team completes Polish together (10 tasks)

---

## Task Summary

- **Total Tasks**: 54
- **Setup Phase**: 6 tasks
- **Foundational Phase**: 7 tasks (BLOCKS all user stories)
- **User Story 1 (P1)**: 14 tasks - Create and View Tasks
- **User Story 2 (P2)**: 7 tasks - Mark Tasks Complete
- **User Story 3 (P3)**: 5 tasks - Update Task Details
- **User Story 4 (P4)**: 5 tasks - Delete Tasks
- **Polish Phase**: 10 tasks
- **Parallel Opportunities**: 20+ tasks marked [P] can run in parallel within their phase
- **Independent Test Criteria**: Each user story phase includes independent test verification

### MVP Scope (Recommended)

- Setup + Foundational + User Story 1 = **27 tasks**
- Delivers: Create tasks, view tasks, exit application
- Time estimate: 2-3 hours for experienced developer
- Validates: Core architecture, data model, console interface

---

## Notes

- All tests follow TDD principles: Write test FIRST, ensure it FAILS, then implement
- [P] tasks = different files or non-overlapping sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are absolute from repository root
- Constitution Section VIII enforced: Tests written before implementation
- Performance targets from spec.md: SC-006 requires 1000 tasks listable in <2 seconds (design achieves ~1ms)
