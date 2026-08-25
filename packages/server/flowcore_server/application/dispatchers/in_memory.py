import logging
from typing import List
from flowcore_shared.events import DomainEvent
from flowcore_server.application.interfaces.dispatcher import AbstractEventDispatcher

logger = logging.getLogger(__name__)

class InMemoryEventDispatcher(AbstractEventDispatcher):
    """
    In-memory dispatcher used for development and testing.
    Logs events and stores them internally for assertion in tests.
    """
    def __init__(self):
        self.published_events: List[DomainEvent] = []
        self._handlers = {}

    async def dispatch(self, event: DomainEvent) -> None:
        """
        Publishes the event by logging it and storing it in memory.
        """
        logger.info(f"Dispatching DomainEvent: {event.event_type} (ID: {event.event_id})")
        self.published_events.append(event)
        
        # Invoke handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                import asyncio
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

    def register_handler(self, event_type: str, handler: callable):
        """Register a handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
