
# Python Broker - Kafka Adapter

## Documentations

[Kafka Documentation](https://kafka.apache.org/documentation/)

[AIOkafka](https://aiokafka.readthedocs.io/en/stable/index.html)

## Usage

```python
# broker/__init__.py
from solkit.broker import BrokerKafkaAdapter

broker_kafka_adapter = BrokerKafkaAdapter.config()
# or
broker_kafka_adapter = BrokerKafkaAdapter.producer_config()
```

```python
# service.py
from solkit.broker import BrokerRepository


class ConsumerService:
    def __init__(self, broker: BrokerRepository) -> None:
        self._broker = broker

    async def consume(self):
        await self._broker.consume(self.execute_something)

    async def execute_something(self, message) -> None:
        print(message, flush=True)
        print(message.__dict__, flush=True)
        
```

```python
# consumer.py
import asyncio

from solkit.broker import BrokerRepository

from adapters.broker import broker_kafka_adapter, get_broker_session
from apps.consumer.service import ConsumerService


async def consumer(broker_session) -> None:
    service = ConsumerService(BrokerRepository(broker_session))
    await service.consume()


async def main() -> None:
    await broker_kafka_adapter.connect()
    await consumer(await get_broker_session())


if __name__ == "__main__":
    asyncio.run(main())
```

Expected Logs for Producer

```bash

```

Expected Logs for Consumer

```bash

```

## Configuration

### Common Parameters

| Parameter              | Environment Variable         | Definition                                |
|------------------------|------------------------------|-------------------------------------------|
| bootstrap_servers      | BROKER_BOOTSTRAP_SERVERS     | Kafka bootstrap servers                   |
| request_timeout_ms     | BROKER_REQUEST_TIMEOUT_MS    | Kafka request timeout in milliseconds     |

### Consumer Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| topics                       | BROKER_TOPICS                      | Kafka topics (comma-separated)            |
| group_id                     | BROKER_GROUP_ID                    | Kafka consumer group ID                   |
| max_poll_records             | BROKER_MAX_POLL_RECORDS            | Maximum number of records per poll (1-500)|
| max_poll_interval_ms         | BROKER_MAX_POLL_INTERVAL_MS        | Maximum poll interval in milliseconds     |
| heartbeat_interval_ms        | BROKER_HEARTBEAT_INTERVAL_MS       | Heartbeat interval in milliseconds        |
| session_timeout_ms           | BROKER_SESSION_TIMEOUT_MS          | Session timeout in milliseconds           |
| consumer_timeout_ms          | BROKER_CONSUMER_TIMEOUT_MS         | Consumer timeout in milliseconds          |

### Producer Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| acks                         | BROKER_ACKS                        | Kafka acknowledgment level (all, 0, 1)    |
| connections_max_idle_ms      | BROKER_CONNECTIONS_MAX_IDLE_MS     | Maximum idle time for connections in ms   |
