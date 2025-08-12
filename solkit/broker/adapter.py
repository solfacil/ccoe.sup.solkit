import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .settings import BrokerKafkaConsumerSettings, BrokerKafkaProducerSettings

logger = logging.getLogger(__name__)


class BrokerKafkaAdapter:
    
    # @classmethod
    # def config_consumer(cls) -> "BrokerKafkaAdapter":
    #    consumer_settings = BrokerKafkaConsumerSettings()
    #    return cls(consumer_settings=consumer_settings)
    
    @classmethod
    def producer_config(cls) -> "BrokerKafkaAdapter":
        """Create a producer configuration."""
        producer_settings = BrokerKafkaProducerSettings()
        return cls(producer_settings=producer_settings)
    
    @classmethod
    def config(cls) -> "BrokerKafkaAdapter":
        producer_settings = BrokerKafkaProducerSettings()
        consumer_settings = BrokerKafkaConsumerSettings()
        return cls(producer_settings=producer_settings, consumer_settings=consumer_settings)
    
    def __init__(
        self,
        producer_settings: BrokerKafkaProducerSettings | None = None,
        consumer_settings: BrokerKafkaConsumerSettings | None = None,
    ) -> None:
        """Initialize the broker Kafka adapter."""
        self._producer_settings = producer_settings
        self._consumer_settings = consumer_settings
        self._producer: AIOKafkaProducer | None = None
        self._consumer: AIOKafkaConsumer | None = None

    def __create_producer(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._producer_settings.bootstrap_servers,
            request_timeout_ms=self._producer_settings.request_timeout_ms,
            acks=self._producer_settings.parsed_acks(),
            connections_max_idle_ms=self._producer_settings.connections_max_idle_ms,
        )
    
    def __create_consumer(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self._consumer_settings.get_topics(),
            bootstrap_servers=self._consumer_settings.bootstrap_servers,
            enable_auto_commit=self._consumer_settings.enable_auto_commit,
            request_timeout_ms=self._consumer_settings.request_timeout_ms,
            group_id=self._consumer_settings.group_id,
            max_poll_records=self._consumer_settings.max_poll_records,
            max_poll_interval_ms=self._consumer_settings.max_poll_interval_ms,
            session_timeout_ms=self._consumer_settings.session_timeout_ms,
            heartbeat_interval_ms=self._consumer_settings.heartbeat_interval_ms,
        )
    
    async def __start_producer(self) -> None:
        logger.info(f"[ADAPTER][BROKER][ACKS: {self._producer_settings.acks}]")
        self.__create_producer()
        await self._producer.start()
    
    async def __start_consumer(self) -> None:
        logger.info(f"[ADAPTER][BROKER][GROUP ID: {self._consumer_settings.group_id}]")
        self.__create_consumer()
        await self._consumer.start()
        logger.info(f"[ADAPTER][BROKER][TOPICS: {await self._consumer.topics()}]")
        # logger.info(f"[ADAPTER][BROKER][ASSIGNED PARTITIONS: {self._consumer.assignment()}]")
        
    async def connect(self) -> None:
        """Connect the producer and consumer."""
        logger.info(f"[ADAPTER][BROKER][BOOTSTRAP SERVERS: {self._producer_settings.bootstrap_servers}]")
        if self._producer_settings is not None:
            await self.__start_producer()
        if self._consumer_settings is not None:
            await self.__start_consumer()
    
    @property
    def producer(self) -> AIOKafkaProducer:
        """Get the producer."""
        return self._producer
    
    @property
    def consumer(self) -> AIOKafkaConsumer:
        """Get the consumer."""
        return self._consumer
    
    async def __disconnect_producer(self) -> None:
        """Disconnect the producer."""
        if self._producer is not None:
            await self._producer.flush()
            await self._producer.stop()
            self._producer = None

    async def __disconnect_consumer(self) -> None:
        """Disconnect the consumer."""
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
        
    async def disconnect(self) -> None:
        """Disconnect the producer and consumer."""
        await self.__disconnect_producer()
        await self.__disconnect_consumer()
