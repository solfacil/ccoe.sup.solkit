import json
from typing import Any, Callable

from aiokafka.structs import ConsumerRecord

from .adapter import BrokerKafkaAdapter


class BrokerRepository:
    def __init__(self, adapter: BrokerKafkaAdapter) -> None:
        self._adapter = adapter
        
    @staticmethod
    def __parse_message_key(key: str) -> bytes:
        return bytes(key, "utf-8")
    
    @staticmethod
    def __parse_message_value(message: dict[str, Any]) -> bytes:
        return bytes(json.dumps(message), "utf-8")

    # @property
    # def __headers(self) -> list[tuple[str, bytes]]:
    #     return [
    #         ('X-Correlation-ID', bytes(correlation_id_context.get(), 'utf-8')),
    #     ]
    
    async def produce(self, topic: str, key: str, message: dict[str, Any]) -> None:
        return await self._adapter._producer.send_and_wait(
            topic=topic, 
            key=self.__parse_message_key(key),
            value=self.__parse_message_value(message),
            # headers=self.__headers,
        )
    
    async def consume(self, func: Callable[[ConsumerRecord], None]) -> None:
        async for message in self._adapter._consumer:
            await func(message)

    # async def healthcheck(self) -> None:
    #     producer = await self._adapter._producer.send_and_wait("healthcheck", "healthcheck")
    #     consumer = self._adapter._consumer.subscription()  # list topics subscribed
    #     consumer = self._adapter._consumer.assignment()  # list partitions assigned
    #     return producer and consumer
