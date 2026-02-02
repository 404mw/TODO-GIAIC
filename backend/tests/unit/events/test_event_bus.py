"""Unit tests for the event bus.

T212: Test event dispatch calls registered handlers
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.events.bus import EventBus, get_event_bus, reset_event_bus
from src.events.types import TaskCreatedEvent, TaskCompletedEvent
from src.schemas.enums import ActivitySource, CompletedBy


@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    bus = EventBus()
    return bus


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return MagicMock()


class TestEventBusRegistration:
    """Tests for handler registration."""

    def test_register_handler(self, event_bus):
        """Test registering a handler for an event type."""
        handler = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler)

        handlers = event_bus.get_handlers(TaskCreatedEvent)
        assert len(handlers) == 1
        assert handlers[0] == handler

    def test_register_multiple_handlers(self, event_bus):
        """Test registering multiple handlers for the same event type."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        event_bus.register(TaskCreatedEvent, handler1)
        event_bus.register(TaskCreatedEvent, handler2)

        handlers = event_bus.get_handlers(TaskCreatedEvent)
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers

    def test_register_handlers_for_different_events(self, event_bus):
        """Test registering handlers for different event types."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        event_bus.register(TaskCreatedEvent, handler1)
        event_bus.register(TaskCompletedEvent, handler2)

        assert len(event_bus.get_handlers(TaskCreatedEvent)) == 1
        assert len(event_bus.get_handlers(TaskCompletedEvent)) == 1

    def test_subscribe_decorator(self, event_bus):
        """Test the subscribe decorator."""
        @event_bus.subscribe(TaskCreatedEvent)
        async def my_handler(event, session, settings):
            pass

        handlers = event_bus.get_handlers(TaskCreatedEvent)
        assert len(handlers) == 1
        assert handlers[0] == my_handler

    def test_unregister_handler(self, event_bus):
        """Test unregistering a handler."""
        handler = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler)

        result = event_bus.unregister(TaskCreatedEvent, handler)

        assert result is True
        assert len(event_bus.get_handlers(TaskCreatedEvent)) == 0

    def test_unregister_nonexistent_handler(self, event_bus):
        """Test unregistering a handler that doesn't exist."""
        handler = AsyncMock()

        result = event_bus.unregister(TaskCreatedEvent, handler)

        assert result is False

    def test_clear_handlers_for_event(self, event_bus):
        """Test clearing handlers for a specific event type."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler1)
        event_bus.register(TaskCompletedEvent, handler2)

        event_bus.clear(TaskCreatedEvent)

        assert len(event_bus.get_handlers(TaskCreatedEvent)) == 0
        assert len(event_bus.get_handlers(TaskCompletedEvent)) == 1

    def test_clear_all_handlers(self, event_bus):
        """Test clearing all handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler1)
        event_bus.register(TaskCompletedEvent, handler2)

        event_bus.clear()

        assert len(event_bus.get_handlers(TaskCreatedEvent)) == 0
        assert len(event_bus.get_handlers(TaskCompletedEvent)) == 0


class TestEventBusDispatch:
    """Tests for event dispatch."""

    @pytest.mark.asyncio
    async def test_dispatch_calls_handlers(self, event_bus, mock_session, mock_settings):
        """T212: Test that dispatch calls all registered handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler1)
        event_bus.register(TaskCreatedEvent, handler2)

        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            source=ActivitySource.USER,
        )

        errors = await event_bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 0
        handler1.assert_called_once_with(event, mock_session, mock_settings)
        handler2.assert_called_once_with(event, mock_session, mock_settings)

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers(self, event_bus, mock_session, mock_settings):
        """Test dispatch when no handlers are registered."""
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
        )

        errors = await event_bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_dispatch_handler_error_isolated(self, event_bus, mock_session, mock_settings):
        """Test that handler errors don't prevent other handlers from running."""
        failing_handler = AsyncMock(side_effect=Exception("Handler failed"))
        successful_handler = AsyncMock()

        event_bus.register(TaskCreatedEvent, failing_handler)
        event_bus.register(TaskCreatedEvent, successful_handler)

        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
        )

        errors = await event_bus.dispatch(event, mock_session, mock_settings)

        assert len(errors) == 1
        assert str(errors[0]) == "Handler failed"
        successful_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_many(self, event_bus, mock_session, mock_settings):
        """Test dispatching multiple events."""
        handler = AsyncMock()
        event_bus.register(TaskCreatedEvent, handler)

        events = [
            TaskCreatedEvent(task_id=uuid4(), user_id=uuid4(), title="Task 1"),
            TaskCreatedEvent(task_id=uuid4(), user_id=uuid4(), title="Task 2"),
        ]

        errors = await event_bus.dispatch_many(events, mock_session, mock_settings)

        assert len(errors) == 0
        assert handler.call_count == 2


class TestGlobalEventBus:
    """Tests for the global event bus singleton."""

    def test_get_event_bus_returns_same_instance(self):
        """Test that get_event_bus returns the same instance."""
        reset_event_bus()

        bus1 = get_event_bus()
        bus2 = get_event_bus()

        assert bus1 is bus2

    def test_reset_event_bus_clears_instance(self):
        """Test that reset_event_bus clears the singleton."""
        bus1 = get_event_bus()
        bus1.register(TaskCreatedEvent, AsyncMock())

        reset_event_bus()
        bus2 = get_event_bus()

        assert bus1 is not bus2
        assert len(bus2.get_handlers(TaskCreatedEvent)) == 0


class TestEventTypes:
    """Tests for event type definitions."""

    def test_task_created_event_type(self):
        """Test TaskCreatedEvent has correct event_type."""
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test",
        )
        assert event.event_type == "task.created"

    def test_task_completed_event_type(self):
        """Test TaskCompletedEvent has correct event_type."""
        event = TaskCompletedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            completed_by=CompletedBy.MANUAL,
        )
        assert event.event_type == "task.completed"

    def test_event_timestamp_set(self):
        """Test that events have a timestamp set."""
        event = TaskCreatedEvent(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test",
        )
        assert event.timestamp is not None
