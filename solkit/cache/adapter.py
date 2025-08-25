import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster
from redis.asyncio.connection import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from .constants import CacheDeploymentMode
from .settings import CacheModeSettings, CacheRedisClusterSettings, CacheRedisSingleNodeSettings

logger = logging.getLogger(__name__)


class CacheRedisAdapter:
    """Cache redis adapter."""

    @classmethod
    def single_node_config(cls) -> 'CacheRedisAdapter':
        """Create a single node cache adapter."""
        settings = CacheRedisSingleNodeSettings()
        return cls(settings)

    @classmethod
    def cluster_config(cls) -> 'CacheRedisAdapter':
        """Create a cluster cache adapter."""
        settings = CacheRedisClusterSettings()
        return cls(settings)

    @classmethod
    def config(cls) -> 'CacheRedisAdapter':
        """Create a cache adapter based on the deployment mode."""
        cache_mode_settings = CacheModeSettings()
        return (
            cls.cluster_config()
            if cache_mode_settings.deployment_mode == CacheDeploymentMode.CLUSTER
            else cls.single_node_config()
        )

    def __init__(self, settings: CacheRedisClusterSettings | CacheRedisSingleNodeSettings) -> None:
        """Initialize the cache adapter."""
        self._connection_pool: ConnectionPool
        self._single_node_connection: Redis
        self._cluster_connection: RedisCluster
        self._settings = settings

    @property
    def __retry_config(self) -> dict[str, Any]:
        retry_config = {
            'retry': Retry(ExponentialBackoff(), retries=self._settings.retry_max_attempts),
            'retry_on_error': [ConnectionError, TimeoutError],
        }
        return retry_config

    @property
    def __common_config(self) -> dict[str, Any]:
        common_config = {
            'host': self._settings.host,
            'port': self._settings.port,
            'db': self._settings.db,
            'socket_timeout': self._settings.socket_timeout,
            'socket_keepalive': self._settings.socket_keepalive,
            'socket_connect_timeout': self._settings.socket_connect_timeout,
            'max_connections': self._settings.max_connections,
            'health_check_interval': self._settings.health_check_interval,
        }
        return common_config

    @property
    def __cluster_config(self) -> dict[str, Any]:
        cluster_config = {
            **self.__common_config,
            **self.__retry_config,
            'read_from_replicas': self._settings.read_from_replicas,  # type: ignore
            'require_full_coverage': self._settings.require_full_coverage,  # type: ignore
        }
        return cluster_config

    @property
    def __single_node_config(self) -> dict[str, Any]:
        single_node_config = {
            **self.__common_config,
            'retry_on_timeout': self._settings.retry_on_timeout,  # type: ignore
        }
        return single_node_config

    def __create_cluster_connection(self) -> None:
        self._cluster_connection = RedisCluster(**self.__cluster_config)

    def __create_single_node_connection(self) -> None:
        self._connection_pool = ConnectionPool(**self.__single_node_config)
        self._single_node_connection = Redis(connection_pool=self._connection_pool)

    async def connect(self) -> None:
        """Connect to the cache."""
        logger.info(f'[ADAPTER][CACHE][CONNECTION URI: {self._settings.build_uri}]')
        logger.info(f'[ADAPTER][CACHE][CONNECTION MODE: {self._settings.deployment_mode.value.upper()}]')
        if self._settings.deployment_mode == CacheDeploymentMode.CLUSTER:
            self.__create_cluster_connection()
            logger.info(f'[ADAPTER][CACHE][CONNECTION ACTIVE: {await self._cluster_connection.ping()}]')
            logger.info(f'[ADAPTER][CACHE][CLUSTER NODES: {self._cluster_connection.get_nodes()}]')
        else:
            self.__create_single_node_connection()
            logger.info(f'[ADAPTER][CACHE][CONNECTION ACTIVE: {await self._single_node_connection.ping()}]')
            logger.info(f'[ADAPTER][CACHE][CONNECTION POOL ACTIVE: {self._connection_pool.can_get_connection()}]')

    async def __disconnect_cluster_connection(self) -> None:
        if self._cluster_connection:
            await self._cluster_connection.aclose()
            del self._cluster_connection

    async def __disconnect_single_node_connection(self) -> None:
        if self._connection_pool:
            await self._connection_pool.aclose()
            del self._connection_pool
            del self._single_node_connection

    async def disconnect(self) -> None:
        """Disconnect from the cache."""
        if self._settings.deployment_mode == CacheDeploymentMode.CLUSTER:
            await self.__disconnect_cluster_connection()
        else:
            await self.__disconnect_single_node_connection()
        logger.info('[ADAPTER][CACHE][DISCONNECTED]')

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Redis | RedisCluster, None]:
        """Get a session from the cache."""
        redis_connection = (
            self._cluster_connection
            if self._settings.deployment_mode == CacheDeploymentMode.CLUSTER
            else self._single_node_connection
        )
        async with redis_connection as session:
            yield session
