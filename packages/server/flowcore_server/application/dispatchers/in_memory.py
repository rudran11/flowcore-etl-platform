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

    async def dispatch(self, event: DomainEvent) -> None:
        """
        Publishes the event by logging it and storing it in memory.
        """
        logger.info(f"Dispatching DomainEvent: {event.event_type} (ID: {event.event_id})")
        self.published_events.append(event)
