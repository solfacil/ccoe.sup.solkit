from pydantic import Field, field_validator
from pydantic.types import PositiveInt
from pydantic_settings import BaseSettings

from .constants import CACHE_SETTINGS_PREFIX, CacheDeploymentMode


class CacheModeSettings(BaseSettings):
    """Cache deployment mode settings."""
    
    deployment_mode: CacheDeploymentMode = Field(
        default=...,
        description="Redis mode",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_DEPLOYMENT_MODE"
    )


class CacheRedisSettings(CacheModeSettings):
    """Cache Redis settings."""
    
    host: str = Field(
        default=...,
        description="Redis cluster host address",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_HOST"
    )
    port: PositiveInt = Field(
        default=6379,
        description="Redis cluster port number",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_PORT"
    )
    max_connections: PositiveInt = Field(
        default=10,
        description="Maximum number of connections in the pool",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_MAX_CONNECTIONS"
    )
    socket_timeout: PositiveInt = Field(
        default=5,
        description="Socket timeout in seconds",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_SOCKET_TIMEOUT"
    )
    socket_connect_timeout: PositiveInt = Field(
        default=5,
        description="Socket connection timeout in seconds",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_SOCKET_CONNECT_TIMEOUT"
    )
    socket_keepalive: bool = Field(
        default=True,
        description="Enable socket keepalive",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_SOCKET_KEEPALIVE"
    )
    health_check_interval: PositiveInt = Field(
        default=10,
        description="Health check interval in seconds",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_HEALTH_CHECK_INTERVAL"
    )
    retry_max_attempts: PositiveInt = Field(
        default=3,
        description="Maximum number of retry attempts",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_RETRY_MAX_ATTEMPTS"
    )
    
    @property
    def build_uri(self) -> str:
        """Builds the Redis URI based on the settings."""
        return f"redis://{self.host}:{self.port}/{self.__getattribute__('db')}"


class CacheRedisClusterSettings(CacheRedisSettings):
    """Cache Redis cluster settings."""
    
    db: int | None = Field(
        default=0,
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_DB"
    )
    read_from_replicas: bool = Field(
        default=True,
        description="Allow reading from replica nodes",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_READ_FROM_REPLICAS"
    )
    require_full_coverage: bool = Field(
        default=False,
        description="Require full cluster coverage",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_REQUIRE_FULL_COVERAGE"
    )
    
    @field_validator("db")
    @classmethod
    def validate_cluster_db(cls, value: int | None) -> int | None:
        """Validate the cluster database number."""
        if value is not None or value != 0:
            raise ValueError("redis.exceptions.RedisClusterException: Argument 'db' must be 0 or None in cluster mode")
        return value


class CacheRedisSingleNodeSettings(CacheRedisSettings):
    """Cache Redis single node settings."""
    
    db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number (0-15)",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_DB"
    )
    retry_on_timeout: bool = Field(
        default=True,
        description="Retry commands on timeout",
        validation_alias=f"{CACHE_SETTINGS_PREFIX}_RETRY_ON_TIMEOUT"
    )
