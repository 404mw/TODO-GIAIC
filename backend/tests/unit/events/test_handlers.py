"""Unit tests for event handlers.

Tests for:
- _map_event_to_activity mapping function
- _get_entity_id / _get_user_id / _get_source helpers
- activity_log_handler
- handle_recurring_task_completed
- handle_task_completed_for_achievements
- handle_note_converted_for_achievements
- register_all_handlers
- create_task_completed_event
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.events.handlers import (
    _get_entity_id,
    _get_source,
    _get_user_id,
    _map_event_to_activity,
    activity_log_handler,
    create_task_completed_event,
    handle_note_converted_for_achievements,
    handle_recurring_task_completed,
    handle_subtask_completed_for_auto_complete,
    handle_task_completed_for_achievements,
    register_all_handlers,
)
from src.events.types import (
    AchievementUnlockedEvent,
    AIChatEvent,
    AISubtasksGeneratedEvent,
    NoteConvertedEvent,
    NoteCreatedEvent,
    NoteDeletedEvent,
    ReminderFiredEvent,
    SubtaskCompletedEvent,
    SubtaskCreatedEvent,
    SubtaskDeletedEvent,
    SubscriptionCancelledEvent,
    SubscriptionCreatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)
from src.schemas.enums import ActivitySource, CompletedBy, EntityType


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    return MagicMock()


# =============================================================================
# _map_event_to_activity TESTS
# =============================================================================


class TestMapEventToActivity:
    """Test event-to-activity mapping function."""

    def test_task_created_event(self):
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            source=ActivitySource.USER,
        )
        result = _map_event_to_activity(event)
        assert result is not None
        entity_type, action, metadata = result
        assert entity_type == EntityType.TASK
        assert action == "task_created"
        assert metadata["title"] == "Test Task"
        assert metadata["source"] == "user"

    def test_task_completed_event(self):
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            completed_at=datetime.now(timezone.utc),
            template_id=None,
        )
        result = _map_event_to_activity(event)
        assert result is not None
        entity_type, action, metadata = result
        assert entity_type == EntityType.TASK
        assert action == "task_completed"
        assert metadata["completed_by"] == "manual"

    def test_task_completed_event_with_template(self):
        template_id = uuid4()
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.AUTO,
            completed_at=datetime.now(timezone.utc),
            template_id=template_id,
        )
        result = _map_event_to_activity(event)
        _, _, metadata = result
        assert metadata["template_id"] == str(template_id)

    def test_task_deleted_event(self):
        tombstone_id = uuid4()
        event = TaskDeletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            hard_delete=True,
            tombstone_id=tombstone_id,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.TASK
        assert action == "task_deleted"
        assert metadata["hard_delete"] is True
        assert metadata["tombstone_id"] == str(tombstone_id)

    def test_task_deleted_event_soft(self):
        event = TaskDeletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            hard_delete=False,
            tombstone_id=None,
        )
        result = _map_event_to_activity(event)
        _, _, metadata = result
        assert metadata["hard_delete"] is False
        assert metadata["tombstone_id"] is None

    def test_task_updated_event(self):
        event = TaskUpdatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            changes={"title": "New Title", "priority": "high"},
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.TASK
        assert action == "task_updated"
        assert "title" in metadata["changes"]
        assert "priority" in metadata["changes"]

    def test_subtask_created_event(self):
        task_id = uuid4()
        event = SubtaskCreatedEvent(
            subtask_id=uuid4(),
            task_id=task_id,
            user_id=uuid4(),
            title="Subtask 1",
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.SUBTASK
        assert action == "subtask_created"
        assert metadata["task_id"] == str(task_id)

    def test_subtask_completed_event(self):
        task_id = uuid4()
        event = SubtaskCompletedEvent(
            subtask_id=uuid4(),
            task_id=task_id,
            user_id=uuid4(),
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.SUBTASK
        assert action == "subtask_completed"
        assert metadata["task_id"] == str(task_id)

    def test_subtask_deleted_event(self):
        event = SubtaskDeletedEvent(
            subtask_id=uuid4(),
            task_id=uuid4(),
            user_id=uuid4(),
        )
        result = _map_event_to_activity(event)
        entity_type, action, _ = result
        assert entity_type == EntityType.SUBTASK
        assert action == "subtask_deleted"

    def test_note_created_event(self):
        event = NoteCreatedEvent(
            note_id=uuid4(),
            user_id=uuid4(),
            has_voice=True,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.NOTE
        assert action == "note_created"
        assert metadata["has_voice"] is True

    def test_note_converted_event(self):
        task_id = uuid4()
        event = NoteConvertedEvent(
            note_id=uuid4(),
            user_id=uuid4(),
            task_id=task_id,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.NOTE
        assert action == "note_converted"
        assert metadata["task_id"] == str(task_id)

    def test_note_deleted_event(self):
        event = NoteDeletedEvent(
            note_id=uuid4(),
            user_id=uuid4(),
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.NOTE
        assert action == "note_deleted"

    def test_ai_chat_event(self):
        task_id = uuid4()
        event = AIChatEvent(
            user_id=uuid4(),
            credits_used=1,
            task_id=task_id,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.AI_CHAT
        assert action == "ai_chat"
        assert metadata["credits_used"] == 1
        assert metadata["task_id"] == str(task_id)

    def test_ai_chat_event_no_task(self):
        event = AIChatEvent(
            user_id=uuid4(),
            credits_used=1,
            task_id=None,
        )
        result = _map_event_to_activity(event)
        _, _, metadata = result
        assert metadata["task_id"] is None

    def test_ai_subtasks_generated_event(self):
        event = AISubtasksGeneratedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            count=3,
            credits_used=1,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.TASK
        assert action == "ai_subtask_generation"
        assert metadata["count"] == 3

    def test_subscription_created_event(self):
        event = SubscriptionCreatedEvent(
            user_id=uuid4(),
            tier="pro",
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.SUBSCRIPTION
        assert action == "subscription_created"
        assert metadata["tier"] == "pro"

    def test_subscription_cancelled_event(self):
        event = SubscriptionCancelledEvent(
            user_id=uuid4(),
            effective_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.SUBSCRIPTION
        assert action == "subscription_cancelled"
        assert metadata["effective_date"] is not None

    def test_subscription_cancelled_event_no_date(self):
        event = SubscriptionCancelledEvent(
            user_id=uuid4(),
            effective_date=None,
        )
        result = _map_event_to_activity(event)
        _, _, metadata = result
        assert metadata["effective_date"] is None

    def test_achievement_unlocked_event(self):
        event = AchievementUnlockedEvent(
            user_id=uuid4(),
            achievement_id="tasks_5",
            achievement_name="Task Starter",
            perk_type="max_tasks",
            perk_value=15,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.ACHIEVEMENT
        assert action == "achievement_unlocked"
        assert metadata["achievement_name"] == "Task Starter"

    def test_reminder_fired_event(self):
        task_id = uuid4()
        event = ReminderFiredEvent(
            reminder_id=uuid4(),
            user_id=uuid4(),
            task_id=task_id,
        )
        result = _map_event_to_activity(event)
        entity_type, action, metadata = result
        assert entity_type == EntityType.REMINDER
        assert action == "reminder_fired"
        assert metadata["task_id"] == str(task_id)

    def test_unknown_event_returns_none(self):
        """Unknown events should return None."""
        event = MagicMock(spec=[])
        result = _map_event_to_activity(event)
        assert result is None


# =============================================================================
# _get_entity_id / _get_user_id / _get_source TESTS
# =============================================================================


class TestGetEntityId:
    """Test entity ID extraction from events."""

    def test_extracts_task_id(self):
        event = MagicMock(task_id=uuid4())
        result = _get_entity_id(event)
        assert result == event.task_id

    def test_extracts_subtask_id(self):
        event = MagicMock(spec=["subtask_id"])
        event.subtask_id = uuid4()
        result = _get_entity_id(event)
        assert result == event.subtask_id

    def test_extracts_note_id(self):
        event = MagicMock(spec=["note_id"])
        event.note_id = uuid4()
        result = _get_entity_id(event)
        assert result == event.note_id

    def test_extracts_reminder_id(self):
        event = MagicMock(spec=["reminder_id"])
        event.reminder_id = uuid4()
        result = _get_entity_id(event)
        assert result == event.reminder_id

    def test_extracts_user_id_as_fallback(self):
        event = MagicMock(spec=["user_id"])
        event.user_id = uuid4()
        result = _get_entity_id(event)
        assert result == event.user_id

    def test_raises_for_unknown_event(self):
        event = MagicMock(spec=[])
        with pytest.raises(ValueError, match="Cannot extract entity_id"):
            _get_entity_id(event)


class TestGetUserId:
    """Test user ID extraction."""

    def test_extracts_user_id(self):
        event = MagicMock(user_id=uuid4())
        result = _get_user_id(event)
        assert result == event.user_id

    def test_raises_for_missing_user_id(self):
        event = MagicMock(spec=[])
        with pytest.raises(ValueError, match="Cannot extract user_id"):
            _get_user_id(event)


class TestGetSource:
    """Test source extraction."""

    def test_extracts_source_attribute(self):
        event = MagicMock(source=ActivitySource.USER)
        result = _get_source(event)
        assert result == ActivitySource.USER

    def test_ai_chat_event_defaults_to_ai(self):
        event = AIChatEvent(
            user_id=uuid4(),
            credits_used=1,
            task_id=None,
        )
        # Remove source if it exists
        if hasattr(event, "source"):
            delattr(event, "source")
        # For AIChatEvent without explicit source, should default to AI
        result = _get_source(event)
        assert result == ActivitySource.AI

    def test_unknown_event_defaults_to_user(self):
        event = MagicMock(spec=["task_id", "user_id"])
        result = _get_source(event)
        assert result == ActivitySource.USER


# =============================================================================
# activity_log_handler TESTS
# =============================================================================


class TestActivityLogHandler:
    """Test the activity log handler."""

    @pytest.mark.asyncio
    async def test_logs_task_created_event(self, mock_session, mock_settings):
        """Handler should create activity log for task created events."""
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            source=ActivitySource.USER,
        )

        await activity_log_handler(event, mock_session, mock_settings)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_unknown_event(self, mock_session, mock_settings):
        """Handler should skip events with no activity mapping."""
        event = MagicMock(spec=[])

        await activity_log_handler(event, mock_session, mock_settings)

        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_db_errors_gracefully(self, mock_session, mock_settings):
        """Handler should not raise on database errors."""
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            source=ActivitySource.USER,
        )
        mock_session.flush.side_effect = Exception("DB error")

        # Should not raise
        await activity_log_handler(event, mock_session, mock_settings)


# =============================================================================
# handle_recurring_task_completed TESTS
# =============================================================================


class TestHandleRecurringTaskCompleted:
    """Test recurring task completion handler."""

    @pytest.mark.asyncio
    async def test_returns_none_if_no_template(self, mock_session, mock_settings):
        """Handler should return None if task has no template."""
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            completed_at=datetime.now(timezone.utc),
            template_id=None,
        )

        result = await handle_recurring_task_completed(event, mock_session, mock_settings)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_if_template_not_found(self, mock_session, mock_settings):
        """Handler should return None if template doesn't exist."""
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            completed_at=datetime.now(timezone.utc),
            template_id=uuid4(),
        )

        # Template query returns None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        result = await handle_recurring_task_completed(event, mock_session, mock_settings)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_if_template_inactive(self, mock_session, mock_settings):
        """Handler should return None if template is inactive."""
        template = MagicMock()
        template.active = False

        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            completed_at=datetime.now(timezone.utc),
            template_id=uuid4(),
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = template
        mock_session.execute.return_value = result_mock

        result = await handle_recurring_task_completed(event, mock_session, mock_settings)
        assert result is None


