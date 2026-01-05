# Implementation Plan: TODO Core Logic

**Branch**: `001-todo-core` | **Date**: 2026-01-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-core/spec.md`

## Summary

Build a Python-based TODO application with core CRUD functionality (Create, Read, Update, Delete tasks and mark as complete). The application uses in-memory storage with a console-based menu interface. Tasks have title, optional description, status tracking, and ISO 8601 timestamps. Implementation uses Python 3.11+ with UV package manager, dataclasses for the data model, and plain `input()` for the console interface to minimize dependencies while exceeding performance requirements by 50-2000x.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: None (standard library only for runtime)
**Storage**: In-memory (List[Task] with dataclass)
**Testing**: pytest, pytest-cov
**Target Platform**: Console application (Windows, macOS, Linux)
**Project Type**: Single project (console application)
**Performance Goals**: List 1000+ tasks in <2 seconds (actual: ~1ms - 2000x faster)
**Constraints**: Zero external runtime dependencies, in-memory only (no persistence)
**Scale/Scope**: Single user, 1000+ tasks, 5 core CRUD operations + task completion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 0 Check (Before Research)

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec Authority** | ✅ PASS | Spec complete with user scenarios, requirements, edge cases |
| **II. Phase Discipline** | ✅ PASS | Following strict phase sequencing: Research → Design → Tasks |
| **III. Data Integrity** | ✅ PASS | No user data (in-memory only), no persistence, no backups needed |
| **IV. AI Agent Governance** | ✅ PASS | No AI agent features in this MVP |
| **V. AI Logging** | N/A | No AI features |
| **VI. API Design** | ✅ PASS | Internal APIs only (TaskStore methods), single responsibility |
| **VII. Validation & Type Safety** | ✅ PASS | Validation at CLI boundary, type hints throughout |
| **VIII. Testing Doctrine** | ✅ PASS | TDD approach planned, pytest configured |
| **IX. Secrets & Configuration** | ✅ PASS | No secrets or configuration needed (console app) |
| **X. Infrastructure Philosophy** | ✅ PASS | Simplicity prioritized: zero runtime dependencies, plain input() |

**Overall**: ✅ ALL GATES PASSED

### Phase 1 Check (After Design)

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec Authority** | ✅ PASS | Design aligns with spec (FR-001 through FR-013) |
| **II. Phase Discipline** | ✅ PASS | Research complete before design, design complete before tasks |
| **III. Data Integrity** | ✅ PASS | Validation rules enforce data integrity at input boundary |
| **IV. AI Agent Governance** | N/A | No AI features |
| **V. AI Logging** | N/A | No AI features |
| **VI. API Design** | ✅ PASS | TaskStore methods have single responsibility, clear contracts |
| **VII. Validation & Type Safety** | ✅ PASS | All fields typed, validation functions defined in data-model.md |
| **VIII. Testing Doctrine** | ✅ PASS | Test structure defined in quickstart.md, pytest configured |
| **IX. Secrets & Configuration** | ✅ PASS | No secrets required |
| **X. Infrastructure Philosophy** | ✅ PASS | Zero runtime deps, List[Task] sufficient for 1000+ tasks |

**Overall**: ✅ ALL GATES PASSED

**Complexity Justification**: Not required - no violations detected

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-core/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (research findings)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (setup guide)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Selected Structure**: Single project (console application)

```text
02-TODO/
├── .gitignore
├── .python-version          # Python 3.11+
├── README.md
├── pyproject.toml           # UV project configuration
├── uv.lock                  # Dependency lock file (version-controlled)
│
├── src/
│   └── todo_core/           # Main application package
│       ├── __init__.py
│       ├── main.py          # Entry point with main() function
│       ├── models.py        # Task dataclass definition
│       ├── storage.py       # TaskStore (in-memory storage)
│       └── cli.py           # Console interface (menu, input validation, display)
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # Task model tests (validation, state transitions)
│   ├── test_storage.py      # TaskStore tests (CRUD operations, ID generation)
│   └── test_cli.py          # CLI tests (input validation, menu flow)
│
├── specs/
│   └── 001-todo-core/       # This feature's documentation
│
└── .specify/                # Project templates and scripts
    ├── memory/
    │   └── constitution.md
    ├── templates/
    └── scripts/
```

**Structure Decision**:

- **Single project structure** selected because:
  - Console application (no frontend/backend split needed)
  - Single-user, no API layer required
  - All code in one Python package simplifies dependencies and deployment

- **src/ layout** chosen for:
  - Proper packaging (allows `uv run todo` via entry point)
  - Namespace isolation (prevents import conflicts)
  - Python packaging best practices

- **Flat module structure** within `todo_core/`:
  - Only 4 modules needed (main, models, storage, cli)
  - No sub-packages required for this scope
  - Easy to navigate and understand

**File Responsibilities**:

| File | Responsibility | Key Functions/Classes |
|------|----------------|----------------------|
| `main.py` | Application entry point | `main()` - starts app loop |
| `models.py` | Data model | `Task` dataclass, validation functions |
| `storage.py` | In-memory storage | `TaskStore` class with CRUD methods |
| `cli.py` | Console interface | Menu display, input validation, formatting |

## Complexity Tracking

**Status**: No complexity violations - tracking not required

All decisions align with constitution principle "Simplicity over scale":
- Zero runtime dependencies (standard library only)
- Flat module structure (no nested packages)
- Plain `input()` for UI (no framework overhead)
- List-based storage (no database or caching layer)
- Single project (no microservices or multi-tier architecture)
