
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


async def main() -> None:
    await broker_kafka_adapter.connect()
    broker = BrokerRepository(broker_kafka_adapter)
    await broker.consume()


if __name__ == "__main__":
    asyncio.run(main())
```

Expected Logs for Producer

```bash
application         | INFO:__main__:Starting consumer
application         | INFO:solkit.broker.adapter:[ADAPTER][BROKER][BOOTSTRAP SERVERS: kafka-broker-one:9092,kafka-broker-two:9093,kafka-broker-three:9094]
application         | INFO:solkit.broker.adapter:[ADAPTER][BROKER][ACKS: all]
```

Expected Logs for Consumer

```bash
application         | INFO:__main__:Starting consumer
application         | INFO:solkit.broker.adapter:[ADAPTER][BROKER][BOOTSTRAP SERVERS: kafka-broker-one:9092,kafka-broker-two:9093,kafka-broker-three:9094]
application         | INFO:solkit.broker.adapter:[ADAPTER][BROKER][ACKS: all]
application         | INFO:solkit.broker.adapter:[ADAPTER][BROKER][GROUP ID: app]
application         | INFO:aiokafka.consumer.subscription_state:Updating subscribed topics to: frozenset({'test-DLQ', 'test', 'test-RETRY-1', 'test-RETRY-2', 'test-RETRY-3'})
```

## Configuration

### Common Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| bootstrap_servers            | BROKER_BOOTSTRAP_SERVERS           | Kafka bootstrap servers                   |
| request_timeout_ms           | BROKER_REQUEST_TIMEOUT_MS          | Kafka request timeout in milliseconds     |

### Consumer Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| topics                       | BROKER_TOPICS                      | Kafka topics (comma-separated)            |
| group_id                     | BROKER_GROUP_ID                    | Kafka consumer group ID                   |
| max_poll_records             | BROKER_MAX_POLL_RECORDS            | Maximum number of records per poll (1-500)|
| max_poll_interval_ms         | BROKER_MAX_POLL_INTERVAL_MS        | Maximum poll interval in milliseconds     |
| heartbeat_interval_ms        | BROKER_HEARTBEAT_INTERVAL_MS       | Heartbeat interval in milliseconds        |
| session_timeout_ms           | BROKER_SESSION_TIMEOUT_MS          | Session timeout in milliseconds           |
| retry_max_times              | BROKER_RETRY_MAX_TIMES             |                                           |
| enable_auto_commit           |                                    |                                           |

### Producer Parameters

| Parameter                    | Environment Variable               | Definition                                |
|------------------------------|------------------------------------|-------------------------------------------|
| acks                         | BROKER_ACKS                        | Kafka acknowledgment level (all, 0, 1)    |
| connections_max_idle_ms      | BROKER_CONNECTIONS_MAX_IDLE_MS     | Maximum idle time for connections in ms   |
