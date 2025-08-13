from abc import ABC, abstractmethod
from typing import Self

from .settings import BrokerKafkaConsumerSettings, BrokerKafkaProducerSettings


class BrokerAdapterAbstract(ABC):
    """Abstract class for the broker adapter."""
    
    @abstractmethod
    def __init__(
        self,
        producer_settings: BrokerKafkaProducerSettings | None = None,
        consumer_settings: BrokerKafkaConsumerSettings | None = None,
    ) -> None:
        """Initialize the broker adapter."""
        raise NotImplementedError()
    
    @classmethod
    @abstractmethod
    def config(cls) -> "Self":
        """Create a producer and consumer configuration."""
        raise NotImplementedError()
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect the producer and consumer."""
        raise NotImplementedError()
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the producer and consumer."""
        raise NotImplementedError()
