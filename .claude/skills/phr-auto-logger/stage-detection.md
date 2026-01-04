# PHR Stage and Feature Detection

## Stage Detection Logic

```python
def detect_stage(work_description: str, files_modified: list[str]) -> str:
    """Detect the appropriate stage for PHR"""

    # Constitution work
    if "constitution.md" in files_modified:
        return "constitution"

    # Spec work
    if any("spec.md" in f for f in files_modified):
        return "spec"

    # Plan work
    if any("plan.md" in f for f in files_modified):
        return "plan"

    # Tasks work
    if any("tasks.md" in f for f in files_modified):
        return "tasks"

    # TDD phases (check for test files and implementation)
    test_files = [f for f in files_modified if "test_" in f or "tests/" in f]
    impl_files = [f for f in files_modified if f not in test_files]

    if test_files and not impl_files:
        return "red"  # Only tests modified
    elif impl_files and test_files:
        return "green"  # Implementation + tests
    elif impl_files and not test_files and "refactor" in work_description.lower():
        return "refactor"

    # Explanation work
    if any(keyword in work_description.lower() for keyword in ["explain", "how does", "what is"]):
        return "explainer"

    # Feature-specific but doesn't fit elsewhere
    if any("specs/" in f for f in files_modified):
        return "misc"

    # Default
    return "general"
```

## Feature Detection

```python
def detect_feature(files_modified: list[str], branch: str) -> str:
    """Detect feature name from context"""

    # Check branch name first
    if branch.startswith("feature/"):
        return branch.replace("feature/", "")

    # Check file paths
    for file in files_modified:
        if file.startswith("specs/"):
            parts = file.split("/")
            if len(parts) >= 2:
                return parts[1]  # specs/<feature-name>/...

    # No feature detected
    return "none"
```

## Routing Logic

```python
def determine_route(stage: str, feature: str) -> str:
    """Determine PHR routing path"""

    # Constitution always goes to constitution/
    if stage == "constitution":
        return "history/prompts/constitution/"

    # Feature stages go to feature subdirectory
    if stage in ["spec", "plan", "tasks", "red", "green", "refactor", "misc"]:
        if feature and feature != "none":
            return f"history/prompts/{feature}/"
        else:
            # No feature detected, but stage is feature-related
            # This is an error state - should not happen
            return "history/prompts/general/"

    # General and explainer go to general/
    return "history/prompts/general/"
```

## Usage Example

```python
# Example 1: Constitution work
work_description = "Update the constitution to add a new principle"
files_modified = [".specify/memory/constitution.md"]
branch = "master"

stage = detect_stage(work_description, files_modified)
# Returns: "constitution"

feature = detect_feature(files_modified, branch)
# Returns: "none"

route = determine_route(stage, feature)
# Returns: "history/prompts/constitution/"

# Filename: history/prompts/constitution/005-add-error-handling-principle.constitution.prompt.md
```

```python
# Example 2: Feature implementation (GREEN phase)
work_description = "Implement the priority field (we already have spec and plan)"
files_modified = [
    "app/models/task.py",
    "app/api/tasks.py",
    "tests/test_task_priority.py",
    "tests/integration/test_priority_api.py"
]
branch = "feature/task-priority"

stage = detect_stage(work_description, files_modified)
# Returns: "green" (implementation + tests)

feature = detect_feature(files_modified, branch)
# Returns: "task-priority" (from branch)

route = determine_route(stage, feature)
# Returns: "history/prompts/task-priority/"

# Filename: history/prompts/task-priority/004-implement-priority-field.green.prompt.md
```

```python
# Example 3: Explanation (general work)
work_description = "Explain how the authentication flow works"
files_modified = []  # No files modified
branch = "master"

stage = detect_stage(work_description, files_modified)
# Returns: "explainer" (keyword "explain" detected)

feature = detect_feature(files_modified, branch)
# Returns: "none"

route = determine_route(stage, feature)
# Returns: "history/prompts/general/"

# Filename: history/prompts/general/023-explain-authentication-flow.general.prompt.md
```

```python
# Example 4: RED phase (tests only)
work_description = "Write tests for the priority feature"
files_modified = [
    "tests/test_task_priority.py",
    "tests/integration/test_priority_api.py"
]
branch = "feature/task-priority"

stage = detect_stage(work_description, files_modified)
# Returns: "red" (only test files modified)

feature = detect_feature(files_modified, branch)
# Returns: "task-priority" (from branch)

route = determine_route(stage, feature)
# Returns: "history/prompts/task-priority/"

# Filename: history/prompts/task-priority/002-write-priority-tests.red.prompt.md
```
