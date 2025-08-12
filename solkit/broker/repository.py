import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka.structs import ConsumerRecord

from solkit.common.trace_correlation_id import (
    CORRELATION_ID_HEADER,
    get_trace_correlation_id,
    set_trace_correlation_id,
)

from .adapter import BrokerKafkaAdapter
from .constants import BROKER_DEAD_LETTER_QUEUE_SUFFIX, BROKER_RETRY_SUFFIX

logger = logging.getLogger(__name__)


class BrokerRepository:
    """Broker repository."""
    
    def __init__(self, adapter: BrokerKafkaAdapter) -> None:
        """Initialize the broker repository."""
        self._adapter = adapter
        
    @staticmethod
    def __parse_message_key(key: str | bytes) -> bytes:
        """Parse the message key."""
        if isinstance(key, str):
            return bytes(key, "utf-8")
        return key
    
    @staticmethod
    def __parse_message_value(message: dict[str, Any] | bytes) -> bytes:
        """Parse the message value."""
        if isinstance(message, dict):
            return bytes(json.dumps(message), "utf-8")
        return message
    
    # @staticmethod
    # def __unparse_message_value(message: bytes) -> dict[str, Any]:
    #     """Unparse the message value."""
    #     return json.loads(message.decode("utf-8"))

    @property
    def __headers(self) -> list[tuple[str, bytes]]:
        headers = []
        if correlation_id := get_trace_correlation_id():
            headers.append((CORRELATION_ID_HEADER, bytes(correlation_id, 'utf-8')))
        return headers
    
    @staticmethod
    def __get_correlation_id(message: ConsumerRecord) -> None:
        for header in message.headers:
            if header[0] == CORRELATION_ID_HEADER:
                set_trace_correlation_id(header[1].decode("utf-8"))
                break
    
    async def produce(self, topic: str, key: str | bytes, message: dict[str, Any] | bytes) -> None:
        """Produce a message to a Kafka topic."""
        await self._adapter.producer.send_and_wait(
            topic=topic, 
            key=self.__parse_message_key(key), 
            value=self.__parse_message_value(message), 
            headers=self.__headers,
        )
        logger.info(f"[BROKER][REPOSITORY][PRODUCE - TOPIC: {topic} - KEY: {key}]")
    
    def __get_retry_topic(self, topic: str, retry_max_times: int) -> str | None:
        if topic.find(BROKER_RETRY_SUFFIX) == -1 and topic.find(BROKER_DEAD_LETTER_QUEUE_SUFFIX) == -1:
            return topic + BROKER_RETRY_SUFFIX + "1"
        
        elif topic.find(BROKER_RETRY_SUFFIX) > 0:
            topic_name, retry_attempt = topic.split(BROKER_RETRY_SUFFIX)
            retry_attempt = int(retry_attempt)
            
            if retry_attempt < retry_max_times:
                return topic_name + BROKER_RETRY_SUFFIX + f"{retry_attempt + 1}"
            else:
                return topic_name + BROKER_DEAD_LETTER_QUEUE_SUFFIX
        
        elif topic.find(BROKER_DEAD_LETTER_QUEUE_SUFFIX) > 0:
            return None
        
        return None

    async def consume(self, func: Callable[[ConsumerRecord], Awaitable[None]]) -> None:
        """Consume messages from a Kafka topic."""
        async for message in self._adapter.consumer:
            self.__get_correlation_id(message)
            try:
                logger.info(f"[BROKER][REPOSITORY][CONSUME - TOPIC: {message.topic} - KEY: {message.key}]")
                await func(message)
            except Exception as e:
                logger.error(f"[BROKER][REPOSITORY][CONSUME - ERROR: {e}]")
                if retry_topic := self.__get_retry_topic(
                    message.topic,
                    self._adapter._consumer_settings.retry_max_times,
                ):
                    await self.produce(topic=retry_topic, key=message.key, message=message.value)
            finally:
                await self._adapter.consumer.commit()
                logger.info(f"[BROKER][REPOSITORY][COMMIT - TOPIC: {message.topic} - KEY: {message.key}]")

    # async def healthcheck(self) -> None:
    #     producer = await self._adapter._producer.send_and_wait("healthcheck", "healthcheck")
    #     consumer = self._adapter._consumer.subscription()  # list topics subscribed
    #     consumer = self._adapter._consumer.assignment()  # list partitions assigned
    #     return producer and consumer
