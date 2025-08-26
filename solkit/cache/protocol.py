from typing import Any, Protocol, runtime_checkable

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster


@runtime_checkable
class CacheRepositoryProtocol(Protocol):
    """Cache repository protocol."""

    def __init__(self, cache_session: Redis | RedisCluster) -> None:
        """Initialize the cache repository."""
        ...

    async def set_key(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set a value in the cache."""
        ...

    async def get_key(self, key: str) -> str | None:
        """Get a value from the cache."""
        ...

    async def exists_key(self, *keys: str) -> bool:
        """Check if a value exists in the cache."""
        ...

    async def delete_key(self, *keys: str) -> bool:
        """Delete a value from the cache."""
        ...

    async def set_hash(self, name: str, mapping: dict[str, Any], ttl: int | None = None) -> bool:
        """Set a hash in the cache."""
        ...

    async def get_hash(self, name: str, field: str) -> str | None:
        """Get a hash from the cache."""
        ...

    async def exists_hash(self, name: str, field: str) -> bool:
        """Check if a hash exists in the cache."""
        ...

    async def delete_hash(self, name: str, field: str) -> bool:
        """Delete a hash from the cache."""
        ...

    async def healthcheck(self) -> tuple[bool, str | None]:
        """Check the health of the cache."""
        ...
