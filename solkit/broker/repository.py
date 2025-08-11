import json
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka.structs import ConsumerRecord

from solkit.common.trace_correlation_id import (
    CORRELATION_ID_HEADER,
    get_trace_correlation_id,
    set_trace_correlation_id,
)

from .adapter import BrokerKafkaAdapter


class BrokerRepository:
    """Broker repository."""
    
    def __init__(self, adapter: BrokerKafkaAdapter) -> None:
        """Initialize the broker repository."""
        self._adapter = adapter
        
    @staticmethod
    def __parse_message_key(key: str) -> bytes:
        """Parse the message key."""
        return bytes(key, "utf-8")
    
    @staticmethod
    def __parse_message_value(message: dict[str, Any]) -> bytes:
        """Parse the message value."""
        return bytes(json.dumps(message), "utf-8")

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
    
    async def produce(self, topic: str, key: str, message: dict[str, Any]) -> None:
        """Produce a message to a Kafka topic."""
        return await self._adapter.producer.send_and_wait(
            topic=topic, 
            key=self.__parse_message_key(key),
            value=self.__parse_message_value(message),
            headers=self.__headers,
        )
    
    async def consume(self, func: Callable[[ConsumerRecord], Awaitable[None]]) -> None:
        """Consume messages from a Kafka topic."""
        async for message in self._adapter.consumer:
            self.__get_correlation_id(message)
            await func(message)

    # async def healthcheck(self) -> None:
    #     producer = await self._adapter._producer.send_and_wait("healthcheck", "healthcheck")
    #     consumer = self._adapter._consumer.subscription()  # list topics subscribed
    #     consumer = self._adapter._consumer.assignment()  # list partitions assigned
    #     return producer and consumer
