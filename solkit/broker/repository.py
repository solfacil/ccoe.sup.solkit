import asyncio
import datetime
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
    
    def __init__(self, adapter: BrokerKafkaAdapter, metadata: dict[str, Any] | None = None) -> None:
        """Initialize the broker repository."""
        self._adapter = adapter
        self._common_metadata = metadata
    
    @staticmethod
    def __parse_message_key(key: str | bytes) -> bytes:
        """Parse the message key."""
        if isinstance(key, str):
            return bytes(key, "utf-8")
        return key
    
    @staticmethod
    def __parse_message_value(data: dict[str, Any], metadata: dict[str, Any]) -> bytes:
        """Concatenate the data and metadata into a bytes object."""
        return bytes(json.dumps({"data": data, "metadata": metadata}), "utf-8")

    @staticmethod
    def __unparse_message_value(value: bytes) -> tuple[dict[str, Any], dict[str, str]]:
        """Unparse the value into a tuple of data and metadata."""
        value_dict: dict = json.loads(value.decode("utf-8"))
        return value_dict.get("data", {}), value_dict.get("metadata", {})
    
    @staticmethod
    def __set_correlation_id() -> list[tuple[str, bytes]]:
        """Set the correlation id in the headers."""
        headers = []
        if correlation_id := get_trace_correlation_id():
            headers.append((CORRELATION_ID_HEADER, bytes(correlation_id, 'utf-8')))
        return headers
    
    @staticmethod
    def __get_correlation_id(message: ConsumerRecord) -> str | None:
        """Get the correlation id from the headers."""
        correlation_id = None
        for header in message.headers:
            if header[0] == CORRELATION_ID_HEADER:
                correlation_id = header[1].decode("utf-8")
                set_trace_correlation_id(correlation_id)
                break
        return correlation_id
    
    @staticmethod
    def __next_retry_topic(topic: str, retry_max_times: int) -> str | None:
        """Get the next retry topic."""
        if topic.find(BROKER_RETRY_SUFFIX) == -1 and topic.find(BROKER_DEAD_LETTER_QUEUE_SUFFIX) == -1:
            return topic + BROKER_RETRY_SUFFIX + "1"
        
        elif topic.find(BROKER_RETRY_SUFFIX) > 0:
            topic_name, retry_attempt = topic.split(BROKER_RETRY_SUFFIX)
            retry_attempt = int(retry_attempt)

            if retry_attempt < retry_max_times:
                return topic_name + BROKER_RETRY_SUFFIX + f"{retry_attempt + 1}"
            else:
                return topic_name + BROKER_DEAD_LETTER_QUEUE_SUFFIX
        else:
            return None
    
    def __concat_metadata(self, topic: str, metadata: dict[str, Any] | None) -> dict[str, Any]:
        """Concatenate the metadata."""
        producer_metadata = {topic.lower(): datetime.datetime.now(datetime.UTC).isoformat()}
        if self._common_metadata:
            producer_metadata.update(self._common_metadata)
        if metadata:
            producer_metadata.update(metadata)
        return producer_metadata
    
    async def produce(
        self,
        topic: str,
        key: str | bytes,
        value: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Produce a message to a Kafka topic."""
        producer_metadata = self.__concat_metadata(topic, metadata)
            
        await self._adapter.producer.send_and_wait(
            topic=topic, 
            key=self.__parse_message_key(key), 
            value=self.__parse_message_value(value, producer_metadata), 
            headers=self.__set_correlation_id(),
        )
        logger.info(f"[BROKER][REPOSITORY][PRODUCE - TOPIC: {topic} - KEY: {key}]")

    async def consume(self, func: Callable[[ConsumerRecord], Awaitable[None]], wait_time: int = 3) -> None:
        """Consume messages from a Kafka topic."""
        async for message in self._adapter.consumer:
            # message: ConsumerRecord
            self.__get_correlation_id(message)
            try:
                logger.info(f"[BROKER][REPOSITORY][CONSUME - TOPIC: {message.topic} - KEY: {message.key}]")
                await func(message)
            # except DLQMessageException as err:
            except Exception as err:
                logger.error(f"[BROKER][REPOSITORY][CONSUME - ERROR: {err}]")
                
                if next_retry_topic := self.__next_retry_topic(message.topic, self._adapter._consumer_settings.retry_max_times):
                    logger.info(f"[BROKER][REPOSITORY][RETRY - TOPIC: {next_retry_topic} - KEY: {message.key} - WAIT: {wait_time}]")
                    await asyncio.sleep(wait_time)
                    value, metadata = self.__unparse_message_value(message.value)
                    metadata.update({"error": repr(err)})
                    await self.produce(
                        topic=next_retry_topic, 
                        key=message.key, 
                        value=value, 
                        metadata=metadata,
                    )
            finally:
                await self._adapter.consumer.commit()
                logger.info(f"[BROKER][REPOSITORY][COMMIT - TOPIC: {message.topic} - KEY: {message.key}]")

    # async def healthcheck(self) -> None:
    #     producer = await self._adapter._producer.send_and_wait("healthcheck", "healthcheck")
    #     consumer = self._adapter._consumer.subscription()  # list topics subscribed
    #     consumer = self._adapter._consumer.assignment()  # list partitions assigned
    #     return producer and consumer


# "TEST"           TEST, 0   
# "TEST-RETRY-1"   TEST, 1
# "TEST-RETRY-2"   TEST, 2
# "TEST-RETRY-3"   TEST, 3
# "TEST-DLQ"       TEST, -1
