# TODO Core Logic

A simple, efficient TODO application with in-memory storage built with Python.

## Features

- Create tasks with title and optional description
- View all tasks in a formatted list
- Mark tasks as complete
- Update task details
- Delete tasks
- Pure Python (3.11+) with zero runtime dependencies

## Quick Start

See [specs/001-todo-core/quickstart.md](specs/001-todo-core/quickstart.md) for detailed setup instructions.

### Installation

```bash
# Install UV package manager (if not already installed)
# Windows
powershell -ExecutionPolicy BypassPolicy -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
uv sync

# Run the app
uv run todo
```

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

## Documentation

- [Feature Specification](specs/001-todo-core/spec.md)
- [Implementation Plan](specs/001-todo-core/plan.md)
- [Data Model](specs/001-todo-core/data-model.md)
- [Quick Start Guide](specs/001-todo-core/quickstart.md)

## License

[License information to be added]
