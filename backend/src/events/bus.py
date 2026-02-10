"""In-process synchronous event bus implementation.

T197: Implement event bus with sync dispatch per plan.md AD-003
T199: Implement event handler registry

Design Decision (AD-003):
- In-process synchronous event bus
- Simpler than external message broker
- Sufficient for single-instance API deployment
- Easy to test and debug
- Can upgrade to async/external later if needed
"""

import logging
from collections import defaultdict
from typing import Any, Callable, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.events.types import BaseEvent, Event


logger = logging.getLogger(__name__)


# Type variable for event types
E = TypeVar("E", bound=BaseEvent)

# Handler signature: async def handler(event: Event, session: AsyncSession, settings: Settings) -> None
EventHandler = Callable[[Any, AsyncSession, Settings], Any]


class EventBus:
    """In-process synchronous event bus.

    T197: Implements sync dispatch pattern per plan.md AD-003

    This event bus provides:
    - Registration of handlers for specific event types
    - Synchronous dispatch of events to all registered handlers
    - Error isolation (one handler failure doesn't stop others)
    - Logging for debugging and observability

    Usage:
        bus = EventBus()

        # Register a handler
        @bus.subscribe(TaskCompletedEvent)
        async def handle_task_completed(event, session, settings):
            ...

        # Or register manually
        bus.register(TaskCompletedEvent, my_handler)

        # Dispatch events
        await bus.dispatch(event, session, settings)
    """

    def __init__(self) -> None:
        """Initialize the event bus."""
        # Map of event type -> list of handlers
        self._handlers: dict[Type[BaseEvent], list[EventHandler]] = defaultdict(list)
        self._middleware: list[Callable] = []

    def register(
        self,
        event_type: Type[E],
        handler: EventHandler,
    ) -> None:
        """Register a handler for an event type.

        T199: Event handler registry implementation

        Args:
            event_type: The event class to handle
            handler: Async function that handles the event
        """
        self._handlers[event_type].append(handler)
        logger.debug(
            f"Registered handler {handler.__name__} for {event_type.__name__}"
        )

    def subscribe(
        self,
        event_type: Type[E],
    ) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register an event handler.

        T199: Decorator-based registration

        Usage:
            @event_bus.subscribe(TaskCompletedEvent)
            async def handle_task_completed(event, session, settings):
                ...

        Args:
            event_type: The event class to handle

        Returns:
            Decorator function
        """
        def decorator(handler: EventHandler) -> EventHandler:
            self.register(event_type, handler)
            return handler
        return decorator

    def unregister(
        self,
        event_type: Type[E],
        handler: EventHandler,
    ) -> bool:
        """Remove a handler for an event type.

        Args:
            event_type: The event class
            handler: The handler to remove

        Returns:
            True if handler was found and removed
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(
                f"Unregistered handler {handler.__name__} for {event_type.__name__}"
            )
            return True
        return False

    def clear(self, event_type: Type[E] | None = None) -> None:
        """Clear handlers for an event type or all handlers.

        Args:
            event_type: Specific event type to clear, or None for all
        """
        if event_type is None:
            self._handlers.clear()
            logger.debug("Cleared all event handlers")
        elif event_type in self._handlers:
            self._handlers[event_type].clear()
            logger.debug(f"Cleared handlers for {event_type.__name__}")

    def get_handlers(self, event_type: Type[E]) -> list[EventHandler]:
        """Get all handlers for an event type.

        Args:
            event_type: The event class

        Returns:
            List of registered handlers
        """
        return list(self._handlers.get(event_type, []))

    async def dispatch(
        self,
        event: Event,
        session: AsyncSession,
        settings: Settings,
    ) -> list[Exception]:
        """Dispatch an event to all registered handlers.

        T197: Synchronous dispatch implementation

        Handlers are called synchronously (one at a time).
        Errors in one handler don't prevent other handlers from running.

        Args:
            event: The event to dispatch
            session: Database session for handlers
            settings: Application settings

        Returns:
            List of exceptions that occurred during handling
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers for {event_type.__name__}")
            return []

        logger.info(
            f"Dispatching {event_type.__name__} to {len(handlers)} handler(s)"
        )

        errors: list[Exception] = []

        for handler in handlers:
            try:
                result = handler(event, session, settings)
                # Handle both sync and async handlers
                if hasattr(result, "__await__"):
                    await result
                logger.debug(
                    f"Handler {handler.__name__} processed {event_type.__name__}"
                )
            except Exception as e:
                logger.error(
                    f"Handler {handler.__name__} failed for {event_type.__name__}: {e}",
                    exc_info=True,
                )
                errors.append(e)

        if errors:
            logger.warning(
                f"{len(errors)} handler(s) failed for {event_type.__name__}"
            )

        return errors

    async def dispatch_many(
        self,
        events: list[Event],
        session: AsyncSession,
        settings: Settings,
    ) -> dict[str, list[Exception]]:
        """Dispatch multiple events.

        Args:
            events: List of events to dispatch
            session: Database session
            settings: Application settings

        Returns:
            Dict mapping event type names to their errors
        """
        all_errors: dict[str, list[Exception]] = {}

        for event in events:
            errors = await self.dispatch(event, session, settings)
            if errors:
                all_errors[type(event).__name__] = errors

        return all_errors


# =============================================================================
# GLOBAL EVENT BUS INSTANCE
# =============================================================================

# Singleton event bus for the application
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    Returns:
        The singleton EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (for testing)."""
    global _event_bus
    if _event_bus is not None:
        _event_bus.clear()
    _event_bus = None


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def subscribe(event_type: Type[E]) -> Callable[[EventHandler], EventHandler]:
    """Convenience decorator using the global event bus.

    Usage:
        @subscribe(TaskCompletedEvent)
        async def handle_task_completed(event, session, settings):
            ...
    """
    return get_event_bus().subscribe(event_type)


async def dispatch(
    event: Event,
    session: AsyncSession,
    settings: Settings,
) -> list[Exception]:
    """Dispatch an event using the global event bus.

    Args:
        event: The event to dispatch
        session: Database session
        settings: Application settings

    Returns:
        List of exceptions from handlers
    """
    return await get_event_bus().dispatch(event, session, settings)
