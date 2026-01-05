# Feature Specification: TODO Core Logic

**Feature Branch**: `001-todo-core`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "## 001: Core Logic - Tech Stack: Python (UV), In-memory storage. - Features: CRUD, Task Completion, Console Interface."

## Clarifications

### Session 2026-01-04

- Q: What exact validation rule should be applied for empty task titles? → A: Empty or whitespace-only titles are rejected (trim whitespace first)
- Q: What are the maximum length constraints for task titles and descriptions? → A: Practical limits (200 chars title, 1000 chars description)
- Q: What should happen when users run multiple concurrent console instances? → A: Each instance maintains independent in-memory state (no synchronization)
- Q: What format should task IDs use? → A: Sequential integers starting from 1
- Q: What timestamp format should be used for display? → A: ISO 8601 format with date and time (e.g., "2026-01-04 14:30:25")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and View Tasks (Priority: P1)

A user wants to quickly capture tasks that need to be done and view their current task list.

**Why this priority**: Core value proposition - without the ability to create and view tasks, the application has no purpose. This is the minimal viable product.

**Independent Test**: Can be fully tested by creating a task via console input, then listing all tasks to verify the created task appears with correct details.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** the user selects "create task" and enters a title and optional description, **Then** the task is added to the list with a unique identifier and "incomplete" status
2. **Given** one or more tasks exist in the system, **When** the user selects "list tasks", **Then** all tasks are displayed with their ID, title, status, and creation timestamp
3. **Given** no tasks exist, **When** the user selects "list tasks", **Then** a message indicating "No tasks found" is displayed

---

### User Story 2 - Mark Tasks as Complete (Priority: P2)

A user wants to mark tasks as complete when they finish them, providing a sense of accomplishment and clear task status.

**Why this priority**: Enables task lifecycle management - users can track progress and distinguish between pending and completed work.

**Independent Test**: Can be tested by creating a task, marking it complete via its ID, then verifying the task's status changes to "completed" in the task list.

**Acceptance Scenarios**:

1. **Given** an incomplete task exists, **When** the user selects "complete task" and provides the task ID, **Then** the task status changes to "complete" and completion timestamp is recorded
2. **Given** a task is already marked complete, **When** the user attempts to complete it again, **Then** a message indicates the task is already complete
3. **Given** an invalid task ID is provided, **When** the user attempts to complete the task, **Then** an error message indicates the task was not found

---

### User Story 3 - Update Task Details (Priority: P3)

A user wants to modify task details (title, description) after creation to correct mistakes or refine requirements.

**Why this priority**: Improves usability - users often need to correct or clarify task information after initial creation.

**Independent Test**: Can be tested by creating a task, updating its title or description, then verifying the changes appear when listing tasks.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** the user selects "update task", provides the task ID and new title, **Then** the task's title is updated
2. **Given** a task exists, **When** the user selects "update task", provides the task ID and new description, **Then** the task's description is updated
3. **Given** an invalid task ID is provided, **When** the user attempts to update the task, **Then** an error message indicates the task was not found

---

### User Story 4 - Delete Tasks (Priority: P4)

A user wants to remove tasks that are no longer relevant or were created by mistake.

**Why this priority**: Provides cleanup capability - useful but not critical for core functionality.

**Independent Test**: Can be tested by creating a task, deleting it by ID, then verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** the user selects "delete task" and provides the task ID, **Then** the task is removed from the system
2. **Given** an invalid task ID is provided, **When** the user attempts to delete the task, **Then** an error message indicates the task was not found
3. **Given** a task was deleted, **When** the user lists all tasks, **Then** the deleted task does not appear

---

### Edge Cases

- **Empty title validation**: When a user enters an empty task title or whitespace-only title (e.g., "   "), the system trims leading/trailing whitespace and rejects the creation with a clear error message
- **Length limits**: Task titles are limited to 200 characters and descriptions to 1000 characters. Inputs exceeding these limits are rejected with a clear error message indicating the maximum allowed length
- **Session persistence**: Tasks are stored in memory only during the application runtime and are lost when the application exits (no persistence between sessions)
- **Special characters**: Task titles and descriptions support all valid unicode characters including special characters and emojis
- **Concurrent instances**: Each console instance maintains its own independent in-memory task list with no synchronization between instances

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create tasks with a required title (max 200 characters) and optional description (max 1000 characters)
- **FR-002**: System MUST generate a unique sequential integer identifier for each task upon creation, starting from 1
- **FR-003**: System MUST store tasks in memory during the application session (each application instance maintains independent state)
- **FR-004**: System MUST allow users to list all tasks with their ID, title, status, and creation timestamp (displayed in ISO 8601 format: YYYY-MM-DD HH:MM:SS)
- **FR-005**: System MUST allow users to mark tasks as complete by providing the task ID
- **FR-006**: System MUST record a completion timestamp when a task is marked complete (stored and displayed in ISO 8601 format: YYYY-MM-DD HH:MM:SS)
- **FR-007**: System MUST allow users to update task title and description by providing the task ID (subject to same length constraints: 200 chars title, 1000 chars description)
- **FR-008**: System MUST allow users to delete tasks by providing the task ID
- **FR-009**: System MUST provide a console-based menu interface for all operations
- **FR-010**: System MUST validate task IDs and display error messages for invalid operations
- **FR-011**: System MUST distinguish between incomplete and complete tasks when displaying the task list
- **FR-012**: System MUST prevent creation of tasks with empty or whitespace-only titles (titles are trimmed of leading/trailing whitespace before validation)
- **FR-013**: Tasks MUST persist only during the application runtime (in-memory storage - lost on application exit)

### Key Entities *(include if feature involves data)*

- **Task**: Represents a single TODO item with the following attributes:
  - Unique identifier (automatically generated sequential integer, starting from 1)
  - Title (required, non-empty string, max 200 characters after trimming)
  - Description (optional string, max 1000 characters)
  - Status (incomplete or complete)
  - Creation timestamp (ISO 8601 format: YYYY-MM-DD HH:MM:SS)
  - Completion timestamp (ISO 8601 format: YYYY-MM-DD HH:MM:SS, null if incomplete)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task and see it in the task list within 5 seconds
- **SC-002**: Users can complete the full CRUD cycle (create, read, update, delete) for a task within 2 minutes using the console interface
- **SC-003**: 100% of valid task operations (create, update, complete, delete) execute successfully without application crashes
- **SC-004**: Task list displays correctly show task status (incomplete vs complete) for 100% of tasks
- **SC-005**: Invalid operations (e.g., accessing non-existent task IDs) provide clear error messages instead of crashes
- **SC-006**: Application handles at least 1000 tasks in memory without performance degradation (list operation completes in under 2 seconds)
