"""Factory for generating Task test data."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import factory

from src.models.user import User


# Note: TaskInstance model will be created in Phase 2
# This factory is set up in advance for when the model is available


class TaskFactory(factory.Factory):
    """Factory for creating TaskInstance instances for testing.

    Usage:
        # Create a basic task
        task = TaskFactory(user_id=user.id)

        # Create a completed task
        completed_task = TaskFactory(completed=True)

        # Create a high priority task
        urgent_task = TaskFactory(priority="high")
    """

    class Meta:
        model = dict  # Will be replaced with TaskInstance model

    id = factory.LazyFunction(uuid4)
    user_id = factory.LazyFunction(uuid4)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=2)
    priority = "medium"
    due_date = factory.LazyFunction(
        lambda: datetime.now(UTC) + timedelta(days=7)
    )
    estimated_duration = factory.Faker("random_int", min=15, max=120)
    focus_time_seconds = 0
    completed = False
    completed_at = None
    completed_by = None
    hidden = False
    archived = False
    version = 1

    class Params:
        """Factory parameters for creating different task variants."""

        completed_task = factory.Trait(
            completed=True,
            completed_at=factory.LazyFunction(lambda: datetime.now(UTC)),
            completed_by="manual",
        )

        overdue = factory.Trait(
            due_date=factory.LazyFunction(
                lambda: datetime.now(UTC) - timedelta(days=1)
            )
        )

        high_priority = factory.Trait(priority="high")
        low_priority = factory.Trait(priority="low")


class SubtaskFactory(factory.Factory):
    """Factory for creating Subtask instances for testing.

    Usage:
        # Create a basic subtask
        subtask = SubtaskFactory(task_id=task.id)

        # Create a completed subtask
        completed_subtask = SubtaskFactory(completed=True)

        # Create an AI-generated subtask
        ai_subtask = SubtaskFactory(source="ai")
    """

    class Meta:
        model = dict  # Will be replaced with Subtask model

    id = factory.LazyFunction(uuid4)
    task_id = factory.LazyFunction(uuid4)
    title = factory.Faker("sentence", nb_words=3)
    completed = False
    completed_at = None
    order_index = factory.Sequence(lambda n: n)
    source = "user"

    class Params:
        """Factory parameters for creating different subtask variants."""

        completed_subtask = factory.Trait(
            completed=True,
            completed_at=factory.LazyFunction(lambda: datetime.now(UTC)),
        )

        ai_generated = factory.Trait(source="ai")