# =============================================================================
# handle_task_completed_for_achievements TESTS
# =============================================================================


class TestHandleTaskCompletedForAchievements:
    """Test achievement handler for task completion."""

    @pytest.mark.asyncio
    async def test_handles_errors_gracefully(self, mock_session, mock_settings):
        """Handler should not raise on errors."""
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            completed_at=datetime.now(timezone.utc),
            template_id=None,
        )

        # Make the session execute fail to trigger the error path
        mock_session.execute = AsyncMock(side_effect=Exception("Service error"))

        result = await handle_task_completed_for_achievements(
            event, mock_session, mock_settings
        )

        assert result == []


# =============================================================================
# handle_note_converted_for_achievements TESTS
# =============================================================================


class TestHandleNoteConvertedForAchievements:
    """Test achievement handler for note conversion."""

    @pytest.mark.asyncio
    async def test_handles_errors_gracefully(self, mock_session, mock_settings):
        """Handler should not raise on errors."""
        event = NoteConvertedEvent(
            note_id=uuid4(),
            user_id=uuid4(),
            task_id=uuid4(),
        )

        # Make the session execute fail to trigger the error path
        mock_session.execute = AsyncMock(side_effect=Exception("Service error"))

        result = await handle_note_converted_for_achievements(
            event, mock_session, mock_settings
        )

        assert result == []


