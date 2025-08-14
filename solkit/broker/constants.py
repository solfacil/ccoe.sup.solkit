from enum import StrEnum

BROKER_HEARTBEAT_PER_SESSION = 4
BROKER_RETRY_SUFFIX = '-RETRY-'
BROKER_DEAD_LETTER_QUEUE_SUFFIX = '-DLQ'
BROKER_TOPIC_PATTERN = r'^[a-z-.]+$'

class BrokerKafkaAcks(StrEnum):
    """Valid values for Kafka Producer ACKS."""
    ALL = "all"
    ZERO = "0"
    ONE = "1"
