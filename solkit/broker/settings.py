from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from .constants import BrokerKafkaAcks


class BrokerKafkaSettings(BaseSettings):
    """Base settings for Kafka."""
    
    bootstrap_servers: str = Field(
        default=...,
        description="Kafka bootstrap servers",
        validation_alias="BROKER_BOOTSTRAP_SERVERS"
    )
    request_timeout_ms: int = Field(
        default=5000,
        description="Kafka request timeout ms",
        validation_alias="BROKER_REQUEST_TIMEOUT_MS"
    )


class BrokerKafkaConsumerSettings(BrokerKafkaSettings):
    """Consumer settings for Kafka."""
    
    topics: str = Field(
        default=...,
        description="Kafka topics",
        validation_alias="BROKER_TOPICS"
    )
    group_id: str = Field(
        default=...,
        description="Kafka group id",
        validation_alias="BROKER_GROUP_ID"
    )
    # enable_auto_commit: bool = Field(
    #     default=False,
    #     description="Kafka enable auto commit",
    #     validation_alias="BROKER_ENABLE_AUTO_COMMIT"
    # )
    max_poll_records: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Kafka max poll records",
        validation_alias="BROKER_MAX_POLL_RECORDS"
    )
    max_poll_interval_ms: int = Field(
        default=(5*60*1000),
        description="Kafka max poll interval ms",
        validation_alias="BROKER_MAX_POLL_INTERVAL_MS"
    )
    heartbeat_interval_ms: int = Field(
        default=(15*1000),
        description="Kafka heartbeat interval ms",
        validation_alias="BROKER_HEARTBEAT_INTERVAL_MS"
    )
    session_timeout_ms: int = Field(
        default=(90*1000),
        description="Kafka session timeout ms",
        validation_alias="BROKER_SESSION_TIMEOUT_MS"
    )
    consumer_timeout_ms: int = Field(
        default=200,
        description="Kafka consumer timeout ms",
        validation_alias="BROKER_CONSUMER_TIMEOUT_MS"
    )
    # rebalance_timeout_ms: int = Field(
    #     default=...,
    #     description="Kafka rebalance timeout ms",
    #     validation_alias="BROKER_REBALANCE_TIMEOUT_MS"
    # )
    # isolation_level: str = Field(
    #     default=...,
    #     description="Kafka isolation level",
    #     validation_alias="BROKER_ISOLATION_LEVEL"
    # )
    
    def parsed_topics(self) -> list[str]:
        """Parse topics."""
        return self.topics.split(",") if self.topics.find(",") > 0 else [self.topics]
    
    @model_validator(mode="after")
    def validate_kafka_session_pool_timeouts(self) -> Self:
        """Validate Kafka session and pool timeouts."""
        if self.max_poll_interval_ms > self.session_timeout_ms:
            raise ValueError("Kafka session and pool timeouts are not valid")
        return self
        
    @model_validator(mode="after")
    def validate_kafka_session_heartbeat(self) -> Self:
        """Validate Kafka session heartbeat.
        
        - each session must have at least 3 heartbeat to ensure consumers it's alive
        """
        if self.session_timeout_ms / self.heartbeat_interval_ms < 3:
            raise ValueError("Kafka session heartbeat is not valid")
        return self


class BrokerKafkaProducerSettings(BrokerKafkaSettings):
    """Producer settings for Kafka."""
    
    acks: BrokerKafkaAcks = Field(
        default=BrokerKafkaAcks.ALL,
        description="Kafka acks",
        validation_alias="BROKER_ACKS"
    )
    connections_max_idle_ms: int = Field(
        default=10000,
        description="Kafka connections max idle ms",
        validation_alias="BROKER_CONNECTIONS_MAX_IDLE_MS"
    )

    def parsed_acks(self) -> int | str:
        """Parse ACKS value to return 0 or 1 as int and 'all' as string."""
        return str(self.acks.value) if self.acks == BrokerKafkaAcks.ALL else int(self.acks.value)
