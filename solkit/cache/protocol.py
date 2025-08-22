from typing import Any, Protocol, runtime_checkable

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster


@runtime_checkable
class CacheRepositoryProtocol(Protocol):
    """Cache repository protocol."""
    
    def __init__(self, cache_session: RedisCluster | Redis) -> None:
        """Initialize the cache repository."""
        ...
    
    async def set(self, key: str, value: dict[str, Any]) -> bool:
        """Set a value in the cache."""
        ...
    
    async def get(self, key: str) -> None | dict[str, Any]:
        """Get a value from the cache."""
        ...
    
    async def delete(self, keys: list[str]) -> str:
        """Delete a value from the cache."""
        ...
    
    async def exists(self, keys: list[str]) -> bool:
        """Check if a value exists in the cache."""
        ...
    
    async def expire(self, key: str, time: int) -> bool:
        """Set a value in the cache with an expiration time."""
        ...
    
    async def ttl(self, key: str) -> int:
        """Get the time to live of a value in the cache."""
        ...
    
    async def healthcheck(self) -> tuple[bool, str | None]:
        """Check the health of the cache."""
        ...
