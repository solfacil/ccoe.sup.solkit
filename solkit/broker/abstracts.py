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
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def producer_config(cls: type['BrokerAdapterAbstract']) -> 'BrokerAdapterAbstract':
        """Create a producer configuration."""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def config(cls: type['BrokerAdapterAbstract']) -> 'BrokerAdapterAbstract':
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
