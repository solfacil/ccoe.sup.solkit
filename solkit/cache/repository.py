import json
from typing import Any

from redis.asyncio.client import Redis
from redis.asyncio.cluster import RedisCluster


class CacheRepository:
    """Cache repository."""

    def __init__(self, cache_session: Redis | RedisCluster) -> None:
        """Initialize the cache repository."""
        self._cache_session = cache_session

    @staticmethod
    def _encode(value: str) -> bytes:
        """Encode a value to a bytes."""
        return value.encode('utf-8')

    @staticmethod
    def _encode_hash_mapping(value: dict[str, Any]) -> str:
        """Encode a value to a string."""
        return json.dumps(value)

    @staticmethod
    def _decode(value: bytes) -> str:
        """Decode a value from a string."""
        return value.decode('utf-8')

    async def set_key(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set a value in the cache."""
        result = await self._cache_session.set(key, self._encode(value))
        if ttl:
            await self._cache_session.expire(key, ttl)
        return result

    async def get_key(self, key: str) -> str | None:
        """Get a value from the cache."""
        result = await self._cache_session.get(key)
        return self._decode(result) if result else None

    async def exists_key(self, *keys: str) -> bool:
        """Check if a value exists in the cache."""
        result = await self._cache_session.exists(*keys)
        return result > 0

    async def delete_key(self, *keys: str) -> bool:
        """Delete a value from the cache."""
        result = await self._cache_session.delete(*keys)
        return result > 0

    async def set_hash(self, name: str, mapping: dict[str, Any], ttl: int | None = None) -> bool:
        """Set a hash in the cache."""
        result = await self._cache_session.hset(name=name, mapping=mapping)  # type: ignore
        if ttl:
            await self._cache_session.expire(name, ttl)
        return result > 0

    async def get_hash(self, name: str, field: str) -> str | None:
        """Get a hash from the cache."""
        result = await self._cache_session.hget(name, field)  # type: ignore
        return self._decode(result) if result else None  # type: ignore

    async def exists_hash(self, name: str, field: str) -> bool:
        """Check if a hash exists in the cache."""
        return await self._cache_session.hexists(name, field)  # type: ignore

    async def delete_hash(self, name: str, field: str) -> bool:
        """Delete a hash from the cache."""
        result = await self._cache_session.hdel(name, field)  # type: ignore
        return result > 0

    async def healthcheck(self) -> tuple[bool, str | None]:
        """Check the health of the cache."""
        try:
            await self._cache_session.ping()
            return True, None
        except Exception as e:
            return False, str(e)
