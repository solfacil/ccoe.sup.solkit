from abc import ABC, abstractmethod

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster

from .settings import CacheRedisSettings


class CacheAdapterAbstract(ABC):
    """Cache adapter abstract class."""

    @abstractmethod
    @classmethod
    def config(cls) -> None:
        """Configure the cache adapter."""
        raise NotImplementedError()

    def __init__(self, settings: CacheRedisSettings) -> None:
        """Initialize the cache adapter."""
        self._settings = settings

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the cache."""
        raise NotImplementedError()

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the cache."""
        raise NotImplementedError()

    @abstractmethod
    async def get_session(self) -> Redis | RedisCluster:
        """Get a session from the cache."""
        raise NotImplementedError()
