from enum import StrEnum


class BrokerKafkaAcks(StrEnum):
    """Valid values for Kafka Producer ACKS."""
    
    ALL = "all"
    ZERO = "0"
    ONE = "1"
