from abc import ABC, abstractmethod
from flowcore_shared.events import DomainEvent

class AbstractEventDispatcher(ABC):
    """
    Protocol for dispatching domain events to external systems
    (e.g., Kafka, RabbitMQ, Redis, or internal observers).
    """

    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None:
        """
        Publishes a DomainEvent.
        Must ONLY be called after a successful transaction commit.
        """
        pass
