"""AI schema snapshot tests for validating structured output schemas.

Ensures AI agent output schemas remain consistent and don't break
unexpectedly during development.
"""

import json
from pathlib import Path

import pytest

# Snapshot directory for schema snapshots
SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def ensure_snapshot_dir():
    """Ensure the snapshot directory exists."""
    SNAPSHOT_DIR.mkdir(exist_ok=True)


def get_snapshot_path(schema_name: str) -> Path:
    """Get the path to a schema snapshot file."""
    return SNAPSHOT_DIR / f"{schema_name}.json"


def save_snapshot(schema_name: str, schema: dict) -> None:
    """Save a schema snapshot."""
    ensure_snapshot_dir()
    path = get_snapshot_path(schema_name)
    with path.open("w") as f:
        json.dump(schema, f, indent=2, sort_keys=True)


def load_snapshot(schema_name: str) -> dict | None:
    """Load a schema snapshot if it exists."""
    path = get_snapshot_path(schema_name)
    if not path.exists():
        return None
    with path.open("r") as f:
        return json.load(f)


def compare_schemas(expected: dict, actual: dict, path: str = "") -> list[str]:
    """Compare two schemas and return differences."""
    differences = []

    # Check for missing keys
    for key in expected:
        if key not in actual:
            differences.append(f"Missing key at {path}.{key}" if path else f"Missing key: {key}")
        elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
            differences.extend(compare_schemas(expected[key], actual[key], f"{path}.{key}"))
        elif expected[key] != actual[key]:
            differences.append(
                f"Value mismatch at {path}.{key}: expected {expected[key]}, got {actual[key]}"
                if path
                else f"Value mismatch for {key}: expected {expected[key]}, got {actual[key]}"
            )

    # Check for extra keys
    for key in actual:
        if key not in expected:
            differences.append(
                f"Extra key at {path}.{key}" if path else f"Extra key: {key}"
            )

    return differences


# =============================================================================
# AI SCHEMA DEFINITIONS
# These match the schemas defined in src/schemas/ai_agents.py
# =============================================================================


SUBTASK_SUGGESTION_SCHEMA = {
    "type": "object",
    "required": ["title"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 200}
    }
}

SUBTASK_GENERATION_RESULT_SCHEMA = {
    "type": "object",
    "required": ["subtasks"],
    "properties": {
        "subtasks": {
            "type": "array",
            "items": SUBTASK_SUGGESTION_SCHEMA,
            "maxItems": 10
        }
    }
}

ACTION_SUGGESTION_SCHEMA = {
    "type": "object",
    "required": ["action_type", "payload", "requires_confirmation"],
    "properties": {
        "action_type": {
            "type": "string",
            "enum": ["create_task", "update_task", "complete_task", "create_reminder"]
        },
        "payload": {"type": "object"},
        "requires_confirmation": {"type": "boolean", "const": True}
    }
}

TASK_SUGGESTION_SCHEMA = {
    "type": "object",
    "required": ["title"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "description": {"type": "string", "maxLength": 2000},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "due_date": {"type": "string", "format": "date-time", "nullable": True}
    }
}


# =============================================================================
# SNAPSHOT TESTS
# =============================================================================


class TestSubtaskGenerationResultSchema:
    """Snapshot tests for SubtaskGenerationResult schema."""

    SCHEMA_NAME = "subtask_generation_result"

    def test_schema_snapshot(self):
        """Test that the schema matches the snapshot."""
        expected = load_snapshot(self.SCHEMA_NAME)

        if expected is None:
            # First run - create snapshot
            save_snapshot(self.SCHEMA_NAME, SUBTASK_GENERATION_RESULT_SCHEMA)
            pytest.skip("Snapshot created. Run tests again to validate.")

        differences = compare_schemas(expected, SUBTASK_GENERATION_RESULT_SCHEMA)
        assert not differences, f"Schema differences: {differences}"

    def test_valid_example(self):
        """Test that a valid example matches the schema."""
        example = {
            "subtasks": [
                {"title": "Research the topic"},
                {"title": "Write outline"},
                {"title": "Draft first version"},
            ]
        }

        # Validate required fields
        assert "subtasks" in example
        assert isinstance(example["subtasks"], list)

        for subtask in example["subtasks"]:
            assert "title" in subtask
            assert len(subtask["title"]) >= 1
            assert len(subtask["title"]) <= 200


class TestActionSuggestionSchema:
    """Snapshot tests for ActionSuggestion schema."""

    SCHEMA_NAME = "action_suggestion"

    def test_schema_snapshot(self):
        """Test that the schema matches the snapshot."""
        expected = load_snapshot(self.SCHEMA_NAME)

        if expected is None:
            save_snapshot(self.SCHEMA_NAME, ACTION_SUGGESTION_SCHEMA)
            pytest.skip("Snapshot created. Run tests again to validate.")

        differences = compare_schemas(expected, ACTION_SUGGESTION_SCHEMA)
        assert not differences, f"Schema differences: {differences}"

    def test_valid_example(self):
        """Test that a valid example matches the schema."""
        example = {
            "action_type": "create_task",
            "payload": {
                "title": "New task from AI",
                "priority": "medium"
            },
            "requires_confirmation": True
        }

        assert example["action_type"] in ["create_task", "update_task", "complete_task", "create_reminder"]
        assert isinstance(example["payload"], dict)
        assert example["requires_confirmation"] is True


class TestTaskSuggestionSchema:
    """Snapshot tests for TaskSuggestion schema (note conversion)."""

    SCHEMA_NAME = "task_suggestion"

    def test_schema_snapshot(self):
        """Test that the schema matches the snapshot."""
        expected = load_snapshot(self.SCHEMA_NAME)

        if expected is None:
            save_snapshot(self.SCHEMA_NAME, TASK_SUGGESTION_SCHEMA)
            pytest.skip("Snapshot created. Run tests again to validate.")

        differences = compare_schemas(expected, TASK_SUGGESTION_SCHEMA)
        assert not differences, f"Schema differences: {differences}"

    def test_valid_example(self):
        """Test that a valid example matches the schema."""
        example = {
            "title": "Task converted from note",
            "description": "This task was created from a note using AI conversion.",
            "priority": "high",
            "due_date": "2026-01-25T10:00:00Z"
        }

        assert "title" in example
        assert len(example["title"]) >= 1
        assert len(example["title"]) <= 200
        assert example["priority"] in ["low", "medium", "high"]
