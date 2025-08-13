from abc import ABC, abstractmethod

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
        NotImplementedError()
    
    @abstractmethod
    @classmethod
    def config(cls) -> "BrokerAdapterAbstract":
        """Create a producer and consumer configuration."""
        NotImplementedError()
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect the producer and consumer."""
        NotImplementedError()
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the producer and consumer."""
        NotImplementedError()
