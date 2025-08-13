import re
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings

from .constants import (
    BROKER_DEAD_LETTER_QUEUE_SUFFIX,
    BROKER_HEARTBEAT_PER_SESSION,
    BROKER_RETRY_SUFFIX,
    BROKER_TOPIC_PATTERN,
    BrokerKafkaAcks,
)


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
    enable_auto_commit: bool = Field(
        default=False,
        description="Kafka enable auto commit",
        validation_alias="BROKER_ENABLE_AUTO_COMMIT"
    )
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
    retry_max_times: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Kafka retry max times",
        validation_alias="BROKER_RETRY_MAX_TIMES"
    )
    
    @staticmethod
    def __parse_topics(topics: str) -> list[str]:
        """Parse topics string into a list of topics."""
        return topics.split(",") if topics.find(",") > 0 else [topics]
    
    def __generate_retry_topics(self) -> list[str]:
        """Generate retry topics."""
        return [
            f"{topic}{BROKER_RETRY_SUFFIX}{i}" 
            for topic in self.__parse_topics(self.topics) 
            for i in range(1, self.retry_max_times + 1)
        ]

    def __generate_dead_letter_queue_topics(self) -> list[str]:
        """Generate dead letter queue topics."""
        return [
            f"{topic}{BROKER_DEAD_LETTER_QUEUE_SUFFIX}" 
            for topic in self.__parse_topics(self.topics)
        ]
    
    def get_topics(self) -> list[str]:
        """Create a list of topics with retry and dead letter queue topics."""
        topics = self.__parse_topics(self.topics)
        topics.extend(self.__generate_dead_letter_queue_topics())
        if self.retry_max_times > 0:
            topics.extend(self.__generate_retry_topics())
        return topics
    
    @field_validator("topics", mode="after")
    @classmethod
    def validate_topics_names(cls, topics: str) -> str:
        """Validate topics names with uppercase letters and hyphens."""
        for topic in cls.__parse_topics(topics):
            if not re.match(BROKER_TOPIC_PATTERN, topic):
                raise ValueError(
                    f"Topic '{topic}' must contain only uppercase letters and hyphens",
                    f"it must follow the regexpattern: {BROKER_TOPIC_PATTERN}"
                )
        return topics
    
    @model_validator(mode="after")
    def validate_session_pool_timeouts(self) -> Self:
        """Validate Kafka session and pool timeouts."""
        if self.max_poll_interval_ms < self.session_timeout_ms:
            raise ValueError("Kafka session max poll interval must be greater than session timeout")
        return self
        
    @model_validator(mode="after")
    def validate_session_heartbeat(self) -> Self:
        """Validate Kafka session heartbeat.
        
        - each session must have at least 3 heartbeat to ensure consumers it's alive
        """
        if (self.session_timeout_ms / self.heartbeat_interval_ms) < BROKER_HEARTBEAT_PER_SESSION:
            raise ValueError(
                f"Kafka heartbeat per session must be greater than or equal to {BROKER_HEARTBEAT_PER_SESSION}"
            )
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
