"""Integration tests for event to activity log flow.

T217: Integration test for event to activity log flow
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from src.events.bus import EventBus, get_event_bus, reset_event_bus
from src.events.types import (
    TaskCreatedEvent,
    TaskCompletedEvent,
    SubtaskCompletedEvent,
)
from src.events.handlers import (
    activity_log_handler,
    register_all_handlers,
)
from src.schemas.enums import ActivitySource, CompletedBy, EntityType


@pytest.fixture(autouse=True)
def reset_bus():
    """Reset the global event bus before and after each test."""
    reset_event_bus()
    yield
    reset_event_bus()


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock()


class TestEventToActivityLogFlow:
    """Integration tests for event dispatch to activity logging."""

    @pytest.mark.asyncio
    async def test_task_created_logs_activity(self, mock_session, mock_settings):
        """T217: Test TaskCreatedEvent creates activity log entry."""
        bus = get_event_bus()
        bus.register(TaskCreatedEvent, activity_log_handler)

        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            source=ActivitySource.USER,
        )

        errors = await bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 0
        # Verify activity log was added to session
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

        # Verify the activity log has correct values
        call_args = mock_session.add.call_args[0][0]
        assert call_args.entity_type == EntityType.TASK
        assert call_args.action == "task_created"
        assert call_args.user_id == event.user_id

    @pytest.mark.asyncio
    async def test_task_completed_logs_activity(self, mock_session, mock_settings):
        """T217: Test TaskCompletedEvent creates activity log entry."""
        bus = get_event_bus()
        bus.register(TaskCompletedEvent, activity_log_handler)

        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
        )

        errors = await bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 0
        mock_session.add.assert_called_once()

        call_args = mock_session.add.call_args[0][0]
        assert call_args.action == "task_completed"
        assert call_args.extra_data["completed_by"] == "manual"

    @pytest.mark.asyncio
    async def test_multiple_handlers_all_execute(self, mock_session, mock_settings):
        """T217: Test multiple handlers execute for same event."""
        bus = get_event_bus()

        handler1_called = False
        handler2_called = False

        async def handler1(event, session, settings):
            nonlocal handler1_called
            handler1_called = True

        async def handler2(event, session, settings):
            nonlocal handler2_called
            handler2_called = True

        bus.register(TaskCreatedEvent, handler1)
        bus.register(TaskCreatedEvent, handler2)

        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test",
        )

        await bus.dispatch(event, mock_session, mock_settings)

        assert handler1_called
        assert handler2_called

    @pytest.mark.asyncio
    async def test_handler_error_doesnt_stop_others(self, mock_session, mock_settings):
        """T217: Test that one handler's error doesn't stop other handlers."""
        bus = get_event_bus()

        successful_handler_called = False

        async def failing_handler(event, session, settings):
            raise Exception("Handler failed")

        async def successful_handler(event, session, settings):
            nonlocal successful_handler_called
            successful_handler_called = True

        bus.register(TaskCreatedEvent, failing_handler)
        bus.register(TaskCreatedEvent, successful_handler)

        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test",
        )

        errors = await bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 1
        assert successful_handler_called


class TestHandlerRegistration:
    """Tests for handler registration on startup."""

    def test_register_all_handlers(self):
        """Test that register_all_handlers registers expected handlers."""
        reset_event_bus()
        register_all_handlers()

        bus = get_event_bus()

        # Check that handlers are registered for key event types
        assert len(bus.get_handlers(TaskCreatedEvent)) >= 1
        assert len(bus.get_handlers(TaskCompletedEvent)) >= 2  # Activity + recurring
        assert len(bus.get_handlers(SubtaskCompletedEvent)) >= 2  # Activity + auto-complete


class TestEventChaining:
    """Tests for events that trigger other events."""

    @pytest.mark.asyncio
    async def test_task_completion_triggers_recurring_check(
        self, mock_session, mock_settings
    ):
        """T217: Test TaskCompletedEvent triggers recurring task generation check."""
        bus = get_event_bus()

        recurring_handler_called = False
        template_id = uuid4()

        async def mock_recurring_handler(event, session, settings):
            nonlocal recurring_handler_called
            if event.template_id == template_id:
                recurring_handler_called = True

        bus.register(TaskCompletedEvent, mock_recurring_handler)

        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
            template_id=template_id,
        )

        await bus.dispatch(event, mock_session, mock_settings)

        assert recurring_handler_called