# =============================================================================
# register_all_handlers TESTS
# =============================================================================


class TestRegisterAllHandlers:
    """Test handler registration."""

    def test_registers_handlers(self):
        """register_all_handlers should register handlers on the event bus."""
        with patch("src.events.handlers.get_event_bus") as mock_get_bus:
            mock_bus = MagicMock()
            mock_get_bus.return_value = mock_bus

            register_all_handlers()

            # Should register multiple handlers
            assert mock_bus.register.call_count > 0


# =============================================================================
# create_task_completed_event TESTS
# =============================================================================


class TestCreateTaskCompletedEvent:
    """Test task completed event creation utility."""

    def test_creates_event_from_task(self):
        """Should create a TaskCompletedEvent from a TaskInstance."""
        task = MagicMock()
        task.id = uuid4()
        task.user_id = uuid4()
        task.template_id = None
        task.completed_by = CompletedBy.MANUAL
        task.completed_at = datetime.now(timezone.utc)

        event = create_task_completed_event(task)

        assert event.task_id == task.id
        assert event.user_id == task.user_id
        assert event.completed_by == CompletedBy.MANUAL

    def test_creates_event_with_default_completed_by(self):
        """Should default completed_by to MANUAL if None."""
        task = MagicMock()
        task.id = uuid4()
        task.user_id = uuid4()
        task.template_id = None
        task.completed_by = None
        task.completed_at = datetime.now(timezone.utc)

        event = create_task_completed_event(task)

        assert event.completed_by == CompletedBy.MANUAL
