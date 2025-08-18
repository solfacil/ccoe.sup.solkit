from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from aiokafka.structs import ConsumerRecord

from .abstracts import BrokerAdapterAbstract


class BrokerRepositoryProtocol(Protocol):
    """Protocol for the broker repository."""
    
    def __init__(self, adapter: BrokerAdapterAbstract, metadata: dict[str, Any] | None = None) -> None:
        """Initialize the broker repository."""
        ...
    
    async def produce(
        self,
        topic: str,
        key: str | bytes,
        value: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Produce a message to the broker."""
        ...
    
    async def consume(self, func: Callable[[ConsumerRecord], Awaitable[None]], wait_time: int = 3) -> None:
        """Consume a message from the broker."""
        ...

    # async def healthcheck(self) -> tuple[bool, str | None]:
    #    """Check the health of the broker.
        
    #    Returns:
    #        tuple[bool, str | None]:
    #            - bool: True if the broker is healthy, False otherwise
    #            - str | None: Optional error message if the broker is not healthy
    #    """
    #    ...
